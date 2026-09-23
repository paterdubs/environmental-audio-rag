"""Test cho head phân cấp DataSEC + consistency loss (ADR-0015)."""

from pathlib import Path

import torch

from ml.models import (
    HierarchicalAudioClassifier,
    HierarchicalLossWeights,
    build_family_mask,
    hierarchical_loss,
    parent_consistency_rate,
)
from ml.models.audio import AudioEncoder
from ml.taxonomy import load_taxonomy

TAXONOMY = load_taxonomy(Path(__file__).resolve().parents[1] / "ml" / "configs" / "taxonomy.yaml")
COARSE_IDS = TAXONOMY.class_ids
SUBCLASS_IDS = tuple(subclass for item in TAXONOMY.classes for subclass in item.subclasses)


def test_family_mask_matches_taxonomy_cardinality() -> None:
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)

    assert mask.shape == (22, 28)
    assert int(mask.sum().item()) == 28  # mỗi subclass thuộc đúng một gia đình
    coarse_without_subclass = [
        index for index, item in enumerate(TAXONOMY.classes) if not item.subclasses
    ]
    assert len(coarse_without_subclass) == 12
    for index in coarse_without_subclass:
        assert mask[index].sum() == 0


def test_forward_returns_both_heads_with_correct_cardinality() -> None:
    model = HierarchicalAudioClassifier(AudioEncoder(), num_coarse=22, num_subclass=28)
    inputs = torch.rand(4, 1, 64, 50)

    coarse_logits, subclass_logits = model(inputs)

    assert coarse_logits.shape == (4, 22)
    assert subclass_logits.shape == (4, 28)


def test_ignored_subclass_targets_contribute_nothing_to_consistency() -> None:
    """12 lớp coarse không subclass: consistency loss chỉ tính trên phần còn lại."""
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)
    coarse_target = torch.tensor([0, 1])  # cả hai đều không có subclass (bells, ...)
    subclass_target = torch.full((2,), -1)
    coarse_logits = torch.rand(2, 22)
    subclass_logits = torch.rand(2, 28)

    result = hierarchical_loss(coarse_logits, subclass_logits, coarse_target, subclass_target, mask)

    assert torch.equal(result["consistency"], torch.zeros(()))


def test_consistency_loss_is_low_when_mass_sits_in_the_right_family() -> None:
    """Đặt gần hết xác suất vào đúng gia đình → -log(mass gần 1) gần 0."""
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)
    cicadas_index = COARSE_IDS.index("cicadas_and_crickets")
    family = mask[cicadas_index].nonzero(as_tuple=True)[0]
    assert len(family) == 2

    logits = torch.full((1, 28), -10.0)
    logits[0, family[0]] = 10.0  # gần hết softmax rơi vào đúng gia đình
    coarse_target = torch.tensor([cicadas_index])
    subclass_target = torch.tensor([int(family[0])])

    result = hierarchical_loss(
        torch.rand(1, 22), logits, coarse_target, subclass_target, mask
    )

    assert result["consistency"].item() < 0.01


def test_consistency_loss_is_high_when_mass_sits_in_the_wrong_family() -> None:
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)
    cicadas_index = COARSE_IDS.index("cicadas_and_crickets")
    workshop_index = COARSE_IDS.index("workshop")
    cicadas_family = mask[cicadas_index].nonzero(as_tuple=True)[0]
    workshop_family = mask[workshop_index].nonzero(as_tuple=True)[0]

    logits = torch.full((1, 28), -10.0)
    logits[0, workshop_family[0]] = 10.0  # xác suất rơi vào SAI gia đình
    coarse_target = torch.tensor([cicadas_index])
    subclass_target = torch.tensor([int(cicadas_family[0])])

    result = hierarchical_loss(
        torch.rand(1, 22), logits, coarse_target, subclass_target, mask
    )

    assert result["consistency"].item() > 5.0


def test_loss_weights_reject_negative_values() -> None:
    import pytest

    with pytest.raises(ValueError, match="âm"):
        HierarchicalLossWeights(subclass=-1.0)


def test_parent_consistency_rate_perfect_and_zero() -> None:
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)
    cicadas_index = COARSE_IDS.index("cicadas_and_crickets")
    family = mask[cicadas_index].nonzero(as_tuple=True)[0]
    coarse_prediction = torch.tensor([cicadas_index, cicadas_index])
    correct = torch.tensor([int(family[0]), int(family[0])])
    workshop_family = mask[COARSE_IDS.index("workshop")].nonzero(as_tuple=True)[0]
    wrong = torch.tensor([int(workshop_family[0]), int(workshop_family[0])])

    assert parent_consistency_rate(coarse_prediction, correct, mask) == 1.0
    assert parent_consistency_rate(coarse_prediction, wrong, mask) == 0.0


def test_parent_consistency_rate_excludes_coarse_without_a_family() -> None:
    """Coarse không subclass (vd `bells`) không có khái niệm "đúng gia đình"."""
    mask = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)
    bells_index = COARSE_IDS.index("bells")
    coarse_prediction = torch.tensor([bells_index])
    subclass_prediction = torch.tensor([0])

    rate = parent_consistency_rate(coarse_prediction, subclass_prediction, mask)

    assert rate != rate  # NaN — không có mẫu nào để tính
