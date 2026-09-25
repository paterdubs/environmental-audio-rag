"""Class mention and G3 forbidden-term lexicons.

A mention resolves to a SET of candidate classes: one class for a class or
specific phrase, several for an ambiguous family phrase ("aircraft"), none for
an out-of-taxonomy source ("wind"). The extension vocabulary lives in
``ml/configs/caption_lexicon.yaml`` (ADR-0022 §3); taxonomy labels are always
included so the template captioner's phrasing is recognised exactly.

Language is a property of a lexicon (ADR-0025). English keeps its original matching
(ASCII boundaries, diacritics folded) so the frozen RQ2 hash is unchanged. Vietnamese
lives in its own file and matches with diacritics preserved and Unicode word
boundaries: folding diacritics would make "tới phạm vi" hit the forbidden "tội phạm".
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml

from ml.taxonomy import Taxonomy, load_taxonomy, normalize_text

DEFAULT_LEXICON_CONFIG = Path(__file__).resolve().parents[2] / "ml/configs/caption_lexicon.yaml"
VI_LEXICON_CONFIG = Path(__file__).resolve().parents[2] / "ml/configs/caption_lexicon_vi.yaml"
KINDS = ("class", "specific", "family", "out_of_taxonomy")
LANGUAGES = ("en", "vi")
_BOUNDARY = {"en": "[a-z0-9]", "vi": r"\w"}

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
    class_ids: frozenset[str]
    start: int
    end: int
    phrase: str
    kind: str = "class"

    @property
    def class_id(self) -> str | None:
        """The single class of an unambiguous mention, else ``None``."""
        return next(iter(self.class_ids)) if len(self.class_ids) == 1 else None


@dataclass(frozen=True)
class LexiconEntry:
    phrase: str
    class_ids: frozenset[str]
    kind: str


def _fold(term: str) -> str:
    """NFC + lower case; identity on the ASCII English vocabulary (hash-stable)."""
    return unicodedata.normalize("NFC", term).lower()


def _pattern(term: str, language: str = "en") -> re.Pattern[str]:
    boundary = _BOUNDARY[language]
    return re.compile(f"(?<!{boundary})" + re.escape(term) + f"(?!{boundary})", re.I)


def _matches(text: str, terms: Iterable[str], language: str = "en") -> tuple[str, ...]:
    normalized = normalize_text(text).replace("_", " ") if language == "en" else _fold(text)
    return tuple(sorted(t for t in terms if _pattern(t, language).search(normalized)))


class CaptionLexicon:
    def __init__(
        self,
        taxonomy: Taxonomy,
        phrases: dict[str, tuple[str, ...]],
        entries: Iterable[LexiconEntry] = (),
        context_terms: Iterable[str] = (),
        version: str = "caption-lexicon-v1",
        *,
        language: str = "en",
        forbidden: Iterable[str] = FORBIDDEN_TERMS,
        canonical: dict[str, str] | None = None,
    ):
        if language not in LANGUAGES:
            raise ValueError(f"unsupported lexicon language: {language!r}")
        self.taxonomy = taxonomy
        self.phrases = phrases
        self.version = version
        self.language = language
        self.canonical = dict(canonical or {})
        self.forbidden_vocabulary = frozenset(_fold(term) for term in forbidden)
        self.context_vocabulary = frozenset(_fold(term) for term in context_terms)
        merged: dict[str, LexiconEntry] = {}
        for class_id, values in phrases.items():
            for phrase in values:
                merged.setdefault(phrase.lower(), LexiconEntry(phrase.lower(),
                                                               frozenset({class_id}), "class"))
        for entry in entries:
            if entry.kind not in KINDS:
                raise ValueError(f"unknown lexicon kind: {entry.kind}")
            unknown = entry.class_ids - set(taxonomy.class_ids)
            if unknown:
                raise ValueError(f"lexicon phrase {entry.phrase!r} maps to unknown {unknown}")
            existing = merged.get(entry.phrase)
            if existing is not None and existing != entry:
                raise ValueError(f"lexicon phrase {entry.phrase!r} defined twice differently")
            merged[entry.phrase] = entry
        self.entries = tuple(sorted(merged.values(), key=lambda e: (-len(e.phrase), e.phrase)))
        self._patterns = tuple((entry, _pattern(entry.phrase, language))
                               for entry in self.entries)

    @classmethod
    def from_taxonomy(
        cls, taxonomy: Taxonomy | Path, config: Path | None = DEFAULT_LEXICON_CONFIG
    ) -> CaptionLexicon:
        if isinstance(taxonomy, Path):
            taxonomy = load_taxonomy(taxonomy)
        phrases: dict[str, tuple[str, ...]] = {}
        for item in taxonomy.classes:
            variants = [item.source_label.lower(), item.class_id.replace("_", " ")]
            if item.class_id == "sirens_and_alarms":
                variants.append("siren- or alarm-like sound")
            if item.class_id == "thunder_fireworks_gunshot":
                variants.append("impulsive sound resembling thunder, fireworks, or a gunshot")
            phrases[item.class_id] = tuple(dict.fromkeys(variants))
        if config is None:
            return cls(taxonomy, phrases)
        raw = yaml.safe_load(config.read_text(encoding="utf-8"))
        language = raw.get("language", "en")
        if language != "en":
            phrases = {}  # taxonomy labels are English; other languages name classes via config
        canonical = {cid: _fold(values[0])
                     for cid, values in (raw.get("class") or {}).items() if values}
        return cls(taxonomy, phrases, _entries_from_config(raw),
                   raw.get("context_terms", ()), raw["version"], language=language,
                   forbidden=raw.get("forbidden_terms") or FORBIDDEN_TERMS, canonical=canonical)

    def sha256(self) -> str:
        """Fingerprint of everything that decides a mention, a G3 hit or a context hit.

        RQ2 test captions may only be scored against a lexicon frozen before
        they were generated (ADR-0022); this hash is what gets frozen.
        """
        content = {
            "version": self.version,
            "entries": [[e.phrase, sorted(e.class_ids), e.kind] for e in self.entries],
            "forbidden": sorted(self.forbidden_vocabulary),
            "context": sorted(self.context_vocabulary),
        }
        if self.language != "en":  # English payload pinned by ADR-0022 §4 — keep it unchanged
            content |= {"language": self.language, "canonical": self.canonical}
        payload = json.dumps(content, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def canonical_phrase(self, class_id: str) -> str:
        """How a template in this language names `class_id` (first config phrase)."""
        try:
            return self.canonical[class_id]
        except KeyError as exc:
            raise ValueError(f"{self.language} lexicon has no phrase for {class_id}") from exc

    def mentions(self, text: str) -> tuple[Mention, ...]:
        if self.language != "en" and unicodedata.normalize("NFC", text) != text:
            # NFD text would silently match nothing; spans must index the caller's text.
            raise ValueError("non-English caption text must be NFC-normalised")
        found: list[Mention] = []
        occupied: list[tuple[int, int]] = []
        for entry, pattern in self._patterns:
            for match in pattern.finditer(text):
                if any(match.start() < end and start < match.end() for start, end in occupied):
                    continue
                found.append(
                    Mention(entry.class_ids, match.start(), match.end(), entry.phrase, entry.kind)
                )
                occupied.append((match.start(), match.end()))
        return tuple(sorted(found, key=lambda item: (item.start, item.end)))

    def forbidden_terms(self, text: str) -> tuple[str, ...]:
        return _matches(text, self.forbidden_vocabulary, self.language)

    def context_terms(self, text: str) -> tuple[str, ...]:
        return _matches(text, self.context_vocabulary, self.language)

    def assert_safe(self, text: str) -> None:
        terms = self.forbidden_terms(text)
        if terms:
            raise ForbiddenTermError("G3 forbidden terms: " + ", ".join(terms))


def _entries_from_config(raw: dict) -> list[LexiconEntry]:
    entries: list[LexiconEntry] = []
    for kind in ("class", "specific"):
        for class_id, phrases in (raw.get(kind) or {}).items():
            entries += [LexiconEntry(_fold(p), frozenset({class_id}), kind) for p in phrases]
    for family in raw.get("families") or ():
        members = frozenset(family["classes"])
        if len(members) < 2:
            raise ValueError("a lexicon family needs at least two classes")
        entries += [LexiconEntry(_fold(p), members, "family") for p in family["phrases"]]
    entries += [
        LexiconEntry(_fold(p), frozenset(), "out_of_taxonomy")
        for p in raw.get("out_of_taxonomy") or ()
    ]
    return entries
