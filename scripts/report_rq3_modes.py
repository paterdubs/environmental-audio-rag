"""So ba chế độ truy hồi (RQ3) trên test: hiệu ghép cặp, theo nhóm câu hỏi, độ đúng bộ lọc.

Chỉ đọc bốn báo cáo `retrieval_benchmark_test_*` (bộ lọc gold) đã sinh và đã khóa; không chạy lại
truy hồi, không mở prediction. Báo cáo cuối từng chỉ in nDCG@10 của ba chế độ mà không nêu hiệu
hybrid − vector_only; script này đưa các số đó vào một artifact có nguồn.

    .venv/Scripts/python.exe -m scripts.report_rq3_modes
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
SOURCES = {
    "f2": "retrieval_benchmark_test_20261002",
    "B0": "retrieval_benchmark_test_s8lite_b0_gold_20261108",
    "lbrv2": "retrieval_benchmark_test_lbrv2_gold_20261110",
    "lbrv3": "retrieval_benchmark_test_lbrv3_gold_20261110",
}
MODES = ("structured_only", "vector_only", "hybrid")
GROUPS = ("duration", "single_class", "multi_class", "temporal")
PAIRS = ("hybrid−vector_only/en", "hybrid−structured_only/en")


def _ci(cell: dict[str, Any]) -> dict[str, float]:
    return {k: cell[k] for k in ("estimate", "lower", "upper")}


def summarise(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data["summary"]
    return {
        "n_queries_scored": data["n_queries_scored"],
        "paired": {name: _ci(data["paired_ndcg@10"][name]) for name in PAIRS},
        "by_group": {mode: {g: summary[f"{mode}/en"]["by_group"][g] for g in GROUPS}
                     for mode in MODES},
        "filter_exactness": {mode: summary[f"{mode}/en"]["filter_exactness"] for mode in MODES},
        "git_dirty": data["git"]["dirty"],
    }


def build() -> dict[str, Any]:
    systems = {label: summarise(M / f"{stem}.json") for label, stem in SOURCES.items()}
    return {"systems": systems, "sources": {k: f"docs/measurements/{s}.json"
                                            for k, s in SOURCES.items()},
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    lines = ["# RQ3: so ba chế độ truy hồi (test, bộ lọc gold, tiếng Anh)", "",
             "> Sinh bởi `scripts.report_rq3_modes` từ các báo cáo `retrieval_benchmark_test_*`; "
             "không tính lại.", "",
             "| Kho | hybrid − vector [CI 95%] | hybrid − structured [CI 95%] | "
             "exactness vector | exactness hybrid |", "|---|---:|---:|---:|---:|"]
    for label, s in data["systems"].items():
        v, h = s["paired"]["hybrid−vector_only/en"], s["paired"]["hybrid−structured_only/en"]
        lines.append(
            f"| {label} | {v['estimate']:+.3f} [{v['lower']:+.3f}, {v['upper']:+.3f}] | "
            f"{h['estimate']:+.3f} [{h['lower']:+.3f}, {h['upper']:+.3f}] | "
            f"{s['filter_exactness']['vector_only']:.3f} | "
            f"{s['filter_exactness']['hybrid']:.3f} |")
    lines += ["", "| Kho | " + " | ".join(GROUPS) + " |", "|---|" + "---:|" * len(GROUPS)]
    for label, s in data["systems"].items():
        cells = [f"{s['by_group']['hybrid'][g]:.3f} / {s['by_group']['vector_only'][g]:.3f}"
                 for g in GROUPS]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines += ["", "Ô nhóm câu hỏi: nDCG@10 hybrid / vector_only."]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = f"rq3_modes_{datetime.now(UTC):%Y%m%d}"
    (M / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    (M / f"{stem}.md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
