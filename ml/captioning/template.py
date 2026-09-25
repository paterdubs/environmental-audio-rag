"""Deterministic baseline captioner whose evidence is explicit.

English is the RQ2 benchmark language; Vietnamese is the interface language
(ADR-0004, ADR-0025). The language comes from the lexicon, so a Vietnamese caption
is always checked against the Vietnamese vocabulary and G3 list.
"""

from __future__ import annotations

from typing import Any

from .lexicon import CaptionLexicon

# (sentence per event, text when no event) — the English strings are frozen: RQ2 scores
# the template on the same timelines as the LLM branches.
SENTENCES = {
    "en": ("A {phrase} is audible from {onset} to {offset} seconds.",
           "No target sound event was detected in this recording."),
    "vi": ("Có thể nghe thấy {phrase} từ {onset} đến {offset} giây.",
           "Không phát hiện sự kiện âm thanh mục tiêu nào trong bản ghi này."),
}


class TemplateCaptioner:
    def __init__(self, lexicon: CaptionLexicon, version: str = "caption-v1.0"):
        self.lexicon = lexicon
        self.version = version

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != self.lexicon.language:
            raise ValueError(f"caption language {language!r} needs a {language!r} lexicon, "
                             f"got {self.lexicon.language!r}")
        sentence, empty = SENTENCES[language]
        events = timeline["events"]
        parts: list[str] = []
        evidence: list[dict[str, Any]] = []
        for event in events:
            text = sentence.format(phrase=self._phrase(event["class_id"]),
                                   onset=self._seconds(event["onset_s"]),
                                   offset=self._seconds(event["offset_s"]))
            start = sum(len(part) for part in parts) + len(parts)
            parts.append(text)
            evidence.append({"event_id": event["event_id"],
                             "mention_span": [start, start + len(text)]})
        text = " ".join(parts) if events else empty
        self.lexicon.assert_safe(text)
        return {
            "recording_id": timeline["recording_id"],
            "language": language,
            "text": text,
            "captioner_version": self.version,
            "grounding_mode": "constrained",
            "evidence": evidence,
        }

    def _seconds(self, value: float) -> str:
        text = f"{value:.1f}"
        return text.replace(".", ",") if self.lexicon.language == "vi" else text

    def _phrase(self, class_id: str) -> str:
        if self.lexicon.language != "en":
            return self.lexicon.canonical_phrase(class_id)
        if class_id == "sirens_and_alarms":
            return "siren- or alarm-like sound"
        if class_id == "thunder_fireworks_gunshot":
            return "impulsive sound resembling thunder, fireworks, or a gunshot"
        return class_id.replace("_", " ")
