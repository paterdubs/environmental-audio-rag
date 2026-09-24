"""Compare event-based per-class F1 between RQ1 branches B and C."""

from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load_per_class(run_dir: Path) -> dict[str, float]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất (complete=false)")
    path = run_dir / "evaluation.json"
    if not path.exists():
        raise SystemExit(f"{run_dir} thiếu evaluation.json")
    values = json.loads(path.read_text(encoding="utf-8"))["event_based_f1_per_class"]
    result = {}
    for class_id, value in values.items():
        if isinstance(value, dict):
            value = value.get("f_measure")
        result[class_id] = float(value) if value is not None else float("nan")
    return result


def compare(
    branch_b: list[dict[str, float]],
    branch_c: list[dict[str, float]],
    class_ids: list[str] | None = None,
) -> dict[str, dict[str, float | int | str]]:
    classes = class_ids or sorted(set().union(*(run.keys() for run in branch_b + branch_c)))
    result = {}
    for class_id in classes:
        b = np.asarray([run.get(class_id, float("nan")) for run in branch_b], dtype=float)
        c = np.asarray([run.get(class_id, float("nan")) for run in branch_c], dtype=float)
        b_valid, c_valid = b[np.isfinite(b)], c[np.isfinite(c)]
        b_mean = float(b_valid.mean()) if len(b_valid) else float("nan")
        c_mean = float(c_valid.mean()) if len(c_valid) else float("nan")
        delta = c_mean - b_mean if math.isfinite(b_mean) and math.isfinite(c_mean) else float("nan")
        paired = [(x, y) for x in b for y in c if math.isfinite(x) and math.isfinite(y)]
        result[class_id] = {
            "mean_b": b_mean,
            "mean_c": c_mean,
            "delta": delta,
            "n_pairs_c_gt_b": int(sum(y > x for x, y in paired)),
            "n_pairs": len(paired),
        }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-b", nargs="+", type=Path, required=True)
    parser.add_argument("--branch-c", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def fmt(value: float) -> str:
    return "N/A" if math.isnan(value) else f"{value:.6f}"


def main() -> None:
    args = parse_args()
    from ml.taxonomy import load_taxonomy

    class_ids = list(load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml").polyphonic_class_ids)
    result = compare(
        [load_per_class(p) for p in args.branch_b],
        [load_per_class(p) for p in args.branch_c],
        class_ids,
    )
    destination = args.output or ROOT / "docs" / "measurements" / (
        f"branch_per_class_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    lines = [
        "# RQ1 — per-class B vs C",
        "",
        "| Class | Mean F1 B | Mean F1 C | Δ (C−B) | Cặp C>B |",
        "|---|---:|---:|---:|---:|",
    ]
    lines.extend(
        f"| {class_id} | {fmt(row['mean_b'])} | {fmt(row['mean_c'])} | "
        f"{fmt(row['delta'])} | {row['n_pairs_c_gt_b']}/{row['n_pairs']} |"
        for class_id, row in result.items()
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
