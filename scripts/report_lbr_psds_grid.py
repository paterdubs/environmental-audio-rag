"""PSDS của LBR với lưới ngưỡng ghi trước (ADR-0047, mục "ghi trước lưới PSDS").

Chỉ áp run LBR đã đóng băng lên posterior test; không fit, không chọn lại gì. Báo số cũ (lưới
`T_GRID` của ứng viên, như `evaluate_run`) và số mới (lưới log) cạnh nhau.
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
from ml.postprocessing.lbr_crossfit import T_GRID
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts import lbr_test_section
from scripts.evaluate_run import (
    PSDS_SCENARIOS,
    load_events_by_recording,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lbr-run", type=Path, action="append", required=True,
                        help="thư mục run sed_lbr đã đóng băng (lặp lại cho nhiều run)")
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
    out = {"predictions": str(args.predictions), "eval_set": args.eval_set,
           "n_recordings": len(recordings), "grid_log": list(PSDS_GRID_LOG),
           "results": results, "git": git_state(ROOT),
           "created_at": datetime.now(UTC).isoformat()}
    stem = f"lbr_psds_grid_{datetime.now(UTC):%Y%m%d}{eval_suffix(args.eval_set)}{args.tag}"
    out_dir = ROOT / "docs" / "measurements"
    (out_dir / f"{stem}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = [f"# PSDS của LBR với lưới ghi trước (ADR-0047) — test, {args.eval_set}, "
             f"n={len(recordings)}", "",
             "| Run | Lưới | PSDS-1 | PSDS-2 | Điểm | Event ở ngưỡng thấp nhất | "
             "Box không bao giờ vào |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for item in results:
        for name, c in item["curves"].items():
            lines.append(f"| {item['lbr_run']} | {name} | {c['psds']['psds_1']:.4f} | "
                         f"{c['psds']['psds_2']:.4f} | {c['n_points']}/{c['n_grid']} | "
                         f"{c['events_at_lowest_threshold']} | {c['boxes_never_included']} |")
    lines += ["", f"git: `{out['git']['revision']}` dirty={out['git']['dirty']}"]
    (out_dir / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
