"""Nested cross-fitting for LBR (ADR-0045 §4–§7).

``fit_lbr`` learns from the boxes of ``fit_folds`` only: boundary shifts used to pick the
operating point (and to label boxes for the rescorer) come from inner models that never saw
the fold they predict. ``crossfit_lbr`` repeats this with each fold held out, so the labels of
a held-out fold reach none of the models or thresholds applied to it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing.boundary_refine import (
    Box,
    EventRows,
    LbrConfig,
    apply_deltas,
    boundary_targets,
    boxes_to_events,
    candidate_boxes,
    feature_matrices,
    fit_classifier,
    fit_regressor,
    matches_intersection,
    matches_primary,
    rescore_features,
)
from ml.postprocessing.sebb import SebbParams

LAMBDA_GRID = (0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95)
T_GRID = (0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
          *(round(0.10 + 0.05 * i, 2) for i in range(16)))
VARIANTS = ("v1", "v2")  # ứng viên tầng C (ADR-0045 §6)
APPLICATION_VARIANTS = ("v3",)  # cấu hình ứng dụng, không qua luật chọn (ADR-0045 §11)
ALL_VARIANTS = VARIANTS + APPLICATION_VARIANTS
RESCORER_LABELS = {"v2": matches_primary, "v3": matches_intersection}
Events = dict[str, list[dict[str, Any]]]
Objective = Callable[[Events, list[str]], float]


@dataclass(frozen=True)
class LbrData:
    boxes: tuple[Box, ...]
    x_on: np.ndarray
    x_off: np.ndarray
    y_on: np.ndarray
    y_off: np.ndarray
    box_folds: np.ndarray
    recordings_by_fold: Mapping[int, tuple[str, ...]]
    reference: EventRows
    n_classes: int

    def rows(self, folds: set[int]) -> np.ndarray:
        return np.flatnonzero(np.isin(self.box_folds, sorted(folds)))

    def recordings(self, folds: set[int]) -> list[str]:
        return [r for k in sorted(folds) for r in self.recordings_by_fold[k]]


@dataclass(frozen=True)
class LbrModel:
    variant: str
    refiner_on: Any
    refiner_off: Any
    rescorer: Any | None
    thresholds: Mapping[str, float]
    n_classes: int
    config: LbrConfig


@dataclass(frozen=True)
class CrossfitResult:
    events: Mapping[str, Events]
    thresholds: Mapping[int, Mapping[str, float]]


def build_data(probabilities: Mapping[str, np.ndarray], reference: EventRows,
               folds: Mapping[str, int], *, class_ids: tuple[str, ...], frame_rate: float,
               params: SebbParams, config: LbrConfig) -> LbrData:
    if set(probabilities) != set(folds):
        raise ValueError("posterior và phép gán fold phải phủ cùng tập recording")
    boxes = candidate_boxes(probabilities, class_ids=class_ids, frame_rate=frame_rate,
                            params=params, min_score=config.min_box_score)
    x_on, x_off = feature_matrices(boxes, probabilities, class_ids=class_ids,
                                   frame_rate=frame_rate, config=config)
    y_on, y_off = boundary_targets(boxes, reference, config=config)
    by_fold: dict[int, list[str]] = {}
    for rid in sorted(folds):
        by_fold.setdefault(int(folds[rid]), []).append(rid)
    return LbrData(tuple(boxes), x_on, x_off, y_on, y_off,
                   np.array([int(folds[b.recording_id]) for b in boxes], dtype=int),
                   {k: tuple(v) for k, v in by_fold.items()}, reference, len(class_ids))


def micro_f1_objective(reference: EventRows, class_ids: tuple[str, ...]) -> Objective:
    """Primary criterion (collar 0.2 s, sed_eval) over the given recordings; NaN → 0."""
    def score(events: Events, recordings: list[str]) -> float:
        value = event_based_f1({r: list(reference.get(r, [])) for r in recordings},
                               {r: events.get(r, []) for r in recordings},
                               event_label_list=list(class_ids))["f_measure"].get("f_measure")
        return float(value) if value is not None and np.isfinite(value) else 0.0
    return score


def select_threshold(boxes: list[Box], scores: np.ndarray, grid: tuple[float, ...],
                     objective: Objective, recordings: list[str]) -> float:
    values = [objective(boxes_to_events(boxes, scores >= t, recordings=recordings), recordings)
              for t in grid]
    return float(grid[int(np.argmax(values))])  # hòa → ngưỡng đầu tiên (thấp nhất) của lưới


def _fit_refiners(data: LbrData, rows: np.ndarray, config: LbrConfig) -> tuple[Any, Any]:
    return (fit_regressor(data.x_on[rows], data.y_on[rows], config),
            fit_regressor(data.x_off[rows], data.y_off[rows], config))


def _inner_shifts(data: LbrData, fit: np.ndarray, fit_folds: set[int], config: LbrConfig
                  ) -> tuple[np.ndarray, np.ndarray]:
    """Shift of every fit box predicted by a refiner trained without its own fold."""
    d_on, d_off = np.zeros(len(fit)), np.zeros(len(fit))
    for j in sorted(fit_folds):
        own = data.box_folds[fit] == j
        on_model, off_model = _fit_refiners(data, fit[~own], config)
        d_on[own] = on_model.predict(data.x_on[fit[own]])
        d_off[own] = off_model.predict(data.x_off[fit[own]])
    return d_on, d_off


def _rescorer_inputs(data: LbrData, fit: np.ndarray, d_on: np.ndarray, d_off: np.ndarray,
                     config: LbrConfig, variant: str) -> tuple[np.ndarray, np.ndarray]:
    refined = apply_deltas([data.boxes[i] for i in fit], d_on, d_off, config=config)
    labels = RESCORER_LABELS[variant](refined, data.reference).astype(int)
    features = rescore_features(data.x_on[fit], data.x_off[fit], d_on, d_off,
                                n_classes=data.n_classes)
    return features, labels


def fit_lbr(data: LbrData, *, fit_folds: set[int], variant: str,
            objectives: Mapping[str, Objective], config: LbrConfig) -> LbrModel:
    """Refiner (+ rescorer for v2) and one threshold per objective, from ``fit_folds`` only."""
    if variant not in ALL_VARIANTS:
        raise ValueError(f"variant phải thuộc {ALL_VARIANTS}")
    if len(fit_folds) < 2:
        raise ValueError("cross-fit lồng nhau cần ít nhất 2 fold fit")
    fit = data.rows(fit_folds)
    recordings = data.recordings(fit_folds)
    d_on, d_off = _inner_shifts(data, fit, fit_folds, config)
    refined = apply_deltas([data.boxes[i] for i in fit], d_on, d_off, config=config)
    rescorer = None
    if variant in RESCORER_LABELS:
        features, labels = _rescorer_inputs(data, fit, d_on, d_off, config, variant)
        scores = np.zeros(len(fit))
        for j in sorted(fit_folds):
            own = data.box_folds[fit] == j
            scores[own] = fit_classifier(features[~own], labels[~own], config).predict_proba(
                features[own])[:, 1]
        rescorer = fit_classifier(features, labels, config)
        grid = T_GRID
    else:
        scores = np.array([data.boxes[i].score for i in fit])
        grid = LAMBDA_GRID
    thresholds = {name: select_threshold(refined, scores, grid, objective, recordings)
                  for name, objective in objectives.items()}
    on_model, off_model = _fit_refiners(data, fit, config)
    return LbrModel(variant, on_model, off_model, rescorer, thresholds, data.n_classes, config)


def apply_lbr(model: LbrModel, boxes: list[Box], x_on: np.ndarray, x_off: np.ndarray
              ) -> tuple[list[Box], np.ndarray]:
    """Refined boxes whose ``score`` is the selection score (box score for v1, P(match) else)."""
    if not boxes:
        return [], np.zeros(0)
    d_on, d_off = model.refiner_on.predict(x_on), model.refiner_off.predict(x_off)
    refined = apply_deltas(boxes, d_on, d_off, config=model.config)
    if model.rescorer is None:
        return refined, np.array([b.score for b in refined])
    probs = model.rescorer.predict_proba(
        rescore_features(x_on, x_off, d_on, d_off, n_classes=model.n_classes))[:, 1]
    return [replace(b, score=float(p)) for b, p in zip(refined, probs, strict=True)], probs


def crossfit_lbr(data: LbrData, *, variant: str, objectives: Mapping[str, Objective],
                 config: LbrConfig, target: LbrData | None = None) -> CrossfitResult:
    """Hold out each fold; fit on the others; apply to the held-out fold of ``target``."""
    target = data if target is None else target
    return crossfit_lbr_multi(data, variant=variant, objectives=objectives, config=config,
                              targets={"target": target})["target"]


def crossfit_lbr_multi(data: LbrData, *, variant: str, objectives: Mapping[str, Objective],
                       config: LbrConfig, targets: Mapping[str, LbrData]
                       ) -> dict[str, CrossfitResult]:
    """Như `crossfit_lbr`, nhưng mỗi model fold được áp lên nhiều đích cùng phép gán fold.

    Đích khác nguồn (vd. OOF ensemble P1×3) là phép kiểm chuyển của ADR-0045 §6.
    """
    folds = sorted(data.recordings_by_fold)
    if any(sorted(t.recordings_by_fold) != folds for t in targets.values()):
        raise ValueError("mọi đích phải dùng cùng phép gán fold")
    events = {name: {obj: {} for obj in objectives} for name in targets}
    thresholds: dict[int, Mapping[str, float]] = {}
    for k in folds:
        model = fit_lbr(data, fit_folds=set(folds) - {k}, variant=variant,
                        objectives=objectives, config=config)
        thresholds[k] = dict(model.thresholds)
        for name, target in targets.items():
            rows = target.rows({k})
            refined, scores = apply_lbr(model, [target.boxes[i] for i in rows],
                                        target.x_on[rows], target.x_off[rows])
            for obj, threshold in model.thresholds.items():
                events[name][obj].update(boxes_to_events(
                    refined, scores >= threshold, recordings=target.recordings_by_fold[k]))
    return {name: CrossfitResult(events[name], thresholds) for name in targets}
