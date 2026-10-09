"""ADR-0041 O-D: BEATs fine-tuned end to end, its recipe and CLI guards."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest
import torch

from ml.models.beats_finetune import BeatsFinetuneSED
from ml.models.sed_factory import beats_finetune_model
from scripts.train_sed import (
    OD_MAX_BATCH,
    RECIPES,
    WAVEFORM_ENCODERS,
    validate_checkpoint_flags,
    validate_od,
)

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "checkpoints" / "BEATs_strong_1.pt"


@pytest.fixture(scope="module")
def model() -> BeatsFinetuneSED:
    torch.manual_seed(0)
    return BeatsFinetuneSED(21)


def test_ten_seconds_become_the_1000_frame_label_grid_and_everything_trains(model) -> None:
    model.eval()
    with torch.no_grad():
        logits = model(torch.randn(1, 160_000) * 0.1)
    assert tuple(logits.shape) == (1, 1000, 21)
    assert torch.equal(logits[:, 0::4], logits[:, 3::4])  # 250 steps repeated onto 10 ms
    assert all(p.requires_grad for p in model.parameters())


def test_train_mode_reaches_beats_unlike_the_frozen_embedder(model) -> None:
    model.train()
    try:
        assert model.encoder.training and model.encoder.beats.training
    finally:
        model.eval()
    assert not model.encoder.beats.training


def test_factory_and_encoder_attribute_for_the_optimizer() -> None:
    built = beats_finetune_model({"window_frames": 1000}, 21)
    assert isinstance(built, BeatsFinetuneSED) and hasattr(built, "encoder")
    head = {id(p) for p in built.head.parameters()}
    assert head.isdisjoint(id(p) for p in built.encoder.parameters())


@pytest.mark.skipif(not CHECKPOINT.exists(), reason="BEATs_strong_1.pt not downloaded")
def test_release_checkpoint_loads_strictly(model) -> None:
    report = model.load_pretrained(CHECKPOINT)
    assert report.loaded_tensors > 0 and report.ignored_keys


def _args(**overrides) -> Namespace:
    base = {"encoder": "beats_ft", "recipe": "od_beats", "evaluate_test": False,
            "batch_size": 8, "audioset_checkpoint": None, "datasec_checkpoint": None,
            "beats_checkpoint": Path("b.pt"), "frame_mn_checkpoint": None}
    base.update(overrides)
    return Namespace(**base)


def test_od_recipe_and_guards() -> None:
    knobs = dict(RECIPES["od_beats"])
    assert "beats_ft" in WAVEFORM_ENCODERS and knobs["encoder_learning_rate"] is not None
    validate_od(_args(), knobs)
    validate_checkpoint_flags(_args())
    with pytest.raises(SystemExit, match="batch-size"):
        validate_od(_args(batch_size=OD_MAX_BATCH + 4), knobs)
    with pytest.raises(SystemExit, match="batch-size"):
        validate_od(_args(batch_size=None), knobs)
    with pytest.raises(SystemExit, match="evaluate-test"):
        validate_od(_args(evaluate_test=True), knobs)
    with pytest.raises(SystemExit, match="lr encoder"):
        validate_od(_args(), {**knobs, "encoder_learning_rate": None})
    with pytest.raises(SystemExit, match="od_beats"):
        validate_od(_args(recipe="t2b"), knobs)
    with pytest.raises(SystemExit, match="cần --beats-checkpoint"):
        validate_checkpoint_flags(_args(beats_checkpoint=None))
