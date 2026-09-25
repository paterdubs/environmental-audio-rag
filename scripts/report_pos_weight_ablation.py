"""Ablation A4 — trần `pos_weight` (ADR-0028): so sánh trên dev, test chỉ để báo.

    .venv/Scripts/python.exe -m scripts.report_pos_weight_ablation ml/runs/<run> [...]

Mỗi run phải có `postproc.json` (sweep trên dev của chính nó) và `evaluation.json` (test một
lần). Event-F1 dev tính với postproc của run, cùng đường đi với evaluate_run. Luật quyết định
đọc từ ADR-0028: trần 50 là mốc; trần khác chỉ "tốt hơn" nếu vượt mốc trên dev quá 2 × SD seed.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.multirun import micro_f1
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_multirun_bootstrap import run_counts

ROOT = Path(__file__).resolve().parents[1]
BASELINE_CAP = 50.0
SEED_SD = 0.0048  # ADR-0021/0028: SD event-F1 giữa seed nhánh B
MARGIN = 2 * SEED_SD


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    return parser.parse_args()


def cap_of(manifest: dict) -> float:
    config = manifest["config"]
    if "pos_weight_cap" not in config:
        return BASELINE_CAP  # run trước khi có cờ: trần mặc định
    return float("inf") if config["pos_weight_cap"] is None else float(config["pos_weight_cap"])


def verdict(dev_f1: float, baseline_dev_f1: float, margin: float = MARGIN) -> str:
    """ADR-0028 §4: only a dev difference beyond 2 × seed SD counts as a difference."""
    delta = dev_f1 - baseline_dev_f1
    if delta > margin:
        return "tốt hơn"
    if -delta > margin:
        return "kém hơn"
    return "không phân biệt được"


def summarise(run: Path, taxonomy) -> dict:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    evaluation = json.loads((run / "evaluation.json").read_text(encoding="utf-8"))
    dev = run_counts(run, taxonomy, split="dev")
    return {"run": run.name, "cap": cap_of(manifest), "git_dirty": manifest["git"]["dirty"],
            "pos_weight_max": max(manifest["pos_weight"]),
            "n_capped": sum(w >= cap_of(manifest) for w in manifest["pos_weight"]),
            "dev_frame_macro_f1": metrics["best_validation"],
            "dev_event_f1": micro_f1(*(sum(c[i] for c in dev.values()) for i in range(3))),
            "test_event_f1": evaluation["event_based_f1"]["f_measure"],
            "test_psds": evaluation["psds"]}


def render(rows: list[dict], verdicts: dict) -> str:
    lines = [
        "# Ablation A4 — trần `pos_weight` (nhánh B, seed 20260922, một run mỗi trần)", "",
        "> Sinh bởi `scripts.report_pos_weight_ablation`, giao thức ADR-0028 (ghi trước khi có "
        "số). So sánh bằng event-F1 **dev** với postproc riêng của từng run; test chạy một lần, "
        f"chỉ để báo. \"Tốt hơn\" chỉ khi vượt trần 50 trên dev quá {MARGIN:.4f} (2 × SD seed). "
        "Event-F1 dev là số in-sample (θ quét trên chính dev) nên lạc quan như nhau ở mọi "
        "trần — dùng để so giữa các trần, không để so với test.",
        "", "| Trần | Lớp chạm trần | pos_weight lớn nhất | Frame macro-F1 dev | Event-F1 dev "
        "| Δ dev vs 50 | Event-F1 test | PSDS-1 test | PSDS-2 test | Kết luận |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    base = next(r for r in rows if r["cap"] == BASELINE_CAP)
    for r in sorted(rows, key=lambda r: r["cap"]):
        cap = "không clip" if r["cap"] == float("inf") else f"{r['cap']:g}"
        psds = list(r["test_psds"].values())
        lines.append(
            f"| {cap} | {r['n_capped']} | {r['pos_weight_max']:.1f} "
            f"| {r['dev_frame_macro_f1']:.4f} | {r['dev_event_f1']:.4f} "
            f"| {r['dev_event_f1'] - base['dev_event_f1']:+.4f} | {r['test_event_f1']:.4f} "
            f"| {psds[0]:.4f} | {psds[1]:.4f} | {verdicts[r['run']]} |")
    lines += ["", "Runs: " + ", ".join(f"`{r['run']}`" for r in rows)]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    rows = [summarise(run, taxonomy) for run in args.runs]
    base = next(r for r in rows if r["cap"] == BASELINE_CAP)
    verdicts = {r["run"]: "mốc" if r is base else verdict(r["dev_event_f1"], base["dev_event_f1"])
                for r in rows}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"ablation_a4_pos_weight_{stamp}.md"
    payload = {"rows": [{**r, "cap": None if r["cap"] == float("inf") else r["cap"]}
                        for r in rows], "verdicts": verdicts, "margin": MARGIN, "git": git}
    out.with_suffix(".json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    out.write_text(render(rows, verdicts), encoding="utf-8")
    print(render(rows, verdicts))


if __name__ == "__main__":
    main()
