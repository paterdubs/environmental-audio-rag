import json
from pathlib import Path

import numpy as np
import pytest

from ml.evaluation.predictions import (
    PredictionArtifact,
    load_predictions,
    save_predictions,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
CLASS_IDS = TAXONOMY.polyphonic_class_ids


def _artifact() -> PredictionArtifact:
    logits = np.arange(2 * 4 * len(CLASS_IDS), dtype=np.float32).reshape(2, 4, -1)
    targets = np.zeros_like(logits, dtype=np.uint8)
    targets[0, 1:3, 0] = 1
    return PredictionArtifact(
        logits=logits,
        targets=targets,
        recording_ids=np.asarray(["datased:S-0001", "datased:S-0002"]),
        frame_offsets_s=np.asarray([0.0, 5.0]),
        mask=np.asarray([[True, True, True, True], [True, True, False, False]]),
        class_ids=CLASS_IDS,
        split="dev",
        model_version="sed-v1.0",
        frame_hop_s=0.02,
        taxonomy_sha256=TAXONOMY.checksum,
    )


def test_prediction_artifact_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "predictions" / "dev.npz"
    digest = save_predictions(path, _artifact(), expected_class_ids=CLASS_IDS)

    loaded = load_predictions(path, expected_class_ids=CLASS_IDS)

    assert len(digest) == 64
    assert loaded.class_ids == CLASS_IDS
    assert loaded.logits.dtype == np.float32
    assert loaded.targets.dtype == np.uint8
    assert loaded.mask.dtype == np.bool_
    np.testing.assert_array_equal(loaded.logits, _artifact().logits)


def test_prediction_artifact_rejects_wrong_class_order(tmp_path: Path) -> None:
    artifact = _artifact()
    wrong_order = tuple(reversed(CLASS_IDS))

    with pytest.raises(ValueError, match="polyphonic_class_ids order"):
        save_predictions(tmp_path / "dev.npz", artifact, expected_class_ids=wrong_order)


def test_prediction_artifact_rejects_non_contiguous_mask(tmp_path: Path) -> None:
    artifact = _artifact()
    invalid = PredictionArtifact(
        **{**artifact.__dict__, "mask": np.asarray([[True, False, True, False]] * 2)}
    )

    with pytest.raises(ValueError, match="contiguous suffix"):
        save_predictions(tmp_path / "dev.npz", invalid, expected_class_ids=CLASS_IDS)


def test_prediction_artifact_rejects_non_binary_targets(tmp_path: Path) -> None:
    artifact = _artifact()
    invalid_targets = artifact.targets.astype(np.float32)
    invalid_targets[0, 0, 0] = 0.5
    invalid = PredictionArtifact(**{**artifact.__dict__, "targets": invalid_targets})

    with pytest.raises(ValueError, match="targets must be binary"):
        save_predictions(tmp_path / "dev.npz", invalid, expected_class_ids=CLASS_IDS)


def test_prediction_artifact_detects_content_tampering(tmp_path: Path) -> None:
    path = tmp_path / "dev.npz"
    save_predictions(path, _artifact(), expected_class_ids=CLASS_IDS)
    with np.load(path, allow_pickle=False) as stored:
        values = {key: stored[key].copy() for key in stored.files}
    values["logits"][0, 0, 0] += 1
    np.savez_compressed(path, **values)

    with pytest.raises(ValueError, match="digest mismatch"):
        load_predictions(path, expected_class_ids=CLASS_IDS)


def test_prediction_artifact_rejects_unknown_schema(tmp_path: Path) -> None:
    path = tmp_path / "dev.npz"
    save_predictions(path, _artifact(), expected_class_ids=CLASS_IDS)
    with np.load(path, allow_pickle=False) as stored:
        values = {key: stored[key].copy() for key in stored.files}
    metadata = json.loads(str(values["metadata_json"].item()))
    metadata["schema_version"] = "prediction-artifact-v999"
    values["metadata_json"] = np.asarray(json.dumps(metadata))
    np.savez_compressed(path, **values)

    with pytest.raises(ValueError, match="unsupported prediction schema"):
        load_predictions(path, expected_class_ids=CLASS_IDS)
