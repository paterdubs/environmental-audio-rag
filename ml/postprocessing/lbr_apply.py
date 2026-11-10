"""Apply a frozen LBR run to new posteriors (test once, or serving) — ADR-0045 §7–§8.

The run directory written by ``scripts.fit_lbr_oof`` holds ``manifest.json`` (task ``sed_lbr``,
``config.model_sha256``) and ``lbr_model.pkl``. Nothing here fits anything: boxes, features,
refiner, rescorer and both operating thresholds come from that run.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from ml.postprocessing.boundary_refine import (
    Box,
    boxes_to_events,
    candidate_boxes,
    feature_matrices,
    load_bundle,
)
from ml.postprocessing.lbr_crossfit import LbrModel, apply_lbr

LBR_TASK = "sed_lbr"
OPERATING_POINTS = ("f1", "recall_first")


def is_lbr_run(manifest: Mapping[str, Any]) -> bool:
    return manifest.get("task") == LBR_TASK


def load_lbr(run_dir: Path, *, class_ids: Sequence[str]) -> dict[str, Any]:
    """Bundle of a complete LBR run, after checking task, SHA-256 and class order."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not is_lbr_run(manifest) or not manifest.get("complete"):
        raise ValueError(f"{run_dir}: cần run {LBR_TASK} hoàn tất")
    sha = manifest["config"].get("model_sha256")
    if not sha:
        raise ValueError(f"{run_dir}: run không có model cuối (không ứng viên nào đạt tầng C)")
    bundle = load_bundle(run_dir / "lbr_model.pkl", sha256=sha)
    if list(bundle["class_ids"]) != list(class_ids):
        raise ValueError(f"{run_dir}: thứ tự lớp của model khác taxonomy đang dùng")
    if set(bundle["thresholds"]) != set(OPERATING_POINTS):
        raise ValueError(f"{run_dir}: model thiếu ngưỡng của một điểm vận hành")
    return {**bundle, "manifest": manifest}


def lbr_scored_boxes(bundle: Mapping[str, Any], probabilities: Mapping[str, np.ndarray], *,
                     frame_rate: float) -> tuple[list[Box], np.ndarray]:
    """Refined boxes and their selection score for every candidate box of ``probabilities``."""
    config = bundle["config"]
    class_ids = tuple(bundle["class_ids"])
    boxes = candidate_boxes(probabilities, class_ids=class_ids, frame_rate=frame_rate,
                            params=bundle["sebb_params"], min_score=config.min_box_score)
    x_on, x_off = feature_matrices(boxes, probabilities, class_ids=class_ids,
                                   frame_rate=frame_rate, config=config)
    model = LbrModel(bundle["variant"], bundle["refiner_on"], bundle["refiner_off"],
                     bundle["rescorer"], bundle["thresholds"], bundle["n_classes"], config)
    return apply_lbr(model, boxes, x_on, x_off)


def clip_events_to_duration(events: Sequence[Mapping[str, Any]], duration_s: float
                            ) -> list[dict[str, Any]]:
    """Kẹp event vào [0, duration_s]; bỏ event không còn độ dài (ADR-0047 §5).

    Box sau tinh chỉnh có thể vượt cuối recording vài phần mười giây. Timeline caption/RAG và
    phục vụ đòi 0 <= onset < offset <= duration nên kẹp ở nơi tiêu thụ; `lbr_events` giữ nguyên
    để số event-F1 đã đo không đổi (collar 0.2 s tính trên box chưa kẹp).
    """
    clipped = []
    for event in events:
        onset, offset = max(0.0, float(event["onset_s"])), min(float(event["offset_s"]), duration_s)
        if offset > onset:
            row = {**event, "onset_s": onset, "offset_s": offset}
            if "onset" in row and "offset" in row:  # boxes_to_events ghi cả hai cặp khóa
                row["onset"], row["offset"] = onset, offset
            clipped.append(row)
    return clipped


def lbr_events(bundle: Mapping[str, Any], boxes: Sequence[Box], scores: np.ndarray, *,
               point: str, recordings: Sequence[str]) -> dict[str, list[dict[str, Any]]]:
    if point not in OPERATING_POINTS:
        raise ValueError(f"điểm vận hành phải thuộc {OPERATING_POINTS}")
    return boxes_to_events(boxes, scores >= float(bundle["thresholds"][point]),
                           recordings=recordings)
