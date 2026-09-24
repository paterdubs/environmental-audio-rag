"""Reference-free grounding metrics for captions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from ml.captioning.lexicon import CaptionLexicon


@dataclass(frozen=True)
class GroundingMetrics:
    event_precision: float
    event_recall: float
    hallucination_rate: float
    omission_rate: float
    temporal_order_accuracy: float
    evidence_coverage: float
    forbidden_term_rate: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def evaluate_grounding(
    timeline: dict[str, Any], caption: dict[str, Any], lexicon: CaptionLexicon
) -> GroundingMetrics:
    mentions = lexicon.mentions(caption.get("text", ""))
    mentioned_classes = [mention.class_id for mention in mentions]
    timeline_classes = [event["class_id"] for event in timeline["events"]]
    supported = [class_id for class_id in mentioned_classes if class_id in timeline_classes]
    precision = len(supported) / len(mentioned_classes) if mentioned_classes else 1.0
    recall = len(set(supported)) / len(set(timeline_classes)) if timeline_classes else 1.0
    event_ids = {event["event_id"] for event in timeline["events"]}
    evidence = caption.get("evidence", [])
    coverage = (
        sum(item.get("event_id") in event_ids for item in evidence) / len(mentions)
        if mentions
        else 1.0
    )
    order = _temporal_order(timeline, mentions)
    forbidden = 1.0 if lexicon.forbidden_terms(caption.get("text", "")) else 0.0
    return GroundingMetrics(
        precision, recall, 1.0 - precision, 1.0 - recall, order, coverage, forbidden
    )


def _temporal_order(timeline: dict[str, Any], mentions: tuple[Any, ...]) -> float:
    """Compare text mention order against event onset order.

    A plain ``{class_id: onset}`` dict silently keeps only the LAST event's
    onset when a class occurs more than once in the timeline — common in real
    polyphonic predictions, never exercised by the single-event fixtures this
    was written against. Each successive text mention of a class instead
    claims the next-earliest still-unclaimed onset of that class, so repeated
    classes are matched to distinct events rather than collapsed to one.
    """
    if len(mentions) < 2:
        return 1.0
    onsets_by_class: dict[str, list[float]] = defaultdict(list)
    for event in sorted(timeline["events"], key=lambda item: item["onset_s"]):
        onsets_by_class[event["class_id"]].append(event["onset_s"])
    claimed: dict[str, int] = defaultdict(int)
    values: list[float | None] = []
    for mention in mentions:
        pool = onsets_by_class.get(mention.class_id, [])
        index = claimed[mention.class_id]
        values.append(pool[index] if index < len(pool) else None)
        claimed[mention.class_id] += 1
    if any(value is None for value in values):
        return 0.0
    pairs = [(values[i], values[j]) for i in range(len(values)) for j in range(i + 1, len(values))]
    return sum(left <= right for left, right in pairs) / len(pairs)
