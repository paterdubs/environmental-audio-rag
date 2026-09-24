"""Leakage-safe duration-prior derivation and threshold calibration."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from ml.evaluation.predictions import PredictionArtifact
from ml.postprocessing.events import DurationPrior, process_recordings
from ml.taxonomy import Taxonomy, load_taxonomy

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAXONOMY_PATH = ROOT / "ml" / "configs" / "taxonomy.yaml"
DEFAULT_THRESHOLD_GRID = tuple(round(value / 100, 2) for value in range(5, 100, 5))
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

EventRows = Mapping[str, Sequence[Mapping[str, Any]]]
Predictions = Mapping[str, np.ndarray]
GlobalScore = Callable[[dict[str, list[dict[str, str | float]]]], float]
ClassScore = Callable[[dict[str, list[dict[str, str | float]]], str], float]


def _taxonomy(taxonomy: Taxonomy | None) -> Taxonomy:
    return taxonomy if taxonomy is not None else load_taxonomy(DEFAULT_TAXONOMY_PATH)


def _require_polyphonic_order(class_ids: Sequence[str], taxonomy: Taxonomy | None) -> None:
    expected = _taxonomy(taxonomy).polyphonic_class_ids
    if len(expected) != 21:
        raise ValueError("taxonomy.polyphonic_class_ids must contain exactly 21 classes")
    if tuple(class_ids) != expected:
        raise ValueError("class_ids must equal taxonomy.polyphonic_class_ids in exact order")


def _class_id(event: Mapping[str, Any]) -> str:
    value = event.get("class_id", event.get("event_label"))
    if not isinstance(value, str):
        raise ValueError("event must contain class_id or event_label")
    return value


def _bounds(event: Mapping[str, Any]) -> tuple[float, float]:
    onset = float(event.get("onset_s", event.get("onset", -1.0)))
    offset = float(event.get("offset_s", event.get("offset", -1.0)))
    if not math.isfinite(onset) or not math.isfinite(offset) or onset < 0 or offset <= onset:
        raise ValueError("event must have finite bounds with 0 <= onset < offset")
    return onset, offset


def _odd_width(value: float) -> int:
    rounded = max(1, int(math.floor(value + 0.5)))
    return rounded if rounded % 2 else rounded + 1


def stack_predictions_by_recording(artifact: PredictionArtifact) -> dict[str, np.ndarray]:
    """Turn a window-indexed `PredictionArtifact` into `process_recordings`'s
    expected `{recording_id: [frames, classes]}` sigmoid-probability mapping.

    `SedFeatureDataset` builds windows recording-by-recording in increasing
    `start_frame` order (H2, ADR-0020 §6), and `collect_predictions` preserves
    that order verbatim — so grouping by first-seen order and concatenating is
    correct without re-sorting. `mask` trims the zero-padded suffix that the
    last (partial) window of a recording carries.
    """
    probabilities = 1.0 / (1.0 + np.exp(-artifact.logits.astype(np.float64)))
    chunks: dict[str, list[np.ndarray]] = defaultdict(list)
    for window_index, recording_id in enumerate(artifact.recording_ids):
        valid = artifact.mask[window_index]
        chunks[str(recording_id)].append(probabilities[window_index][valid])
    return {
        recording_id: np.concatenate(windows, axis=0) for recording_id, windows in chunks.items()
    }


def derive_duration_priors(
    events_by_recording: EventRows,
    *,
    class_ids: Sequence[str],
    frame_rate: float,
    source_split: str,
    taxonomy: Taxonomy | None = None,
    d_min_percentile: float = 5.0,
    g_max_percentile: float = 50.0,
) -> dict[str, DurationPrior]:
    """Derive ADR-0003 priors from train annotations only.

    `d_min_percentile`/`g_max_percentile` default to the values ADR-0003 §3
    picked without empirical backing (nợ kỹ thuật #8) — exposed as parameters
    so `scripts/report_duration_prior_ablation.py` can sweep alternatives
    through this exact function instead of duplicating the percentile logic.
    """
    if source_split != "train":
        raise ValueError("duration priors may only be derived from split='train'")
    _require_polyphonic_order(class_ids, taxonomy)
    if frame_rate <= 0:
        raise ValueError("frame_rate must be positive")
    if not 0.0 <= d_min_percentile <= 100.0:
        raise ValueError("d_min_percentile must be in [0, 100]")
    if not 0.0 <= g_max_percentile <= 100.0:
        raise ValueError("g_max_percentile must be in [0, 100]")

    durations: dict[str, list[float]] = defaultdict(list)
    gaps: dict[str, list[float]] = defaultdict(list)
    allowed = set(class_ids)
    for recording_events in events_by_recording.values():
        by_class: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for event in recording_events:
            class_id = _class_id(event)
            if class_id not in allowed:
                raise ValueError(f"event class is outside polyphonic taxonomy: {class_id}")
            onset, offset = _bounds(event)
            durations[class_id].append(offset - onset)
            by_class[class_id].append((onset, offset))
        for class_id, spans in by_class.items():
            ordered = sorted(spans)
            for (_, previous_offset), (next_onset, _) in zip(ordered, ordered[1:], strict=False):
                if next_onset >= previous_offset:
                    gaps[class_id].append(next_onset - previous_offset)

    missing = [class_id for class_id in class_ids if not durations[class_id]]
    if missing:
        raise ValueError(f"cannot derive duration prior without train events: {missing}")

    priors = {}
    for class_id in class_ids:
        d_min_s = float(np.percentile(durations[class_id], d_min_percentile))
        class_gaps = gaps[class_id]
        g_max_s = float(np.percentile(class_gaps, g_max_percentile)) if class_gaps else 0.0
        priors[class_id] = DurationPrior(
            median_w=_odd_width(d_min_s * frame_rate / 2),
            d_min_s=d_min_s,
            g_max_s=g_max_s,
            n_events=len(durations[class_id]),
            n_gaps=len(class_gaps),
        )
    return priors


def _validate_sweep(split: str, grid: Sequence[float]) -> tuple[float, ...]:
    if split != "dev":
        raise ValueError("threshold calibration may only run on split='dev'")
    values = tuple(float(value) for value in grid)
    if not values or any(not 0.0 < value < 1.0 for value in values):
        raise ValueError("threshold grid must contain values strictly between 0 and 1")
    if list(values) != sorted(set(values)):
        raise ValueError("threshold grid must be sorted and unique")
    return values


def _best(scored: Sequence[tuple[float, float]]) -> tuple[float, float]:
    for _, score in scored:
        if not math.isfinite(score):
            raise ValueError("threshold objective returned a non-finite score")
    return max(scored, key=lambda item: (item[1], -item[0]))


def sweep_global_threshold(
    predictions: Predictions,
    *,
    class_ids: Sequence[str],
    priors: Mapping[str, DurationPrior],
    frame_rate: float,
    score_fn: GlobalScore,
    split: str,
    grid: Sequence[float] = DEFAULT_THRESHOLD_GRID,
    taxonomy: Taxonomy | None = None,
) -> tuple[float, dict[float, float]]:
    """Choose one global threshold on dev; lower theta wins score ties."""
    _require_polyphonic_order(class_ids, taxonomy)
    values = _validate_sweep(split, grid)
    scores = {}
    for theta in values:
        events = process_recordings(
            predictions,
            class_ids=class_ids,
            thresholds=dict.fromkeys(class_ids, theta),
            priors=priors,
            frame_rate=frame_rate,
        )
        scores[theta] = float(score_fn(events))
    best_theta, _ = _best(list(scores.items()))
    return best_theta, scores


def sweep_per_class_thresholds(
    predictions: Predictions,
    *,
    class_ids: Sequence[str],
    priors: Mapping[str, DurationPrior],
    frame_rate: float,
    score_fn: ClassScore,
    split: str,
    grid: Sequence[float] = DEFAULT_THRESHOLD_GRID,
    taxonomy: Taxonomy | None = None,
) -> tuple[dict[str, float], dict[str, dict[float, float]]]:
    """Choose each class threshold independently on dev event metrics."""
    _require_polyphonic_order(class_ids, taxonomy)
    values = _validate_sweep(split, grid)
    thresholds: dict[str, float] = {}
    curves: dict[str, dict[float, float]] = {}
    for class_id in class_ids:
        class_scores = {}
        for theta in values:
            candidate = dict.fromkeys(class_ids, 1.0)
            candidate[class_id] = theta
            events = process_recordings(
                predictions,
                class_ids=class_ids,
                thresholds=candidate,
                priors=priors,
                frame_rate=frame_rate,
                # Every other class is suppressed via theta=1.0 above and would
                # yield empty output anyway — skip computing it. Cuts a real
                # 21-class sweep from ~4.3s/call to a fraction of that (H2,
                # 2026-09-23: this loop is 21 x len(grid) calls).
                only_classes=frozenset({class_id}),
            )
            class_scores[theta] = float(score_fn(events, class_id))
        thresholds[class_id], _ = _best(list(class_scores.items()))
        curves[class_id] = class_scores
    return thresholds, curves


def _require_sha256(name: str, value: str) -> None:
    if not SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")


def build_postproc_artifact(
    *,
    class_ids: Sequence[str],
    thresholds: Mapping[str, float],
    priors: Mapping[str, DurationPrior],
    taxonomy_sha256: str,
    split_sha256: str,
    data_manifest_sha256: str,
    dev_predictions_sha256: str,
    threshold_mode: str,
    threshold_grid: Sequence[float] = DEFAULT_THRESHOLD_GRID,
    calibrated_on: str = "dev",
    duration_prior_from: str = "train",
    taxonomy: Taxonomy | None = None,
) -> dict[str, Any]:
    """Create a frozen, provenance-rich ``postproc.json`` value."""
    artifact = {
        "schema_version": "1.0",
        "frozen": True,
        "class_ids": list(class_ids),
        "taxonomy_sha256": taxonomy_sha256,
        "split_sha256": split_sha256,
        "data_manifest_sha256": data_manifest_sha256,
        "dev_predictions_sha256": dev_predictions_sha256,
        "calibrated_on": calibrated_on,
        "duration_prior_from": duration_prior_from,
        "threshold_mode": threshold_mode,
        "threshold_grid": [float(value) for value in threshold_grid],
        "per_class": {
            class_id: {
                "theta": float(thresholds[class_id]),
                "median_w": priors[class_id].median_w,
                "d_min_s": priors[class_id].d_min_s,
                "g_max_s": priors[class_id].g_max_s,
                "n_train_events": priors[class_id].n_events,
                "n_train_gaps": priors[class_id].n_gaps,
            }
            for class_id in class_ids
        },
    }
    validate_postproc_artifact(artifact, taxonomy=taxonomy)
    return artifact


def validate_postproc_artifact(
    artifact: Mapping[str, Any], *, taxonomy: Taxonomy | None = None
) -> None:
    """Apply semantic guards that JSON Schema alone cannot express."""
    active_taxonomy = _taxonomy(taxonomy)
    if artifact.get("schema_version") != "1.0":
        raise ValueError("unsupported postproc schema_version")
    if artifact.get("calibrated_on") != "dev":
        raise ValueError("postproc artifact must be calibrated on dev")
    if artifact.get("duration_prior_from") != "train":
        raise ValueError("postproc duration priors must come from train")
    if artifact.get("frozen") is not True:
        raise ValueError("postproc artifact must be frozen before test evaluation")
    class_ids = artifact.get("class_ids")
    if not isinstance(class_ids, list):
        raise ValueError("postproc class_ids must be a list")
    _require_polyphonic_order(class_ids, active_taxonomy)
    for name in (
        "taxonomy_sha256",
        "split_sha256",
        "data_manifest_sha256",
        "dev_predictions_sha256",
    ):
        _require_sha256(name, str(artifact.get(name, "")))
    if artifact["taxonomy_sha256"] != active_taxonomy.checksum:
        raise ValueError("taxonomy_sha256 does not match the active taxonomy")
    if artifact.get("threshold_mode") not in {"global", "per_class"}:
        raise ValueError("threshold_mode must be 'global' or 'per_class'")
    grid = artifact.get("threshold_grid")
    if not isinstance(grid, list):
        raise ValueError("threshold_grid must be a list")
    _validate_sweep("dev", grid)
    per_class = artifact.get("per_class")
    if not isinstance(per_class, Mapping) or list(per_class) != class_ids:
        raise ValueError("postproc per_class keys must preserve exact class_ids order")
    for class_id in class_ids:
        parameters = per_class[class_id]
        if not isinstance(parameters, Mapping):
            raise ValueError(f"postproc parameters for {class_id} must be an object")
        theta = float(parameters.get("theta", -1.0))
        median_w = parameters.get("median_w")
        d_min_s = float(parameters.get("d_min_s", -1.0))
        g_max_s = float(parameters.get("g_max_s", -1.0))
        if not 0.0 <= theta <= 1.0:
            raise ValueError(f"theta for {class_id} must be in [0, 1]")
        if not isinstance(median_w, int) or median_w < 1 or median_w % 2 == 0:
            raise ValueError(f"median_w for {class_id} must be a positive odd integer")
        if d_min_s < 0 or g_max_s < 0:
            raise ValueError(f"duration prior for {class_id} cannot be negative")


def write_postproc_json(
    path: Path, artifact: Mapping[str, Any], *, taxonomy: Taxonomy | None = None
) -> None:
    validate_postproc_artifact(artifact, taxonomy=taxonomy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
