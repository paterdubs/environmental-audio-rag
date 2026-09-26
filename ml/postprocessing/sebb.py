"""Event boxes from frame scores by change detection (cSEBB) or hysteresis thresholding.

Frame-level thresholding couples an event's extent to its confidence: with θ = 0.95 an
onset is placed where the score *reaches* 0.95, not where it starts rising — the onset
errors measured in `sed_ceilings_20260926.md`. Two alternatives:

* **cSEBB** — change-detection sound event bounding boxes (Ebbers, Germain, Wichern,
  Le Roux, Interspeech 2024). Written from the paper's description, not from the
  AGPL reference code. A step filter of length τ gives a delta score per frame boundary
  (mean of the next τ/2 minus mean of the previous τ/2); rising local maxima open
  tentative events, falling local minima close them; a gap is merged when its lowest
  score is close to the peak of **both** neighbouring events (absolute difference or
  ratio); a box's confidence is its mean score. An event-level threshold then decides
  which boxes are kept, without moving their boundaries.
* **Hysteresis** — an event spans a run of frames ≥ `low` that contains a frame ≥ `high`.

Deviation from the reference: scores are edge-padded (not zero-padded) and onsets need a
positive, offsets a negative delta, so a non-zero baseline does not open an event at the
clip start; an event already active at the start is opened at frame 0 explicitly.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from ml.postprocessing.events import PostprocessedEvent, _active_runs


@dataclass(frozen=True)
class SebbParams:
    step_filter_s: float
    merge_abs: float | None = None
    merge_rel: float | None = None

    def __post_init__(self) -> None:
        if self.step_filter_s <= 0:
            raise ValueError("step_filter_s must be positive")
        if (self.merge_abs is None) == (self.merge_rel is None):
            raise ValueError("set exactly one of merge_abs / merge_rel")

    @property
    def label(self) -> str:
        merge = (f"abs{self.merge_abs:g}" if self.merge_abs is not None
                 else f"rel{self.merge_rel:g}")
        return f"tau{self.step_filter_s:g}_{merge}"


def step_delta(scores: np.ndarray, half_frames: int) -> np.ndarray:
    """Delta at every frame boundary 0..T: mean of the next minus the previous half window."""
    padded = np.pad(np.asarray(scores, dtype=np.float64), half_frames, mode="edge")
    cumulative = np.concatenate([[0.0], np.cumsum(padded)])
    positions = np.arange(len(scores) + 1) + half_frames
    right = cumulative[positions + half_frames] - cumulative[positions]
    left = cumulative[positions] - cumulative[positions - half_frames]
    # Rounded so flat stretches are exactly 0 and plateaus compare equal (cumsum noise
    # of ~1e-17 would otherwise create spurious extrema inside a constant region).
    return np.round((right - left) / half_frames, 9)


def _extrema(delta: np.ndarray) -> list[tuple[int, int]]:
    """Rising maxima (+1) and falling minima (-1), in time order; plateaus keep their start."""
    before_max = np.concatenate([[-np.inf], delta[:-1]])
    after_max = np.concatenate([delta[1:], [-np.inf]])
    before_min = np.concatenate([[np.inf], delta[:-1]])
    after_min = np.concatenate([delta[1:], [np.inf]])
    maxima = (delta > 0) & (delta > before_max) & (delta >= after_max)
    minima = (delta < 0) & (delta < before_min) & (delta <= after_min)
    return sorted([(int(n), 1) for n in np.flatnonzero(maxima)]
                  + [(int(n), -1) for n in np.flatnonzero(minima)])


def change_point_events(scores: np.ndarray, half_frames: int) -> list[tuple[int, int]]:
    """Tentative events [onset, offset) with strict onset/offset alternation."""
    events: list[tuple[int, int]] = []
    onset: int | None = None
    for position, kind in _extrema(step_delta(scores, half_frames)):
        if kind == 1 and onset is None:
            onset = position
        elif kind == -1 and onset is not None:
            events.append((onset, position))
            onset = None
        elif kind == -1 and not events:
            events.append((0, position))  # already active when the clip starts
    if onset is not None:
        events.append((onset, len(scores)))
    return [(on, off) for on, off in events if off > on]


def _close_to_gap(left_peak: float, right_peak: float, floor: float, params: SebbParams
                  ) -> bool:
    if params.merge_abs is not None:
        return left_peak - floor < params.merge_abs and right_peak - floor < params.merge_abs
    if floor <= 0:
        return False
    return left_peak / floor < params.merge_rel and right_peak / floor < params.merge_rel


def _merge(scores: np.ndarray, events: list[tuple[int, int]], params: SebbParams
           ) -> list[tuple[int, int]]:
    """One pass over the gaps, each judged against the original neighbouring peaks."""
    if len(events) < 2:
        return events
    peaks = [float(scores[on:off].max()) for on, off in events]
    merged = [events[0]]
    for index in range(1, len(events)):
        gap = scores[events[index - 1][1]:events[index][0]]
        if gap.size == 0 or _close_to_gap(peaks[index - 1], peaks[index], float(gap.min()),
                                          params):
            merged[-1] = (merged[-1][0], events[index][1])
        else:
            merged.append(events[index])
    return merged


def csebbs(scores: np.ndarray, *, frame_rate: float, params: SebbParams
           ) -> list[tuple[int, int, float]]:
    """(onset_frame, offset_frame, confidence) boxes for one class of one recording."""
    half = max(1, round(params.step_filter_s / 2 * frame_rate))
    events = _merge(scores, change_point_events(scores, half), params)
    return [(on, off, float(np.mean(scores[on:off]))) for on, off in events]


def hysteresis_runs(scores: np.ndarray, *, high: float, low: float) -> list[tuple[int, int]]:
    if not 0.0 <= low <= high <= 1.0:
        raise ValueError("need 0 <= low <= high <= 1")
    return [(start, stop) for start, stop in _active_runs(scores >= low)
            if scores[start:stop].max() >= high]


def sebb_candidates(probabilities_by_recording: Mapping[str, np.ndarray], *,
                    class_ids: Sequence[str], frame_rate: float, params: SebbParams
                    ) -> dict[str, list[PostprocessedEvent]]:
    """Every box of every class; the event-level threshold is applied by `select_boxes`."""
    output: dict[str, list[PostprocessedEvent]] = {}
    for recording_id, probabilities in probabilities_by_recording.items():
        boxes = [
            PostprocessedEvent(recording_id, class_id, on / frame_rate, off / frame_rate,
                               confidence)
            for index, class_id in enumerate(class_ids)
            for on, off, confidence in csebbs(probabilities[:, index], frame_rate=frame_rate,
                                              params=params)
        ]
        output[recording_id] = sorted(boxes, key=lambda e: (e.onset_s, e.offset_s, e.class_id))
    return output


def select_boxes(candidates: Mapping[str, list[PostprocessedEvent]], threshold: float
                 ) -> dict[str, list[dict[str, str | float]]]:
    """sed_eval-ready events whose box confidence reaches `threshold`."""
    return {recording_id: [box.as_dict() for box in boxes if box.score >= threshold]
            for recording_id, boxes in candidates.items()}
