"""RQ3 chế độ backfill (ADR-0049): lọc cứng trước, nối kết quả ngữ nghĩa không thỏa bộ lọc sau.

Chỉ đọc danh sách `retrieved` trong các báo cáo `retrieval_benchmark_*` đã khóa; không dựng DB,
không embed lại, không chạy lại truy hồi, không chạm prediction SED. Relevance tính lại từ ground
truth như `evaluate_retrieval` và phải khớp nDCG@10 đã lưu của cả ba chế độ, lệch thì dừng.

    .venv/Scripts/python.exe -m scripts.report_rq3_backfill --split validation
    .venv/Scripts/python.exe -m scripts.report_rq3_backfill --split test     # một lần (ADR-0049 §4)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from ml.evaluation.bootstrap import recording_bootstrap
from ml.provenance import git_state
from ml.retrieval import fusion
from ml.retrieval.relevance import relevant_recordings
from scripts.evaluate_retrieval import QUERYSET, corpus_ground_truth, rank_metrics

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
K = 10
RRF_K = 60
SEED = 20260922
N_RESAMPLE = 10_000
SOURCES = {  # kho → (tiền tố gold, tiền tố parsed), {split} được thay
    "f2": ("retrieval_benchmark_{split}_20261002", "retrieval_benchmark_{split}_parsed_20261002"),
    "B0": ("retrieval_benchmark_{split}_s8lite_b0_gold_20261108",
           "retrieval_benchmark_{split}_s8lite_b0_parsed_20261108"),
    "lbrv2": ("retrieval_benchmark_{split}_lbrv2_gold_20261110",
              "retrieval_benchmark_{split}_lbrv2_parsed_20261110"),
    "lbrv3": ("retrieval_benchmark_{split}_lbrv3_gold_20261110",
              "retrieval_benchmark_{split}_lbrv3_parsed_20261110"),
}
MODES = ("structured_only", "vector_only", "hybrid", "backfill", "rrf")
PAIRS = (("backfill", "vector_only"), ("backfill", "hybrid"), ("rrf", "vector_only"))
LANGUAGES = ("en", "vi")
TOL = 1e-9


def backfill(hybrid: Sequence[str], vector: Sequence[str], k: int = K) -> list[str]:
    """Hybrid results first, then vector results not already present, cut at k."""
    return fusion.backfill(hybrid, vector, k)


def rrf(lists: Sequence[Sequence[str]], k_rrf: int = RRF_K, k: int = K) -> list[str]:
    """Reciprocal rank fusion; ties broken by recording id."""
    scores: dict[str, float] = {}
    for ranked in lists:
        for rank, rid in enumerate(ranked):
            scores[rid] = scores.get(rid, 0.0) + 1.0 / (k_rrf + rank + 1)
    return [rid for rid, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))][:k]


def permutation_pvalue(diffs: Sequence[float], n: int = N_RESAMPLE, seed: int = SEED) -> float:
    """Two-sided paired sign-flip test of mean(diffs) = 0."""
    values = np.asarray(diffs, dtype=float)
    observed = abs(values.mean())
    if observed <= TOL:
        return 1.0
    rng = np.random.default_rng(seed)
    signs = rng.choice((-1.0, 1.0), size=(n, values.size))
    extreme = np.sum(np.abs((signs * values).mean(axis=1)) >= observed - TOL)
    return float((extreme + 1) / (n + 1))


def win_tie_loss(diffs: Sequence[float]) -> dict[str, int]:
    return {"win": sum(d > TOL for d in diffs), "tie": sum(abs(d) <= TOL for d in diffs),
            "loss": sum(d < -TOL for d in diffs)}


def score_queries(per_query: list[dict], queries: dict[str, dict],
                  ground_truth: dict[str, list], language: str) -> list[dict[str, Any]]:
    """One row per scored query with metrics for every mode; checks stored nDCG."""
    rows = {(r["query_id"], r["mode"]): r for r in per_query if r["language"] == language}
    out = []
    for qid in sorted({q for q, _ in rows}):
        relevant = set(relevant_recordings(queries[qid], ground_truth))
        lists = {m: rows[(qid, m)]["retrieved"] for m in ("structured_only", "vector_only",
                                                          "hybrid")}
        for mode, ranked in lists.items():
            recomputed = rank_metrics(ranked, relevant, [])["ndcg@10"]
            if abs(recomputed - rows[(qid, mode)]["ndcg@10"]) > TOL:
                raise ValueError(f"{qid}/{mode}/{language}: nDCG lệch artifact đã lưu")
        lists["backfill"] = backfill(lists["hybrid"], lists["vector_only"])
        lists["rrf"] = rrf([lists["hybrid"], lists["vector_only"]])
        tier1 = set(lists["hybrid"])
        metrics = {}
        for mode, ranked in lists.items():
            m = rank_metrics(ranked, relevant, [])
            metrics[mode] = {"ndcg@10": m["ndcg@10"], "recall@10": m["recall@10"],
                             "mrr": m["mrr"], "n": len(ranked),
                             "tier1_share": (sum(r in tier1 for r in ranked) / len(ranked)
                                             if ranked else 1.0)}
        out.append({"query_id": qid, "group": queries[qid]["group"],
                    "n_hybrid": len(lists["hybrid"]), "metrics": metrics})
    return out


def _ci(ids: list[str], stat: Callable[[Sequence[str]], float]) -> dict[str, float]:
    ci = asdict(recording_bootstrap(ids, stat, n_bootstrap=N_RESAMPLE, seed=SEED))
    return {k: ci[k] for k in ("estimate", "lower", "upper")}


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {r["query_id"]: r for r in rows}
    ids = sorted(by_id)
    means = {mode: {key: mean(by_id[i]["metrics"][mode][key] for i in ids)
                    for key in ("ndcg@10", "recall@10", "mrr", "tier1_share")} for mode in MODES}
    groups = sorted({r["group"] for r in rows})
    by_group = {mode: {g: mean(r["metrics"][mode]["ndcg@10"] for r in rows if r["group"] == g)
                       for g in groups} for mode in MODES}
    paired = {}
    for a, b in PAIRS:
        diffs = [by_id[i]["metrics"][a]["ndcg@10"] - by_id[i]["metrics"][b]["ndcg@10"]
                 for i in ids]
        paired[f"{a}−{b}"] = {**_ci(ids, lambda s, a=a, b=b: mean(
            by_id[i]["metrics"][a]["ndcg@10"] - by_id[i]["metrics"][b]["ndcg@10"] for i in s)),
            "p_permutation": permutation_pvalue(diffs), **win_tie_loss(diffs)}
    return {"n_queries": len(ids), "mean": means, "by_group": by_group, "paired_ndcg@10": paired,
            "hybrid_empty": sum(by_id[i]["n_hybrid"] == 0 for i in ids),
            "hybrid_short": sum(by_id[i]["n_hybrid"] < K for i in ids)}


def build(split: str) -> dict[str, Any]:
    queries = {q["query_id"]: q for q in json.loads(QUERYSET.read_text(encoding="utf-8"))}
    ground_truth = corpus_ground_truth(split)
    results, sources = {}, {}
    for corpus, stems in SOURCES.items():
        for filters, stem in zip(("gold", "parsed"), stems, strict=True):
            name = stem.format(split=split)
            data = json.loads((M / f"{name}.json").read_text(encoding="utf-8"))
            if data["split"] != split:
                raise ValueError(f"{name}: split {data['split']} khác {split}")
            sources[f"{corpus}/{filters}"] = f"docs/measurements/{name}.json"
            for language in LANGUAGES:
                rows = score_queries(data["per_query"], queries, ground_truth, language)
                results[f"{corpus}/{filters}/{language}"] = {"summary": summarise(rows),
                                                             "per_query": rows}
    return {"split": split, "adr": "ADR-0049", "k": K, "rrf_k": RRF_K, "seed": SEED,
            "n_resample": N_RESAMPLE, "results": results, "sources": sources,
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def _fmt(cell: dict[str, Any]) -> str:
    return (f"{cell['estimate']:+.3f} [{cell['lower']:+.3f}, {cell['upper']:+.3f}] "
            f"p={cell['p_permutation']:.4f} ({cell['win']}/{cell['tie']}/{cell['loss']})")


def render(data: dict[str, Any]) -> str:
    lines = [f"# RQ3 backfill ({data['split']}, ADR-0049)", "",
             "> Sinh bởi `scripts.report_rq3_backfill` từ danh sách `retrieved` đã lưu; không chạy "
             "lại truy hồi. Hiệu ghép cặp nDCG@10 [CI 95% bootstrap], p hoán vị, "
             "(thắng/hòa/thua).", ""]
    for filters in ("gold", "parsed"):
        for language in LANGUAGES:
            lines += [f"## Bộ lọc {filters}, {language}", "",
                      "| Kho | n | rỗng | structured | vector | hybrid | backfill | rrf | "
                      "tầng 1 backfill |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
            for corpus in SOURCES:
                s = data["results"][f"{corpus}/{filters}/{language}"]["summary"]
                nd = {m: s["mean"][m]["ndcg@10"] for m in MODES}
                lines.append(f"| {corpus} | {s['n_queries']} | {s['hybrid_empty']} | "
                             + " | ".join(f"{nd[m]:.3f}" for m in MODES)
                             + f" | {s['mean']['backfill']['tier1_share']:.3f} |")
            lines += ["", "| Kho | backfill − vector | backfill − hybrid | rrf − vector |",
                      "|---|---|---|---|"]
            for corpus in SOURCES:
                p = data["results"][f"{corpus}/{filters}/{language}"]["summary"]["paired_ndcg@10"]
                lines.append(f"| {corpus} | " + " | ".join(_fmt(p[f"{a}−{b}"]) for a, b in PAIRS)
                             + " |")
            lines.append("")
    lines.append("Tầng 1: tỷ lệ kết quả top-10 thỏa bộ lọc (kết quả hybrid).")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"), required=True)
    args = parser.parse_args()
    data = build(args.split)
    stem = M / f"retrieval_backfill_{args.split}_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
