from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_rq1_delta import load_branch


def _write_run(run_dir: Path, *, weight_source: str, dirty: bool, f1: float) -> None:
    run_dir.mkdir(parents=True)
    manifest = {
        "complete": True,
        "config": {"weight_source": weight_source},
        "git": {"dirty": dirty},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    evaluation = {
        "event_based_f1": {"f_measure": f1},
        "event_based_f1_bootstrap": {"estimate": f1, "lower": f1 - 0.01, "upper": f1 + 0.01},
        "psds": {"psds_1": f1 * 2, "psds_2": f1 * 3},
    }
    (run_dir / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")


def test_load_branch_reads_metrics_verbatim(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _write_run(run_dir, weight_source="datasec:some-run", dirty=False, f1=0.5)

    branch = load_branch(run_dir, expected_weight_source_prefix="datasec")

    assert branch["event_f1"] == 0.5
    assert branch["psds_1"] == 1.0
    assert branch["psds_2"] == 1.5
    assert branch["git_dirty"] is False


def test_load_branch_rejects_incomplete_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"complete": False}), encoding="utf-8")

    with pytest.raises(SystemExit, match="chưa hoàn tất"):
        load_branch(run_dir)


def test_load_branch_rejects_wrong_weight_source(tmp_path: Path) -> None:
    """Guards against passing run_b/run_c in the wrong CLI position."""
    run_dir = tmp_path / "run"
    _write_run(run_dir, weight_source="audioset", dirty=False, f1=0.5)

    with pytest.raises(SystemExit, match="sai thứ tự"):
        load_branch(run_dir, expected_weight_source_prefix="datasec")


def test_load_branch_rejects_missing_evaluation_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"complete": True}), encoding="utf-8")

    with pytest.raises(SystemExit, match="evaluate_run"):
        load_branch(run_dir)
