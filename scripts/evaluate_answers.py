"""W6 6.8 — câu trả lời ràng buộc evidence: unsupported-claim rate, evidence precision.

    .venv/Scripts/python.exe -m scripts.evaluate_answers --split validation
    .venv/Scripts/python.exe -m scripts.evaluate_answers --split test

Với mỗi câu hỏi có relevant (query set v2), cấu hình có lọc cứng (structured_only, hybrid),
EN và VI: sinh câu trả lời bằng `ml.retrieval.answer`, kiểm contract `retrieval_result`,
đọc lại văn bản bằng lexicon cùng ngôn ngữ để tìm khẳng định không có evidence (A1) và từ cấm
(A3), kiểm mỗi evidence là một event có thật trong DB và các event trích thoả bộ lọc.
Thêm để tham khảo: tỷ lệ recording được trích mà ground truth cũng coi là relevant.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.provenance import git_state
from ml.retrieval import store
from ml.retrieval.answer import answer, supporting_events, unsupported_claims
from ml.retrieval.embedding import Embedder
from ml.retrieval.relevance import relevant_recordings
from ml.taxonomy import load_taxonomy
from scripts.evaluate_retrieval import LANGUAGES, QUERYSET, corpus_ground_truth

ROOT = Path(__file__).resolve().parents[1]
MODES = ("structured_only", "hybrid")
K = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"), default="validation")
    parser.add_argument("--device", default=None)
    return parser.parse_args()


def check(result: dict, query: dict, events: dict, lexicon, relevant: set, validator) -> dict:
    by_id = {e["event_id"]: (rid, e) for rid, evs in events.items() for e in evs}
    real = [e for e in result["evidence"] if e["event_id"] in by_id
            and by_id[e["event_id"]][0] == e["recording_id"]
            and by_id[e["event_id"]][1]["class_id"] == e["class_id"]]
    cited = sorted({e["recording_id"] for e in result["evidence"]})
    supported = all(supporting_events(events.get(rid, []), query["filters"]) for rid in cited)
    return {"contract_ok": not list(validator.iter_errors(result)),
            "unsupported": unsupported_claims(result, lexicon),
            "evidence_real": len(real) == len(result["evidence"]),
            "citations_satisfy_filters": supported, "answered": bool(result["evidence"]),
            "cited_relevant": [rid in relevant for rid in cited]}


def evaluate(args, queries, vectors, version) -> list[dict]:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicons = {"en": CaptionLexicon.from_taxonomy(taxonomy),
                "vi": CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG)}
    labels = {c.class_id: c.source_label.lower() for c in taxonomy.classes}
    names = {"en": labels.__getitem__, "vi": lexicons["vi"].canonical_phrase}
    schema = json.loads((ROOT / "contracts/retrieval_result.schema.json").read_text("utf-8"))
    validator = Draft202012Validator(schema)
    conn = store.connect()
    events = store.events_with_ids(conn, args.split)
    ground_truth = corpus_ground_truth(args.split)
    rows = []
    for index, query in enumerate(queries):
        relevant = set(relevant_recordings(query, ground_truth))
        if not relevant:
            continue
        for mode in MODES:
            for language, field in LANGUAGES.items():
                vector = vectors[language][index] if mode == "hybrid" else None
                ranked = store.search(conn, mode, args.split, query["filters"], vector, version, K)
                result = answer(query[field], query["filters"], mode, ranked, events, language,
                                names[language], K)
                rows.append({"query_id": query["query_id"], "mode": mode, "language": language,
                             **check(result, query, events, lexicons[language], relevant,
                                     validator), "answer": result["answer"]})
    return rows


def summarise(rows: list[dict]) -> dict:
    out = {}
    for mode in MODES:
        for language in LANGUAGES:
            sel = [r for r in rows if r["mode"] == mode and r["language"] == language]
            cited = [flag for r in sel for flag in r["cited_relevant"]]
            out[f"{mode}/{language}"] = {
                "n": len(sel), "contract_ok": sum(r["contract_ok"] for r in sel),
                "unsupported_claim_rate": sum(bool(r["unsupported"]) for r in sel) / len(sel),
                "evidence_real": sum(r["evidence_real"] for r in sel),
                "citations_satisfy_filters": sum(r["citations_satisfy_filters"] for r in sel),
                "answered": sum(r["answered"] for r in sel),
                "cited_relevant_share": sum(cited) / len(cited) if cited else float("nan")}
    return out


def render(result: dict) -> str:
    lines = [
        f"# Câu trả lời ràng buộc evidence (6.8) — corpus `{result['split']}`", "",
        "> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã "
        "index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "
        "\"Trích đúng GT\" = tỷ lệ recording được trích mà ground truth cũng coi là relevant "
        "(đo chất lượng SED + retrieval, không phải grounding).", "",
        "| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật "
        "| Trích thoả lọc | Có trả lời | Trích đúng GT |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, s in result["summary"].items():
        n = s["n"]
        lines.append(f"| {key} | {n} | {s['contract_ok']}/{n} | {s['unsupported_claim_rate']:.3f} "
                     f"| {s['evidence_real']}/{n} | {s['citations_satisfy_filters']}/{n} "
                     f"| {s['answered']}/{n} | {s['cited_relevant_share']:.3f} |")
    lines += ["", "## Ví dụ", ""] + [f"- `{e['query_id']}` {e['mode']}/{e['language']}: "
                                     f"{e['answer']}" for e in result["examples"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    queries = json.loads(QUERYSET.read_text(encoding="utf-8"))
    embedder = Embedder(device=args.device)
    vectors = {lang: embedder.encode([q[field] for q in queries])
               for lang, field in LANGUAGES.items()}
    rows = evaluate(args, queries, vectors, embedder.version)
    examples = [r for r in rows if r["mode"] == "hybrid" and r["query_id"] in ("q-001", "q-049")]
    result = {"split": args.split, "summary": summarise(rows), "examples": examples, "git": git,
              "rows": rows}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    destination = ROOT / "docs/measurements" / f"retrieval_answers_{args.split}_{stamp}.md"
    destination.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                                encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
