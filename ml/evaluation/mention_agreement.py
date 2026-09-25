"""Agreement between the lexicon mention extractor and a human annotator (C2 validity).

The grounding metrics (C2) are only as good as the extractor that turns caption text
into class mentions. A human reads captions *blind* (no timeline, no extractor output)
and lists the sound sources each caption asserts; this module compares both readings.

A mention is a *unit*: the set of classes it may refer to. A plain class is a singleton;
an ambiguous word ("aircraft") is written ``jet_aircrafts|propeller_aircrafts`` by the
annotator and matches the extractor's family mention covering exactly those classes.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from ml.captioning.lexicon import CaptionLexicon
from ml.evaluation.grounding import collapse_enumerations

NONE_MARK = "none"
Unit = frozenset[str]


def parse_units(cell: str, known: Iterable[str]) -> set[Unit]:
    """``"birds; jet_aircrafts|propeller_aircrafts"`` → {{birds}, {jet, propeller}}."""
    value = cell.strip()
    if not value:
        raise ValueError("empty cell — write 'none' when the caption names no source")
    if value.lower() == NONE_MARK:
        return set()
    known_set = set(known)
    units = set()
    for part in value.split(";"):
        unit = frozenset(c.strip() for c in part.split("|") if c.strip())
        unknown = unit - known_set
        if not unit or unknown:
            raise ValueError(f"unknown class id(s) {sorted(unknown)} in {cell!r}")
        units.add(unit)
    return units


def extractor_units(text: str, lexicon: CaptionLexicon) -> set[Unit]:
    """The extractor's reading of a caption, in the same unit form (taxonomy mentions only)."""
    mentions = collapse_enumerations(text, lexicon.mentions(text))
    return {frozenset(m.class_ids) for m in mentions if m.class_ids}


def extractor_outside(text: str, lexicon: CaptionLexicon) -> bool:
    """Whether the extractor saw an out-of-taxonomy source."""
    return any(not m.class_ids for m in lexicon.mentions(text))


@dataclass(frozen=True)
class Agreement:
    true_positive: int
    false_positive: int
    false_negative: int
    exact_captions: int
    n_captions: int

    @property
    def precision(self) -> float:
        found = self.true_positive + self.false_positive
        return self.true_positive / found if found else 1.0

    @property
    def recall(self) -> float:
        wanted = self.true_positive + self.false_negative
        return self.true_positive / wanted if wanted else 1.0


def agreement(pairs: Sequence[tuple[set[Unit], set[Unit]]]) -> Agreement:
    """pairs = (extractor units, human units) per caption; unit-level counts."""
    tp = sum(len(ext & hum) for ext, hum in pairs)
    fp = sum(len(ext - hum) for ext, hum in pairs)
    fn = sum(len(hum - ext) for ext, hum in pairs)
    exact = sum(ext == hum for ext, hum in pairs)
    return Agreement(tp, fp, fn, exact, len(pairs))


def unsupported(units: set[Unit], present: set[str], outside: bool) -> bool:
    """A caption hallucinates if a unit shares no class with the timeline, or names an
    out-of-taxonomy source — the same rule as `evaluate_grounding` (ADR-0022 §3)."""
    return outside or any(not unit & present for unit in units)
