"""Event-F1 **macro** cho mọi lần đánh giá SED đã có (PLAN nợ #20, evaluation_protocol Q2).

    .venv/Scripts/python.exe -m scripts.report_event_f1_macro

Mọi event-F1 headline đến 26/09 là **micro** (`overall` của sed_eval). Macro của sed_eval
(`class_wise_average`) là `nanmean` của F1 theo lớp — và `evaluation*.json` đã lưu F1 của cả 21
lớp. Nên macro được **tổng hợp lại từ số đã lưu**: không nạp logit, không chạy lại test. Với file
mới (có `event_based_f1_macro` do `evaluate_run` ghi), hai cách tính phải khớp.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "ml" / "runs"
MEASUREMENTS = ROOT / "docs" / "measurements"


def macro_from_per_class(per_class: dict) -> float:
    values = [float(v["f_measure"]) for v in per_class.values()
              if isinstance(v, dict) and "f_measure" in v]
    return float(np.nanmean(values)) if values else float("nan")


def row(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    macro = macro_from_per_class(result["event_based_f1_per_class"])
    stored = result.get("event_based_f1_macro", {}).get("f_measure")
    if stored is not None and not math.isclose(stored, macro, abs_tol=1e-9):
        raise SystemExit(f"{path}: macro lưu {stored} ≠ tổng hợp {macro}")
    return {"run": path.parent.name, "file": path.name,
            "split": result.get("split", "dev" if path.name.startswith("dev_") else "test"),
            "postproc": Path(result.get("postproc", "postproc.json")).name,
            "micro": float(result["event_based_f1"]["f_measure"]), "macro": macro}


def render(rows: list[dict], git: dict) -> str:
    lines = ["# Event-F1 micro và macro cho mọi lần đánh giá SED", "",
             "> Sinh bởi `scripts.report_event_f1_macro`. Macro = nanmean F1 theo lớp đã lưu "
             "(= `class_wise_average` của sed_eval); **không chạy lại test**. "
             f"git `{git['revision'][:7]}`.", "",
             "| Run | File | Split | Hậu xử lý | Event-F1 micro | Event-F1 macro |",
             "|---|---|---|---|---:|---:|"]
    lines += [f"| `{r['run']}` | `{r['file']}` | {r['split']} | `{r['postproc']}` | "
              f"{r['micro']:.4f} | {r['macro']:.4f} |" for r in rows]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    files = sorted([*RUNS.glob("*/evaluation*.json"), *RUNS.glob("*/dev_evaluation*.json")])
    rows = [row(path) for path in files]
    git = git_state(ROOT)
    out = MEASUREMENTS / f"event_f1_macro_{datetime.now(UTC):%Y%m%d}.md"
    out.with_suffix(".json").write_text(json.dumps({"rows": rows, "git": git}, indent=1),
                                        encoding="utf-8")
    out.write_text(render(rows, git), encoding="utf-8")
    print(render(rows, git))


if __name__ == "__main__":
    main()
