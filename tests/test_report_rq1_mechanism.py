import json

import numpy as np
import pytest

from ml.evaluation.predictions import PredictionArtifact
from scripts.report_rq1_mechanism import compare_branches, decompose, frame_map, learning_curve


def test_learning_curve_uses_validation_min_loss_and_missing_epochs(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"epochs": [
        {"epoch": 3, "validation": {"macro_average_precision": 0.8, "macro_f1": 0.2,
                                    "loss": 0.3}},
        {"epoch": 1, "validation": {"macro_average_precision": 0.4, "macro_f1": 0.5,
                                    "loss": 0.7}},
    ]}))
    result = learning_curve(path)
    assert result["best"]["loss"] == {"epoch": 3, "value": 0.3}
    assert result["best"]["macro_f1"]["epoch"] == 1
    assert result["selected_epochs"]["30"] is None
    assert result["curve"][0]["epoch"] == 1


def artifact(split="dev"):
    # Excluded recording and padding would spoil AP if either entered the calculation.
    return PredictionArtifact(
        logits=np.array([[[4, 4], [-4, -4], [10, 10]],
                         [[10, 10], [-10, -10], [10, 10]]], dtype=np.float32),
        targets=np.array([[[1, 0], [0, 0], [0, 1]],
                          [[0, 0], [1, 0], [0, 1]]], dtype=np.uint8),
        mask=np.array([[True, True, False], [True, True, False]]),
        recording_ids=np.array(["annotated", "missing_gt"]), frame_offsets_s=np.array([0., 0.]),
        class_ids=("bells", "birds"), split=split, model_version="sed-v1.0", frame_hop_s=0.1,
        taxonomy_sha256="a" * 64)


def test_frame_map_excludes_padding_missing_gt_and_classes_without_positive():
    result = frame_map(artifact(), ["annotated"])
    assert result["value"] == 1
    assert result["n_active_classes"] == 1
    assert result["n_valid_window_frames"] == 2
    assert result["per_class"] == {"bells": 1}


def test_decomposition_rejects_test_metadata_even_under_dev_filename(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.report_rq1_mechanism.load_predictions",
                        lambda *a, **kw: artifact(split="test"))
    with pytest.raises(ValueError, match="prediction dev"):
        decompose(tmp_path, {}, ("bells", "birds"))


def test_decomposition_filters_recordings_and_uses_shared_metrics(tmp_path, monkeypatch):
    import scripts.report_rq1_mechanism as report

    (tmp_path / "predictions").mkdir()
    (tmp_path / "predictions/dev.npz").write_bytes(b"fixture")
    (tmp_path / "postproc_cv.json").write_text(json.dumps({
        "class_ids": ["bells", "birds"], "calibrated_on": "dev",
        "per_class": {c: {"theta": 0.5} for c in ("bells", "birds")}}))
    monkeypatch.setattr(report, "load_predictions", lambda *a, **kw: artifact())
    monkeypatch.setattr(report, "priors_from_postproc", lambda *a: {})
    seen = {}

    def process(probabilities, **kwargs):
        seen.update(probabilities)
        return {rid: [] for rid in probabilities}

    collars = []
    monkeypatch.setattr(report, "process_recordings", process)
    monkeypatch.setattr(report, "segment_f1", lambda *a: 0.7)
    monkeypatch.setattr(report, "f1", lambda *a, **kw: collars.append(kw) or 0.5)
    result = decompose(tmp_path, {"annotated": []}, ("bells", "birds"))
    assert set(seen) == {"annotated"}
    assert {"t_collar": 1.0, "percentage_of_length": 0.5} in collars
    assert {"evaluate_onset": False} in collars
    assert {"evaluate_offset": False} in collars
    assert result["metrics"]["segment_f1_1s"] == 0.7


def test_branch_means_and_cartesian_wins_include_ties(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"epochs": [{"epoch": 1, "validation": {
        "macro_average_precision": 0.4, "macro_f1": 0.2, "loss": 0.3}}]}))
    learning = learning_curve(path)
    branches = {b: [{"metrics": {"event_f1": v}, "learning": learning} for v in values]
                for b, values in {"B": [0.1, 0.2, 0.3], "C": [0.2, 0.3, 0.4]}.items()}
    result = compare_branches(branches)
    assert result["comparison"]["event_f1"]["c_gt_b_pairs"] == 6
    assert result["comparison"]["event_f1"]["total_pairs"] == 9
    assert result["comparison"]["event_f1"]["delta_c_minus_b"] == pytest.approx(0.1)
