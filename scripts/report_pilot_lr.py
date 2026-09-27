"""Pilot learning rate (ADR-0030 §2, ADR-0032 §8): dev macro-AP per epoch, pre-registered choice.

    .venv/Scripts/python.exe -m scripts.report_pilot_lr --name t2a ml/runs/<r1> ml/runs/<r2> ...

The rule was written before the pilots ran: pick the learning rate with the highest frame
macro-AP on dev at the last epoch. The runs must differ only in `learning_rate` (same recipe,
seed, epoch count, constant schedule) and be complete, clean-tree runs. Writes
`docs/measurements/pilot_lr_<name>_<date>.{md,json}` and prints the chosen rate last.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAME_ACROSS_PILOTS = ("recipe", "encoder_type", "seed", "epochs", "warmup_epochs", "cosine_decay",
                      "batch_size")
METRIC = "macro_average_precision"


def pilot_row(run: Path) -> dict[str, object]:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if not manifest["complete"] or manifest["git"]["dirty"]:
        raise SystemExit(f"{run.name}: pilot must be a complete clean-tree run")
    config = manifest["config"]
    if config["warmup_epochs"] or config["cosine_decay"]:
        raise SystemExit(f"{run.name}: pilot uses a constant learning rate")
    history = json.loads((run / "logs" / "history.json").read_text(encoding="utf-8"))["epochs"]
    return {"run": run.name, "learning_rate": float(config["learning_rate"]),
            "curve": [epoch["validation"][METRIC] for epoch in history],
            **{key: config[key] for key in SAME_ACROSS_PILOTS}}


def choose(rows: list[dict[str, object]]) -> dict[str, object]:
    for key in (*SAME_ACROSS_PILOTS, "curve"):
        values = {len(row[key]) if key == "curve" else json.dumps(row[key]) for row in rows}
        if len(values) != 1:
            raise SystemExit(f"pilots differ in {key}: {sorted(values)}")
    if len({row["learning_rate"] for row in rows}) != len(rows):
        raise SystemExit("each pilot needs its own learning rate")
    return max(rows, key=lambda row: row["curve"][-1])


def to_markdown(name: str, rows: list[dict[str, object]], chosen: dict[str, object]) -> str:
    epochs = len(chosen["curve"])
    header = " | ".join(f"epoch {i}" for i in range(1, epochs + 1))
    lines = [f"# Pilot lr — {name}, {date.today().isoformat()}", "",
             "Sinh bởi `scripts/report_pilot_lr.py`. Luật ghi trước: macro-AP frame dev cao nhất "
             f"ở epoch {epochs}. Seed {chosen['seed']}, lr hằng số, recipe `{chosen['recipe']}`.",
             "", f"| lr | {header} | run |", "|---:|" + "---:|" * epochs + "---|"]
    for row in sorted(rows, key=lambda row: row["learning_rate"]):
        mark = "**" if row is chosen else ""
        cells = " | ".join(f"{mark}{value:.4f}{mark}" for value in row["curve"])
        lines.append(f"| {row['learning_rate']:g} | {cells} | `{row['run']}` |")
    lines += ["", f"→ lr **{chosen['learning_rate']:g}**."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    rows = [pilot_row(run) for run in args.runs]
    chosen = choose(rows)
    stem = ROOT / "docs" / "measurements" / f"pilot_lr_{args.name}_{date.today():%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps({"rule": f"max {METRIC} at last epoch",
                                                     "pilots": rows, "chosen": chosen}, indent=2),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(to_markdown(args.name, rows, chosen), encoding="utf-8")
    print(to_markdown(args.name, rows, chosen))
    print(chosen["learning_rate"])


if __name__ == "__main__":
    main()
