import pandas as pd
import pytest

from ml.evaluation import classify_event_errors, event_based_f1, psds_score, recording_bootstrap
from ml.evaluation.sed_metrics import MissingMetricDependency


def event(label, onset, offset):
    return {"event_label": label, "onset": onset, "offset": offset}


def _psds_fixture() -> tuple[pd.DataFrame, pd.DataFrame, list[tuple[pd.DataFrame]]]:
    """Two non-overlapping classes, two recordings — enough for a real PSD-ROC."""
    metadata = pd.DataFrame({"filename": ["r0.wav", "r1.wav"], "duration": [60.0, 60.0]})
    ground_truth = pd.DataFrame(
        [
            {"filename": "r0.wav", "event_label": "bird", "onset": 2.0, "offset": 6.0},
            {"filename": "r0.wav", "event_label": "car", "onset": 10.0, "offset": 14.0},
            {"filename": "r1.wav", "event_label": "bird", "onset": 2.0, "offset": 6.0},
            {"filename": "r1.wav", "event_label": "car", "onset": 10.0, "offset": 14.0},
        ]
    )
    detections = pd.DataFrame(
        [
            {"filename": "r0.wav", "event_label": "bird", "onset": 2.1, "offset": 5.9,
             "confidence": 0.9},
            {"filename": "r0.wav", "event_label": "car", "onset": 10.2, "offset": 13.8,
             "confidence": 0.4},
            {"filename": "r1.wav", "event_label": "bird", "onset": 1.9, "offset": 6.1,
             "confidence": 0.7},
        ]
    )
    operating_points = [
        (subset,)
        for threshold in (0.3, 0.6, 0.85)
        if len(subset := detections[detections["confidence"] >= threshold].drop(
            columns=["confidence"]
        ))
    ]
    return ground_truth, metadata, operating_points


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


def test_event_based_f1_runs_end_to_end_with_real_sed_eval():
    refs = {"r1": [event("bird", 0, 10), event("car", 40, 50)]}
    preds = {"r1": [event("bird", 0, 9), event("car", 40, 51)]}
    result = event_based_f1(refs, preds, event_label_list=["bird", "car"])
    assert 0.0 <= result["f_measure"]["f_measure"] <= 1.0
    assert set(result["per_class"]) == {"bird", "car"}


@pytest.mark.parametrize(
    "scenario",
    [
        {"dtc_threshold": 0.7, "gtc_threshold": 0.7, "alpha_ct": 0.0, "alpha_st": 1.0,
         "max_efpr": 100},
        {"dtc_threshold": 0.1, "gtc_threshold": 0.1, "cttc_threshold": 0.3, "alpha_ct": 0.5,
         "alpha_st": 1.0, "max_efpr": 100},
    ],
    ids=["psds-1", "psds-2"],
)
def test_psds_score_runs_end_to_end_with_the_locked_scenarios(scenario):
    """H1 (2026-09-23): locks two real bugs found only by running this for real,
    never exercised before because sed_eval/psds_eval were never installed:

    1. psds_eval 0.5.3's internal `_auc` calls `int(np.argwhere(...))`, which
       numpy 2.x rejects for any array with ndim > 0 (even size==1). Patched in
       `sed_metrics._patch_psds_eval_for_numpy2` — every real PSDS-1/PSDS-2 call
       with `max_efpr` outside the observed FPR range hit this, i.e. always.
    2. `PSDSEval.psds()` returns a `PSDS` namedtuple, not a bare number —
       `float(result)` raised `TypeError` unconditionally before this fix.

    Uses evaluation_protocol.md §3.3's exact PSDS-1/PSDS-2 parameters (max_efpr
    included) so this cannot pass by accident on an easier scenario.
    """
    ground_truth, metadata, operating_points = _psds_fixture()
    score = psds_score(
        ground_truth=ground_truth,
        metadata=metadata,
        operating_points=operating_points,
        scenario=scenario,
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_standard_metric_adapters_report_missing_optional_dependencies(monkeypatch):
    """H1 (2026-09-23): sed_eval/psds_eval are now pinned (requirements-eval.txt)
    and installed in this environment, so the adapters can no longer rely on a
    genuinely absent import to exercise this path. Simulate absence instead —
    the behaviour under test is the adapter's own ImportError handling, not
    whether the environment happens to have the package."""
    import builtins

    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name in {"sed_eval", "psds_eval"}:
            raise ImportError(f"simulated missing dependency: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    with pytest.raises(MissingMetricDependency):
        event_based_f1({"r": []}, {"r": []}, event_label_list=["bird"])
    with pytest.raises(MissingMetricDependency):
        psds_score(ground_truth=None, metadata=None, operating_points=[], scenario={})
