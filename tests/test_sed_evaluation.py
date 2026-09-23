import pytest

from ml.evaluation import classify_event_errors, event_based_f1, psds_score, recording_bootstrap
from ml.evaluation.sed_metrics import MissingMetricDependency


def event(label, onset, offset):
    return {"event_label": label, "onset": onset, "offset": offset}


def test_recording_bootstrap_is_reproducible_and_recording_level():
    rows = [{"score": value} for value in [0.0, 1.0, 2.0, 3.0]]
    result = recording_bootstrap(
        rows,
        lambda sample: sum(row["score"] for row in sample) / len(sample),
        n_bootstrap=200,
    )
    assert result.estimate == 1.5
    assert result.lower <= result.estimate <= result.upper
    assert result.n_recordings == 4


def test_error_classification_fixture():
    refs = {
        "r1": [
            event("bird", 0, 10),
            event("bird", 20, 30),
            event("bird", 25, 35),
            event("car", 40, 50),
        ]
    }
    preds = {
        "r1": [
            event("bird", 0, 4),
            event("bird", 4, 10),
            event("bird", 20, 30),
            event("bird", 22, 29),
            event("bird", 40, 50),
            event("noise", 70, 71),
        ]
    }
    errors, summary = classify_event_errors(refs, preds)
    assert summary["r1"]["fragmentation"] >= 2
    assert summary["r1"]["merging"] >= 1
    assert summary["r1"]["confusion"] == 1
    assert any(error.error_type == "confusion" for error in errors)


def test_standard_metric_adapters_report_missing_optional_dependencies():
    with pytest.raises(MissingMetricDependency):
        event_based_f1({"r": []}, {"r": []}, event_label_list=["bird"])
    with pytest.raises(MissingMetricDependency):
        psds_score(ground_truth=None, metadata=None, operating_points=[], scenario={})
