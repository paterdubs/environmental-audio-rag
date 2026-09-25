"""Tối ưu SED — kiểm lưới θ có cắt cụt điểm tối ưu không (chỉ DEV).

    .venv/Scripts/python.exe -m scripts.report_threshold_edge ml/runs/<run> [...]

CV (ADR-0024) chọn θ global = 0.95, đúng biên trên của `DEFAULT_THRESHOLD_GRID`
(0.05–0.95). Nếu event-F1 trên dev còn tăng sau 0.95 thì lưới đã cắt mất điểm tối
ưu. Script đo event-F1 trên **toàn dev** với θ global quanh và vượt biên, cho mỗi
percentile `g_max` của lưới CV. Không đổi lưới, không chọn gì — chỉ trả lời câu hỏi
đó; không mở file test nào.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID
from scripts.select_postproc_cv import G_MAX_PERCENTILES, load_context, score

ROOT = Path(__file__).resolve().parents[1]
PROBE = (0.90, 0.95, 0.97, 0.98, 0.99)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def probe(run_dir: Path) -> dict[str, dict[str, float]]:
    ctx = load_context(run_dir, n_folds=5)  # folds unused: whole dev
    curves: dict[str, dict[str, float]] = {}
    for p in G_MAX_PERCENTILES:
        curves[f"{p:g}"] = {
            f"{theta:.2f}": score(ctx["probabilities"], ctx["reference"],
                                  dict.fromkeys(ctx["class_ids"], theta), ctx["class_ids"],
                                  ctx["priors_by_p"][p], ctx["frame_rate"])
            for theta in PROBE
        }
        print(run_dir.name, p, curves[f"{p:g}"], flush=True)
    return curves


def render(result: dict) -> str:
    grid_max = max(DEFAULT_THRESHOLD_GRID)
    lines = [
        "# Lưới θ có cắt cụt điểm tối ưu không (dev)", "",
        "> Sinh bởi `scripts.report_threshold_edge`. Event-F1 trên **toàn dev**, θ global; "
        f"biên trên của lưới hiện tại = {grid_max}. Không mở file test.", "",
        "| Run | g_max percentile | " + " | ".join(f"θ={t:.2f}" for t in PROBE) + " | đỉnh |",
        "|---|---:|" + "---:|" * len(PROBE) + "---:|",
    ]
    for run, curves in result["runs"].items():
        for p, curve in curves.items():
            peak = max(curve, key=curve.get)
            cells = " | ".join(f"{curve[f'{t:.2f}']:.4f}" for t in PROBE)
            lines.append(f"| `{run}` | {p} | {cells} | {peak} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = {"probe_thetas": list(PROBE), "grid_max": max(DEFAULT_THRESHOLD_GRID),
              "runs": {run.name: probe(run) for run in args.runs}}
    destination = args.output or (
        ROOT / "docs/measurements"
        / f"threshold_grid_edge_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
