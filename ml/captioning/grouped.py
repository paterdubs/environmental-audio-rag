"""Served captioner (ADR-0050): one clause per class, event counts, hedging from SED scores.

`TemplateCaptioner` stays frozen for RQ2; this one only changes how a timeline is phrased, never
which classes are named, so G1–G3 hold by the same construction (every clause cites the first event
of its class, and the text passes `assert_safe`).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .lexicon import CaptionLexicon
from .template import SENTENCES, TemplateCaptioner

# Notification style (user, 24/11): one line per class, a label then the facts. The label never
# says "warning"/"cảnh báo" — both are G3 terms (no danger claims, ADR-0001).
CLAUSES = {
    "en": {"one": "{label}: {phrase}, {onset}–{offset} s.",
           "many": "{label}: {phrase}, {n} times, {onset}–{offset} s.",
           "label": ("Detected", "Possible (low confidence)")},
    "vi": {"one": "{label}: {phrase}, {onset}–{offset} giây.",
           "many": "{label}: {phrase}, {n} lần, {onset}–{offset} giây.",
           "label": ("Phát hiện", "Có thể có (độ tin cậy thấp)")},
}


class GroupedTemplateCaptioner(TemplateCaptioner):
    def __init__(self, lexicon: CaptionLexicon, hedge_threshold: float | None = None,
                 version: str = "caption-grouped-v1.0"):
        super().__init__(lexicon, version)
        self.hedge_threshold = hedge_threshold

    def hedged(self, events: list[dict[str, Any]]) -> bool:
        """A class is hedged when even its most confident event scores below the threshold."""
        if self.hedge_threshold is None:
            return False
        scores = [e["score"] for e in events if e.get("score") is not None]
        return bool(scores) and max(scores) < self.hedge_threshold

    def clauses(self, timeline: dict[str, Any]) -> list[dict[str, Any]]:
        """Per class, in order of first onset: events, first event and hedge flag."""
        by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in sorted(timeline["events"], key=lambda e: (e["onset_s"], e["event_id"])):
            by_class[event["class_id"]].append(event)
        return [{"class_id": c, "events": ev, "first": ev[0], "hedged": self.hedged(ev)}
                for c, ev in by_class.items()]

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != self.lexicon.language:
            raise ValueError(f"caption language {language!r} needs a {language!r} lexicon, "
                             f"got {self.lexicon.language!r}")
        words = CLAUSES[language]
        parts: list[str] = []
        evidence: list[dict[str, Any]] = []
        for clause in self.clauses(timeline):
            events = clause["events"]
            text = words["one" if len(events) == 1 else "many"].format(
                label=words["label"][clause["hedged"]], phrase=self._phrase(clause["class_id"]),
                n=len(events),
                onset=self._seconds(events[0]["onset_s"]),
                offset=self._seconds(max(e["offset_s"] for e in events)))
            start = sum(len(part) for part in parts) + len(parts)
            parts.append(text)
            evidence.append({"event_id": clause["first"]["event_id"],
                             "mention_span": [start, start + len(text)]})
        text = " ".join(parts) if parts else SENTENCES[language][1]
        self.lexicon.assert_safe(text)
        return {"recording_id": timeline["recording_id"], "language": language, "text": text,
                "captioner_version": self.version, "grounding_mode": "constrained",
                "evidence": evidence}
