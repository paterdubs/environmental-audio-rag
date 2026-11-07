"""O6 (ADR-0041 §12): served systems may override the members' window hop and merging."""

from __future__ import annotations

import pytest

from ml.evaluation.predictions import UNIFORM_WEIGHTING
from ml.inference.sed import MemberConfig, serving_config

BASE = MemberConfig(frame_rate=100.0, window_frames=1000, hop_frames=1000,
                    feature_set="logmel_panns_v1", input_kind="waveform_16k")


def test_no_serving_block_keeps_the_training_cut() -> None:
    assert serving_config(BASE, None) == (BASE, UNIFORM_WEIGHTING)


def test_b0_serving_block_sets_hop_and_triangular_merge() -> None:
    config, weighting = serving_config(
        BASE, {"hop_seconds": 5, "window_weighting": "triangular:0.3"})
    assert config.hop_frames == 500 and config.window_frames == 1000
    assert weighting == "triangular:0.3"


@pytest.mark.parametrize("serving", [{"hop_seconds": 0}, {"hop_seconds": 20},
                                     {"hop_seconds": 5, "window_weighting": "gaussian"}])
def test_invalid_serving_blocks_are_refused(serving: dict) -> None:
    with pytest.raises(ValueError):
        serving_config(BASE, serving)
