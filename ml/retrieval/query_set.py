"""Versioned, deterministic query-set fixture for retrieval evaluation.

Classes come from the caller (the taxonomy's polyphonic class ids), never from a
hard-coded list: a name outside the taxonomy filters to an empty set without any
error (`relevance.validate_query_classes` checks a loaded set against the taxonomy).
Relevance is declared as ground truth — `ml.retrieval.relevance` computes it
from annotations, not from the filter being evaluated (evaluation_protocol §9.1).
"""

from collections.abc import Sequence
from math import gcd
from typing import Any

from ml.retrieval.relevance import GROUND_TRUTH

PREDICATES = ("before", "after", "overlaps", "within")
PHRASES = {"before": "before", "after": "after", "overlaps": "overlapping with",
           "within": "during"}


def _stride(n_items: int, size: int) -> int:
    """Smallest step >= n_items // size that is coprime with n_items (full cycle)."""
    step = max(1, n_items // size)
    while gcd(step, n_items) != 1:
        step += 1
    return step


def build_query_set(class_ids: Sequence[str], size: int = 100) -> list[dict[str, Any]]:
    """Create temporal queries over ordered class pairs without consulting any result."""
    classes = list(dict.fromkeys(class_ids))
    pairs = [(a, b) for a in classes for b in classes if a != b]
    if size < 1 or not pairs or size > len(pairs):
        raise ValueError(f"need 1 <= size <= {len(pairs)} distinct class pairs")
    step = _stride(len(pairs), size)
    queries = []
    for index in range(size):
        a, b = pairs[(index * step) % len(pairs)]
        predicate = PREDICATES[index % len(PREDICATES)]
        queries.append({
            "query_id": f"q-{index + 1:03d}",
            "question": (f"Which recordings have {a.replace('_', ' ')} "
                         f"{PHRASES[predicate]} {b.replace('_', ' ')}?"),
            "filters": {"temporal": {"predicate": predicate, "a": a, "b": b,
                                     "tolerance_s": 0.0}},
            "relevance": {"type": "recording_ids", "source": GROUND_TRUTH},
        })
    return queries
