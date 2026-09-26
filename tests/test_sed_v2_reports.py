"""Ablation noise rule (ADR-0030 §4) and boundary-error accounting (PLAN debt #22)."""

import numpy as np
import pytest

from scripts.report_boundary_errors import score_distribution, signed_errors, summarize
from scripts.report_sed_v2_ablation import noise_threshold, paired_reference, verdict


def _row(seed: int, mean: float, sd: float = 0.05) -> dict:
    return {"seed": seed, "cv_mean": mean, "cv_sd": sd}


def test_noise_threshold_is_the_larger_of_fold_sd_and_twice_seed_sd():
    full = [_row(20260922, 0.19, sd=0.05), _row(2, 0.20), _row(3, 0.18)]
    anchor = paired_reference(full, 20260922)
    assert noise_threshold(full, anchor) == pytest.approx(max(0.05, 2 * 0.01))
    spread = [_row(20260922, 0.19, sd=0.01), _row(2, 0.25), _row(3, 0.13)]
    assert noise_threshold(spread, spread[0]) == pytest.approx(2 * 0.06)


def test_verdict_calls_small_differences_indistinguishable():
    assert verdict(-0.01, 0.05) == "không phân biệt được"
    assert "giảm" in verdict(-0.08, 0.05)
    assert "tăng" in verdict(+0.08, 0.05)


def test_ablation_is_compared_with_the_full_run_of_the_same_seed():
    full = [_row(2, 0.30), _row(20260922, 0.19)]
    assert paired_reference(full, 20260922)["cv_mean"] == 0.19


def test_signed_errors_use_the_best_overlapping_same_class_estimate():
    reference = {"r": [{"event_label": "birds", "onset": 10.0, "offset": 20.0}]}
    estimate = {"r": [
        {"class_id": "birds", "onset_s": 10.5, "offset_s": 19.0},   # best overlap
        {"class_id": "birds", "onset_s": 19.5, "offset_s": 21.0},
        {"class_id": "voices", "onset_s": 10.0, "offset_s": 20.0},  # other class: ignored
    ]}
    onsets, offsets = signed_errors(reference, estimate)
    assert onsets.tolist() == [0.5] and offsets.tolist() == [-1.0]


def test_unmatched_reference_events_are_not_counted():
    onsets, _ = signed_errors({"r": [{"event_label": "birds", "onset": 1.0, "offset": 2.0}]},
                              {"r": [{"class_id": "birds", "onset_s": 5.0, "offset_s": 6.0}]})
    assert onsets.size == 0 and summarize(onsets) == {"n": 0}


def test_summary_splits_late_early_and_within_collar():
    summary = summarize(np.array([-0.5, -0.1, 0.0, 0.1, 0.6]))
    assert summary["within_collar"] == pytest.approx(0.6)
    assert summary["late"] == pytest.approx(0.2) and summary["early"] == pytest.approx(0.2)


def test_score_distribution_separates_negative_and_positive_frames():
    probabilities = {"r": np.array([[0.1], [0.2], [0.96], [0.4]])}
    truth = {"r": np.array([[0], [0], [1], [1]], dtype=np.float32)}
    row = score_distribution(probabilities, truth, ("birds",))["birds"]
    assert row["neg_median"] == pytest.approx(0.15)
    assert row["pos_ge_0.95"] == pytest.approx(0.5)
    assert row["n_pos_frames"] == 2


def test_macro_is_nanmean_of_stored_per_class_f1():
    from scripts.report_event_f1_macro import macro_from_per_class

    per_class = {"a": {"f_measure": 0.2}, "b": {"f_measure": 0.0},
                 "c": {"f_measure": float("nan")}, "d": {}}
    assert macro_from_per_class(per_class) == pytest.approx(0.1)


def test_event_based_f1_reports_macro_equal_to_sed_eval_class_wise_average():
    from ml.evaluation.sed_metrics import event_based_f1
    from scripts.report_event_f1_macro import macro_from_per_class

    reference = {"r": [{"event_label": "birds", "onset": 0.0, "offset": 2.0},
                       {"event_label": "horn", "onset": 5.0, "offset": 6.0}]}
    estimate = {"r": [{"event_label": "birds", "onset": 0.05, "offset": 2.0},
                      {"event_label": "horn", "onset": 3.0, "offset": 4.0}]}
    result = event_based_f1(reference, estimate, event_label_list=["birds", "horn"])
    per_class = {c: v["f_measure"] for c, v in result["per_class"].items()}
    assert result["macro"]["f_measure"] == pytest.approx(macro_from_per_class(per_class))
    assert result["macro"]["f_measure"] == pytest.approx(0.5)  # birds 1.0, horn 0.0
    assert result["f_measure"]["f_measure"] == pytest.approx(0.5)  # micro: 1 TP of 2 / 2
