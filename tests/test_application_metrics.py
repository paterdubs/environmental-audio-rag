from __future__ import annotations

import argparse
import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from ml.evaluation.application_metrics import application_metrics, event_f1_collar, segment_f1
from ml.postprocessing import DurationPrior


def event(label, onset, offset):
    return {"event_label": label, "onset": onset, "offset": offset}


def test_segment_micro_macro_and_per_class_use_standard_library():
    reference = {"a": [event("bird", 0, 2)], "b": [event("car", 0, 2)]}
    estimate = {"a": [event("bird", 0, 2)], "b": []}
    result = segment_f1(reference, estimate, ("bird", "car"))
    assert result["micro"] == pytest.approx(2 / 3)
    assert result["macro"] == 1.0  # sed_eval excludes undefined F1 via nanmean.
    assert result["per_class"]["bird"] == 1.0
    assert np.isnan(result["per_class"]["car"])


def test_segment_counts_false_positives_in_estimate_only_recording():
    result = segment_f1({"a": [event("bird", 0, 1)]},
                        {"a": [event("bird", 0, 1)], "extra": [event("bird", 0, 1)]},
                        ("bird",))
    assert result["micro"] == pytest.approx(2 / 3)


def test_segment_nondefault_resolution_and_absent_class():
    reference = {"a": [event("bird", 0, 0.4)]}
    estimate = {"a": [event("bird", 0.6, 0.9)]}
    assert segment_f1(reference, estimate, ("bird",), resolution=1)["micro"] == 1
    assert segment_f1(reference, estimate, ("bird",), resolution=0.5)["micro"] == 0
    result = segment_f1(reference, reference, ("bird", "absent"))
    assert np.isnan(result["per_class"]["absent"])
    assert result["macro"] == 1


def test_event_collar_keeps_default_offset_percentage():
    reference = {"a": [event("bird", 0, 10)]}
    estimate = {"a": [event("bird", 0.8, 13)]}
    # 3 s offset error > max(1 s, 20% of 10 s); would pass with 50%.
    assert event_f1_collar(reference, estimate, ("bird",))["micro"] == 0
    assert event_f1_collar(reference, estimate, ("bird",), collar=3)["micro"] == 1


def test_application_ratio_with_empty_reference():
    result = application_metrics({"a": []}, {"a": [event("bird", 0, 1)]}, ("bird",),
                                 recall_micro=0.0)
    assert result["n_events_estimate_over_reference"] is None
    assert result["recall_micro"] == 0


@pytest.fixture
def evaluator(tmp_path, monkeypatch):
    from scripts import evaluate_run as script

    root = tmp_path / "repo"
    run = tmp_path / "run"
    run.mkdir()
    (root / "docs/measurements").mkdir(parents=True)
    (run / "manifest.json").write_text('{"complete": true}')
    monkeypatch.setattr(script, "ROOT", root)
    classes = ("bird", "car")
    monkeypatch.setattr(script, "load_taxonomy", lambda _: SimpleNamespace(
        polyphonic_class_ids=classes, checksum="abc"))
    monkeypatch.setattr(script, "validate_postproc_artifact", lambda *a, **kw: None)
    monkeypatch.setattr(script, "load_predictions", lambda *a, **kw:
                        SimpleNamespace(split="dev", frame_hop_s=1.0))
    monkeypatch.setattr(script, "restrict", lambda probabilities, _: probabilities)
    probabilities = {"r1": np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.1]])}
    monkeypatch.setattr(script, "stack_predictions_by_recording", lambda _: probabilities)
    reference = {"r1": [event("bird", 0, 2), event("car", 0, 1)]}
    monkeypatch.setattr(script, "load_events_by_recording", lambda _: reference)
    monkeypatch.setattr(script, "bootstrap_event_f1", lambda *a: {
        "estimate": 2 / 3, "lower": 0.25, "upper": 1.0, "confidence": 0.95, "n_recordings": 1})
    monkeypatch.setattr(script, "psds_operating_points", lambda *a, **kw: [(None,)])
    monkeypatch.setattr(script, "sebb_operating_points", lambda *a, **kw: [(None,)])
    monkeypatch.setattr(script, "psds_score", lambda **kw: 0.125)
    return script, run, classes


@pytest.mark.parametrize("family", ["theta", "csebb"])
def test_evaluate_run_adds_metrics_without_changing_legacy_json(evaluator, monkeypatch, family):
    script, run, classes = evaluator
    postproc = run / "postproc_cv.json"
    postproc.write_text(json.dumps({"taxonomy_sha256": "abc", "family": family,
                                   "per_class": {c: {"theta": 0.5} for c in classes}}))
    args = argparse.Namespace(run_dir=run, postproc=postproc, tag="fixture", split="dev",
                              render_only=False, eval_set="annotated")
    monkeypatch.setattr(script, "parse_args", lambda: args)
    priors = {c: DurationPrior(1, 0, 0, 1) for c in classes}
    monkeypatch.setattr(script, "priors_from_postproc", lambda *a: priors)
    # Frozen fixture: both families supply the identical event, with one missed car event.
    estimate = {"r1": [{**event("bird", 0, 2), "class_id": "bird", "onset_s": 0,
                         "offset_s": 2, "score": 0.9}]}
    monkeypatch.setattr(script, "process_recordings", lambda *a, **kw: estimate)
    monkeypatch.setattr(script, "sebb_params", lambda *a, **kw: (None, 0.5))
    monkeypatch.setattr(script, "sebb_candidates", lambda *a, **kw: {})
    monkeypatch.setattr(script, "select_boxes", lambda *a, **kw: estimate)
    script.main()
    result = json.loads((run / "dev_evaluation_fixture_annotated.json").read_text())
    added = result.pop("application_metrics")
    legacy = {
        "run": str(run), "split": "dev", "eval_set": "annotated", "n_recordings": 1,
        "postproc": str(postproc), "postproc_family": family,
        "event_based_f1": {"f_measure": 2 / 3, "precision": 1.0, "recall": 0.5},
        "event_based_f1_macro": {"f_measure": 1.0, "precision": 1.0, "recall": 0.5},
        "event_based_f1_per_class": {
            "bird": {"f_measure": 1.0, "precision": 1.0, "recall": 1.0},
            "car": {"f_measure": float("nan"), "precision": float("nan"), "recall": 0.0}},
        "event_based_f1_bootstrap": {"estimate": 2 / 3, "lower": 0.25, "upper": 1.0,
                                     "confidence": 0.95, "n_recordings": 1},
        "psds": {"psds_1": 0.125, "psds_2": 0.125}, "error_totals": {"deletion": 1},
        "n_events_reference": 2, "n_events_estimate": 1, "n_error_instances": 1}
    assert json.dumps(result, sort_keys=True) == json.dumps(legacy, sort_keys=True)
    assert added["segment_f1_1s"]["micro"] == pytest.approx(0.8)
    assert added["event_f1_collar_1s"]["micro"] == pytest.approx(2 / 3)
    assert added["recall_micro"] == 0.5
    assert added["n_events_estimate_over_reference"] == 0.5


def test_render_only_accepts_legacy_json_without_loading_predictions(evaluator, monkeypatch):
    script, run, _ = evaluator
    old = {"run": str(run), "split": "dev", "postproc": "postproc_cv.json",
           "event_based_f1": {"f_measure": 0.25}, "event_based_f1_bootstrap": {
               "lower": 0.1, "upper": 0.4, "n_recordings": 1}, "psds": {},
           "error_totals": {}, "n_events_reference": 2, "n_events_estimate": 1}
    original = copy.deepcopy(old)
    (run / "dev_evaluation_legacy.json").write_text(json.dumps(old))
    monkeypatch.setattr(script, "parse_args", lambda: argparse.Namespace(
        run_dir=run, tag="legacy", split="dev", eval_set="all", render_only=True))
    monkeypatch.setattr(script, "load_predictions", lambda *a, **kw:
                        pytest.fail("render-only must not load predictions"))
    script.main()
    assert json.loads((run / "dev_evaluation_legacy.json").read_text()) == original
    assert "Chỉ số ứng dụng" not in script._render_report(old)
