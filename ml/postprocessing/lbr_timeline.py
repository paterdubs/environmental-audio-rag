"""Event LBR cho timeline caption/RAG (ADR-0047): áp run đóng băng lên test, đọc event cross-fit
cho dev.

Model LBR cuối fit trên đủ 5 fold OOF, tức đã thấy mọi recording dev; áp nó lên dev cho số
in-sample. Vì vậy dev chỉ nhận event cross-fit (`scripts.export_lbr_oof_events`): mỗi recording
được chấm bằng model không thấy fold của nó.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from ml.dataops.inventory import sha256_file
from ml.postprocessing.lbr_apply import (
    OPERATING_POINTS,
    is_lbr_run,
    lbr_events,
    lbr_scored_boxes,
    load_lbr,
)

OOF_EVENTS_TASK = "sed_lbr_oof_events"
EVENTS_FILE = "events.json"
Events = dict[str, list[dict[str, Any]]]


def is_oof_events(manifest: Mapping[str, Any]) -> bool:
    return manifest.get("task") == OOF_EVENTS_TASK


def is_lbr_postproc(manifest: Mapping[str, Any]) -> bool:
    return is_lbr_run(manifest) or is_oof_events(manifest)


def model_version(manifest: Mapping[str, Any], point: str) -> str:
    """Tên phiên bản ghi vào timeline: run LBR gốc và điểm vận hành."""
    run = manifest["config"]["lbr_run"] if is_oof_events(manifest) else manifest["run_id"]
    return f"{run}:{point}"


def _frozen_run_events(run_dir: Path, probabilities: Mapping[str, np.ndarray], *,
                       class_ids: Sequence[str], frame_rate: float, split: str,
                       point: str) -> Events:
    if split != "test":
        raise ValueError("model LBR cuối đã thấy dev (fit trên đủ 5 fold OOF); "
                         "dev phải dùng event cross-fit từ scripts.export_lbr_oof_events")
    bundle = load_lbr(run_dir, class_ids=class_ids)
    boxes, scores = lbr_scored_boxes(bundle, probabilities, frame_rate=frame_rate)
    return lbr_events(bundle, boxes, scores, point=point, recordings=sorted(probabilities))


def _oof_events(manifest: Mapping[str, Any], run_dir: Path,
                probabilities: Mapping[str, np.ndarray], *, split: str, point: str) -> Events:
    config = manifest["config"]
    if not manifest.get("complete"):
        raise ValueError(f"{run_dir}: run event cross-fit chưa hoàn tất")
    if config["point"] != point:
        raise ValueError(f"{run_dir}: event của điểm {config['point']!r}, cần {point!r}")
    if config["predictions_split"] != split:
        raise ValueError(f"{run_dir}: event cho split {config['predictions_split']!r}, "
                         f"cần {split!r}")
    path = run_dir / EVENTS_FILE
    if sha256_file(path) != config["events_sha256"]:
        raise ValueError(f"{path}: SHA-256 lệch manifest")
    events = json.loads(path.read_text(encoding="utf-8"))
    if set(events) != set(probabilities):
        missing = sorted(set(probabilities) - set(events))[:3]
        extra = sorted(set(events) - set(probabilities))[:3]
        raise ValueError(f"{run_dir}: tập recording lệch posterior (thiếu {missing}, "
                         f"thừa {extra})")
    return {rid: events[rid] for rid in sorted(probabilities)}


def lbr_postproc_events(manifest: Mapping[str, Any], manifest_path: Path,
                        probabilities: Mapping[str, np.ndarray], *, class_ids: Sequence[str],
                        frame_rate: float, split: str, point: str) -> Events:
    """Event của một hậu xử lý LBR (run đóng băng hoặc event cross-fit) tại ``point``."""
    if point not in OPERATING_POINTS:
        raise ValueError(f"điểm vận hành phải thuộc {OPERATING_POINTS}")
    if is_lbr_run(manifest):
        return _frozen_run_events(manifest_path.parent, probabilities, class_ids=class_ids,
                                  frame_rate=frame_rate, split=split, point=point)
    if is_oof_events(manifest):
        return _oof_events(manifest, manifest_path.parent, probabilities, split=split,
                           point=point)
    raise ValueError(f"{manifest_path}: không phải hậu xử lý LBR")
