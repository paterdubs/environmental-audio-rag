"""Versioned, deterministic query-set fixture for retrieval evaluation."""

from itertools import cycle
from typing import Any

CLASSES = ("birds", "bells", "car", "voices", "music", "horn", "dog")
PREDICATES = ("before", "after", "overlaps", "within")


def build_query_set(size: int = 100) -> list[dict[str, Any]]:
    """Create queries and oracle filters without consulting retrieval results."""
    if size < 1:
        raise ValueError("size must be positive")
    class_pairs = cycle(
        (CLASSES[i % len(CLASSES)], CLASSES[(i + 1) % len(CLASSES)])
        for i in range(len(CLASSES))
    )
    queries = []
    for index in range(size):
        a, b = next(class_pairs)
        predicate = PREDICATES[index % len(PREDICATES)]
        queries.append({
            "query_id": f"q-{index + 1:03d}",
            "question": f"Which recordings have {a} {predicate} {b}?",
            "filters": {"temporal": {"predicate": predicate, "a": a, "b": b, "tolerance_s": 0.0}},
            "relevance": {"type": "recording_ids", "source": "temporal_filter"},
        })
    return queries
