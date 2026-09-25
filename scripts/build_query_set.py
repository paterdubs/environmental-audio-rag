"""W6 6.7 — dựng và đóng băng query set v2 (ADR-0027) từ ground truth TRAIN.

    .venv/Scripts/python.exe -m scripts.build_query_set

Chọn câu hỏi theo tần suất điều kiện trên **train** (không nhìn dev/test, không nhìn output
hệ thống), ghi `data/manifests/retrieval_queryset_v2.json` — bất biến: đã có mà nội dung khác
thì dừng. Sau đó chỉ **báo** độ phủ relevance trên dev/test (không dùng để chọn lại).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.retrieval.query_set import GROUP_SIZES, build_query_set
from ml.retrieval.relevance import (
    DATASET_PREFIX,
    load_ground_truth,
    relevant_recordings,
    validate_query_classes,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
QUERYSET = ROOT / "data/manifests/retrieval_queryset_v2.json"
SPLITS = ("train", "validation", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=QUERYSET)
    return parser.parse_args()


def split_members() -> dict[str, set[str]]:
    members: dict[str, set[str]] = {split: set() for split in SPLITS}
    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            members[row["split"]].add(DATASET_PREFIX + row["recording_id"])
    return members


def write_frozen(path: Path, queries: list[dict]) -> str:
    text = json.dumps(queries, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{path} đã đóng băng và khác bản dựng lại — không ghi đè")
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def coverage(queries: list[dict], ground_truth: dict, ids: set[str]) -> dict:
    corpus = {rid: ground_truth.get(rid, []) for rid in ids}
    counts = [len(relevant_recordings(q, corpus)) for q in queries]
    by_group = {g: sum(c > 0 for q, c in zip(queries, counts, strict=True) if q["group"] == g)
                for g in GROUP_SIZES}
    return {"n_recordings": len(ids), "with_relevant": sum(c > 0 for c in counts),
            "by_group": by_group, "median_relevant": median(counts)}


def render(result: dict) -> str:
    lines = [
        "# Query set v2 — nhóm và độ phủ relevance", "",
        f"> Sinh bởi `scripts.build_query_set`. `retrieval_queryset_v2.json` sha256 "
        f"`{result['sha256'][:8]}…`. Câu hỏi chọn theo ground truth **train** (ADR-0027); độ phủ "
        "dev/test dưới đây chỉ để báo, không dùng để chọn.", "",
        "| Nhóm | Số câu |", "|---|---:|",
        *[f"| {g} | {n} |" for g, n in result["groups"].items()], "",
        "| Split | recording | câu có ≥1 relevant | theo nhóm | trung vị relevant |",
        "|---|---:|---:|---|---:|",
    ]
    for split, c in result["coverage"].items():
        groups = ", ".join(f"{g} {n}" for g, n in c["by_group"].items())
        lines.append(f"| {split} | {c['n_recordings']} | {c['with_relevant']}/{result['n']} "
                     f"| {groups} | {c['median_relevant']:g} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    vi = CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG)
    labels = {c.class_id: c.source_label.lower() for c in taxonomy.classes}
    ground_truth = load_ground_truth(ROOT / "data/annotations/datased_polyphonic_events.csv")
    members = split_members()
    train = {rid: ground_truth.get(rid, []) for rid in members["train"]}
    queries = build_query_set(train, taxonomy.polyphonic_class_ids, labels.__getitem__,
                              vi.canonical_phrase)
    validate_query_classes(queries, taxonomy.polyphonic_class_ids)
    sha = write_frozen(args.output, queries)
    result = {"sha256": sha, "n": len(queries),
              "groups": {g: sum(q["group"] == g for q in queries) for g in GROUP_SIZES},
              "coverage": {s: coverage(queries, ground_truth, members[s]) for s in SPLITS}}
    destination = (ROOT / "docs/measurements"
                   / f"retrieval_queryset_v2_{datetime.now(UTC).strftime('%Y%m%d')}.md")
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
