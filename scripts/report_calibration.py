"""Bảng định cỡ event-F1: B0/LBR V2/V3 cạnh mức đồng thuận quan sát giữa hai lần gán nhãn.

Chỉ đọc lại số đã nằm trong `evaluation_phase_lbr_annotated.json` (test annotated, đã đóng băng và
đã có sổ test) và `human_ceiling` trong `oof_selection_20261109_LBR.json`. Không tính lại metric,
không đọc dự đoán test, nên không thêm lượt chạm test mới.

    .venv/Scripts/python.exe -m scripts.report_calibration
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
EVAL = (ROOT / "ml/runs/sed_ensemble_B0_final_test_20261014T085016Z"
        / "evaluation_phase_lbr_annotated.json")
OOF = M / "oof_selection_20261109_LBR.json"


def _system(cell: dict[str, Any]) -> dict[str, float | None]:
    inter = cell.get("intersection") or {}
    micro = inter.get("micro", {}) if isinstance(inter, dict) else {}
    return {
        "micro": cell["micro_f1"], "macro": cell["macro_f1"],
        "collar_1s": cell["event_f1_collar_1s"]["micro"],
        "segment_1s": cell["segment_f1_1s"]["micro"],
        "intersection_recall": micro.get("recall"),
        "intersection_precision": micro.get("precision"),
    }


def build() -> dict[str, Any]:
    evaluation = json.loads(EVAL.read_text(encoding="utf-8"))
    v2, v3 = evaluation["lbr"], evaluation["lbr_extra"][0]
    rows = {
        "B0": _system(v2["baseline"]["all"]),
        "LBR V2, điểm f1": _system(v2["points"]["f1"]["all"]),
        "LBR V3, điểm f1": _system(v3["points"]["f1"]["all"]),
        "LBR V3, recall_first": _system(v3["points"]["recall_first"]["all"]),
    }
    human = json.loads(OOF.read_text(encoding="utf-8"))["human_ceiling"]["all"]
    ratios = {
        "v2_micro_over_human": rows["LBR V2, điểm f1"]["micro"] / human["micro_f1"],
        "v2_collar_1s_over_human": (rows["LBR V2, điểm f1"]["collar_1s"]
                                    / human["event_f1_collar_1s"]),
        "b0_segment_over_human": rows["B0"]["segment_1s"] / human["segment_f1_1s"],
    }
    return {"n_recordings": evaluation["n_recordings"], "rows": rows, "human": human,
            "ratios": ratios, "sources": [EVAL.relative_to(ROOT).as_posix(),
                                          OOF.relative_to(ROOT).as_posix()],
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    lines = [f"# Bảng định cỡ event-F1 (test annotated, n = {data['n_recordings']})", "",
             "> Sinh bởi `scripts.report_calibration`; đọc lại số đã đóng băng, "
             "không tính lại.", "",
             "| Hệ thống | Micro, collar 0,2 s | Collar 1 s | Segment-F1 1 s | Giao nhau R / P |",
             "|---|---:|---:|---:|---:|"]
    for name, r in data["rows"].items():
        inter = ("—" if r["intersection_recall"] is None
                 else f"{r['intersection_recall']:.4f} / {r['intersection_precision']:.4f}")
        lines.append(f"| {name} | {r['micro']:.4f} | {r['collar_1s']:.4f} | "
                     f"{r['segment_1s']:.4f} | {inter} |")
    h = data["human"]
    lines += [f"| Đồng thuận người–người ({h['pairs']} cặp) | {h['micro_f1']:.4f} | "
              f"{h['event_f1_collar_1s']:.4f} | {h['segment_f1_1s']:.4f} | — |", "",
              "V2 / người: "
              f"{data['ratios']['v2_micro_over_human']:.3f} (0,2 s), "
              f"{data['ratios']['v2_collar_1s_over_human']:.3f} (1 s); "
              f"B0 segment / người: {data['ratios']['b0_segment_over_human']:.3f}.", ""]
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = f"calibration_{datetime.now(UTC):%Y%m%d}"
    (M / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    (M / f"{stem}.md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
