"""ADR-0030 §5 selection rule, in code before the v2 numbers are in."""

import json
from pathlib import Path

import pytest

from scripts.select_sed_v2 import Candidate, best_config, model_count, select


def _candidate(label: str, mean: float, models: int = 1, sd: float = 0.02) -> Candidate:
    return Candidate(label, f"run_{label}", models, "theta", "global|25", mean, sd)


def test_highest_cv_mean_wins():
    winner, ranking, _ = select([_candidate("a", 0.15, 4), _candidate("b", 0.19),
                                 _candidate("c", 0.21, 3)])
    assert winner.label == "c"
    assert [c.label for c in ranking] == ["c", "b", "a"]


def test_exact_tie_goes_to_fewer_models():
    winner, _, _ = select([_candidate("ens", 0.2, 3), _candidate("single", 0.2, 1)])
    assert winner.label == "single"


def test_gap_within_fold_sd_is_flagged_not_called_better():
    _, _, note = select([_candidate("a", 0.200, sd=0.05), _candidate("b", 0.190)])
    assert "không" in note and "`b`" in note
    _, _, clear = select([_candidate("a", 0.300, sd=0.05), _candidate("b", 0.190)])
    assert clear == ""


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_best_config_looks_across_both_post_processing_families(tmp_path: Path):
    _write(tmp_path / "postproc_cv_selection.json",
           {"cv": {"global|25": {"mean": 0.19, "sd": 0.05},
                   "global|50": {"mean": 0.14, "sd": 0.04}}})
    _write(tmp_path / "sebb_cv_selection.json",
           {"cv": {"tau0.48_abs0.15": {"mean": 0.095, "sd": 0.03}}})
    assert best_config(tmp_path) == ("theta", "global|25", 0.19, 0.05)


def test_run_without_any_cv_is_refused(tmp_path: Path):
    with pytest.raises(SystemExit):
        best_config(tmp_path)


def test_model_count_reads_ensemble_members():
    assert model_count({"config": {"members": ["r1", "r2", "r3"]}}) == 3
    assert model_count({"config": {"seed": 1}}) == 1
