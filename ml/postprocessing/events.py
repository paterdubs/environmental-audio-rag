"""Convert frame probabilities into deterministic event timelines."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DurationPrior:
    """Train-derived post-processing parameters for one class."""

    median_w: int
    d_min_s: float
    g_max_s: float
    n_events: int = 0
    n_gaps: int = 0


@dataclass(frozen=True)
class PostprocessedEvent:
    recording_id: str
    class_id: str
    onset_s: float
    offset_s: float
    score: float

    def as_dict(self) -> dict[str, str | float]:
        return {
            "recording_id": self.recording_id,
            "class_id": self.class_id,
            "event_label": self.class_id,
            "onset": self.onset_s,
            "offset": self.offset_s,
            "onset_s": self.onset_s,
            "offset_s": self.offset_s,
            "score": self.score,
        }


def _validate_inputs(
    probabilities: np.ndarray,
    class_ids: Sequence[str],
    thresholds: Mapping[str, float],
    priors: Mapping[str, DurationPrior],
    frame_rate: float,
) -> np.ndarray:
    values = np.asarray(probabilities)
    if values.ndim != 2 or values.shape[1] != len(class_ids):
        raise ValueError("probabilities must have shape [frame, class]")
    if not np.issubdtype(values.dtype, np.floating):
        raise TypeError("probabilities must use a floating dtype")
    if not np.isfinite(values).all() or np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("probabilities must be finite values in [0, 1]")
    if frame_rate <= 0:
        raise ValueError("frame_rate must be positive")
    expected = set(class_ids)
    if set(thresholds) != expected or set(priors) != expected:
        raise ValueError("thresholds and priors must cover exactly class_ids")
    for class_id in class_ids:
        theta = float(thresholds[class_id])
        prior = priors[class_id]
        if not 0.0 <= theta <= 1.0:
            raise ValueError(f"threshold for {class_id} must be in [0, 1]")
        if prior.median_w < 1 or prior.median_w % 2 == 0:
            raise ValueError(f"median_w for {class_id} must be a positive odd integer")
        if prior.d_min_s < 0 or prior.g_max_s < 0:
            raise ValueError(f"duration prior for {class_id} cannot be negative")
    return values


def _median_filter(values: np.ndarray, width: int) -> np.ndarray:
    if width == 1 or values.size == 0:
        return values.copy()
    radius = width // 2
    padded = np.pad(values, (radius, radius), mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, width)
    return np.median(windows, axis=-1)


def _active_runs(active: np.ndarray) -> list[tuple[int, int]]:
    padded = np.pad(active.astype(np.int8), (1, 1))
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    stops = np.flatnonzero(changes == -1)
    return list(zip(starts.tolist(), stops.tolist(), strict=True))


def _merge_runs(
    runs: list[tuple[int, int]], *, max_gap_s: float, frame_rate: float
) -> list[tuple[int, int]]:
    if not runs:
        return []
    merged = [runs[0]]
    for start, stop in runs[1:]:
        previous_start, previous_stop = merged[-1]
        gap_s = (start - previous_stop) / frame_rate
        if gap_s <= max_gap_s + 1e-12:
            merged[-1] = (previous_start, stop)
        else:
            merged.append((start, stop))
    return merged


def probabilities_to_events(
    probabilities: np.ndarray,
    *,
    recording_id: str,
    class_ids: Sequence[str],
    thresholds: Mapping[str, float],
    priors: Mapping[str, DurationPrior],
    frame_rate: float,
    only_classes: frozenset[str] | None = None,
) -> list[PostprocessedEvent]:
    """Apply median filter, threshold, gap merging, then minimum duration.

    `only_classes` restricts the (expensive — median filter over every frame)
    per-class work to a subset, for callers that already know every other
    class is suppressed for this call. This changes nothing about the classes
    that ARE processed (each column is independent); it only skips redundant
    work for the rest. Default (`None`) processes every class, identical to
    the original behaviour — added after `sweep_per_class_thresholds` (W3.6)
    was measured at ~4.3s per call over a full test recording set purely from
    reprocessing 20 suppressed classes to search **one**: 21 classes x 19
    threshold values = 399 calls, each doing all 21 classes' median filter for
    a candidate that suppresses 20 of them via `theta=1.0` — ~30 min total for
    output that is otherwise entirely thrown away (H2, 2026-09-23).
    """
    values = _validate_inputs(probabilities, class_ids, thresholds, priors, frame_rate)
    events: list[PostprocessedEvent] = []
    for class_index, class_id in enumerate(class_ids):
        if only_classes is not None and class_id not in only_classes:
            continue
        prior = priors[class_id]
        filtered = _median_filter(values[:, class_index], prior.median_w)
        runs = _active_runs(filtered >= float(thresholds[class_id]))
        runs = _merge_runs(runs, max_gap_s=prior.g_max_s, frame_rate=frame_rate)
        for start, stop in runs:
            duration_s = (stop - start) / frame_rate
            if duration_s + 1e-12 < prior.d_min_s:
                continue
            events.append(
                PostprocessedEvent(
                    recording_id=recording_id,
                    class_id=class_id,
                    onset_s=start / frame_rate,
                    offset_s=stop / frame_rate,
                    score=float(np.max(filtered[start:stop])),
                )
            )
    return sorted(events, key=lambda item: (item.onset_s, item.offset_s, item.class_id))


def process_recordings(
    probabilities_by_recording: Mapping[str, np.ndarray],
    *,
    class_ids: Sequence[str],
    thresholds: Mapping[str, float],
    priors: Mapping[str, DurationPrior],
    frame_rate: float,
    only_classes: frozenset[str] | None = None,
) -> dict[str, list[dict[str, str | float]]]:
    """Post-process multiple recordings into sed_eval-compatible event rows.

    See `probabilities_to_events` for `only_classes`.
    """
    return {
        recording_id: [
            event.as_dict()
            for event in probabilities_to_events(
                probabilities,
                recording_id=recording_id,
                class_ids=class_ids,
                thresholds=thresholds,
                priors=priors,
                frame_rate=frame_rate,
                only_classes=only_classes,
            )
        ]
        for recording_id, probabilities in probabilities_by_recording.items()
    }
