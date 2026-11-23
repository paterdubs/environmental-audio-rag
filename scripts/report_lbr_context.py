"""LBR trong bối cảnh: các mốc đơn giản hơn, trần sửa biên và độ vững, trên dự đoán ngoài mẫu (OOF).

Chỉ đọc `oof_selection_20261109_LBR.json` (tầng C, 564 bản ghi annotated) và
`lbr_diagnosis_20261109.md` (trần sửa biên); không đọc test, không tính lại. Hai mốc đơn giản hơn
(ngưỡng riêng từng lớp, dịch onset toàn cục) đo bằng script nháp trước khi có ADR-0045 và chưa có
artifact sinh bằng script repo (PLAN, nợ #30): chúng được nhập là hằng số có nhãn "thăm dò".

    .venv/Scripts/python.exe -m scripts.report_lbr_context
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
OOF = M / "oof_selection_20261109_LBR.json"
DIAGNOSIS = M / "lbr_diagnosis_20261109.md"
# Script nháp, ADR-0045 (Alternatives considered 1–2); không có artifact sinh bằng script repo.
EXPLORATORY = {"per_class_lambda": 0.2335, "global_onset_shift": 0.2469}


def oracle_ceiling(text: str, window: str = "1 s") -> float:
    match = re.search(rf"^\| {re.escape(window)} \| ([0-9.]+) \|", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"không thấy trần ±{window} trong {DIAGNOSIS.name}")
    return float(match.group(1))


def _row(results: dict[str, Any], name: str) -> dict[str, float]:
    cell = results[name]["f1"]["all"]
    return {"micro": cell["micro_f1"], "macro": cell["macro_f1"]}


def build() -> dict[str, Any]:
    data = json.loads(OOF.read_text(encoding="utf-8"))
    results, deltas = data["results"], data["deltas"]
    rows = {name: _row(results, name)
            for name in ("B0", "P1x3", "LBR_v1", "LBR_v2", "LBR_v2_on_P1x3")}
    folds = data["fold_thresholds"]["LBR_v2"]
    return {
        "rows": rows,
        "deltas": {k: {f: v[f] for f in ("estimate", "lower", "upper", "baseline")}
                   for k, v in deltas.items()},
        "exploratory": EXPLORATORY,
        "oracle_ceiling_1s": oracle_ceiling(DIAGNOSIS.read_text(encoding="utf-8")),
        "recall_first_threshold_folds_at_floor": sum(
            1 for fold in folds.values() if fold["recall_first"] == 0.005),
        "n_folds": len(folds),
        "sources": [OOF.relative_to(ROOT).as_posix(), DIAGNOSIS.relative_to(ROOT).as_posix()],
        "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat(),
    }


def render(data: dict[str, Any]) -> str:
    r, d = data["rows"], data["deltas"]
    lines = ["# LBR trong bối cảnh (OOF 564 bản ghi annotated, 21 lớp)", "",
             "> Sinh bởi `scripts.report_lbr_context`; không đọc test.", "",
             "| Cấu hình | Micro | Macro | Δ micro [95% CI] |", "|---|---:|---:|---|"]

    def delta(key: str) -> str:
        c = d[key]
        return f"{c['estimate']:+.4f} [{c['lower']:+.4f}, {c['upper']:+.4f}] so với {c['baseline']}"

    ex = data["exploratory"]
    lines += [
        f"| B0 (mốc) | {r['B0']['micro']:.4f} | {r['B0']['macro']:.4f} | — |",
        f"| Ngưỡng riêng từng lớp (thăm dò) | {ex['per_class_lambda']:.4f} | — | — |",
        f"| Dịch onset toàn cục (thăm dò) | {ex['global_onset_shift']:.4f} | — | — |",
        f"| LBR V1 | {r['LBR_v1']['micro']:.4f} | {r['LBR_v1']['macro']:.4f} | "
        f"{delta('LBR_v1')} |",
        f"| LBR V2 (số chính) | {r['LBR_v2']['micro']:.4f} | {r['LBR_v2']['macro']:.4f} | "
        f"{delta('LBR_v2')} |",
        f"| P1×3 (ensemble 3 seed, mốc) | {r['P1x3']['micro']:.4f} | "
        f"{r['P1x3']['macro']:.4f} | — |",
        f"| LBR V2 học trên một mô hình, áp lên P1×3 | {r['LBR_v2_on_P1x3']['micro']:.4f} | "
        f"{r['LBR_v2_on_P1x3']['macro']:.4f} | {delta('LBR_v2_on_P1x3')} |",
        f"| Trần: sửa biên mọi hộp 1-1 trong ±1 s | {data['oracle_ceiling_1s']:.4f} | — | — |",
        "", f"Ngưỡng điểm 'ưu tiên phát hiện' của V2 nằm ở đáy lưới (0,005) ở "
        f"{data['recall_first_threshold_folds_at_floor']}/{data['n_folds']} fold.", ""]
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = f"lbr_context_{datetime.now(UTC):%Y%m%d}"
    (M / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    (M / f"{stem}.md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
