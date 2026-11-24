"""RQ3: phân loại vì sao bản ghi liên quan không vào top-10 của hybrid (từ danh sách đã lưu).

Không dựng DB. Dùng một tính chất đã kiểm ở ADR-0049: khi structured_only trả dưới 10 bản ghi, đó là
**toàn bộ** bản ghi thỏa bộ lọc trên sự kiện dự đoán. Với mỗi cặp (truy vấn, bản ghi liên quan theo
nhãn gốc) mà hybrid không trả về:

- `sed_miss`: structured_only < 10 và bản ghi không có trong đó — sự kiện dự đoán không thỏa bộ lọc
  (SED bỏ sót lớp, lệch biên làm sai quan hệ thời gian hay thời lượng).
- `beyond_top10_or_miss`: structured_only đủ 10 — không phân biệt được bị cắt ở top-10 hay SED bỏ
  sót.

Thêm: số kết quả hybrid không liên quan theo nhãn gốc (`sed_false_match`: thỏa bộ lọc trên sự kiện
dự đoán nhưng nhãn gốc thì không). Bộ lọc parser so với gold: số truy vấn có danh sách hybrid khác.

    .venv/Scripts/python.exe -m scripts.report_rq3_failures --split validation
    .venv/Scripts/python.exe -m scripts.report_rq3_failures --split test   # mô tả số đã khóa
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state
from ml.retrieval.relevance import relevant_recordings
from scripts.evaluate_retrieval import QUERYSET, corpus_ground_truth
from scripts.report_rq3_backfill import SOURCES, K

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
CAUSES = ("hit", "sed_miss", "beyond_top10_or_miss")


def classify(relevant: set[str], structured: list[str], hybrid: list[str]) -> Counter:
    """Counts of relevant recordings by cause, plus hybrid results that are not relevant."""
    counts: Counter = Counter()
    complete = len(structured) < K
    for rid in relevant:
        if rid in hybrid:
            counts["hit"] += 1
        elif complete and rid not in structured:
            counts["sed_miss"] += 1
        else:
            counts["beyond_top10_or_miss"] += 1
    counts["sed_false_match"] = sum(rid not in relevant for rid in hybrid)
    counts["retrieved"] = len(hybrid)
    return counts


def by_group(per_query: list[dict], queries: dict[str, dict], gt: dict[str, list],
             language: str = "en") -> dict[str, dict[str, int]]:
    rows = {(r["query_id"], r["mode"]): r for r in per_query if r["language"] == language}
    totals: dict[str, Counter] = {}
    for qid in sorted({q for q, _ in rows}):
        relevant = set(relevant_recordings(queries[qid], gt))
        counts = classify(relevant, rows[(qid, "structured_only")]["retrieved"],
                          rows[(qid, "hybrid")]["retrieved"])
        for key in ("all", queries[qid]["group"]):
            totals.setdefault(key, Counter()).update(counts)
    return {g: dict(c) for g, c in sorted(totals.items())}


def parser_divergence(gold: list[dict], parsed: list[dict], language: str = "en") -> dict:
    def lists(rows: list[dict]) -> dict[str, list[str]]:
        return {r["query_id"]: r["retrieved"] for r in rows
                if r["mode"] == "hybrid" and r["language"] == language}
    g, p = lists(gold), lists(parsed)
    common = sorted(set(g) & set(p))
    return {"n": len(common), "different": sum(g[q] != p[q] for q in common)}


def build(split: str) -> dict[str, Any]:
    queries = {q["query_id"]: q for q in json.loads(QUERYSET.read_text(encoding="utf-8"))}
    gt = corpus_ground_truth(split)
    results, sources = {}, {}
    for corpus, (gold_stem, parsed_stem) in SOURCES.items():
        names = [s.format(split=split) for s in (gold_stem, parsed_stem)]
        gold, parsed = (json.loads((M / f"{n}.json").read_text(encoding="utf-8"))["per_query"]
                        for n in names)
        sources[corpus] = [f"docs/measurements/{n}.json" for n in names]
        results[corpus] = {"by_group": by_group(gold, queries, gt),
                           "parser_vs_gold": parser_divergence(gold, parsed)}
    return {"split": split, "k": K, "results": results, "sources": sources,
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    title = "# RQ3: vì sao bản ghi liên quan lọt khỏi top-10 của hybrid"
    lines = [f"{title} ({data['split']}, gold, EN)",
             "", "> Sinh bởi `scripts.report_rq3_failures` từ danh sách đã lưu.", "",
             "| Kho | Nhóm | Cặp liên quan | Trúng | SED bỏ sót | Ngoài top-10 hoặc bỏ sót | "
             "Trả về không liên quan / tổng trả về |", "|---|---|---:|---:|---:|---:|---:|"]
    for corpus, r in data["results"].items():
        for group, c in r["by_group"].items():
            total = sum(c.get(k, 0) for k in CAUSES)
            lines.append(f"| {corpus} | {group} | {total} | {c.get('hit', 0)} | "
                         f"{c.get('sed_miss', 0)} | {c.get('beyond_top10_or_miss', 0)} | "
                         f"{c.get('sed_false_match', 0)} / {c.get('retrieved', 0)} |")
    lines += ["", "| Kho | Truy vấn có danh sách hybrid khác khi dùng bộ lọc parser |",
              "|---|---:|"]
    for corpus, r in data["results"].items():
        d = r["parser_vs_gold"]
        lines.append(f"| {corpus} | {d['different']}/{d['n']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"), required=True)
    data = build(parser.parse_args().split)
    stem = M / f"retrieval_failures_{data['split']}_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
