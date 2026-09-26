"""ADR-0020: validation guards for encoder/checkpoint flag combinations."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from scripts.train_sed import (
    ENCODER_FEATURE_SET,
    ENCODER_FRAME_RATE,
    best_validation_metrics,
    validate_checkpoint_flags,
)


def _args(**overrides) -> Namespace:
    base = {"encoder": "audio", "audioset_checkpoint": None, "datasec_checkpoint": None}
    base.update(overrides)
    return Namespace(**base)


def test_audio_encoder_rejects_any_checkpoint_flag() -> None:
    with pytest.raises(SystemExit, match="chỉ dùng với --encoder panns"):
        validate_checkpoint_flags(_args(audioset_checkpoint=Path("x.pth")))
    with pytest.raises(SystemExit, match="chỉ dùng với --encoder panns"):
        validate_checkpoint_flags(_args(datasec_checkpoint=Path("x.pt")))


def test_audio_encoder_with_no_checkpoint_flags_is_fine() -> None:
    validate_checkpoint_flags(_args())  # must not raise


def test_panns_encoder_requires_exactly_one_checkpoint_flag() -> None:
    with pytest.raises(SystemExit, match="ĐÚNG MỘT"):
        validate_checkpoint_flags(_args(encoder="panns"))
    with pytest.raises(SystemExit, match="ĐÚNG MỘT"):
        validate_checkpoint_flags(
            _args(
                encoder="panns",
                audioset_checkpoint=Path("a.pth"),
                datasec_checkpoint=Path("b.pt"),
            )
        )


@pytest.mark.parametrize("flag", ["audioset_checkpoint", "datasec_checkpoint"])
def test_panns_encoder_accepts_exactly_one_flag(flag: str) -> None:
    validate_checkpoint_flags(_args(encoder="panns", **{flag: Path("x")}))  # must not raise


def test_encoder_feature_and_frame_rate_tables_cover_both_encoders() -> None:
    assert ENCODER_FEATURE_SET["audio"] == "logmel_v1"
    assert ENCODER_FEATURE_SET["panns"] == "logmel_panns_v1"
    assert ENCODER_FRAME_RATE["audio"] == 50.0
    assert ENCODER_FRAME_RATE["panns"] == 100.0


def _history(*, macro_f1: list[float], macro_average_precision: list[float]) -> list[dict]:
    return [
        {"validation": {"macro_f1": f1, "macro_average_precision": ap}}
        for f1, ap in zip(macro_f1, macro_average_precision, strict=True)
    ]


def test_best_validation_uses_macro_f1_for_v1_recipe() -> None:
    # v1 always selects on macro_f1 -- behaviour must be unchanged by nợ #24's fix.
    history = _history(macro_f1=[0.5, 0.7, 0.6], macro_average_precision=[0.9, 0.1, 0.2])
    metrics = best_validation_metrics(history, "macro_f1")
    assert metrics == {"select_metric": "macro_f1", "best_validation": 0.7}


def test_best_validation_uses_macro_average_precision_for_v2_recipe() -> None:
    # v2 selects checkpoints on macro-AP (ADR-0030 §1); before the fix this field always reported
    # max macro_f1 instead -- a number unrelated to which checkpoint `best.pt` actually is.
    history = _history(macro_f1=[0.5, 0.7, 0.6], macro_average_precision=[0.9, 0.1, 0.2])
    metrics = best_validation_metrics(history, "macro_average_precision")
    assert metrics == {"select_metric": "macro_average_precision", "best_validation": 0.9}
