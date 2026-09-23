from __future__ import annotations

from ml.postprocessing import DurationPrior
from scripts.evaluate_run import (
    priors_from_postproc,
    psds_operating_points,
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
