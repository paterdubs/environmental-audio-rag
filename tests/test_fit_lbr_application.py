"""Cấu hình ứng dụng LBR V3 (ADR-0045 §11): cross-fit trên OOF và bảng báo cáo."""

from test_fit_lbr_oof import synthetic_ctx

from ml.postprocessing.boundary_refine import LbrConfig
from ml.postprocessing.sebb import SebbParams
from scripts import fit_lbr_application as script

FAST = LbrConfig(max_iter=30, max_leaf_nodes=7, min_samples_leaf=2)


def test_run_v3_produces_source_and_transfer_events_for_both_points():
    ctx = synthetic_ctx()
    run = script.run_v3(ctx, ctx, SebbParams(step_filter_s=0.32, merge_abs=0.3), FAST)
    assert set(run["events"]) == {"B0", "P1x3", "LBR_v3", "LBR_v3_on_P1x3"}
    for name in ("LBR_v3", "LBR_v3_on_P1x3"):
        assert set(run["events"][name]) == {"f1", "recall_first"}
        assert set(run["events"][name]["f1"]) == set(ctx["recordings"])
    assert set(run["thresholds"]) == {"0", "1", "2"}


def test_render_marks_v3_as_not_preregistered():
    metric = {"micro_f1": 0.2, "macro_f1": 0.1, "nsys": 1, "nref": 2,
              "event_f1_collar_1s": {"micro": 0.4}, "segment_f1_1s": {"micro": 0.7},
              "intersection": {"micro": {"precision": 0.8, "recall": 0.6, "f1": 0.69}}}
    point = {"all": metric, "vn": metric}
    text = script.render({"results": {"LBR_v3": {"f1": point, "recall_first": point}},
                          "deltas": {}, "fold_thresholds": {}})
    assert "không phải ứng viên ghi trước" in text and "19 lớp Việt Nam" in text
