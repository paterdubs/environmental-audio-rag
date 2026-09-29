import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import scripts.report_multirun_bootstrap as report
from scripts.report_multirun_bootstrap import check_pairing, run_counts


def test_pairing_accepts_matching_or_unrecorded_postproc() -> None:
    check_pairing({"postproc": "D:/repo/ml/runs/r/postproc_cv.json"}, "postproc_cv.json", "r")
    check_pairing({}, "postproc.json", "r")  # older evaluations do not record the file


def test_pairing_rejects_evaluation_from_another_postproc() -> None:
    with pytest.raises(SystemExit, match="cặp file lệch"):
        check_pairing({"postproc": "ml/runs/r/postproc.json"}, "postproc_cv.json", "r")


def test_run_counts_uses_recorded_postproc_and_annotated_eval_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = tmp_path / "run"
    (run / "predictions").mkdir(parents=True)
    postproc = tmp_path / "chosen.json"
    postproc.write_text(json.dumps({"per_class": {"bird": {"theta": 0.5}}}), encoding="utf-8")
    evaluation = {
        "postproc": str(postproc),
        "eval_set": "annotated",
        "event_based_f1": {"f_measure": 1.0},
    }
    (run / "evaluation_cv_annotated.json").write_text(json.dumps(evaluation), encoding="utf-8")
    monkeypatch.setattr(
        report,
        "load_predictions",
        lambda *args, **kwargs: SimpleNamespace(split="test", frame_hop_s=0.1),
    )
    monkeypatch.setattr(report, "stack_predictions_by_recording", lambda artifact: {
        "keep": np.array([[0.9], [0.9]]), "drop": np.array([[0.9], [0.9]])
    })
    monkeypatch.setattr(
        report,
        "restrict",
        lambda probabilities, eval_set: {"keep": probabilities["keep"]},
    )
    monkeypatch.setattr(report, "priors_from_postproc", lambda payload, class_ids: {})
    monkeypatch.setattr(report, "process_recordings", lambda *args, **kwargs: {
        "keep": [{"class_id": "bird", "onset_s": 0.0, "offset_s": 0.2}]
    })
    monkeypatch.setattr(report, "load_events_by_recording", lambda ids: {
        "keep": [{"event_label": "bird", "onset": 0.0, "offset": 0.2}]
    })
    monkeypatch.setattr(
        report,
        "event_counts_per_recording",
        lambda *args, **kwargs: {"keep": (1, 1, 1)},
    )
    taxonomy = SimpleNamespace(polyphonic_class_ids=("bird",))

    counts = run_counts(
        run,
        taxonomy,
        postproc_name="wrong.json",
        evaluation_name="evaluation_cv_annotated.json",
        postproc_from_evaluation=True,
    )

    assert set(counts) == {"keep"}
