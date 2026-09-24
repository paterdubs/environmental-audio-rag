from __future__ import annotations

from pathlib import Path

import numpy as np

from ml.postprocessing import DurationPrior
from scripts.report_threshold_ablation import overall_event_f1, priors_from_postproc, render_report


def test_priors_from_postproc_extracts_duration_prior_fields() -> None:
    postproc = {
        "per_class": {
            "a": {"median_w": 3, "d_min_s": 0.2, "g_max_s": 0.5, "n_train_events": 10},
            "b": {"median_w": 5, "d_min_s": 0.1, "g_max_s": 0.3, "n_train_events": 4},
        }
    }
    priors = priors_from_postproc(postproc, ("a", "b"))
    assert priors["a"] == DurationPrior(median_w=3, d_min_s=0.2, g_max_s=0.5, n_events=10)
    assert priors["b"].n_events == 4


def test_overall_event_f1_recovers_perfect_match() -> None:
    class_ids = ("a",)
    priors = {"a": DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1)}
    probabilities = {"R1": np.array([[0.0], [0.9], [0.9], [0.0]])}
    reference = {"R1": [{"event_label": "a", "onset": 1.0, "offset": 3.0}]}

    score = overall_event_f1(
        probabilities,
        class_ids=class_ids,
        thresholds={"a": 0.5},
        priors=priors,
        frame_rate=1.0,
        reference=reference,
    )

    assert score == 1.0


def test_render_report_flags_overfit_when_per_class_gap_is_larger() -> None:
    results = {"dev": {"global": 0.5, "per_class": 0.6}, "test": {"global": 0.45, "per_class": 0.2}}
    gaps = {"global": 0.05, "per_class": 0.4}

    text = render_report(Path("ml/runs/x"), 0.5, results, gaps)

    assert "Dấu hiệu overfit dev" in text


def test_render_report_no_overfit_signal_when_gaps_close() -> None:
    results = {
        "dev": {"global": 0.5, "per_class": 0.55},
        "test": {"global": 0.48, "per_class": 0.53},
    }
    gaps = {"global": 0.02, "per_class": 0.02}

    text = render_report(Path("ml/runs/x"), 0.5, results, gaps)

    assert "Không có dấu hiệu overfit" in text
