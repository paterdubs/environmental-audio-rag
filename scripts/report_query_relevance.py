"""W6 — độ phủ relevance của query set trên ground truth DataSED, theo split.

    .venv/Scripts/python.exe -m scripts.report_query_relevance

Relevance tính từ annotation (`ml.retrieval.relevance`), không từ output hệ thống nào,
nên đo được trước khi có retrieval. Query không có recording relevant nào thì Recall@k
không xác định — HANDOFF_CODEX §A4 coi đó là query vô dụng (sửa hoặc bỏ ở task 6.7).
Script chỉ đếm; không chọn, không sửa query nào.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

from ml.retrieval.query_set import build_query_set
from ml.retrieval.relevance import (
    DATASET_PREFIX,
    load_ground_truth,
    relevant_recordings,
    validate_query_classes,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ("train", "validation", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def split_members() -> dict[str, set[str]]:
    members: dict[str, set[str]] = {split: set() for split in SPLITS}
    path = ROOT / "data/splits/datased_polyphonic.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            members[row["split"]].add(DATASET_PREFIX + row["recording_id"])
    return members


def coverage(queries: list[dict], ground_truth: dict, members: dict[str, set[str]]) -> dict:
    result = {}
    for split, ids in members.items():
        subset = {rid: ground_truth.get(rid, []) for rid in ids}
        counts = [len(relevant_recordings(q, subset)) for q in queries]
        result[split] = {"n_recordings": len(ids),
                         "queries_with_relevant": sum(c > 0 for c in counts),
                         "median_relevant": median(counts), "max_relevant": max(counts)}
    return result


def render(result: dict) -> str:
    lines = [
        "# Độ phủ relevance của query set (ground truth DataSED)", "",
        "> Sinh bởi `scripts.report_query_relevance`. Relevance từ annotation, không từ "
        f"hệ thống nào. {result['n_queries']} query temporal từ `build_query_set`.", "",
        "| Split | recording | query có ≥1 relevant | trung vị số relevant | lớn nhất |",
        "|---|---:|---:|---:|---:|",
    ]
    for split, row in result["splits"].items():
        lines.append(f"| {split} | {row['n_recordings']} | {row['queries_with_relevant']}/"
                     f"{result['n_queries']} | {row['median_relevant']:g} | "
                     f"{row['max_relevant']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    queries = build_query_set(class_ids)
    validate_query_classes(queries, class_ids)
    ground_truth = load_ground_truth(ROOT / "data/annotations/datased_polyphonic_events.csv")
    result = {"n_queries": len(queries), "splits": coverage(queries, ground_truth, split_members())}
    destination = args.output or (
        ROOT / "docs/measurements" / f"query_relevance_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
