"""ADR-0043 P4: recipe p4_gaineq passes the frame_mn guards that train_sed runs before training."""

import sys

import pytest

import scripts.train_sed as train_sed

ARGV = ["train_sed", "--encoder", "frame_mn", "--frame-mn-checkpoint", "x.pt",
        "--learning-rate", "0.0003", "--batch-size", "24", "--train-fixes",
        "--recipe", "p4_gaineq"]


def test_p4_recipe_passes_frame_mn_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ARGV)
    args = train_sed.parse_args()
    knobs = train_sed.resolve_recipe(args)
    train_sed.validate_track2b(args, knobs)
    assert knobs["gain_eq_p"] == 0.5
    assert "frame_mn" in train_sed.WAVEFORM_ENCODERS
    assert train_sed.FRAME_MN_RECIPES["p4_gaineq"] == train_sed.FRAME_MN_RECIPES["t2b"]
