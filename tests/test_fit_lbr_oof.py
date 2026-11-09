"""Luật chọn ADR-0045 §6, baseline cSEBB cross-fit và bảng báo cáo của scripts.fit_lbr_oof."""

import numpy as np
import pytest

from ml.postprocessing.lbr_crossfit import micro_f1_objective
from ml.postprocessing.sebb import SebbParams
from scripts import fit_lbr_oof as script

FR = 25.0
CLASSES = ("a", "b")


def results_with(micro: dict[str, float]) -> dict:
    return {name: {"f1": {"all": {"micro_f1": value}}} for name, value in micro.items()}


def delta(lower: float) -> dict:
    return {"estimate": lower + 0.01, "lower": lower, "upper": lower + 0.02, "baseline": "B0"}


def test_candidate_needs_both_source_and_transfer_ci_above_zero():
    res = results_with({"LBR_v1": 0.30, "LBR_v2": 0.34})
    deltas = {"LBR_v1": delta(0.05), "LBR_v1_on_P1x3": delta(0.04),
              "LBR_v2": delta(0.06), "LBR_v2_on_P1x3": delta(-0.01)}
    assert script.select_candidate(res, deltas) == "v1"
    deltas["LBR_v1_on_P1x3"] = delta(-0.001)
    assert script.select_candidate(res, deltas) is None


def test_near_tie_prefers_simpler_v1():
    deltas = {k: delta(0.05) for k in ("LBR_v1", "LBR_v1_on_P1x3", "LBR_v2", "LBR_v2_on_P1x3")}
    assert script.select_candidate(results_with({"LBR_v1": 0.300, "LBR_v2": 0.304}), deltas) == "v1"
    assert script.select_candidate(results_with({"LBR_v1": 0.300, "LBR_v2": 0.310}), deltas) == "v2"


def synthetic_ctx() -> dict:
    probabilities, reference, folds = {}, {}, {}
    for fold in range(3):
        for i in range(3):
            rid = f"r{fold}_{i}"
            p = np.full((int(20 * FR), 2), 0.02)
            p[int(2 * FR):int(6 * FR), 0] = 0.95          # khớp nhãn
            p[int(10 * FR):int(12 * FR), 1] = 0.6         # vệt giả, không nhãn
            probabilities[rid] = p
            reference[rid] = [{"class_id": "a", "event_label": "a", "onset": 2.0, "offset": 6.0}]
            folds[rid] = fold
    return {"probabilities": probabilities, "reference": reference, "folds": folds,
            "recordings": sorted(probabilities), "class_ids": CLASSES, "frame_rate": FR,
            "durations": {r: 20.0 for r in probabilities}}


def test_baseline_cross_fits_lambda_and_keeps_every_recording():
    ctx = synthetic_ctx()
    objs = {"f1": micro_f1_objective(ctx["reference"], CLASSES)}
    events = script.baseline_events(ctx, SebbParams(step_filter_s=0.32, merge_abs=0.3), objs)
    assert set(events["f1"]) == set(ctx["recordings"])
    assert objs["f1"](events["f1"], ctx["recordings"]) == pytest.approx(1.0)
    assert all(e["class_id"] == "a" for rows in events["f1"].values() for e in rows)


def test_render_states_when_no_candidate_passes():
    metric = {"micro_f1": 0.2, "macro_f1": 0.1, "nsys": 1, "nref": 2, "recall": 0.5,
              "event_f1_collar_1s": {"micro": 0.4}, "segment_f1_1s": {"micro": 0.7},
              "intersection": {"micro": {"precision": 0.8, "recall": 0.6, "f1": 0.69},
                               "macro_f1": 0.6}}
    point = {"all": metric, "vn": metric}
    human = {"pairs": 8, "micro_f1": 0.58, "event_f1_collar_1s": 0.76, "segment_f1_1s": 0.8,
             "intersection_f1": 0.9}
    text = script.render({"results": {"B0": {"f1": point, "recall_first": point}},
                          "deltas": {}, "selected": None,
                          "human_ceiling": {"all": human, "vn": human}})
    assert "giữ B0, không mở test" in text
    assert "19 lớp Việt Nam" in text and "Người–người (8 cặp)" in text
