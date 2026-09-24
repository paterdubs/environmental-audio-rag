"""Versioned run-manifest helpers and reportability policy.

This module does not inspect D3/D4 itself.  A launcher must only create a
non-provisional manifest after its data preflight has passed.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

MANIFEST_VERSION = 2
SEED_NAMES = ("python", "numpy", "torch", "cuda")
PREDICTION_SPLITS = frozenset({"dev", "test"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_REVISION = re.compile(r"^[0-9a-f]{40,64}$")


class ManifestValidationError(ValueError):
    """Raised when a run manifest violates reproducibility policy."""


def sha256_json(value: object) -> str:
    """Hash JSON data using a stable, whitespace-independent representation."""

    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_portable_relative(value: str | Path) -> bool:
    """True only for a relative path that stays relative on every OS.

    `Path.is_absolute()` follows the host: on Linux `C:/x` is relative, on Windows
    `/x` is relative (no drive). Manifests move between both, so reject a path that
    is absolute, drive-qualified or rooted under either convention.
    """
    text = str(value)
    if not text:
        return False
    windows, posix = PureWindowsPath(text), PurePosixPath(text.replace("\\", "/"))
    if windows.drive or windows.root or posix.is_absolute():
        return False
    return ".." not in windows.parts and ".." not in posix.parts


def prediction_reference(path: str | Path, sha256: str) -> dict[str, str]:
    """Build a portable reference to an immutable prediction artifact."""

    if not _is_portable_relative(path):
        raise ManifestValidationError("prediction path must be relative to the run directory")
    _require_sha256("prediction sha256", sha256)
    return {"path": Path(path).as_posix(), "sha256": sha256}


def build_run_manifest(
    *,
    command: list[str],
    config: Mapping[str, Any],
    class_ids: list[str],
    taxonomy_sha256: str,
    split_sha256: str,
    data_manifest_sha256: str,
    feature_config_sha256: str,
    seeds: Mapping[str, int],
    git: Mapping[str, Any],
    environment: Mapping[str, Any],
    provisional: bool,
    branch: str,
    checkpoint_selection_rule: str,
    primary_metric: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an incomplete v2 manifest and validate its immutable provenance."""

    manifest: dict[str, Any] = {
        "manifest_version": MANIFEST_VERSION,
        "command": list(command),
        "config": dict(config),
        "config_sha256": sha256_json(config),
        "class_ids": list(class_ids),
        "taxonomy_sha256": taxonomy_sha256,
        "split_sha256": split_sha256,
        "data_manifest_sha256": data_manifest_sha256,
        "feature_config_sha256": feature_config_sha256,
        "postproc_sha256": None,
        "predictions": {},
        "seeds": dict(seeds),
        "git": dict(git),
        "environment": dict(environment),
        "provisional": provisional,
        "branch": branch,
        "checkpoint_selection_rule": checkpoint_selection_rule,
        "primary_metric": primary_metric,
        "wall_clock_s": None,
        "complete": False,
        "best_checkpoint": None,
    }
    if extra:
        overlap = manifest.keys() & extra.keys()
        if overlap:
            raise ManifestValidationError(
                f"extra cannot replace manifest fields: {sorted(overlap)}"
            )
        manifest.update(deepcopy(dict(extra)))
    validate_run_manifest(manifest)
    return manifest


def attach_prediction(
    manifest: Mapping[str, Any],
    *,
    split: str,
    path: str | Path,
    sha256: str,
) -> dict[str, Any]:
    """Return a copy with a content-addressed dev or test prediction reference."""

    if split not in PREDICTION_SPLITS:
        raise ManifestValidationError(
            f"prediction split must be one of {sorted(PREDICTION_SPLITS)}"
        )
    updated = deepcopy(dict(manifest))
    updated.setdefault("predictions", {})[split] = prediction_reference(path, sha256)
    validate_run_manifest(updated)
    return updated


def attach_postproc(manifest: Mapping[str, Any], *, sha256: str) -> dict[str, Any]:
    """Return a copy bound to a frozen post-processing artifact."""

    _require_sha256("postproc_sha256", sha256)
    updated = deepcopy(dict(manifest))
    updated["postproc_sha256"] = sha256
    validate_run_manifest(updated)
    return updated


def complete_run(
    manifest: Mapping[str, Any], *, best_checkpoint: str | Path, wall_clock_s: float
) -> dict[str, Any]:
    """Return a completed copy; interrupted runs remain incomplete by default."""

    if not _is_portable_relative(best_checkpoint):
        raise ManifestValidationError("best_checkpoint must be relative to the run directory")
    checkpoint = Path(best_checkpoint).as_posix()
    updated = deepcopy(dict(manifest))
    updated.update(
        complete=True,
        best_checkpoint=checkpoint,
        wall_clock_s=wall_clock_s,
    )
    validate_run_manifest(updated)
    return updated


def validate_run_manifest(
    manifest: Mapping[str, Any], *, for_final_measurement: bool = False
) -> None:
    """Validate v2 structure and optionally the stricter final-report policy."""

    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise ManifestValidationError(f"manifest_version must be {MANIFEST_VERSION}")

    required = {
        "command",
        "config",
        "config_sha256",
        "class_ids",
        "taxonomy_sha256",
        "split_sha256",
        "data_manifest_sha256",
        "feature_config_sha256",
        "postproc_sha256",
        "predictions",
        "seeds",
        "git",
        "environment",
        "provisional",
        "branch",
        "checkpoint_selection_rule",
        "primary_metric",
        "wall_clock_s",
        "complete",
        "best_checkpoint",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ManifestValidationError(f"missing manifest fields: {missing}")

    for name in (
        "config_sha256",
        "taxonomy_sha256",
        "split_sha256",
        "data_manifest_sha256",
        "feature_config_sha256",
    ):
        _require_sha256(name, manifest[name])
    if manifest["config_sha256"] != sha256_json(manifest["config"]):
        raise ManifestValidationError("config_sha256 does not match config")
    if manifest["postproc_sha256"] is not None:
        _require_sha256("postproc_sha256", manifest["postproc_sha256"])

    _validate_seeds(manifest["seeds"])
    _validate_git(manifest["git"])
    _validate_predictions(manifest["predictions"])
    _require_nonempty_strings(manifest)

    if not isinstance(manifest["provisional"], bool) or not isinstance(manifest["complete"], bool):
        raise ManifestValidationError("provisional and complete must be booleans")
    if manifest["complete"]:
        if not isinstance(manifest["best_checkpoint"], str) or not manifest["best_checkpoint"]:
            raise ManifestValidationError("complete run requires best_checkpoint")
        wall_clock_s = manifest["wall_clock_s"]
        if isinstance(wall_clock_s, bool) or not isinstance(wall_clock_s, (int, float)):
            raise ManifestValidationError("complete run requires numeric wall_clock_s")
        if not math.isfinite(wall_clock_s) or wall_clock_s < 0:
            raise ManifestValidationError("wall_clock_s must be non-negative")
    elif manifest["best_checkpoint"] is not None or manifest["wall_clock_s"] is not None:
        raise ManifestValidationError(
            "incomplete run cannot claim checkpoint or wall-clock completion"
        )

    if for_final_measurement:
        _validate_final_measurement_policy(manifest)


def _require_sha256(name: str, value: object) -> None:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ManifestValidationError(f"{name} must be a lowercase SHA-256")


def _validate_seeds(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != set(SEED_NAMES):
        raise ManifestValidationError(f"seeds must contain exactly {list(SEED_NAMES)}")
    invalid = (
        isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
        for seed in value.values()
    )
    if any(invalid):
        raise ManifestValidationError("every RNG seed must be a non-negative integer")


def _validate_git(value: object) -> None:
    if not isinstance(value, Mapping):
        raise ManifestValidationError("git must be an object")
    if set(value) != {"revision", "dirty"}:
        raise ManifestValidationError("git must contain exactly revision and dirty")
    if not isinstance(value["revision"], str) or not value["revision"]:
        raise ManifestValidationError("git.revision must be a non-empty string")
    if not isinstance(value["dirty"], bool):
        raise ManifestValidationError("git.dirty must be boolean")


def _validate_predictions(value: object) -> None:
    if not isinstance(value, Mapping) or not set(value).issubset(PREDICTION_SPLITS):
        raise ManifestValidationError("predictions may only reference dev and test")
    for split, reference in value.items():
        if not isinstance(reference, Mapping) or set(reference) != {"path", "sha256"}:
            raise ManifestValidationError(f"predictions.{split} must contain path and sha256")
        prediction_reference(reference["path"], reference["sha256"])


def _require_nonempty_strings(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest["config"], Mapping):
        raise ManifestValidationError("config must be an object")
    if not isinstance(manifest["environment"], Mapping):
        raise ManifestValidationError("environment must be an object")
    if not isinstance(manifest["command"], list) or not manifest["command"]:
        raise ManifestValidationError("command must be a non-empty list")
    if not all(isinstance(item, str) and item for item in manifest["command"]):
        raise ManifestValidationError("command entries must be non-empty strings")
    if not isinstance(manifest["class_ids"], list) or not manifest["class_ids"]:
        raise ManifestValidationError("class_ids must be a non-empty list")
    if not all(isinstance(class_id, str) and class_id for class_id in manifest["class_ids"]):
        raise ManifestValidationError("class_ids entries must be non-empty strings")
    if len(manifest["class_ids"]) != len(set(manifest["class_ids"])):
        raise ManifestValidationError("class_ids must be unique")
    for name in ("branch", "checkpoint_selection_rule", "primary_metric"):
        if not isinstance(manifest[name], str) or not manifest[name]:
            raise ManifestValidationError(f"{name} must be a non-empty string")


def _validate_final_measurement_policy(manifest: Mapping[str, Any]) -> None:
    if not manifest["complete"]:
        raise ManifestValidationError("final measurement requires a complete run")
    if manifest["provisional"]:
        raise ManifestValidationError("provisional run cannot produce a final measurement")
    if manifest["git"]["dirty"]:
        raise ManifestValidationError("dirty working tree cannot produce a final measurement")
    if _GIT_REVISION.fullmatch(manifest["git"]["revision"]) is None:
        raise ManifestValidationError("final measurement requires a concrete Git revision")
