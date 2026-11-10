"""Chẩn đoán PSDS (ADR-0048 §2): đường PSD-ROC, vị trí điểm vận hành, luật H1–H4 ghi trước."""

import pandas as pd
import pytest

from ml.evaluation import psds_diagnosis as diag

SCENARIO = {"dtc_threshold": 0.5, "gtc_threshold": 0.5, "cttc_threshold": 0.3,
            "alpha_ct": 0.0, "alpha_st": 1.0, "max_efpr": 100.0}


@pytest.fixture()
def tiny():
    gt = pd.DataFrame([{"filename": "a", "onset": 1.0, "offset": 3.0, "event_label": "x"},
                       {"filename": "a", "onset": 5.0, "offset": 6.0, "event_label": "y"}])
    meta = pd.DataFrame({"filename": ["a"], "duration": [3600.0]})
    hit_x = pd.DataFrame([{"filename": "a", "onset": 1.0, "offset": 3.0, "event_label": "x"}])
    both = pd.DataFrame([{"filename": "a", "onset": 1.0, "offset": 3.0, "event_label": "x"},
                         {"filename": "a", "onset": 5.0, "offset": 6.0, "event_label": "y"},
                         {"filename": "a", "onset": 100.0, "offset": 101.0, "event_label": "y"}])
    return gt, meta, hit_x, both


def test_step_lookup_is_a_staircase_like_psds_eval():
    xp, yp = [0.0, 10.0, 50.0], [0.1, 0.3, 0.6]
    assert diag.step_lookup(xp, yp, 5.0) == 0.1
    assert diag.step_lookup(xp, yp, 10.0) == 0.3
    assert diag.step_lookup(xp, yp, 100.0) == 0.6


def test_grid_points_skips_thresholds_without_events_and_counts_sizes():
    events = {0.1: {"a": [{"class_id": "x", "onset_s": 1.0, "offset_s": 2.0, "score": 0.5}]},
              0.9: {"a": []}}
    points, sizes = diag.grid_points(lambda t: events[t], [0.1, 0.9])
    assert sizes == [1, 0] and len(points) == 1
    assert list(points[0][0].columns) == ["filename", "event_label", "onset", "offset"]


def test_curve_stats_and_operating_position_on_a_known_case(tiny):
    gt, meta, hit_x, both = tiny
    evaluator = diag.build_evaluator(gt, meta, SCENARIO, [(hit_x,), (both,)])
    stats = diag.curve_stats(evaluator, SCENARIO, efpr_points=(0.5, 2.0))
    assert set(stats) >= {"psds", "psds_alpha_st0", "mean_tpr_at", "per_class_auc",
                          "efpr_max", "max_mean_tpr"}
    assert stats["max_mean_tpr"] == pytest.approx(1.0)  # `both` bắt cả hai event
    assert stats["mean_tpr_at"]["0.5"] == pytest.approx(0.5)  # chỉ x, chưa có FP
    assert stats["psds_alpha_st0"] >= stats["psds"]
    assert set(stats["per_class_auc"]) == {"x", "y"}
    assert stats["per_class_auc"]["x"] > stats["per_class_auc"]["y"]  # x bắt từ eFPR 0
    position = diag.operating_position(gt, meta, SCENARIO, hit_x)
    assert position == {"mean_tpr": pytest.approx(0.5), "mean_efpr": pytest.approx(0.0)}


def _system(ef1, base, *, log=None, st0=None, dtc05=None, tpr=None, sel=50.0):
    """base/log/st0: {scenario: psds}; dtc05: psds_1 với DTC=GTC=0.5; tpr: {eFPR: tpr}."""
    log, st0 = log or base, st0 or base
    tpr = tpr or {str(e): 0.5 for e in diag.EFPR_POINTS}

    def grid(values, alt):
        return {"scenarios": {s: {"psds": v, "psds_alpha_st0": alt[s], "mean_tpr_at": tpr}
                              for s, v in values.items()}
                | {"psds_1_dtc05": {"psds": dtc05 if dtc05 is not None else values["psds_1"],
                                    "psds_alpha_st0": 0.0, "mean_tpr_at": tpr}}}

    return {"event_f1_micro": ef1,
            "selected": {s: {"mean_tpr": 0.5, "mean_efpr": sel} for s in ("psds_1", "psds_2")},
            "grids": {"linear": grid(base, st0), "log": grid(log, log)}}


def test_no_hypothesis_is_read_when_dev_does_not_reproduce_s21():
    v1 = _system(0.20, {"psds_1": 0.30, "psds_2": 0.60})
    v2 = _system(0.19, {"psds_1": 0.25, "psds_2": 0.55})  # event-F1 v2 không hơn v1
    result = diag.evaluate_hypotheses({"v1": v1, "v2": v2})
    assert result["reproduced"] is False and result["hypotheses"] == {}
    assert result["explained"] is False


def test_grid_hypothesis_needs_the_gap_to_flip_or_halve_on_the_log_grid():
    v1 = _system(0.15, {"psds_1": 0.30, "psds_2": 0.60}, log={"psds_1": 0.30, "psds_2": 0.60})
    v2 = _system(0.20, {"psds_1": 0.26, "psds_2": 0.50}, log={"psds_1": 0.29, "psds_2": 0.40})
    result = diag.evaluate_hypotheses({"v1": v1, "v2": v2})
    assert result["reproduced"] is True
    assert result["hypotheses"]["H1"]["psds_1"]["supported"] is True    # −0.04 → −0.01
    assert result["hypotheses"]["H1"]["psds_2"]["supported"] is False   # −0.10 → −0.20
    assert result["explained"] is True


def test_alpha_st_and_dtc_hypotheses_use_their_own_variants():
    base = {"psds_1": 0.30, "psds_2": 0.60}
    v1 = _system(0.15, base, st0={"psds_1": 0.40, "psds_2": 0.70}, dtc05=0.35)
    v2 = _system(0.20, {"psds_1": 0.25, "psds_2": 0.55},
                 st0={"psds_1": 0.42, "psds_2": 0.69}, dtc05=0.36)
    result = diag.evaluate_hypotheses({"v1": v1, "v2": v2})
    h3, h4 = result["hypotheses"]["H3"], result["hypotheses"]["H4"]
    assert h3["psds_1"]["supported"] is True and h3["psds_2"]["supported"] is True
    assert h4["psds_1"]["supported"] is True and "psds_2" not in h4
    assert result["hypotheses"]["H1"]["psds_1"]["supported"] is False


def test_localised_gain_hypothesis_compares_tpr_below_and_above_the_chosen_point():
    efprs = [str(e) for e in diag.EFPR_POINTS]  # 5, 10, 30, 60, 100
    low = dict(zip(efprs, [0.2, 0.3, 0.4, 0.5, 0.6], strict=True))
    v2_tpr = dict(zip(efprs, [0.25, 0.35, 0.38, 0.45, 0.55], strict=True))
    base1, base2 = {"psds_1": 0.30, "psds_2": 0.60}, {"psds_1": 0.28, "psds_2": 0.58}
    v1 = _system(0.15, base1, tpr=low, sel=12.0)
    v2 = _system(0.20, base2, tpr=v2_tpr, sel=12.0)
    h2 = diag.evaluate_hypotheses({"v1": v1, "v2": v2})["hypotheses"]["H2"]["psds_1"]
    assert h2["low_efpr"] == ["5.0", "10.0"] and h2["high_efpr"] == ["30.0", "60.0", "100.0"]
    assert h2["supported"] is True
    v2_flat = _system(0.20, base2, tpr=dict(zip(efprs, [0.1] * 5, strict=True)), sel=12.0)
    assert diag.evaluate_hypotheses({"v1": v1, "v2": v2_flat})[
        "hypotheses"]["H2"]["psds_1"]["supported"] is False
