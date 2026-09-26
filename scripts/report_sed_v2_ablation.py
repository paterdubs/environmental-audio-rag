"""ADR-0030 §4 — bảng ablation bỏ-từng-phần của SED v2, **chỉ trên dev**.

    .venv/Scripts/python.exe -m scripts.report_sed_v2_ablation \\
        --full ml/runs/<v2 seed 20260922> ml/runs/<v2 seed 2> ml/runs/<v2 seed 3> \\
        --ablation "không độ phân giải (pool /64)=ml/runs/<run>" \\
        --ablation "trần pos_weight 50=ml/runs/<run>" \\
        --ablation "không augmentation=ml/runs/<run>" \\
        [--reference "ensemble C v1=ml/runs/<run>"]

Mỗi run: CV event-F1 micro của cấu hình hậu xử lý tốt nhất (họ θ và cSEBB,
`select_sed_v2.best_config`) và frame macro-AP dev tốt nhất (`logs/history.json`). Ablation so
với v2 đủ **cùng seed**. Ngưỡng nhiễu = max(sd giữa fold của v2 đủ cùng seed, 2 × sd giữa seed
của v2 đủ); chênh lệch nhỏ hơn ngưỡng → "không phân biệt được" (ADR-0030 §4).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, stdev

from ml.provenance import git_state
from scripts.select_sed_v2 import best_config, cell

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--full", nargs="+", type=Path, required=True)
    parser.add_argument("--ablation", action="append", default=[])
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "measurements")
    return parser.parse_args()


def run_row(label: str, run_dir: Path) -> dict:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    config = manifest["config"]
    family, post, cv_mean, cv_sd = best_config(run_dir)
    history_path = run_dir / "logs" / "history.json"
    ap = None
    if history_path.exists():
        epochs = json.loads(history_path.read_text(encoding="utf-8"))["epochs"]
        ap = max(e["validation"]["macro_average_precision"] for e in epochs)
    return {"label": label, "run": run_dir.name, "seed": config.get("seed"),
            "dirty": manifest.get("git", {}).get("dirty"), "family": family, "config": post,
            "cv_mean": cv_mean, "cv_sd": cv_sd, "best_dev_ap": ap}


def noise_threshold(full: list[dict], reference: dict) -> float:
    seed_means = [row["cv_mean"] for row in full]
    seed_sd = stdev(seed_means) if len(seed_means) > 1 else 0.0
    return max(reference["cv_sd"], 2 * seed_sd)


def verdict(delta: float, threshold: float) -> str:
    if abs(delta) < threshold:
        return "không phân biệt được"
    return "bỏ đi làm **giảm**" if delta < 0 else "bỏ đi làm **tăng**"


def paired_reference(full: list[dict], seed: object) -> dict:
    return next((row for row in full if row["seed"] == seed), full[0])


def render(full: list[dict], ablations: list[dict], references: list[dict], git: dict) -> str:
    anchor = paired_reference(full, 20260922)
    threshold = noise_threshold(full, anchor)
    seed_means = [row["cv_mean"] for row in full]
    lines = [
        "# SED v2 — ablation bỏ-từng-phần (chỉ dev, ADR-0030 §4)", "",
        "> Sinh bởi `scripts.report_sed_v2_ablation`. CV event-F1 **micro**, 5 fold dev; "
        f"git `{git['revision'][:7]}`. Không chạm test.", "",
        f"v2 đủ, {len(full)} seed: CV mean {mean(seed_means):.4f} ± "
        f"{stdev(seed_means) if len(seed_means) > 1 else 0.0:.4f} (sd giữa seed). "
        f"Ngưỡng nhiễu = {threshold:.4f}.", "",
        "| Cấu hình | Run | Seed | Hậu xử lý | CV mean ± sd (fold) | Δ vs v2 đủ cùng seed | Đọc | "
        "AP frame dev |", "|---|---|---:|---|---:|---:|---|---:|"]
    for row in [*full, *ablations, *references]:
        is_ablation = row in ablations
        delta = row["cv_mean"] - paired_reference(full, row["seed"])["cv_mean"]
        ap = f"{row['best_dev_ap']:.3f}" if row["best_dev_ap"] is not None else "—"
        lines.append(
            f"| {row['label']} | `{row['run']}` | {row['seed']} | {row['family']} "
            f"{cell(row['config'])} | {row['cv_mean']:.4f} ± {row['cv_sd']:.4f} | "
            f"{f'{delta:+.4f}' if is_ablation else '—'} | "
            f"{verdict(delta, threshold) if is_ablation else ''} | {ap} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    full = [run_row(f"v2 đủ (seed {i + 1}/{len(args.full)})", path)
            for i, path in enumerate(args.full)]
    specs = [(spec.partition("=")[0], Path(spec.partition("=")[2])) for spec in args.ablation]
    ablations = [run_row(label, path) for label, path in specs]
    references = [run_row(spec.partition("=")[0], Path(spec.partition("=")[2]))
                  for spec in args.reference]
    git = git_state(ROOT)
    report = render(full, ablations, references, git)
    out = args.out_dir / f"sed_v2_ablation_{datetime.now(UTC):%Y%m%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(
        {"full": full, "ablations": ablations, "references": references, "git": git},
        indent=1, ensure_ascii=False), encoding="utf-8")
    out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
