"""Phần LBR của `evaluate_run` (ADR-0045 §8, ADR-0046): một lượt mở test cho cả hai điểm vận hành.

Chỉ áp model đã đóng băng; không fit, không chọn ngưỡng. So ghép cặp với B0 ở điểm F1 (thước
chính, 21 lớp) — phép so ghi trước duy nhất; các thước còn lại chỉ báo kèm.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from ml.evaluation.application_metrics import vn_class_ids
from ml.evaluation.multirun import paired_branch_bootstrap
from ml.postprocessing.boundary_refine import boxes_to_events
from ml.postprocessing.lbr_apply import OPERATING_POINTS, lbr_events, lbr_scored_boxes, load_lbr
from ml.postprocessing.lbr_crossfit import LAMBDA_GRID, T_GRID
from ml.postprocessing.sebb import SebbParams, sebb_candidates, select_boxes
from scripts.fit_lbr_oof import evaluate


def estimate(lbr_run: Path, probabilities: Mapping[str, np.ndarray], *,
             class_ids: tuple[str, ...], frame_rate: float) -> dict[str, Any]:
    """Event của điểm F1 (số chính) và event theo lưới ngưỡng của ứng viên (cho PSDS)."""
    bundle = load_lbr(lbr_run, class_ids=class_ids)
    boxes, scores = lbr_scored_boxes(bundle, probabilities, frame_rate=frame_rate)
    recordings = sorted(probabilities)
    grid = T_GRID if bundle["variant"] == "v2" else LAMBDA_GRID
    return {"bundle": bundle, "boxes": boxes, "scores": scores,
            "estimate": lbr_events(bundle, boxes, scores, point="f1", recordings=recordings),
            "psds_events": [boxes_to_events(boxes, scores >= t, recordings=recordings)
                            for t in grid]}


def _strip(metrics: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in metrics.items() if k != "counts"}


def section(lbr: Mapping[str, Any], reference: Mapping[str, list], probabilities: Mapping[str,
            np.ndarray], *, class_ids: tuple[str, ...], frame_rate: float,
            baseline: tuple[SebbParams, float] | None) -> dict[str, Any]:
    recordings = sorted(probabilities)
    ctx = {"reference": reference, "recordings": recordings,
           "durations": {r: probabilities[r].shape[0] / frame_rate for r in recordings}}
    sets = {"all": class_ids, "vn": vn_class_ids(class_ids)}
    bundle = lbr["bundle"]
    points = {point: {s: evaluate(ctx, lbr_events(bundle, lbr["boxes"], lbr["scores"],
                                                  point=point, recordings=recordings), ids)
                      for s, ids in sets.items()} for point in OPERATING_POINTS}
    out: dict[str, Any] = {
        "lbr_run": bundle["manifest"]["run_id"], "variant": bundle["variant"],
        "thresholds": dict(bundle["thresholds"]),
        "points": {p: {s: _strip(m) for s, m in v.items()} for p, v in points.items()}}
    if baseline is not None:
        params, threshold = baseline
        events = select_boxes(sebb_candidates(probabilities, class_ids=class_ids,
                                              frame_rate=frame_rate, params=params), threshold)
        base = {s: evaluate(ctx, events, ids) for s, ids in sets.items()}
        diff = paired_branch_bootstrap({"B0": base["all"]["counts"],
                                        "LBR": points["f1"]["all"]["counts"]},
                                       {"B0": ["B0"], "LBR": ["LBR"]})["differences"]["LBR-B0"]
        out["baseline"] = {s: _strip(m) for s, m in base.items()}
        out["delta_micro_vs_baseline"] = diff
    return out


def _fmt(value: Any) -> str:
    return "—" if value is None or not np.isfinite(value) else f"{value:.4f}"


def _row(name: str, m: Mapping[str, Any]) -> str:
    i = m["intersection"]["micro"]
    return (f"| {name} | {_fmt(m['macro_f1'])} | {_fmt(m['micro_f1'])} | "
            f"{m['nsys']}/{m['nref']} | {_fmt(m['event_f1_collar_1s']['micro'])} | "
            f"{_fmt(m['segment_f1_1s']['micro'])} | {_fmt(i['precision'])} | "
            f"{_fmt(i['recall'])} | {_fmt(i['f1'])} |")


def render(sec: Mapping[str, Any]) -> list[str]:
    lines = ["", f"## LBR `{sec['lbr_run']}` (variant {sec['variant']})", "",
             f"Ngưỡng đóng băng: {sec['thresholds']}. Điểm `f1` là số chính; các cột từ collar 1 s "
             "trở đi là thước ứng dụng ADR-0046 (báo kèm, không dùng để chọn).", ""]
    for set_name, title in (("all", "21 lớp"), ("vn", "19 lớp Việt Nam")):
        lines += [f"### {title}", "",
                  "| Hệ thống | Macro | Micro | Nsys/Nref | Collar 1 s | Segment 1 s | "
                  "Giao nhau P | Giao nhau R | Giao nhau F1 |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        if "baseline" in sec:
            lines.append(_row("B0 (cSEBB, λ đóng băng)", sec["baseline"][set_name]))
        for point in OPERATING_POINTS:
            lines.append(_row(f"LBR — {point}", sec["points"][point][set_name]))
        lines.append("")
    if "delta_micro_vs_baseline" in sec:
        d = sec["delta_micro_vs_baseline"]
        lines.append(f"Δ micro LBR − B0 (thước chính, 21 lớp, ghép cặp theo recording): "
                     f"{d['estimate']:+.4f} [{d['lower']:+.4f}, {d['upper']:+.4f}].")
    return lines
