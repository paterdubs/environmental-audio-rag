from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_rq1_multiseed import METRICS, is_dirty, load_metrics, summarize, welch_tests


def write_run(path: Path, complete: bool = True, name: str = "evaluation.json",
              per_class: dict | None = None, **values: float) -> None:
    path.mkdir()
    (path / "manifest.json").write_text(json.dumps({"complete": complete}), encoding="utf-8")
    per_class = per_class or {"birds": {"f_measure": 0.1}, "voices": {"f_measure": 0.3}}
    evaluation = {"event_based_f1": {"f_measure": values.get("event_f1", 0.1)},
                  "event_based_f1_per_class": per_class, "psds": {
        "psds_1": values.get("psds_1", 0.2), "psds_2": values.get("psds_2", 0.3)}}
    (path / name).write_text(json.dumps(evaluation), encoding="utf-8")


def test_load_and_summarize(tmp_path: Path) -> None:
    write_run(tmp_path / "r", event_f1=0.2, psds_1=0.4, psds_2=0.6)
    metrics = load_metrics(tmp_path / "r")
    assert summarize([metrics, metrics])["event_f1"]["mean"] == pytest.approx(0.2)


def test_macro_is_nan_ignoring_mean_of_per_class_f(tmp_path: Path) -> None:
    write_run(tmp_path / "r", per_class={"birds": {"f_measure": 0.1}, "voices": {"f_measure": 0.3},
                                         "horn": {"f_measure": float("nan")}})
    assert load_metrics(tmp_path / "r")["event_f1_macro"] == pytest.approx(0.2)


def test_reads_the_named_evaluation_file(tmp_path: Path) -> None:
    write_run(tmp_path / "r", name="evaluation_cv.json", event_f1=0.25)
    assert load_metrics(tmp_path / "r", "evaluation_cv.json")["event_f1"] == pytest.approx(0.25)
    with pytest.raises(SystemExit, match="evaluation.json"):
        load_metrics(tmp_path / "r")


def test_rejects_incomplete_or_missing_evaluation(tmp_path: Path) -> None:
    write_run(tmp_path / "bad", complete=False)
    with pytest.raises(SystemExit, match="complete=false"):
        load_metrics(tmp_path / "bad")
    missing = tmp_path / "missing"
    missing.mkdir()
    (missing / "manifest.json").write_text(json.dumps({"complete": True}), encoding="utf-8")
    with pytest.raises(SystemExit, match="evaluation.json"):
        load_metrics(missing)


def test_dirty_provenance_is_reported_but_not_rejected(tmp_path: Path) -> None:
    run = tmp_path / "dirty"
    write_run(run)
    (run / "manifest.json").write_text(
        json.dumps({"complete": True, "git": {"dirty": True}}), encoding="utf-8"
    )
    assert is_dirty(run)
    assert load_metrics(run)["event_f1"] == pytest.approx(0.1)


def test_welch_is_two_sided_and_finite() -> None:
    b = [{"event_f1_macro": 0.1, "event_f1": 0.1, "psds_1": 0.2, "psds_2": 0.3}] * 2
    c = [{"event_f1_macro": 0.2, "event_f1": 0.2, "psds_1": 0.4, "psds_2": 0.6}] * 2
    result = welch_tests(b, c)
    assert set(result) == set(METRICS) == {"event_f1_macro", "event_f1", "psds_1", "psds_2"}
    assert result["event_f1"]["p"] == pytest.approx(0.0)
