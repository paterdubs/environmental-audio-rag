"""Evidence-bound answers for retrieval (W6 6.8, SYSTEM §7.4 constraints A1–A4).

The generator is deterministic: it cites only recordings whose *indexed* events satisfy the
applied filters, and every sentence restates an evidence event (class + time span) — A1.
Nothing matched → ``evidence: []`` with the filters applied (A2, A4). No cause, intent or
danger is ever stated (A3, same G3 lexicon as captions). `unsupported_claims` re-reads the
answer text independently and reports any class/time claim not backed by evidence.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.retrieval.relevance import satisfied
from ml.retrieval.temporal import PREDICATES

MAX_CITED = 3
TEXT = {
    "en": {"none": "No indexed recording satisfies the applied filters.",
           "count": "{n} of the top {k} results satisfy the filters.",
           "cite": "In {rid}, {items}.", "item": "{name} at {on}–{off} s", "join": ", then "},
    "vi": {"none": "Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.",
           "count": "{n} trong {k} kết quả đầu thoả bộ lọc.",
           "cite": "Trong {rid}, {items}.", "item": "{name} ở {on}–{off} giây",
           "join": ", sau đó "},
}
_SPAN = re.compile(r"(\d+[.,]\d)–(\d+[.,]\d) (?:s|giây)")


def supporting_events(events: Sequence[Mapping[str, Any]], filters: Mapping[str, Any]
                      ) -> list[Mapping[str, Any]] | None:
    """Events that make `filters` true for one recording, or None if they are not."""
    if not satisfied(events, filters):
        return None
    ordered = sorted(events, key=lambda e: (e["onset_s"], e["event_id"]))
    support: list[Mapping[str, Any]] = []
    for class_id in filters.get("classes_all", ()):
        support.append(next(e for e in ordered if e["class_id"] == class_id))
    if "temporal" in filters:
        rule = filters["temporal"]
        holds = PREDICATES[rule["predicate"]].holds
        support += next([a, b] for a in ordered if a["class_id"] == rule["a"]
                        for b in ordered if b["class_id"] == rule["b"]
                        and holds(a, b, float(rule["tolerance_s"])))
    if "duration" in filters:
        rule = filters["duration"]
        support.append(next(e for e in ordered if e["class_id"] == rule["class_id"]
                            and e["offset_s"] - e["onset_s"] > float(rule["min_s"])))
    unique = {e["event_id"]: e for e in support}
    return sorted(unique.values(), key=lambda e: (e["onset_s"], e["event_id"]))


def _seconds(value: float, language: str) -> str:
    text = f"{value:.1f}"
    return text.replace(".", ",") if language == "vi" else text


def answer(question: str, filters: Mapping[str, Any], mode: str, ranked: Sequence[str],
           events: Mapping[str, Sequence[Mapping[str, Any]]], language: str,
           name: Callable[[str], str], k: int) -> dict[str, Any]:
    """Retrieval result (contracts/retrieval_result.schema.json) for one query."""
    words = TEXT[language]
    matched = [(rid, s) for rid in ranked
               if (s := supporting_events(events.get(rid, []), filters))]
    evidence = [{"recording_id": rid, "event_id": int(e["event_id"]), "class_id": e["class_id"],
                 "onset_s": float(e["onset_s"]), "offset_s": float(e["offset_s"])}
                for rid, support in matched[:MAX_CITED] for e in support]
    sentences = ([words["count"].format(n=len(matched), k=len(ranked))] if matched
                 else [words["none"]])
    for rid, support in matched[:MAX_CITED]:
        items = words["join"].join(words["item"].format(
            name=name(e["class_id"]), on=_seconds(e["onset_s"], language),
            off=_seconds(e["offset_s"], language)) for e in support)
        sentences.append(words["cite"].format(rid=rid, items=items))
    return {"question": question, "answer": " ".join(sentences), "evidence": evidence,
            "filters_applied": {"mode": mode, "hard_filters": dict(filters), "k": k,
                                "language": language},
            "documents": [{"recording_id": rid, "text": "", "score": float(len(ranked) - i)}
                          for i, rid in enumerate(ranked)]}


def unsupported_claims(result: Mapping[str, Any], lexicon: CaptionLexicon) -> list[str]:
    """Class/time claims in the answer text with no matching evidence item, plus G3 terms.

    Each time span is attributed to the last class mention between it and the previous span
    — class names may contain commas ("quạ, mòng biển…"), so text is never split on commas.
    A span with no recognisable class is itself reported.
    """
    backed = {(e["recording_id"], e["class_id"], round(e["onset_s"], 1), round(e["offset_s"], 1))
              for e in result["evidence"]}
    problems = [f"G3:{term}" for term in lexicon.forbidden_terms(result["answer"])]
    for segment in re.split(r"(?=\b(?:In|Trong) (?:datased|datasec|upload):)", result["answer"]):
        rid = re.match(r"(?:In|Trong) ((?:datased|datasec|upload):[^,]+),", segment)
        if not rid:
            continue
        cursor = rid.end()
        for span in _SPAN.finditer(segment):
            classes = [m.class_id for m in lexicon.mentions(segment[cursor:span.start()])
                       if m.class_id]
            cursor = span.end()
            on, off = (round(float(v.replace(",", ".")), 1) for v in span.groups())
            claim = (rid.group(1), classes[-1] if classes else None, on, off)
            if claim not in backed:
                problems.append(f"{claim[0]}:{claim[1]}:{on}-{off}")
    return problems
