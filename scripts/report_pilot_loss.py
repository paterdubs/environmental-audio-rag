"""Chọn gamma focal từ pilot macro-AP dev đã đăng ký trước trong ADR-0038."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMMA_GRID = (0.5, 1.0, 2.0)
SAME = (
    "encoder_type", "recipe", "seed", "epochs", "warmup_epochs", "cosine_decay",
    "batch_size", "loss",
)


def pilot_row(run: Path) -> dict[str, object]:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete") or manifest.get("git", {}).get("dirty"):
        raise SystemExit(f"{run.name}: pilot phải hoàn tất trên tree sạch")
    config = manifest["config"]
    if config.get("loss") != "focal" or config.get("recipe") != "t2b":
        raise SystemExit(f"{run.name}: không phải pilot focal t2b")
    gamma = float(config.get("focal_gamma"))
    if gamma not in GAMMA_GRID:
        raise SystemExit(f"{run.name}: gamma {gamma} ngoài lưới {GAMMA_GRID}")
    history = json.loads((run / "logs" / "history.json").read_text(encoding="utf-8"))["epochs"]
    return {
        "run": run.name,
        "focal_gamma": gamma,
        "macro_average_precision": [
            float(epoch["validation"]["macro_average_precision"]) for epoch in history
        ],
        **{key: config[key] for key in SAME},
    }


def choose(rows: list[dict[str, object]]) -> dict[str, object]:
    if len(rows) != 3:
        raise SystemExit("pilot loss cần đúng 3 cấu hình")
    for key in (*SAME, "macro_average_precision"):
        values = {json.dumps(row[key], sort_keys=True) for row in rows}
        if len(values) != 1 and key != "macro_average_precision":
            raise SystemExit(f"pilot khác nhau ở {key}")
    gammas = [float(row["focal_gamma"]) for row in rows]
    if sorted(gammas) != list(GAMMA_GRID):
        raise SystemExit(f"pilot phải đủ đúng lưới gamma {GAMMA_GRID}, nhận {gammas}")
    if {len(row["macro_average_precision"]) for row in rows} != {3}:
        raise SystemExit("pilot phải chạy đúng 3 epoch")
    return max(rows, key=lambda row: (row["macro_average_precision"][-1], -row["focal_gamma"]))


def render(name: str, rows: list[dict[str, object]], chosen: dict[str, object]) -> str:
    lines = [
        f"# Pilot focal loss — {name}, {date.today().isoformat()}",
        "",
        "Sinh bởi `scripts.report_pilot_loss.py`; chỉ macro-AP frame trên dev, không mở test.",
        "",
        "| gamma | epoch 1 | epoch 2 | epoch 3 | run |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in sorted(rows, key=lambda item: item["focal_gamma"]):
        mark = "**" if row is chosen else ""
        values = " | ".join(f"{mark}{value:.4f}{mark}" for value in row["macro_average_precision"])
        lines.append(f"| {row['focal_gamma']:g} | {values} | `{row['run']}` |")
    lines += [
        "",
        f"→ Chọn gamma **{chosen['focal_gamma']:g}** theo macro-AP epoch 3 "
        "(hoà chọn gamma nhỏ hơn).",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    rows = [pilot_row(run) for run in args.runs]
    chosen = choose(rows)
    stem = ROOT / "docs" / "measurements" / f"pilot_loss_{args.name}_{date.today():%Y%m%d}"
    payload = {
        "grid": GAMMA_GRID,
        "rule": "max dev macro-AP epoch 3; tie lower gamma",
        "pilots": rows,
        "chosen": chosen,
    }
    stem.with_suffix(".json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    stem.with_suffix(".md").write_text(render(args.name, rows, chosen), encoding="utf-8")
    print(render(args.name, rows, chosen))
    print(chosen["focal_gamma"])


if __name__ == "__main__":
    main()
