"""Deterministic baseline captioner whose evidence is explicit."""

from __future__ import annotations

from typing import Any

from .lexicon import CaptionLexicon


class TemplateCaptioner:
    def __init__(self, lexicon: CaptionLexicon, version: str = "caption-v1.0"):
        self.lexicon = lexicon
        self.version = version

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != "en":
            raise ValueError("template baseline currently supports English only")
        events = timeline["events"]
        if not events:
            text = "No target sound event was detected in this recording."
            evidence: list[dict[str, Any]] = []
        else:
            parts: list[str] = []
            evidence = []
            for event in events:
                phrase = self._phrase(event["class_id"])
                sentence = (
                    f"A {phrase} is audible from {event['onset_s']:.1f} "
                    f"to {event['offset_s']:.1f} seconds."
                )
                start = sum(len(part) for part in parts)
                if parts:
                    start += 1
                parts.append(sentence)
                evidence.append(
                    {"event_id": event["event_id"], "mention_span": [start, start + len(sentence)]}
                )
            text = " ".join(parts)
        self.lexicon.assert_safe(text)
        return {
            "recording_id": timeline["recording_id"],
            "language": language,
            "text": text,
            "captioner_version": self.version,
            "grounding_mode": "constrained",
            "evidence": evidence,
        }

    def _phrase(self, class_id: str) -> str:
        if class_id == "sirens_and_alarms":
            return "siren- or alarm-like sound"
        if class_id == "thunder_fireworks_gunshot":
            return "impulsive sound resembling thunder, fireworks, or a gunshot"
        return class_id.replace("_", " ")
