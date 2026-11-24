"""Backfill (ADR-0049): hard-filtered results first, then semantic results that do not satisfy
the filters, cut at k. Tier 1 keeps the exactness guarantee of hybrid; tier 2 is labelled as near
matches so an answer never states them as satisfying the filters."""

from __future__ import annotations

from collections.abc import Sequence


def backfill(hybrid: Sequence[str], vector: Sequence[str], k: int) -> list[str]:
    """Hybrid results first, then vector results not already present, cut at k."""
    seen = set(hybrid)
    return (list(hybrid) + [r for r in vector if r not in seen])[:k]
