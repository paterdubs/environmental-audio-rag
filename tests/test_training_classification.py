"""Test cho vòng lặp huấn luyện phân cấp DataSEC (ADR-0019 D1).

Dữ liệu giả lập nhỏ, chạy trên CPU — không cần GPU hay dataset thật. Mục tiêu
là khoá đúng hợp đồng: batch 3 phần tử, loss giảm qua vài bước, chọn best
checkpoint theo `coarse_macro_f1`, không phải theo loss hay theo subclass.
"""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset

from ml.models import HierarchicalAudioClassifier, build_family_mask
from ml.models.audio import AudioEncoder
from ml.taxonomy import load_taxonomy
from ml.training.classification import (
    ClassificationTrainingConfig,
    run_hierarchical_epoch,
    train_hierarchical_classifier,
)

TAXONOMY = load_taxonomy(Path(__file__).resolve().parents[1] / "ml" / "configs" / "taxonomy.yaml")
COARSE_IDS = TAXONOMY.class_ids
SUBCLASS_IDS = tuple(subclass for item in TAXONOMY.classes for subclass in item.subclasses)
FAMILY_MASK = build_family_mask(TAXONOMY, COARSE_IDS, SUBCLASS_IDS)


class _SyntheticDataSEC(Dataset):
    """Sinh (x, coarse, subclass) ngẫu nhiên nhưng **học được**: mỗi coarse có
    một mẫu log-mel trung tâm cố định, item chỉ cộng thêm nhiễu nhỏ — đủ để
    loss giảm thật qua vài bước, không phải giảm vì trùng khớp ngẫu nhiên."""

    def __init__(self, size: int, *, seed: int) -> None:
        generator = torch.Generator().manual_seed(seed)
        self.coarse = torch.randint(0, 22, (size,), generator=generator)
        self.subclass = torch.full((size,), -1)
        has_subclass = FAMILY_MASK.sum(dim=-1) > 0
        for index, coarse_id in enumerate(self.coarse.tolist()):
            if has_subclass[coarse_id]:
                options = FAMILY_MASK[coarse_id].nonzero(as_tuple=True)[0]
                choice = options[torch.randint(0, len(options), (1,), generator=generator)]
                self.subclass[index] = int(choice)
        centers = torch.randn(22, 64, generator=generator) * 3.0
        noise = torch.randn(size, 1, 64, 20, generator=generator) * 0.1
        self.features = centers[self.coarse].reshape(size, 1, 64, 1) + noise

    def __len__(self) -> int:
        return len(self.coarse)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.features[index], self.coarse[index], self.subclass[index]


def _loaders(train_size: int, validation_size: int) -> dict[str, DataLoader]:
    return {
        "train": DataLoader(_SyntheticDataSEC(train_size, seed=1), batch_size=8, shuffle=True),
        "validation": DataLoader(
            _SyntheticDataSEC(validation_size, seed=2), batch_size=8, shuffle=False
        ),
    }


def test_run_hierarchical_epoch_consumes_three_element_batches() -> None:
    model = HierarchicalAudioClassifier(AudioEncoder(), num_coarse=22, num_subclass=28)
    loader = DataLoader(_SyntheticDataSEC(16, seed=3), batch_size=4)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)

    metrics = run_hierarchical_epoch(
        model,
        loader,
        device=torch.device("cpu"),
        coarse_weight=torch.ones(22),
        family_mask=FAMILY_MASK,
        supported_subclass_ids=set(range(28)),
        optimizer=optimizer,
        scaler=None,
    )

    assert {"coarse_macro_f1", "subclass_macro_f1_all", "parent_consistency_rate"} <= set(metrics)
    assert metrics["items"] == 16


def test_training_loss_decreases_over_a_few_epochs(tmp_path: Path) -> None:
    """Dữ liệu tổng hợp học được — nếu loss không giảm thì vòng lặp có lỗi thật."""
    model = HierarchicalAudioClassifier(AudioEncoder(), num_coarse=22, num_subclass=28)
    config = ClassificationTrainingConfig(epochs=5, batch_size=8, learning_rate=0.01)

    history, _ = train_hierarchical_classifier(
        model,
        _loaders(64, 16),
        device=torch.device("cpu"),
        coarse_weight=torch.ones(22),
        family_mask=FAMILY_MASK,
        supported_subclass_ids=set(range(28)),
        config=config,
        checkpoint_directory=tmp_path,
    )

    assert history[-1]["train"]["loss"] < history[0]["train"]["loss"]


def test_best_checkpoint_selected_by_coarse_macro_f1_not_loss(tmp_path) -> None:
    model = HierarchicalAudioClassifier(AudioEncoder(), num_coarse=22, num_subclass=28)
    config = ClassificationTrainingConfig(epochs=3, batch_size=8, learning_rate=0.01)

    history, best_path = train_hierarchical_classifier(
        model,
        _loaders(48, 16),
        device=torch.device("cpu"),
        coarse_weight=torch.ones(22),
        family_mask=FAMILY_MASK,
        supported_subclass_ids=set(range(28)),
        config=config,
        checkpoint_directory=tmp_path,
    )

    best_epoch = max(history, key=lambda record: record["validation"]["coarse_macro_f1"])
    checkpoint = torch.load(best_path, map_location="cpu", weights_only=True)
    expected = best_epoch["validation"]["coarse_macro_f1"]
    assert checkpoint["validation"]["coarse_macro_f1"] == expected
