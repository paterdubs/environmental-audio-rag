"""LBR (ADR-0045): learned boundary refinement and box rescoring on frame posteriors.

cSEBB boxes are kept when their score reaches ``min_box_score``. For each box, the class
posterior sampled around each boundary (plus the max over the other classes and box metadata)
feeds a gradient-boosting regressor that predicts the signed shift to the annotated boundary.
An optional classifier then rescores the refined box. Every hyperparameter is fixed in
``LbrConfig`` (ADR-0045 §3); nothing here is tuned on evaluation data.

Torch-free. Models are pickled; ``load_bundle`` refuses any file whose SHA-256 differs from
the value recorded in the run manifest, so only artifacts produced by this repo are unpickled.
"""

from __future__ import annotations

import hashlib
import pickle
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from ml.postprocessing.sebb import SebbParams, sebb_candidates

EventRows = Mapping[str, Iterable[Mapping[str, Any]]]
META_FEATURES = 4  # score, length, onset, time from offset to recording end


@dataclass(frozen=True)
class LbrConfig:
    min_box_score: float = 0.5
    window_s: float = 4.0
    step_s: float = 0.08
    other_stride: int = 5
    max_target_s: float = 4.0
    min_duration_s: float = 0.04
    max_iter: int = 300
    learning_rate: float = 0.05
    max_leaf_nodes: int = 31
    min_samples_leaf: int = 20
    seed: int = 20260922

    @property
    def offsets_s(self) -> np.ndarray:
        n = int(round(2 * self.window_s / self.step_s)) + 1
        return np.linspace(-self.window_s, self.window_s, n)

    def model_params(self) -> dict[str, Any]:
        return {"max_iter": self.max_iter, "learning_rate": self.learning_rate,
                "max_leaf_nodes": self.max_leaf_nodes, "min_samples_leaf": self.min_samples_leaf,
                "early_stopping": False, "random_state": self.seed}


@dataclass(frozen=True)
class Box:
    recording_id: str
    class_id: str
    onset_s: float
    offset_s: float
    score: float


def _label(event: Mapping[str, Any]) -> str:
    return str(event.get("class_id", event.get("event_label")))


def _bounds(event: Mapping[str, Any]) -> tuple[float, float]:
    return (float(event.get("onset", event.get("onset_s"))),
            float(event.get("offset", event.get("offset_s"))))


def candidate_boxes(probabilities_by_recording: Mapping[str, np.ndarray], *,
                    class_ids: Sequence[str], frame_rate: float, params: SebbParams,
                    min_score: float) -> list[Box]:
    """cSEBB boxes with score ≥ ``min_score``, in recording then time order."""
    candidates = sebb_candidates(probabilities_by_recording, class_ids=class_ids,
                                 frame_rate=frame_rate, params=params)
    return [Box(rid, box.class_id, box.onset_s, box.offset_s, box.score)
            for rid in sorted(candidates) for box in candidates[rid] if box.score >= min_score]


def feature_size(n_classes: int, config: LbrConfig) -> int:
    n_curve = len(config.offsets_s)
    return META_FEATURES + n_classes + n_curve + len(range(0, n_curve, config.other_stride))


def _curve(values: np.ndarray, t: float, frame_rate: float, offsets: np.ndarray) -> np.ndarray:
    positions = t + offsets
    index = np.clip(np.round(positions * frame_rate).astype(int), 0, len(values) - 1)
    curve = values[index].astype(np.float64)
    curve[(positions < 0) | (positions * frame_rate > len(values) - 1)] = -1.0
    return curve


def feature_matrices(boxes: Sequence[Box], probabilities_by_recording: Mapping[str, np.ndarray],
                     *, class_ids: Sequence[str], frame_rate: float, config: LbrConfig
                     ) -> tuple[np.ndarray, np.ndarray]:
    """(onset features, offset features), one row per box (ADR-0045 §2)."""
    index_of = {c: i for i, c in enumerate(class_ids)}
    offsets = config.offsets_s
    rows_on, rows_off = [], []
    for box in boxes:
        probabilities = probabilities_by_recording[box.recording_id]
        k = index_of[box.class_id]
        own = probabilities[:, k]
        other = np.delete(probabilities, k, axis=1).max(axis=1)
        onehot = np.zeros(len(class_ids))
        onehot[k] = 1.0
        duration = len(own) / frame_rate
        meta = np.r_[box.score, box.offset_s - box.onset_s, box.onset_s,
                     duration - box.offset_s, onehot]
        for t, rows in ((box.onset_s, rows_on), (box.offset_s, rows_off)):
            rows.append(np.r_[meta, _curve(own, t, frame_rate, offsets),
                              _curve(other, t, frame_rate, offsets)[::config.other_stride]])
    width = feature_size(len(class_ids), config)
    return (np.asarray(rows_on, dtype=np.float64).reshape(-1, width),
            np.asarray(rows_off, dtype=np.float64).reshape(-1, width))


def _overlapping(box: Box, reference: EventRows) -> list[tuple[float, float]]:
    spans = [_bounds(e) for e in reference.get(box.recording_id, []) if _label(e) == box.class_id]
    return [(a, b) for a, b in spans if min(b, box.offset_s) - max(a, box.onset_s) > 0]


def boundary_targets(boxes: Sequence[Box], reference: EventRows, *, config: LbrConfig
                     ) -> tuple[np.ndarray, np.ndarray]:
    """Signed shift to the nearest overlapping annotated boundary; NaN when none within range."""
    y_on = np.full(len(boxes), np.nan)
    y_off = np.full(len(boxes), np.nan)
    for i, box in enumerate(boxes):
        spans = _overlapping(box, reference)
        if not spans:
            continue
        d_on = min((a - box.onset_s for a, _ in spans), key=abs)
        d_off = min((b - box.offset_s for _, b in spans), key=abs)
        if abs(d_on) <= config.max_target_s:
            y_on[i] = d_on
        if abs(d_off) <= config.max_target_s:
            y_off[i] = d_off
    return y_on, y_off


def fit_regressor(features: np.ndarray, target: np.ndarray, config: LbrConfig
                  ) -> HistGradientBoostingRegressor:
    keep = np.isfinite(target)
    if keep.sum() < 2:
        raise ValueError("refiner cần ít nhất 2 box có đích hữu hạn")
    model = HistGradientBoostingRegressor(loss="absolute_error", **config.model_params())
    return model.fit(features[keep], target[keep])


def fit_classifier(features: np.ndarray, labels: np.ndarray, config: LbrConfig
                   ) -> HistGradientBoostingClassifier:
    if len(set(labels.tolist())) < 2:
        raise ValueError("rescorer cần cả box khớp và không khớp")
    return HistGradientBoostingClassifier(**config.model_params()).fit(features, labels)


def apply_deltas(boxes: Sequence[Box], delta_on: np.ndarray, delta_off: np.ndarray, *,
                 config: LbrConfig) -> list[Box]:
    out = []
    for box, d_on, d_off in zip(boxes, delta_on, delta_off, strict=True):
        onset = max(0.0, box.onset_s + float(d_on))
        offset = box.offset_s + float(d_off)
        if offset <= onset + config.min_duration_s:
            offset = onset + config.min_duration_s
        out.append(replace(box, onset_s=onset, offset_s=offset))
    return out


def matches_primary(boxes: Sequence[Box], reference: EventRows, *, collar: float = 0.2,
                    percentage: float = 0.2) -> np.ndarray:
    """Whether each box alone meets the primary event criterion with some same-class event."""
    matched = np.zeros(len(boxes), dtype=bool)
    for i, box in enumerate(boxes):
        for event in reference.get(box.recording_id, []):
            if _label(event) != box.class_id:
                continue
            onset, offset = _bounds(event)
            if (abs(onset - box.onset_s) <= collar
                    and abs(offset - box.offset_s) <= max(collar, percentage * (offset - onset))):
                matched[i] = True
                break
    return matched


def matches_intersection(boxes: Sequence[Box], reference: EventRows, *,
                         min_cover: float = 0.1) -> np.ndarray:
    """Whether each box overlaps a same-class event by ≥ ``min_cover`` of both durations.

    Nhãn của rescorer V3 (ADR-0045 §11): gần với DTC/GTC 0.1 của thước giao nhau (ADR-0046),
    thay vì tiêu chí biên 0.2 s của V2.
    """
    matched = np.zeros(len(boxes), dtype=bool)
    for i, box in enumerate(boxes):
        for event in reference.get(box.recording_id, []):
            if _label(event) != box.class_id:
                continue
            onset, offset = _bounds(event)
            inter = min(offset, box.offset_s) - max(onset, box.onset_s)
            if (inter > 0 and inter >= min_cover * (box.offset_s - box.onset_s)
                    and inter >= min_cover * (offset - onset)):
                matched[i] = True
                break
    return matched


def rescore_features(x_on: np.ndarray, x_off: np.ndarray, delta_on: np.ndarray,
                     delta_off: np.ndarray, *, n_classes: int) -> np.ndarray:
    return np.c_[x_on, x_off[:, META_FEATURES + n_classes:], delta_on, delta_off]


def _merge_same_class(boxes: list[Box]) -> list[Box]:
    """Gộp box cùng lớp giao hoặc chạm nhau (onset min, offset max, score max).

    Đầu ra hệ thống không chứa hai event cùng lớp chồng nhau — `psds_eval` từ chối bảng như vậy
    và timeline của caption (G1–G3) cũng giả định điều này (ADR-0045 §3, sửa 10/11).
    """
    merged: list[Box] = []
    for box in sorted(boxes, key=lambda b: (b.recording_id, b.class_id, b.onset_s, b.offset_s)):
        last = merged[-1] if merged else None
        if (last is not None and last.recording_id == box.recording_id
                and last.class_id == box.class_id and box.onset_s <= last.offset_s):
            merged[-1] = replace(last, offset_s=max(last.offset_s, box.offset_s),
                                 score=max(last.score, box.score))
        else:
            merged.append(box)
    return sorted(merged, key=lambda b: (b.recording_id, b.onset_s, b.offset_s, b.class_id))


def boxes_to_events(boxes: Sequence[Box], keep: np.ndarray | None, *,
                    recordings: Iterable[str] = ()) -> dict[str, list[dict[str, Any]]]:
    """sed_eval-ready rows of the kept boxes, same-class overlaps merged; every id in
    ``recordings`` is present even without events."""
    kept = [box for i, box in enumerate(boxes) if keep is None or keep[i]]
    events: dict[str, list[dict[str, Any]]] = {rid: [] for rid in recordings}
    for box in _merge_same_class(kept):
        events.setdefault(box.recording_id, []).append({
            "recording_id": box.recording_id, "class_id": box.class_id,
            "event_label": box.class_id, "onset": box.onset_s, "offset": box.offset_s,
            "onset_s": box.onset_s, "offset_s": box.offset_s, "score": box.score})
    return events


def save_bundle(path: Path, bundle: Mapping[str, Any]) -> str:
    payload = pickle.dumps(dict(bundle), protocol=pickle.HIGHEST_PROTOCOL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def load_bundle(path: Path, *, sha256: str) -> dict[str, Any]:
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != sha256:
        raise ValueError(f"{path}: SHA-256 {actual} khác giá trị ghi trong manifest {sha256}")
    return pickle.loads(payload)  # noqa: S301 — chỉ sau khi SHA khớp artifact do repo sinh
