"""Class mention and G3 forbidden-term lexicons."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ml.taxonomy import Taxonomy, load_taxonomy, normalize_text

FORBIDDEN_TERMS = frozenset(
    {
        "emergency",
        "crime",
        "criminal",
        "accident",
        "intruder",
        "danger",
        "dangerous",
        "threat",
        "threatening",
        "attack",
        "attacker",
        "victim",
        "police",
        "ambulance",
        "fire truck",
        "rescue",
        "intentional",
        "illegal",
        "trespasser",
        "weapon",
        "warning",
        "risk",
        "hazard",
    }
)


class ForbiddenTermError(ValueError):
    """Raised when generated text violates G3."""


@dataclass(frozen=True)
class Mention:
    class_id: str
    start: int
    end: int
    phrase: str


class CaptionLexicon:
    def __init__(self, taxonomy: Taxonomy, phrases: dict[str, tuple[str, ...]]):
        self.taxonomy = taxonomy
        self.phrases = phrases
        entries = [(phrase, class_id) for class_id, values in phrases.items() for phrase in values]
        entries.sort(key=lambda pair: len(pair[0]), reverse=True)
        self._patterns = tuple(
            (
                class_id,
                phrase,
                re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", re.I),
            )
            for phrase, class_id in entries
        )

    @classmethod
    def from_taxonomy(cls, taxonomy: Taxonomy | Path) -> CaptionLexicon:
        if isinstance(taxonomy, Path):
            taxonomy = load_taxonomy(taxonomy)
        phrases: dict[str, tuple[str, ...]] = {}
        for item in taxonomy.classes:
            source = item.source_label.lower()
            variants = [source, item.class_id.replace("_", " ")]
            if item.class_id == "sirens_and_alarms":
                variants.append("siren- or alarm-like sound")
            if item.class_id == "thunder_fireworks_gunshot":
                variants.append("impulsive sound resembling thunder, fireworks, or a gunshot")
            phrases[item.class_id] = tuple(dict.fromkeys(variants))
        return cls(taxonomy, phrases)

    def mentions(self, text: str) -> tuple[Mention, ...]:
        found: list[Mention] = []
        occupied: list[tuple[int, int]] = []
        for class_id, phrase, pattern in self._patterns:
            for match in pattern.finditer(text):
                if any(match.start() < end and start < match.end() for start, end in occupied):
                    continue
                found.append(Mention(class_id, match.start(), match.end(), phrase))
                occupied.append((match.start(), match.end()))
        return tuple(sorted(found, key=lambda item: (item.start, item.end)))

    @staticmethod
    def forbidden_terms(text: str) -> tuple[str, ...]:
        normalized = normalize_text(text).replace("_", " ")
        return tuple(
            sorted(
                term
                for term in FORBIDDEN_TERMS
                if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", normalized)
            )
        )

    def assert_safe(self, text: str) -> None:
        terms = self.forbidden_terms(text)
        if terms:
            raise ForbiddenTermError("G3 forbidden terms: " + ", ".join(terms))
