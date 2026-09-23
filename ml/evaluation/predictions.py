from __future__ import annotations

import hashlib
import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

SCHEMA_VERSION = "prediction-artifact-v1"
_MODEL_VERSION_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*-v\d+\.\d+$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_NPZ_KEYS = {
    "logits",
    "targets",
    "recording_ids",
    "frame_offsets_s",
    "mask",
    "metadata_json",
    "content_sha256",
}


@dataclass(frozen=True)
class PredictionArtifact:
    """Framework-neutral SED output arranged as [window, frame, class]."""

    logits: NDArray[np.float32]
    targets: NDArray[np.uint8]
    recording_ids: NDArray[np.str_]
    frame_offsets_s: NDArray[np.float64]
    mask: NDArray[np.bool_]
    class_ids: tuple[str, ...]
    split: str
    model_version: str
    frame_hop_s: float
    taxonomy_sha256: str


def _metadata(artifact: PredictionArtifact) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "split": artifact.split,
        "model_version": artifact.model_version,
        "class_ids": list(artifact.class_ids),
        "frame_hop_s": artifact.frame_hop_s,
        "taxonomy_sha256": artifact.taxonomy_sha256,
    }


def _normalized(artifact: PredictionArtifact) -> PredictionArtifact:
    if not np.isin(artifact.targets, (0, 1)).all():
        raise ValueError("targets must be binary")
    if not np.isin(artifact.mask, (0, 1)).all():
        raise ValueError("mask must be binary")
    return PredictionArtifact(
        logits=np.ascontiguousarray(artifact.logits, dtype=np.float32),
        targets=np.ascontiguousarray(artifact.targets, dtype=np.uint8),
        recording_ids=np.ascontiguousarray(artifact.recording_ids, dtype=np.str_),
        frame_offsets_s=np.ascontiguousarray(artifact.frame_offsets_s, dtype=np.float64),
        mask=np.ascontiguousarray(artifact.mask, dtype=np.bool_),
        class_ids=tuple(artifact.class_ids),
        split=str(artifact.split),
        model_version=str(artifact.model_version),
        frame_hop_s=float(artifact.frame_hop_s),
        taxonomy_sha256=str(artifact.taxonomy_sha256),
    )


def validate_predictions(
    artifact: PredictionArtifact,
    *,
    expected_class_ids: tuple[str, ...],
) -> None:
    """Reject artifacts whose layout or provenance cannot support valid SED metrics."""
    if artifact.logits.ndim != 3:
        raise ValueError("logits must have shape [window, frame, class]")
    if artifact.targets.shape != artifact.logits.shape:
        raise ValueError("targets must have the same shape as logits")
    windows, frames, classes = artifact.logits.shape
    if windows == 0 or frames == 0:
        raise ValueError("prediction artifact cannot contain empty window/frame axes")
    if artifact.mask.shape != (windows, frames):
        raise ValueError("mask must have shape [window, frame]")
    if artifact.recording_ids.shape != (windows,):
        raise ValueError("recording_ids must have shape [window]")
    if artifact.frame_offsets_s.shape != (windows,):
        raise ValueError("frame_offsets_s must have shape [window]")
    if artifact.class_ids != expected_class_ids:
        raise ValueError("class_ids do not match configured polyphonic_class_ids order")
    if classes != len(artifact.class_ids) or len(set(artifact.class_ids)) != classes:
        raise ValueError("class axis and unique class_ids must have the same length")
    if artifact.split not in {"dev", "test"}:
        raise ValueError("split must be 'dev' or 'test'")
    if not _MODEL_VERSION_PATTERN.fullmatch(artifact.model_version):
        raise ValueError("model_version must follow <component>-v<major>.<minor>")
    if not _SHA256_PATTERN.fullmatch(artifact.taxonomy_sha256):
        raise ValueError("taxonomy_sha256 must be a lowercase SHA-256 digest")
    if not np.isfinite(artifact.frame_hop_s) or artifact.frame_hop_s <= 0:
        raise ValueError("frame_hop_s must be finite and positive")
    if not np.isfinite(artifact.frame_offsets_s).all() or (artifact.frame_offsets_s < 0).any():
        raise ValueError("frame_offsets_s must be finite and non-negative")
    if any(not str(recording_id).strip() for recording_id in artifact.recording_ids):
        raise ValueError("recording_ids cannot contain empty values")
    if not np.isfinite(artifact.logits[artifact.mask]).all():
        raise ValueError("valid logits must be finite")
    if not np.isin(artifact.targets, (0, 1)).all():
        raise ValueError("targets must be binary")
    for row in artifact.mask:
        false_indices = np.flatnonzero(~row)
        if false_indices.size and row[false_indices[0] :].any():
            raise ValueError("mask padding must be a contiguous suffix")


def _content_sha256(artifact: PredictionArtifact, metadata_json: str) -> str:
    digest = hashlib.sha256(metadata_json.encode("utf-8"))
    for array in (
        artifact.logits,
        artifact.targets,
        artifact.recording_ids,
        artifact.frame_offsets_s,
        artifact.mask,
    ):
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def save_predictions(
    path: Path,
    artifact: PredictionArtifact,
    *,
    expected_class_ids: tuple[str, ...],
) -> str:
    """Validate and atomically save an NPZ artifact; return its content digest."""
    normalized = _normalized(artifact)
    validate_predictions(normalized, expected_class_ids=expected_class_ids)
    metadata_json = json.dumps(_metadata(normalized), sort_keys=True, separators=(",", ":"))
    content_sha256 = _content_sha256(normalized, metadata_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as handle:
            temporary_path = Path(handle.name)
            np.savez_compressed(
                handle,
                logits=normalized.logits,
                targets=normalized.targets,
                recording_ids=normalized.recording_ids,
                frame_offsets_s=normalized.frame_offsets_s,
                mask=normalized.mask,
                metadata_json=np.asarray(metadata_json),
                content_sha256=np.asarray(content_sha256),
            )
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return content_sha256


def load_predictions(
    path: Path,
    *,
    expected_class_ids: tuple[str, ...],
) -> PredictionArtifact:
    """Load an NPZ without pickle and verify schema, class order, and content digest."""
    with np.load(path, allow_pickle=False) as stored:
        if set(stored.files) != _NPZ_KEYS:
            raise ValueError(f"prediction artifact keys must be {sorted(_NPZ_KEYS)}")
        try:
            metadata_json = str(stored["metadata_json"].item())
            metadata = json.loads(metadata_json)
            stored_digest = str(stored["content_sha256"].item())
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError("prediction artifact metadata is invalid") from error
        if not isinstance(metadata, dict):
            raise ValueError("prediction artifact metadata must be an object")
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"unsupported prediction schema: {metadata.get('schema_version')!r}")
        required_metadata = {
            "schema_version",
            "split",
            "model_version",
            "class_ids",
            "frame_hop_s",
            "taxonomy_sha256",
        }
        if set(metadata) != required_metadata:
            raise ValueError("prediction artifact metadata fields are invalid")
        try:
            artifact = PredictionArtifact(
                logits=np.asarray(stored["logits"], dtype=np.float32),
                targets=np.asarray(stored["targets"]),
                recording_ids=np.asarray(stored["recording_ids"], dtype=np.str_),
                frame_offsets_s=np.asarray(stored["frame_offsets_s"], dtype=np.float64),
                mask=np.asarray(stored["mask"]),
                class_ids=tuple(metadata["class_ids"]),
                split=str(metadata["split"]),
                model_version=str(metadata["model_version"]),
                frame_hop_s=float(metadata["frame_hop_s"]),
                taxonomy_sha256=str(metadata["taxonomy_sha256"]),
            )
        except (TypeError, ValueError) as error:
            raise ValueError("prediction artifact arrays or metadata types are invalid") from error
    artifact = _normalized(artifact)
    validate_predictions(artifact, expected_class_ids=expected_class_ids)
    actual_digest = _content_sha256(artifact, metadata_json)
    if not _SHA256_PATTERN.fullmatch(stored_digest) or actual_digest != stored_digest:
        raise ValueError("prediction artifact content digest mismatch")
    return artifact
