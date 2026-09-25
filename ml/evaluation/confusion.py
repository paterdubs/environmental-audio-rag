"""Class substitutions between reference and estimated events (taxonomy.md §8, W4 4.6).

A *substitution* a→b is one reference event of class ``a`` that the system missed (no
overlapping estimate of ``a``) overlapped by an estimate of class ``b`` that is itself a false
positive (no overlapping reference of ``b``). Requiring both sides keeps polyphony out of the
count: an estimate of ``b`` overlapping a reference ``a`` while a real ``b`` also sounds is a
correct detection, not a confusion.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

Event = Mapping[str, Any]


def _label(event: Event) -> str:
    return str(event.get("event_label", event.get("class_id")))


def _overlap(left: Event, right: Event) -> float:
    return max(0.0, min(float(left["offset"]), float(right["offset"]))
               - max(float(left["onset"]), float(right["onset"])))


def _covered(event: Event, others: Sequence[Event]) -> bool:
    return any(_label(o) == _label(event) and _overlap(event, o) > 0 for o in others)


def substitutions(reference: Mapping[str, Sequence[Event]],
                  estimate: Mapping[str, Sequence[Event]]
                  ) -> tuple[Counter[tuple[str, str]], Counter[tuple[str, str]]]:
    """Counts and overlap seconds of substitutions (reference class, estimated class)."""
    counts: Counter[tuple[str, str]] = Counter()
    seconds: Counter[tuple[str, str]] = Counter()
    for rid in sorted(set(reference) | set(estimate)):
        refs, preds = reference.get(rid, []), estimate.get(rid, [])
        missed = [r for r in refs if not _covered(r, preds)]
        false_pos = [p for p in preds if not _covered(p, refs)]
        for ref in missed:
            for pred in false_pos:
                shared = _overlap(ref, pred)
                if shared > 0 and _label(ref) != _label(pred):
                    counts[(_label(ref), _label(pred))] += 1
                    seconds[(_label(ref), _label(pred))] += shared
    return counts, seconds


def unordered(counts: Mapping[tuple[str, str], float]) -> Counter[tuple[str, str]]:
    """Fold a→b and b→a into one sorted pair."""
    folded: Counter[tuple[str, str]] = Counter()
    for (a, b), value in counts.items():
        folded[tuple(sorted((a, b)))] += value
    return folded
