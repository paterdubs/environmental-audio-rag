"""W6 6.9 — benchmark RQ3: structured_only / vector_only / hybrid (ADR-0027).

    .venv/Scripts/python.exe -m scripts.evaluate_retrieval --split validation
    .venv/Scripts/python.exe -m scripts.evaluate_retrieval --split test

Query set v2 đóng băng (`data/manifests/retrieval_queryset_v2.json`), câu hỏi EN và VI.
Relevance từ ground truth (`ml.retrieval.relevance`); câu không có relevant trong corpus bị
loại và đếm riêng. Filter exactness đo trên **event đã index** (dự đoán) — structured_only và
hybrid phải = 1.000 (evaluation_protocol §9.2). Không có tham số nào được chỉnh: hybrid theo
SYSTEM §7.2, top-k = 10.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from ml.evaluation.bootstrap import recording_bootstrap
from ml.provenance import git_state
from ml.retrieval import store
from ml.retrieval.embedding import Embedder
from ml.retrieval.relevance import (
    DATASET_PREFIX,
    load_ground_truth,
    relevant_recordings,
    satisfied,
)

ROOT = Path(__file__).resolve().parents[1]
QUERYSET = ROOT / "data/manifests/retrieval_queryset_v2.json"
K = 10
METRICS = ("recall@1", "recall@5", "recall@10", "mrr", "ndcg@10", "filter_exactness")
LANGUAGES = {"en": "question", "vi": "question_vi"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"), default="validation")
    parser.add_argument("--device", default=None)
    parser.add_argument("--parsed-filters", type=Path,
                        help="measurement JSON của evaluate_query_parser; chỉ dùng template")
    parser.add_argument("--gold-reference", type=Path,
                        help="measurement retrieval gold để báo delta nDCG ghép cặp")
    return parser.parse_args()


def rank_metrics(ranked: list[str], relevant: set[str], exact: list[bool]) -> dict[str, float]:
    hits = [rid in relevant for rid in ranked]
    first = next((i for i, hit in enumerate(hits) if hit), None)
    dcg = sum(1 / math.log2(i + 2) for i, hit in enumerate(hits) if hit)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), K)))
    return {"recall@1": sum(hits[:1]) / len(relevant), "recall@5": sum(hits[:5]) / len(relevant),
            "recall@10": sum(hits[:10]) / len(relevant),
            "mrr": 0.0 if first is None else 1 / (first + 1), "ndcg@10": dcg / ideal,
            "filter_exactness": sum(exact) / len(exact) if exact else 1.0}


def corpus_ground_truth(split: str) -> dict[str, list]:
    import csv

    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8", newline="") as f:
        ids = {DATASET_PREFIX + r["recording_id"] for r in csv.DictReader(f)
               if r["split"] == split}
    ground_truth = load_ground_truth(ROOT / "data/annotations/datased_polyphonic_events.csv")
    return {rid: ground_truth.get(rid, []) for rid in ids}


def run_queries(conn, split, queries, vectors, version, indexed, parsed=None) -> list[dict]:
    rows = []
    ground_truth = corpus_ground_truth(split)
    for index, query in enumerate(queries):
        relevant = set(relevant_recordings(query, ground_truth))
        if not relevant:
            continue
        for mode in store.MODES:
            for language in LANGUAGES:
                filters = (query["filters"] if parsed is None
                           else parsed.get((query["query_id"], language)))
                if filters is None:
                    rows.append({"query_id": query["query_id"], "group": query["group"],
                                 "mode": mode, "language": language,
                                 "n_relevant": len(relevant), "retrieved": [],
                                 **rank_metrics([], relevant, []), "parse_error": True})
                    continue
                vector = vectors[language][index] if mode != "structured_only" else None
                ranked = store.search(conn, mode, split, filters, vector, version, K)
                exact = [satisfied(indexed.get(rid, []), filters) for rid in ranked]
                rows.append({"query_id": query["query_id"], "group": query["group"],
                             "mode": mode, "language": language, "n_relevant": len(relevant),
                             "retrieved": ranked, **rank_metrics(ranked, relevant, exact),
                             "parse_error": False})
    return rows


def _ndcg_ci(rows: list[dict]) -> dict:
    return asdict(recording_bootstrap(rows, lambda s: mean(r["ndcg@10"] for r in s)))


def _select(rows: list[dict], mode: str, language: str) -> list[dict]:
    return [r for r in rows if r["mode"] == mode and r["language"] == language]


def summarise(rows: list[dict]) -> dict:
    summary, paired = {}, {}
    for mode in store.MODES:
        for language in LANGUAGES:
            sel = _select(rows, mode, language)
            summary[f"{mode}/{language}"] = {
                "n": len(sel), **{m: mean(r[m] for r in sel) for m in METRICS},
                "ci_ndcg@10": _ndcg_ci(sel),
                "by_group": {g: mean(r["ndcg@10"] for r in sel if r["group"] == g)
                             for g in sorted({r["group"] for r in sel})}}
    for language in LANGUAGES:
        hybrid = {r["query_id"]: r for r in _select(rows, "hybrid", language)}
        for other in ("structured_only", "vector_only"):
            base = {r["query_id"]: r for r in _select(rows, other, language)}
            ci = recording_bootstrap(sorted(hybrid), lambda s, h=hybrid, b=base: mean(
                h[i]["ndcg@10"] - b[i]["ndcg@10"] for i in s))
            paired[f"hybrid−{other}/{language}"] = asdict(ci)
    return {"summary": summary, "paired_ndcg@10": paired}


def _parsed_filters(path: Path) -> tuple[dict[tuple[str, str], dict | None], str]:
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    parsed = {(row["query_id"], row["language"]): row["predicted"]
              for row in payload["predictions"] if row["dataset"] == "template"}
    return parsed, hashlib.sha256(text.encode()).hexdigest()


def compare_gold(rows: list[dict], path: Path) -> dict[str, dict]:
    gold = json.loads(path.read_text(encoding="utf-8"))["per_query"]
    lookup = {(row["query_id"], row["mode"], row["language"]): row for row in gold}
    comparison = {}
    for mode in store.MODES:
        for language in LANGUAGES:
            selected = [row for row in rows if row["mode"] == mode and row["language"] == language]
            deltas = [row["ndcg@10"] - lookup[(row["query_id"], mode, language)]["ndcg@10"]
                      for row in selected]
            comparison[f"{mode}/{language}"] = {
                "n": len(deltas), "parsed_minus_gold": mean(deltas)}
    return comparison


def render(result: dict) -> str:
    lines = [
        f"# Benchmark retrieval RQ3 — corpus `{result['split']}`", "",
        f"> Sinh bởi `scripts.evaluate_retrieval`. Query set `{result['queryset_sha256'][:8]}…`, "
        f"{result['n_queries_scored']}/{result['n_queries']} câu có relevant (còn lại loại); "
        f"embedding `{result['embedding_version']}`; SED `{result['sed_run']}`. Relevance từ "
        "ground truth; filter exactness trên event đã index. Không có tham số nào được "
        "chỉnh.", "",
        "| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] "
        "| Filter exactness |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, s in result["summary"].items():
        ci = s["ci_ndcg@10"]
        lines.append(f"| {key} | {s['n']} | {s['recall@1']:.3f} | {s['recall@5']:.3f} "
                     f"| {s['recall@10']:.3f} | {s['mrr']:.3f} | {s['ndcg@10']:.3f} "
                     f"[{ci['lower']:.3f}, {ci['upper']:.3f}] | {s['filter_exactness']:.3f} |")
    lines += ["", "## nDCG@10 theo nhóm câu hỏi", "",
              "| Cấu hình / ngôn ngữ | " + " | ".join(result["groups"]) + " |",
              "|---|" + "---:|" * len(result["groups"])]
    for key, s in result["summary"].items():
        lines.append(f"| {key} | " + " | ".join(f"{s['by_group'].get(g, float('nan')):.3f}"
                                                for g in result["groups"]) + " |")
    lines += ["", "## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%", "",
              "| So sánh | Δ [CI 95%] |", "|---|---:|"]
    for key, ci in result["paired_ndcg@10"].items():
        lines.append(f"| {key} | {ci['estimate']:+.3f} [{ci['lower']:+.3f}, {ci['upper']:+.3f}] |")
    if "gold_comparison_ndcg@10" in result:
        lines += ["", "## So với filter gold trên cùng câu", "",
                  "> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.", "",
                  "| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |", "|---|---:|---:|"]
        for key, row in result["gold_comparison_ndcg@10"].items():
            lines.append(f"| {key} | {row['n']} | {row['parsed_minus_gold']:+.3f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    text = QUERYSET.read_text(encoding="utf-8")
    queries = json.loads(text)
    parsed, parser_sha = (None, None)
    if args.parsed_filters is not None:
        parsed, parser_sha = _parsed_filters(args.parsed_filters)
    embedder = Embedder(device=args.device)
    vectors = {lang: embedder.encode([q[field] for q in queries])
               for lang, field in LANGUAGES.items()}
    conn = store.connect()
    indexed = store.indexed_events(conn, args.split)
    sed_run = conn.execute("SELECT DISTINCT model_version FROM events e JOIN recordings r "
                           "USING (recording_id) WHERE r.split = %s", (args.split,)).fetchall()
    rows = run_queries(conn, args.split, queries, vectors, embedder.version, indexed, parsed)
    result = {"split": args.split, "queryset_sha256": hashlib.sha256(text.encode()).hexdigest(),
              "n_queries": len(queries), "n_queries_scored": len({r["query_id"] for r in rows}),
              "embedding_version": embedder.version, "sed_run": ",".join(r[0] for r in sed_run),
              "groups": sorted({q["group"] for q in queries}), "git": git,
              **summarise(rows), "per_query": rows}
    if parsed is not None:
        result["parser_measurement"] = str(args.parsed_filters)
        result["parser_measurement_sha256"] = parser_sha
    if args.gold_reference is not None:
        result["gold_reference"] = str(args.gold_reference)
        result["gold_comparison_ndcg@10"] = compare_gold(rows, args.gold_reference)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    kind = "_parsed" if parsed is not None else ""
    destination = ROOT / "docs/measurements" / f"retrieval_benchmark_{args.split}{kind}_{stamp}.md"
    destination.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                                encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
