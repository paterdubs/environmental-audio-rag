from __future__ import annotations

from ml.postprocessing import DurationPrior
from scripts.evaluate_run import (
    priors_from_postproc,
    psds_operating_points,
    sebb_operating_points,
    sebb_params,
    to_detection_frame,
    to_reference_frame,
)

CLASS_IDS = ("bird", "car")


def test_to_detection_frame_flattens_events_with_confidence() -> None:
    events = {
        "r1": [{"class_id": "bird", "onset_s": 1.0, "offset_s": 2.0, "score": 0.9}],
        "r2": [],
    }
    frame = to_detection_frame(events)
    assert list(frame.columns) == ["filename", "event_label", "onset", "offset", "confidence"]
    assert len(frame) == 1
    assert frame.iloc[0]["filename"] == "r1"
    assert frame.iloc[0]["confidence"] == 0.9


def test_to_reference_frame_flattens_events_without_confidence() -> None:
    events = {"r1": [{"event_label": "bird", "onset": 1.0, "offset": 2.0}]}
    frame = to_reference_frame(events)
    assert list(frame.columns) == ["filename", "event_label", "onset", "offset"]
    assert len(frame) == 1


def test_priors_from_postproc_reads_frozen_per_class_parameters() -> None:
    postproc = {
        "per_class": {
            "bird": {"median_w": 3, "d_min_s": 0.1, "g_max_s": 0.2, "n_train_events": 5},
            "car": {"median_w": 5, "d_min_s": 0.3, "g_max_s": 0.4, "n_train_events": 7},
        }
    }
    priors = priors_from_postproc(postproc, CLASS_IDS)
    assert priors["bird"] == DurationPrior(median_w=3, d_min_s=0.1, g_max_s=0.2, n_events=5)
    assert priors["car"] == DurationPrior(median_w=5, d_min_s=0.3, g_max_s=0.4, n_events=7)


def test_psds_operating_points_sweeps_the_full_grid_not_one_frozen_theta() -> None:
    """PSDS needs a range of operating points (evaluation_protocol.md §3.1), not
    the single frozen theta used for event-based F1 — this locks that distinction."""
    import numpy as np

    priors = {
        class_id: DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1)
        for class_id in CLASS_IDS
    }
    # r1: bird active frames 0-3 at high prob, car always low.
    probabilities = {
        "r1": np.array(
            [[0.9, 0.1], [0.9, 0.1], [0.9, 0.1], [0.1, 0.1], [0.1, 0.1]], dtype=np.float64
        )
    }
    points = psds_operating_points(
        probabilities, class_ids=CLASS_IDS, priors=priors, frame_rate=10.0
    )
    # At low thresholds bird is detected, at high thresholds nothing survives
    # (0.9 < 0.95) -- so the swept grid must yield more than one distinct point.
    assert len(points) >= 2
    assert len({len(point[0]) for point in points}) > 1


def test_report_names_the_postproc_file_used() -> None:
    from scripts.evaluate_run import _render_report

    result = {
        "run": "ml/runs/x", "postproc": "ml/runs/x/postproc_cv.json",
        "event_based_f1": {"f_measure": 0.1, "precision": 0.2, "recall": 0.05},
        "event_based_f1_bootstrap": {"lower": 0.05, "upper": 0.15, "n_recordings": 142},
        "psds": {"psds_1": 0.3, "psds_2": 0.7}, "error_totals": {"deletion": 3},
        "n_events_reference": 10, "n_events_estimate": 4,
    }
    assert "Hậu xử lý: `postproc_cv.json`." in _render_report(result)


def test_sebb_params_reads_frozen_annotated_selection() -> None:
    selection = {
        "family": "csebb",
        "eval_set": "annotated",
        "selected": {
            "step_filter_s": 0.64,
            "merge_abs": None,
            "merge_rel": 2.0,
            "threshold": 0.9,
        },
    }

    params, threshold = sebb_params(selection, eval_set="annotated")

    assert params.step_filter_s == 0.64
    assert params.merge_rel == 2.0
    assert params.merge_abs is None
    assert threshold == 0.9


def test_sebb_params_rejects_wrong_eval_set() -> None:
    import pytest

    selection = {
        "family": "csebb",
        "eval_set": "all",
        "selected": {
            "step_filter_s": 0.64,
            "merge_abs": 0.2,
            "merge_rel": None,
            "threshold": 0.9,
        },
    }

    with pytest.raises(ValueError, match="eval_set của cSEBB không khớp"):
        sebb_params(selection, eval_set="annotated")


def test_sebb_operating_points_sweep_box_confidence_without_moving_boundaries() -> None:
    from ml.postprocessing.events import PostprocessedEvent

    candidates = {
        "r1": [PostprocessedEvent("r1", "bird", 0.1, 0.4, 0.9)],
        "r2": [],
    }

    points = sebb_operating_points(candidates)

    assert len(points) >= 2
    assert {tuple(frame[["onset", "offset"]].iloc[0]) for (frame,) in points} == {(0.1, 0.4)}
