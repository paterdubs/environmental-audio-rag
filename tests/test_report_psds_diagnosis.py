"""Script chẩn đoán PSDS (ADR-0048 §2): đi trọn họ θ và cSEBB trên dữ liệu tổng hợp, chỉ dev."""

import json

import numpy as np
import pytest

from scripts import report_psds_diagnosis as script
from scripts.report_psds_diagnosis_render import render_markdown

CLASSES = ("x", "y")
FR = 10.0
GRIDS = {"linear": (0.2, 0.5, 0.8), "log": (0.01, 0.1, 0.5)}


def _probabilities() -> dict[str, np.ndarray]:
    a = np.zeros((300, 2))
    a[20:60, 0] = 0.9  # x 2–6 s
    a[100:120, 1] = 0.6  # y 10–12 s
    a[200:210, 1] = 0.3  # y yếu, chỉ vào ở ngưỡng thấp
    return {"r1": a}


REFERENCE = {"r1": [{"event_label": "x", "onset": 2.0, "offset": 6.0},
                    {"event_label": "y", "onset": 10.0, "offset": 12.0}]}


def _theta_postproc(theta: float) -> dict:
    return {"per_class": {c: {"theta": theta, "median_w": 1, "d_min_s": 0.0, "g_max_s": 0.0,
                              "n_train_events": 5} for c in CLASSES}}


def test_theta_family_sweeps_one_threshold_for_all_classes_and_keeps_the_chosen_point():
    events_at, chosen = script.theta_family(_probabilities(), _theta_postproc(0.5),
                                            class_ids=CLASSES, frame_rate=FR)
    assert sorted(e["class_id"] for e in chosen["r1"]) == ["x", "y"]
    assert len(events_at(0.2)["r1"]) == 3  # thêm y yếu
    assert events_at(0.95)["r1"] == []


def test_system_result_has_every_grid_scenario_and_selected_position():
    events_at, chosen = script.theta_family(_probabilities(), _theta_postproc(0.5),
                                            class_ids=CLASSES, frame_rate=FR)
    result = script.system_result(events_at, chosen, reference=REFERENCE,
                                  durations={"r1": 30.0}, class_ids=CLASSES, grids=GRIDS)
    assert result["event_f1_micro"] == pytest.approx(1.0)
    assert set(result["grids"]) == {"linear", "log"}
    for grid in result["grids"].values():
        assert set(grid["scenarios"]) == {"psds_1", "psds_2", "psds_1_dtc05"}
        assert grid["n_points"] <= grid["n_grid"] == 3
    assert result["selected"]["psds_1"]["mean_tpr"] == pytest.approx(1.0)
    assert result["selected"]["psds_2"]["mean_efpr"] == pytest.approx(0.0)


def test_sebb_family_uses_box_confidence_thresholds(monkeypatch):
    def fake_params(postproc, *, eval_set):
        assert eval_set == "annotated"
        return "params", 0.5

    boxes = {"r1": ["strong", "weak"]}
    monkeypatch.setattr(script, "sebb_params", fake_params)
    monkeypatch.setattr(script, "sebb_candidates", lambda *a, **k: boxes)
    monkeypatch.setattr(script, "select_boxes", lambda cands, t: {"r1": [t]})
    events_at, chosen = script.sebb_family({}, {"family": "csebb", "eval_set": "annotated"},
                                           class_ids=CLASSES, frame_rate=FR)
    assert chosen == {"r1": [0.5]} and events_at(0.2) == {"r1": [0.2]}


def test_consistency_check_only_for_v1_on_all_and_compares_to_the_stored_dev_evaluation(tmp_path):
    stored = {"psds": {"psds_1": 0.1, "psds_2": 0.2}}
    (tmp_path / "dev_evaluation_cv.json").write_text(json.dumps(stored), encoding="utf-8")
    result = {"grids": {"linear": {"scenarios": {"psds_1": {"psds": 0.1},
                                                  "psds_2": {"psds": 0.2}}}}}
    assert script.consistency_check("v1", tmp_path, "all", result)["match"] is True
    assert script.consistency_check("v1", tmp_path, "annotated", result) is None
    assert script.consistency_check("v2", tmp_path, "all", result) is None
    result["grids"]["linear"]["scenarios"]["psds_2"]["psds"] = 0.25
    assert script.consistency_check("v1", tmp_path, "all", result)["match"] is False


def test_parse_systems_and_default_systems_match_adr_0048():
    assert script.parse_systems(["a=run:run/p.json"]) == {"a": ("run", "run/p.json")}
    with pytest.raises(SystemExit):
        script.parse_systems(["a=run"])
    assert set(script.DEFAULT_SYSTEMS) == {"v1", "v2", "f2", "B0"}
    assert script.DEFAULT_SYSTEMS["v2"][1].startswith("sed_ensemble_v2_20260926T150934Z/")


def test_render_reports_inputs_tables_and_verdicts():
    events_at, chosen = script.theta_family(_probabilities(), _theta_postproc(0.5),
                                            class_ids=CLASSES, frame_rate=FR)
    one = script.system_result(events_at, chosen, reference=REFERENCE, durations={"r1": 30.0},
                               class_ids=CLASSES, grids=GRIDS)
    out = {"eval_set": "annotated", "efpr_points": [5.0, 10.0, 30.0, 60.0, 100.0],
           "inputs": {k: {"predictions": "p", "postproc": "q", "family": "theta",
                          "n_recordings": 1} for k in ("v1", "v2")},
           "results": {"v1": one, "v2": one}, "consistency_checks": {},
           "hypotheses": {"candidate": "v2", "reference": "v1", "delta_event_f1_micro": 0.0,
                          "delta_psds_linear": {"psds_1": 0.0, "psds_2": 0.0},
                          "reproduced": False, "hypotheses": {}, "explained": False},
           "git": {"revision": "abc", "dirty": False}}
    text = render_markdown(out)
    assert "## PSDS theo lưới và biến thể" in text and "Tái hiện S21 trên dev:** không" in text
    assert "| x |" in text  # AUC theo lớp
