"""PSDS của LBR với lưới ngưỡng ghi trước (ADR-0047, mục "ghi trước lưới PSDS").

Chỉ áp run LBR đã đóng băng lên posterior test; không fit, không chọn lại gì. Báo số cũ (lưới
`T_GRID` của ứng viên, như `evaluate_run`) và số mới (lưới log) cạnh nhau.

`--b0-postproc` (ADR-0048 §3): chấm box cSEBB của B0 trên cùng hai thước — lưới tuyến tính của
`evaluate_run` (phải tái tạo đúng `--b0-reference-evaluation`, lệch thì dừng trước khi ghi) và lưới
log — để bảng B0 ↔ LBR cùng lưới. Có thể chạy không kèm `--lbr-run` để không chấm lại LBR.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml.evaluation.coverage import EVAL_SETS, eval_suffix, restrict
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import psds_score
from ml.postprocessing import stack_predictions_by_recording
from ml.postprocessing.boundary_refine import boxes_to_events
from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID
from ml.postprocessing.lbr_crossfit import T_GRID
from ml.postprocessing.sebb import sebb_candidates, select_boxes
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts import lbr_test_section
from scripts.evaluate_run import (
    PSDS_SCENARIOS,
    load_events_by_recording,
    sebb_params,
    to_detection_frame,
    to_reference_frame,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = (ROOT / "ml/runs/sed_ensemble_B0_final_test_20261014T085016Z"
                       / "predictions" / "test.npz")
# ADR-0047: cố định trước khi đọc số test; không thử lưới khác.
PSDS_GRID_LOG = tuple(float(t) for t in np.geomspace(1e-5, 0.99, 48))


def psds_curve(boxes, scores: np.ndarray, grid, *, recordings, ground_truth: pd.DataFrame,
               metadata: pd.DataFrame) -> dict[str, Any]:
    """PSDS-1/2 của đường cong tạo bởi ``grid``; điểm không có event bị bỏ như `evaluate_run`."""
    points, sizes = [], []
    for threshold in grid:
        events = boxes_to_events(boxes, scores >= threshold, recordings=recordings)
        count = sum(len(v) for v in events.values())
        sizes.append(count)
        if count:
            points.append((to_detection_frame(events).drop(columns=["confidence"]),))
    psds = {name: (psds_score(ground_truth=ground_truth, metadata=metadata,
                              operating_points=points, scenario=scenario) if points else 0.0)
            for name, scenario in PSDS_SCENARIOS.items()}
    return {"psds": psds, "n_points": len(points), "n_grid": len(list(grid)),
            "events_at_lowest_threshold": sizes[0] if sizes else 0,
            "boxes_never_included": int(np.sum(scores < min(grid)))}


def sebb_curve(candidates, grid, *, ground_truth: pd.DataFrame,
               metadata: pd.DataFrame) -> dict[str, Any]:
    """Như `psds_curve` cho box cSEBB: mỗi ngưỡng chỉ lọc confidence của box đã dựng."""
    points, sizes = [], []
    for threshold in grid:
        events = select_boxes(candidates, threshold)
        count = sum(len(v) for v in events.values())
        sizes.append(count)
        if count:
            points.append((to_detection_frame(events).drop(columns=["confidence"]),))
    psds = {name: (psds_score(ground_truth=ground_truth, metadata=metadata,
                              operating_points=points, scenario=scenario) if points else 0.0)
            for name, scenario in PSDS_SCENARIOS.items()}
    scores = [box.score for boxes in candidates.values() for box in boxes]
    return {"psds": psds, "n_points": len(points), "n_grid": len(list(grid)),
            "events_at_lowest_threshold": sizes[0] if sizes else 0,
            "boxes_never_included": int(sum(s < min(grid) for s in scores))}


def check_reference(curve: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    """Lưới tuyến tính tính lại phải trùng lượt đánh giá đã lưu (tới 1e-9), không thì dừng."""
    stored = {k: float(reference["psds"][k]) for k in ("psds_1", "psds_2")}
    match = all(abs(curve["psds"][k] - stored[k]) < 1e-9 for k in stored)
    result = {"stored": stored, "recomputed": dict(curve["psds"]), "match": match}
    if not match:
        raise SystemExit(f"PSDS B0 trên lưới tuyến tính không tái tạo được số đã lưu: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lbr-run", type=Path, action="append", default=[],
                        help="thư mục run sed_lbr đã đóng băng (lặp lại cho nhiều run)")
    parser.add_argument("--b0-postproc", type=Path, default=None,
                        help="selection cSEBB của B0 (ADR-0048 §3)")
    parser.add_argument("--b0-reference-evaluation", type=Path, default=None,
                        help="evaluation JSON đã lưu của B0 để kiểm lưới tuyến tính")
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    if not args.lbr_run and args.b0_postproc is None:
        parser.error("cần ít nhất một --lbr-run hoặc --b0-postproc")
    if (args.b0_postproc is None) != (args.b0_reference_evaluation is None):
        parser.error("--b0-postproc và --b0-reference-evaluation phải đi cùng nhau")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    stem = f"lbr_psds_grid_{datetime.now(UTC):%Y%m%d}{eval_suffix(args.eval_set)}{args.tag}"
    out_dir = ROOT / "docs" / "measurements"
    if (out_dir / f"{stem}.json").exists():
        raise SystemExit(f"{stem}.json đã có — đổi --tag, không ghi đè số đã báo")

    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    artifact = load_predictions(args.predictions, expected_class_ids=class_ids)
    if artifact.split != "test":
        raise SystemExit(f"{args.predictions}: split={artifact.split!r}, cần 'test'")
    probabilities = restrict(stack_predictions_by_recording(artifact), args.eval_set)
    frame_rate = 1.0 / artifact.frame_hop_s
    recordings = sorted(probabilities)
    ground_truth = to_reference_frame(load_events_by_recording(set(probabilities)))
    metadata = pd.DataFrame({"filename": recordings, "duration": [
        probabilities[r].shape[0] / frame_rate for r in recordings]})

    results = []
    for run in args.lbr_run:
        lbr = lbr_test_section.estimate(run, probabilities, class_ids=class_ids,
                                        frame_rate=frame_rate)
        grids = {"T_GRID (cũ)": T_GRID, "log 1e-5..0.99 (mới)": PSDS_GRID_LOG}
        results.append({
            "lbr_run": lbr["bundle"]["manifest"]["run_id"],
            "curves": {name: psds_curve(lbr["boxes"], lbr["scores"], grid,
                                        recordings=recordings, ground_truth=ground_truth,
                                        metadata=metadata) for name, grid in grids.items()}})
    if args.b0_postproc is not None:
        selection = json.loads(args.b0_postproc.read_text(encoding="utf-8"))
        params, _ = sebb_params(selection, eval_set=args.eval_set)
        candidates = sebb_candidates(probabilities, class_ids=class_ids, frame_rate=frame_rate,
                                     params=params)
        grids = {"tuyến tính (evaluate_run)": tuple(DEFAULT_THRESHOLD_GRID),
                 "log 1e-5..0.99 (mới)": PSDS_GRID_LOG}
        curves = {name: sebb_curve(candidates, grid, ground_truth=ground_truth,
                                   metadata=metadata) for name, grid in grids.items()}
        reference = json.loads(args.b0_reference_evaluation.read_text(encoding="utf-8"))
        check = check_reference(curves["tuyến tính (evaluate_run)"], reference)
        results.append({"system": "B0 (cSEBB)", "postproc": args.b0_postproc.as_posix(),
                        "reference_evaluation": args.b0_reference_evaluation.name,
                        "reference_check": check, "curves": curves})
    out = {"predictions": str(args.predictions), "eval_set": args.eval_set,
           "n_recordings": len(recordings), "grid_log": list(PSDS_GRID_LOG),
           "results": results, "git": git,
           "created_at": datetime.now(UTC).isoformat()}
    (out_dir / f"{stem}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = [f"# PSDS của LBR với lưới ghi trước (ADR-0047) — test, {args.eval_set}, "
             f"n={len(recordings)}", "",
             "| Run | Lưới | PSDS-1 | PSDS-2 | Điểm | Event ở ngưỡng thấp nhất | "
             "Box không bao giờ vào |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for item in results:
        label = item.get("lbr_run") or item["system"]
        for name, c in item["curves"].items():
            lines.append(f"| {label} | {name} | {c['psds']['psds_1']:.4f} | "
                         f"{c['psds']['psds_2']:.4f} | {c['n_points']}/{c['n_grid']} | "
                         f"{c['events_at_lowest_threshold']} | {c['boxes_never_included']} |")
    for item in results:
        if "reference_check" in item:
            lines += ["", f"{item['system']}: lưới tuyến tính tái tạo đúng "
                          f"`{item['reference_evaluation']}` (ADR-0048 §3)."]
    lines += ["", f"git: `{out['git']['revision']}` dirty={out['git']['dirty']}"]
    (out_dir / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
