"""Summarise RQ1 metrics across multiple completed SED runs."""

from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.stats import ttest_ind

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("event_f1", "psds_1", "psds_2")
LABELS = {"event_f1": "event-based F1", "psds_1": "PSDS-1", "psds_2": "PSDS-2"}


def load_metrics(run_dir: Path) -> dict[str, float]:
    manifest_path = run_dir / "manifest.json"
    evaluation_path = run_dir / "evaluation.json"
    if not manifest_path.exists():
        raise SystemExit(f"{run_dir} thiếu manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất (complete=false)")
    if not evaluation_path.exists():
        raise SystemExit(f"{run_dir} thiếu evaluation.json — chạy evaluate_run trước")
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    return {
        "event_f1": float(evaluation["event_based_f1"]["f_measure"]),
        "psds_1": float(evaluation["psds"]["psds_1"]),
        "psds_2": float(evaluation["psds"]["psds_2"]),
    }


def is_dirty(run_dir: Path) -> bool:
    """Read provenance without excluding dirty runs from the statistical sample."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    return bool(manifest.get("git", {}).get("dirty", False))


def summarize(runs: list[dict[str, float]]) -> dict[str, dict[str, float | int]]:
    if not runs:
        raise ValueError("at least one run is required")
    result: dict[str, dict[str, float | int]] = {}
    for metric in METRICS:
        values = np.asarray([run[metric] for run in runs], dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{metric} contains non-finite values")
        result[metric] = {
            "mean": float(values.mean()),
            "sd": float(values.std(ddof=1)) if len(values) > 1 else float("nan"),
            "min": float(values.min()),
            "max": float(values.max()),
            "n": len(values),
        }
    return result


def welch_tests(
    branch_b: list[dict[str, float]], branch_c: list[dict[str, float]]
) -> dict[str, dict[str, float]]:
    return {
        metric: {
            "t": float(test.statistic),
            "p": float(test.pvalue),
        }
        for metric in METRICS
        for test in [ttest_ind(
            [run[metric] for run in branch_c],
            [run[metric] for run in branch_b],
            equal_var=False,
        )]
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-b", nargs="+", type=Path, required=True)
    parser.add_argument("--branch-c", nargs="+", type=Path, required=True)
    parser.add_argument("--branch-a", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _fmt(value: float) -> str:
    return "N/A" if math.isnan(value) else f"{value:.6f}"


def main() -> None:
    args = parse_args()
    loaded = {
        "B": [load_metrics(path) for path in args.branch_b],
        "C": [load_metrics(path) for path in args.branch_c],
    }
    if args.branch_a:
        loaded["A"] = [load_metrics(path) for path in args.branch_a]
    paths = {"B": args.branch_b, "C": args.branch_c}
    if args.branch_a:
        paths["A"] = args.branch_a
    summaries = {branch: summarize(runs) for branch, runs in loaded.items()}
    tests = welch_tests(loaded["B"], loaded["C"])
    deltas = {
        metric: summaries["C"][metric]["mean"] - summaries["B"][metric]["mean"]
        for metric in METRICS
    }
    dirty_runs = {
        branch: [str(path) for path in branch_paths if is_dirty(path)]
        for branch, branch_paths in paths.items()
    }
    result = {
        "branches": summaries,
        "delta_mean_c_minus_b": deltas,
        "welch": tests,
        "dirty_runs_included": dirty_runs,
    }
    destination = args.output or ROOT / "docs" / "measurements" / (
        f"rq1_multiseed_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    lines = [
        "# RQ1 — tổng hợp đa seed",
        "",
        "> Welch t-test hai phía, `equal_var=False`; không tính lại metric.",
        "> Cỡ mẫu nhỏ (n được ghi rõ), nên diễn giải thận trọng.",
        "",
        "| Metric | Nhánh | Mean ± SD | Min | Max | n |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        for branch in loaded:
            summary = summaries[branch][metric]
            lines.append(
                f"| {LABELS[metric]} | {branch} | "
                f"{_fmt(summary['mean'])} ± {_fmt(summary['sd'])} | "
                f"{_fmt(summary['min'])} | {_fmt(summary['max'])} | {summary['n']} |"
            )
    lines += ["", "## Δ mean (C − B)", "", "| Metric | Δ |", "|---|---:|"]
    lines.extend(f"| {LABELS[m]} | {deltas[m]:+.6f} |" for m in METRICS)
    lines += ["", "## Welch t-test (C vs B)", "", "| Metric | t | p |", "|---|---:|---:|"]
    lines.extend(f"| {LABELS[m]} | {tests[m]['t']:.12g} | {tests[m]['p']:.12g} |" for m in METRICS)
    lines += ["", "Không gọi là có ý nghĩa thống kê khi p ≥ 0.05."]
    dirty = [path for branch in dirty_runs.values() for path in branch]
    if dirty:
        lines += [
            "",
            "⚠️ Các run `git.dirty=true` vẫn được giữ trong phép tính (không loại):",
            *[f"- `{path}`" for path in dirty],
        ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=True), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
