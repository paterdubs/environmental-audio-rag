"""Reference-free grounding metrics for captions (C2, SYSTEM.md §8.3).

Mentions come from ``CaptionLexicon`` and resolve to a set of candidate
classes. Ambiguity is always resolved in favour of the caption (ADR-0022 §3):
a family mention ("aircraft") counts as supported, and covers recall, when ANY
of its classes is in the timeline. The RQ2 delta against the unconstrained
branch is therefore a lower bound.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from ml.captioning.lexicon import CaptionLexicon, Mention

# Text allowed between two overlapping-class mentions for them to name ONE source:
# an enumeration ("crows, seagulls, and magpies") or a descriptor + "of"/"from"
# ("the boom of fireworks", "chirping birds", "noise from a lawn mower").
_LIST_GAP = re.compile(
    r"^[\s,;/]*(?:(?:and|or|of|from)\s+(?:(?:the|a|an)\s+)?)?[\s,;/]*$", re.I
)
_KIND_RANK = {"specific": 0, "class": 1, "family": 2}


@dataclass(frozen=True)
class GroundingMetrics:
    event_precision: float
    event_recall: float
    hallucination_rate: float
    omission_rate: float
    temporal_order_accuracy: float
    evidence_coverage: float
    forbidden_term_rate: float
    over_specific_rate: float = 0.0
    context_term_rate: float = 0.0
    n_mentions: int = 0

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def evaluate_grounding(
    timeline: dict[str, Any], caption: dict[str, Any], lexicon: CaptionLexicon
) -> GroundingMetrics:
    text = caption.get("text", "")
    mentions = collapse_enumerations(text, lexicon.mentions(text))
    timeline_classes = {event["class_id"] for event in timeline["events"]}
    supported = [m for m in mentions if m.class_ids & timeline_classes]
    precision = len(supported) / len(mentions) if mentions else 1.0
    covered = set().union(*(m.class_ids & timeline_classes for m in supported))
    recall = len(covered) / len(timeline_classes) if timeline_classes else 1.0
    event_ids = {event["event_id"] for event in timeline["events"]}
    evidence = caption.get("evidence", [])
    coverage = (
        sum(item.get("event_id") in event_ids for item in evidence) / len(mentions)
        if mentions
        else 1.0
    )
    over_specific = (
        sum(m.kind == "specific" for m in mentions) / len(mentions) if mentions else 0.0
    )
    return GroundingMetrics(
        event_precision=precision,
        event_recall=recall,
        hallucination_rate=1.0 - precision,
        omission_rate=1.0 - recall,
        temporal_order_accuracy=_temporal_order(timeline, supported, evidence),
        evidence_coverage=coverage,
        forbidden_term_rate=1.0 if lexicon.forbidden_terms(text) else 0.0,
        over_specific_rate=over_specific,
        context_term_rate=1.0 if lexicon.context_terms(text) else 0.0,
        n_mentions=len(mentions),
    )


def collapse_enumerations(text: str, mentions: tuple[Mention, ...]) -> tuple[Mention, ...]:
    """Merge adjacent mentions that name one source.

    Two neighbours merge when their candidate classes overlap and only list
    punctuation, and/or, or of/from (plus an article) separates them. "Birds
    ... Birds again later" stays two mentions; "thunder, fireworks, and
    gunshots" and "the chirping of birds" become one. The merged mention keeps
    the shared classes and the most specific kind, so over-specificity is
    still counted.
    """
    merged: list[Mention] = []
    for mention in mentions:
        previous = merged[-1] if merged else None
        shared = previous.class_ids & mention.class_ids if previous is not None else frozenset()
        if shared and _LIST_GAP.match(text[previous.end : mention.start]):
            kind = min(previous.kind, mention.kind, key=_KIND_RANK.__getitem__)
            merged[-1] = Mention(shared, previous.start, mention.end,
                                 text[previous.start : mention.end], kind)
        else:
            merged.append(mention)
    return tuple(merged)


def _temporal_order(
    timeline: dict[str, Any], mentions: list[Mention], evidence: list[dict[str, Any]]
) -> float:
    """Compare text mention order against event onset order.

    Only supported mentions take part — an unsupported one is already charged
    to hallucination. A mention covered by an evidence item (G2) takes the
    onset of the event it cites: without that, a caption that skips an earlier
    event of a class and cites a later one gets pinned to the skipped onset
    and scored out of order (found on constrained dev captions, ADR-0023).
    Other mentions claim the earliest still-unclaimed onset of their class(es)
    — never a single ``{class_id: onset}`` value, which collapses repeated
    classes. A mention left with nothing to claim (more mentions than events)
    scores the whole caption 0.
    """
    if len(mentions) < 2:
        return 1.0
    events = {event["event_id"]: event for event in timeline["events"]}
    cited = _cited_events(mentions, evidence, events)
    pools: dict[str, list[float]] = defaultdict(list)
    for event in sorted(timeline["events"], key=lambda item: item["onset_s"]):
        if event["event_id"] not in cited.values():
            pools[event["class_id"]].append(event["onset_s"])
    values: list[float | None] = []
    for index, mention in enumerate(mentions):
        if index in cited:
            values.append(events[cited[index]]["onset_s"])
            continue
        candidates = [(pools[c][0], c) for c in sorted(mention.class_ids) if pools.get(c)]
        if not candidates:
            values.append(None)
            continue
        onset, class_id = min(candidates)
        pools[class_id].pop(0)
        values.append(onset)
    if any(value is None for value in values):
        return 0.0
    pairs = [(values[i], values[j]) for i in range(len(values)) for j in range(i + 1, len(values))]
    return sum(left <= right for left, right in pairs) / len(pairs)


def _cited_events(
    mentions: list[Mention], evidence: list[dict[str, Any]], events: dict[Any, dict[str, Any]]
) -> dict[int, Any]:
    """Mention index -> event_id, for mentions whose span an evidence item covers."""
    cited: dict[int, Any] = {}
    used: set[Any] = set()
    for index, mention in enumerate(mentions):
        for item in evidence:
            event = events.get(item.get("event_id"))
            span = item.get("mention_span") or [0, 0]
            if (
                event is not None
                and item["event_id"] not in used
                and event["class_id"] in mention.class_ids
                and span[0] < mention.end
                and mention.start < span[1]
            ):
                cited[index] = item["event_id"]
                used.add(item["event_id"])
                break
    return cited
