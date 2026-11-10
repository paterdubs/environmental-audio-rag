"""LBR (ADR-0045): đặc trưng, đích, cross-fit lồng nhau không rò nhãn fold held-out."""

import numpy as np
import pytest

from ml.postprocessing.boundary_refine import (
    Box,
    LbrConfig,
    apply_deltas,
    boundary_targets,
    boxes_to_events,
    candidate_boxes,
    feature_matrices,
    feature_size,
    fit_regressor,
    load_bundle,
    matches_intersection,
    matches_primary,
    save_bundle,
)
from ml.postprocessing.lbr_crossfit import (
    LbrData,
    build_data,
    crossfit_lbr,
    fit_lbr,
    micro_f1_objective,
)
from ml.postprocessing.sebb import SebbParams

FR = 25.0
CLASSES = ("a", "b")
PARAMS = SebbParams(step_filter_s=0.32, merge_abs=0.3)
FAST = LbrConfig(max_iter=30, max_leaf_nodes=7, min_samples_leaf=2)


def make_dataset(onset_lag: float = 0.3, fold0_extra: float = 0.0):
    """3 fold × 4 recording; box luôn sớm hơn nhãn `onset_lag` giây, kèm một vệt giả.

    Vệt posterior 0.7 của lớp `a` ở 26–27.5 s không có nhãn: rescorer (v2) cần cả box khớp
    lẫn box sai để học. Fold 0 có mức posterior riêng (0.85) để một model *rò nhãn* học được
    độ lệch riêng của fold 0 — nhờ vậy test chống rò nhãn bắt được đột biến.
    """
    probabilities, reference, folds = {}, {}, {}
    for fold in range(3):
        for i in range(4):
            rid = f"r{fold}_{i}"
            p = np.full((int(30 * FR), 2), 0.02)
            events = []
            for c, starts in enumerate(((3.0 + i, 15.0 + i), (8.0 + i, 22.0 + i))):
                for start in starts:
                    dur = 3.0 + 0.5 * i
                    p[int(start * FR):int((start + dur) * FR), c] = 0.85 if fold == 0 else 0.95
                    lag = onset_lag + (fold0_extra if fold == 0 else 0.0)
                    events.append({"class_id": CLASSES[c], "event_label": CLASSES[c],
                                   "onset": start + lag, "offset": start + dur})
            p[int(26.0 * FR):int(27.5 * FR), 0] = 0.7
            probabilities[rid], reference[rid], folds[rid] = p, events, fold
    return probabilities, reference, folds


def data_for(probabilities, reference, folds) -> LbrData:
    return build_data(probabilities, reference, folds, class_ids=CLASSES, frame_rate=FR,
                      params=PARAMS, config=FAST)


def test_feature_size_and_padding_outside_recording():
    p = np.linspace(0.0, 1.0, 100)[:, None].repeat(2, axis=1)
    box = Box("r", "a", 0.0, 1.0, 0.9)
    x_on, x_off = feature_matrices([box], {"r": p}, class_ids=CLASSES, frame_rate=FR,
                                   config=LbrConfig())
    assert x_on.shape == x_off.shape == (1, feature_size(len(CLASSES), LbrConfig()))
    meta = 4 + len(CLASSES)
    curve = x_on[0, meta:meta + 101]
    assert np.all(curve[:50] == -1.0)  # trước t = 0
    assert curve[50] == pytest.approx(p[0, 0])
    assert x_on[0, :4].tolist() == pytest.approx([0.9, 1.0, 0.0, 100 / FR - 1.0])
    assert x_on[0, 4:meta].tolist() == [1.0, 0.0]


def test_targets_sign_range_and_class():
    reference = {"r": [{"class_id": "a", "onset": 1.5, "offset": 4.0},
                       {"class_id": "b", "onset": 0.0, "offset": 9.0}]}
    boxes = [Box("r", "a", 1.0, 4.2, 0.9),     # chồng lấn, Δon +0.5, Δoff −0.2
             Box("r", "a", 6.0, 7.0, 0.9),     # không chồng event lớp a
             Box("r", "b", 5.0, 14.0, 0.9)]    # Δon −5 > 4 s → bỏ, Δoff −5 → bỏ
    y_on, y_off = boundary_targets(boxes, reference, config=LbrConfig())
    assert y_on[0] == pytest.approx(0.5) and y_off[0] == pytest.approx(-0.2)
    assert np.isnan(y_on[1]) and np.isnan(y_off[1])
    assert np.isnan(y_on[2]) and np.isnan(y_off[2])


def test_apply_deltas_clips_at_zero_and_keeps_min_duration():
    boxes = [Box("r", "a", 0.1, 1.0, 0.9), Box("r", "a", 2.0, 3.0, 0.8)]
    out = apply_deltas(boxes, np.array([-0.5, 0.5]), np.array([0.0, -2.0]), config=LbrConfig())
    assert out[0].onset_s == 0.0 and out[0].offset_s == 1.0
    assert out[1].onset_s == pytest.approx(2.5) and out[1].offset_s == pytest.approx(2.54)


def test_matches_primary_uses_onset_collar_and_offset_percentage():
    reference = {"r": [{"class_id": "a", "onset": 1.0, "offset": 11.0}]}
    boxes = [Box("r", "a", 1.15, 12.9, 0.9),  # offset lệch 1.9 ≤ 0.2·10
             Box("r", "a", 1.3, 11.0, 0.9),   # onset lệch 0.3 > 0.2
             Box("r", "b", 1.0, 11.0, 0.9)]   # sai lớp
    assert matches_primary(boxes, reference).tolist() == [True, False, False]


def test_matches_intersection_needs_ten_percent_of_both_durations():
    reference = {"r": [{"class_id": "a", "onset": 1.0, "offset": 11.0}]}
    boxes = [Box("r", "a", 9.5, 12.0, 0.9),   # giao 1.5 s: ≥ 10% event, ≥ 10% box
             Box("r", "a", 10.5, 30.0, 0.9),  # giao 0.5 s < 10% event
             Box("r", "b", 1.0, 11.0, 0.9),   # sai lớp
             Box("r", "a", 11.0, 12.0, 0.9)]  # chỉ chạm biên
    assert matches_intersection(boxes, reference).tolist() == [True, False, False, False]
    assert matches_primary(boxes[:1], reference).tolist() == [False]


def test_boxes_to_events_keeps_empty_recordings():
    events = boxes_to_events([Box("r1", "a", 1.0, 2.0, 0.9)], np.array([False]),
                             recordings=["r1", "r2"])
    assert events == {"r1": [], "r2": []}


def test_regressor_is_deterministic():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(60, 5))
    y = x[:, 0] * 0.5
    y[::7] = np.nan
    first = fit_regressor(x, y, FAST).predict(x)
    second = fit_regressor(x, y, FAST).predict(x)
    assert np.array_equal(first, second)


def test_bundle_roundtrip_and_sha_mismatch_rejected(tmp_path):
    path = tmp_path / "lbr.pkl"
    sha = save_bundle(path, {"variant": "v1", "values": [1, 2]})
    assert load_bundle(path, sha256=sha) == {"variant": "v1", "values": [1, 2]}
    with pytest.raises(ValueError):
        load_bundle(path, sha256="0" * 64)


def test_candidate_boxes_respect_min_score():
    p = np.full((250, 2), 0.02)
    p[50:100, 0] = 0.95
    p[150:200, 1] = 0.4
    boxes = candidate_boxes({"r": p}, class_ids=CLASSES, frame_rate=FR, params=PARAMS,
                            min_score=0.5)
    assert [b.class_id for b in boxes] == ["a"]


@pytest.mark.parametrize("variant", ["v1", "v2", "v3"])
def test_crossfit_learns_systematic_onset_lag(variant):
    probabilities, reference, folds = make_dataset()
    data = data_for(probabilities, reference, folds)
    objective = micro_f1_objective(reference, CLASSES)
    result = crossfit_lbr(data, variant=variant, objectives={"f1": objective}, config=FAST)
    baseline = boxes_to_events(data.boxes, None, recordings=list(reference))
    assert objective(baseline, list(reference)) == 0.0  # mọi onset lệch 0.3 s > collar
    assert objective(result.events["f1"], list(reference)) > 0.9


@pytest.mark.parametrize("variant", ["v1", "v2", "v3"])
def test_heldout_fold_predictions_ignore_its_own_labels(variant):
    probabilities, reference, folds = make_dataset()
    _, perturbed, _ = make_dataset(fold0_extra=0.15)
    held = [r for r, f in folds.items() if f == 0]
    # Nhiễu +0.15 s chỉ ở fold 0: đổi đích và nhãn của fold 0, vẫn để các fold fit có box khớp.
    runs = []
    for ref in (reference, perturbed):
        data = data_for(probabilities, ref, folds)
        result = crossfit_lbr(data, variant=variant,
                              objectives={"f1": micro_f1_objective(ref, CLASSES)}, config=FAST)
        runs.append({r: result.events["f1"][r] for r in held})
    assert runs[0] == runs[1]


def test_fit_lbr_requires_two_fit_folds():
    probabilities, reference, folds = make_dataset()
    data = data_for(probabilities, reference, folds)
    with pytest.raises(ValueError):
        fit_lbr(data, fit_folds={0}, variant="v1",
                objectives={"f1": micro_f1_objective(reference, CLASSES)}, config=FAST)


def test_kept_boxes_of_same_class_that_overlap_are_merged():
    boxes = [Box("r", "a", 1.0, 3.0, 0.9), Box("r", "a", 2.5, 5.0, 0.8),
             Box("r", "a", 5.0, 6.0, 0.7),   # chạm biên → vẫn gộp (psds_eval coi là giao)
             Box("r", "b", 2.0, 4.0, 0.9),   # lớp khác → giữ riêng
             Box("r", "a", 5.5, 9.0, 0.95)]  # bị loại bởi keep → không kéo dài event
    keep = np.array([True, True, True, True, False])
    events = boxes_to_events(boxes, keep)["r"]
    a = [e for e in events if e["class_id"] == "a"]
    assert [(e["onset"], e["offset"], e["score"]) for e in a] == [(1.0, 6.0, 0.9)]
    assert [(e["onset"], e["offset"]) for e in events if e["class_id"] == "b"] == [(2.0, 4.0)]
