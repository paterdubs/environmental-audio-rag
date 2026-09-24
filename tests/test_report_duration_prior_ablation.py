from __future__ import annotations

import numpy as np
import pytest

from ml.postprocessing import DurationPrior
from scripts.report_duration_prior_ablation import evaluate_test_f1


def test_evaluate_test_f1_recovers_perfect_match() -> None:
    class_ids = ("a",)
    priors = {"a": DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1)}
    probabilities = {"R1": np.array([[0.0], [0.9], [0.9], [0.0]])}
    reference = {"R1": [{"event_label": "a", "onset": 1.0, "offset": 3.0}]}

    score = evaluate_test_f1(
        probabilities=probabilities,
        class_ids=class_ids,
        thresholds={"a": 0.5},
        priors=priors,
        frame_rate=1.0,
        reference=reference,
    )

    assert score == 1.0


def test_evaluate_test_f1_averages_over_pooled_events_not_per_class() -> None:
    """Real ablation runs always pass the full 21-class list, not one class in
    isolation. `event_based_f1`'s overall score is a MICRO average over pooled
    events across the whole `class_ids` list, not a per-class macro average —
    so one class with zero detections does not make the aggregate NaN as long
    as some other class has correct predictions (unlike the isolated per-class
    score used in `sweep_threshold.py`, which needs its own NaN guard)."""
    class_ids = ("a", "b")
    priors = {
        "a": DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1),
        "b": DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1),
    }
    # "a" never crosses threshold (no detection); "b" matches perfectly.
    probabilities = {"R1": np.array([[0.0, 0.0], [0.0, 0.9], [0.0, 0.9], [0.0, 0.0]])}
    reference = {
        "R1": [
            {"event_label": "a", "onset": 1.0, "offset": 3.0},
            {"event_label": "b", "onset": 1.0, "offset": 3.0},
        ]
    }

    score = evaluate_test_f1(
        probabilities=probabilities,
        class_ids=class_ids,
        thresholds={"a": 0.5, "b": 0.5},
        priors=priors,
        frame_rate=1.0,
        reference=reference,
    )

    # 1 TP, 1 predicted (precision=1.0), 2 reference (recall=0.5) -> F1=2/3.
    assert score == pytest.approx(2 / 3)
