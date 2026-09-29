import json
from pathlib import Path

import pytest

from scripts.report_s13_test import load_results, render


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_report_keeps_cv_order_and_does_not_reselect_on_test(tmp_path: Path) -> None:
    selection = tmp_path / "selection.json"
    _write(
        selection,
        {
            "provisional": False,
            "selected": "f2",
            "ranking": [{"label": "f2", "rank": 1}, {"label": "f1", "rank": 2}],
        },
    )
    common = {
        "split": "test",
        "eval_set": "annotated",
        "n_recordings": 139,
        "event_based_f1_macro": {"f_measure": 0.1},
        "event_based_f1_bootstrap": {"lower": 0.05, "upper": 0.2},
        "psds": {"psds_1": 0.3, "psds_2": 0.7},
    }
    for label, micro in (("f2", 0.15), ("f1", 0.2)):
        _write(
            tmp_path / label / "evaluation_cv_annotated.json",
            {**common, "event_based_f1": {"f_measure": micro}},
        )

    selected, results = load_results(
        selection,
        [f"f2={tmp_path / 'f2'}", f"f1={tmp_path / 'f1'}"],
        "evaluation_cv_annotated.json",
    )
    report = render(selected, results)

    assert [item["label"] for item in results] == ["f2", "f1"]
    assert "Hệ thống đã khóa bằng CV dev: `f2`" in report
    assert "Test micro cao nhất: `f1`" in report
    assert "Không chọn lại sau khi xem test" in report


def test_report_rejects_non_annotated_evaluation(tmp_path: Path) -> None:
    selection = tmp_path / "selection.json"
    _write(
        selection,
        {"provisional": False, "selected": "f2", "ranking": [{"label": "f2", "rank": 1}]},
    )
    _write(tmp_path / "f2" / "evaluation_cv_annotated.json", {"split": "test", "eval_set": "all"})

    with pytest.raises(ValueError, match="không phải test annotated"):
        load_results(
            selection,
            [f"f2={tmp_path / 'f2'}"],
            "evaluation_cv_annotated.json",
        )
