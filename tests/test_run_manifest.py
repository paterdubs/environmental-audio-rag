import json
import random
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
import torch
from jsonschema import Draft202012Validator

from ml.training.common import seed_everything
from ml.training.manifest import (
    ManifestValidationError,
    attach_postproc,
    attach_prediction,
    build_run_manifest,
    complete_run,
    sha256_json,
    validate_run_manifest,
)

SHA = "a" * 64
ROOT = Path(__file__).resolve().parents[1]


def make_manifest(*, provisional: bool = False) -> dict:
    config = {"epochs": 8, "learning_rate": 0.001}
    return build_run_manifest(
        command=["python", "-m", "scripts.train_sed"],
        config=config,
        class_ids=["birds", "bells"],
        taxonomy_sha256=SHA,
        split_sha256="b" * 64,
        data_manifest_sha256="c" * 64,
        feature_config_sha256="d" * 64,
        seeds={"python": 7, "numpy": 7, "torch": 7, "cuda": 7},
        git={"revision": "e" * 40, "dirty": provisional},
        environment={"torch": torch.__version__},
        provisional=provisional,
        branch="B",
        checkpoint_selection_rule="best dev frame_macro_f1",
        primary_metric="event_macro_f1",
    )


def test_seed_everything_repeats_all_cpu_rngs() -> None:
    evidence = seed_everything(29)
    first = (random.random(), np.random.random(), torch.rand(2))

    seed_everything(29)
    second = (random.random(), np.random.random(), torch.rand(2))

    assert evidence == {"python": 29, "numpy": 29, "torch": 29, "cuda": 29}
    assert first[0] == second[0]
    assert first[1] == second[1]
    assert torch.equal(first[2], second[2])


def test_seed_everything_rejects_negative_seed() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        seed_everything(-1)


def test_manifest_binds_config_and_artifacts_by_hash() -> None:
    manifest = make_manifest()
    manifest = attach_prediction(
        manifest, split="dev", path="predictions/dev.npz", sha256="f" * 64
    )
    manifest = attach_postproc(manifest, sha256="1" * 64)

    assert manifest["config_sha256"] == sha256_json(manifest["config"])
    assert manifest["predictions"]["dev"]["path"] == "predictions/dev.npz"
    assert manifest["postproc_sha256"] == "1" * 64


def test_manifest_v2_matches_json_schema() -> None:
    schema = json.loads(
        (ROOT / "contracts" / "run_manifest.schema.json").read_text(encoding="utf-8")
    )

    Draft202012Validator(schema).validate(make_manifest())


def test_manifest_rejects_config_changed_after_hashing() -> None:
    manifest = make_manifest()
    manifest["config"]["epochs"] = 9

    with pytest.raises(ManifestValidationError, match="config_sha256"):
        validate_run_manifest(manifest)


def test_manifest_rejects_missing_rng_seed() -> None:
    manifest = make_manifest()
    del manifest["seeds"]["cuda"]

    with pytest.raises(ManifestValidationError, match="seeds"):
        validate_run_manifest(manifest)


def test_incomplete_run_cannot_claim_completion_artifacts() -> None:
    manifest = make_manifest()
    manifest["best_checkpoint"] = "checkpoints/best.pt"

    with pytest.raises(ManifestValidationError, match="incomplete"):
        validate_run_manifest(manifest)


def test_complete_clean_run_is_eligible_for_final_measurement() -> None:
    manifest = complete_run(
        make_manifest(), best_checkpoint="checkpoints/best.pt", wall_clock_s=12.5
    )

    validate_run_manifest(manifest, for_final_measurement=True)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"complete": False}, "complete"),
        ({"provisional": True}, "provisional"),
        ({"git": {"revision": "e" * 40, "dirty": True}}, "dirty"),
        ({"git": {"revision": "HEAD", "dirty": False}}, "concrete Git revision"),
    ],
)
def test_final_measurement_policy_rejects_ineligible_run(change: dict, message: str) -> None:
    manifest = complete_run(
        make_manifest(), best_checkpoint="checkpoints/best.pt", wall_clock_s=12.5
    )
    manifest.update(deepcopy(change))
    if change.get("complete") is False:
        manifest["best_checkpoint"] = None
        manifest["wall_clock_s"] = None

    with pytest.raises(ManifestValidationError, match=message):
        validate_run_manifest(manifest, for_final_measurement=True)


def test_prediction_reference_rejects_test_typo_and_absolute_path() -> None:
    with pytest.raises(ManifestValidationError, match="split"):
        attach_prediction(make_manifest(), split="validation", path="x.npz", sha256=SHA)
    with pytest.raises(ManifestValidationError, match="relative"):
        attach_prediction(make_manifest(), split="dev", path="C:/tmp/dev.npz", sha256=SHA)
