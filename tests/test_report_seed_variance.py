from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_seed_variance import load_metrics, seed_variance


def _write_run(run_dir: Path, *, event_f1: float, psds_1: float, psds_2: float) -> None:
    run_dir.mkdir(parents=True)
    manifest = {"complete": True}
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    evaluation = {
        "event_based_f1": {"f_measure": event_f1},
        "psds": {"psds_1": psds_1, "psds_2": psds_2},
    }
    (run_dir / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")


def test_load_metrics_reads_the_three_tracked_fields(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _write_run(run_dir, event_f1=0.5, psds_1=0.3, psds_2=0.7)

    metrics = load_metrics(run_dir)

    assert metrics == {"event_f1": 0.5, "psds_1": 0.3, "psds_2": 0.7}


def test_load_metrics_rejects_incomplete_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"complete": False}), encoding="utf-8")

    with pytest.raises(SystemExit, match="chưa hoàn tất"):
        load_metrics(run_dir)


def test_load_metrics_rejects_missing_evaluation_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"complete": True}), encoding="utf-8")

    with pytest.raises(SystemExit, match="evaluate_run"):
        load_metrics(run_dir)


def test_seed_variance_is_absolute_difference_per_metric() -> None:
    seed0 = {"event_f1": 0.5, "psds_1": 0.3, "psds_2": 0.7}
    seed1 = {"event_f1": 0.45, "psds_1": 0.35, "psds_2": 0.7}

    variance = seed_variance(seed0, seed1)

    assert variance == {
        "event_f1": pytest.approx(0.05),
        "psds_1": pytest.approx(0.05),
        "psds_2": 0.0,
    }
