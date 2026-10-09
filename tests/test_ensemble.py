from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from ml.evaluation.ensemble import average_predictions
from ml.evaluation.predictions import PredictionArtifact
from ml.taxonomy import load_taxonomy

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml")
CLASS_IDS = TAXONOMY.polyphonic_class_ids


def artifact(logit: float) -> PredictionArtifact:
    shape = (2, 3, len(CLASS_IDS))
    return PredictionArtifact(
        logits=np.full(shape, logit, dtype=np.float32),
        targets=np.zeros(shape, dtype=np.uint8), recording_ids=np.array(["r1", "r1"]),
        frame_offsets_s=np.array([0.0, 0.06]), mask=np.ones((2, 3), dtype=bool),
        class_ids=CLASS_IDS, split="dev", model_version="sed-v1.0", frame_hop_s=0.02,
        taxonomy_sha256=TAXONOMY.checksum,
    )


def test_ensemble_averages_probabilities_not_logits() -> None:
    merged = average_predictions([artifact(10.0), artifact(-10.0)])
    probability = 1.0 / (1.0 + np.exp(-merged.logits.astype(np.float64)))
    assert np.allclose(probability, 0.5, atol=1e-4)
    assert merged.model_version == "sed-ensemble-v1.0"


def test_ensemble_rejects_misaligned_members() -> None:
    shifted = replace(artifact(0.0), frame_offsets_s=np.array([0.0, 0.08]))
    with pytest.raises(ValueError, match="frame_offsets_s"):
        average_predictions([artifact(0.0), shifted])
    with pytest.raises(ValueError, match="split"):
        average_predictions([artifact(0.0), replace(artifact(0.0), split="test")])
    triangular = replace(artifact(0.0), window_weighting="triangular:0.3")
    with pytest.raises(ValueError, match="window_weighting"):
        average_predictions([artifact(0.0), triangular])
    assert average_predictions([triangular, triangular]).window_weighting == "triangular:0.3"


def test_ensemble_needs_two_members() -> None:
    with pytest.raises(ValueError, match="two"):
        average_predictions([artifact(0.0)])


def test_ensemble_manifest_satisfies_run_manifest_contract() -> None:
    import json

    from jsonschema import Draft202012Validator

    from scripts.build_ensemble import ensemble_manifest

    root = Path(__file__).parents[1]
    schema = json.loads((root / "contracts" / "run_manifest.schema.json").read_text("utf-8"))
    member = {"split_sha256": "a" * 64, "data_manifest_sha256": "b" * 64,
              "taxonomy_sha256": TAXONOMY.checksum, "git": {"revision": "c" * 40, "dirty": False}}
    manifest = ensemble_manifest(
        "sed_ensemble_X_20260925T000000Z", "X", [Path("r1"), Path("r2")], [member, member],
        CLASS_IDS, command=["python", "-m", "scripts.build_ensemble"],
        git={"revision": "d" * 40, "dirty": False},
    )
    Draft202012Validator(schema).validate(manifest)
    assert manifest["task"] == "sed_ensemble" and "cv_folds_sha256" not in manifest["config"]


def test_ensemble_of_oof_runs_stays_oof_and_refuses_mixed_members() -> None:
    """ADR-0041 §7: the cross-family tier-C ensemble must keep per-fold priors downstream."""
    from scripts.build_ensemble import ensemble_manifest, oof_folds_sha256

    base = {"split_sha256": "a" * 64, "data_manifest_sha256": "b" * 64,
            "taxonomy_sha256": TAXONOMY.checksum, "git": {"revision": "c" * 40, "dirty": False}}
    oof = {**base, "task": "sed_oof", "config": {"cv_folds_sha256": "e" * 64}}
    manifest = ensemble_manifest("sed_oof_X_20261009T000000Z", "X", [Path("a"), Path("b")],
                                 [oof, oof], CLASS_IDS, command=["python"],
                                 git={"revision": "d" * 40, "dirty": False})
    assert manifest["task"] == "sed_oof" and manifest["config"]["cv_folds_sha256"] == "e" * 64
    with pytest.raises(SystemExit, match="không trộn"):
        oof_folds_sha256([oof, {**base, "task": "sed_polyphonic"}])
    other = {**oof, "config": {"cv_folds_sha256": "f" * 64}}
    with pytest.raises(SystemExit, match="file fold"):
        oof_folds_sha256([oof, other])
