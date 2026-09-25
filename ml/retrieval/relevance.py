"""Relevance judgments from ground-truth events (evaluation_protocol §9.1).

Retrieval only ever sees *predicted* events. A query's relevant set is computed here
from *annotations*, with the same predicate semantics as the SQL filter
(`ml.retrieval.temporal`), so Recall@k/MRR measure the whole pipeline (SED errors
included) instead of the filter agreeing with itself. Filter exactness (§9.2) is the
metric that is computed against the indexed predictions, not this module.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ml.retrieval.temporal import PREDICATES, Event

GROUND_TRUTH = "ground_truth"
DATASET_PREFIX = "datased:"


def query_classes(query: Mapping[str, Any]) -> tuple[str, str]:
    temporal = query["filters"]["temporal"]
    return str(temporal["a"]), str(temporal["b"])


def validate_query_classes(queries: Iterable[Mapping[str, Any]],
                           class_ids: Sequence[str]) -> None:
    """Refuse unknown class ids: they would filter to an empty set without any error."""
    known = set(class_ids)
    unknown = sorted({c for q in queries for c in query_classes(q)} - known)
    if unknown:
        raise ValueError(f"query set uses class ids outside the taxonomy: {unknown}")


def load_ground_truth(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Annotation CSV → events per canonical recording id (`datased:S-0001`)."""
    events: dict[str, list[dict[str, Any]]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            events.setdefault(DATASET_PREFIX + row["recording_id"], []).append({
                "class_id": row["class_id"], "onset_s": float(row["onset_s"]),
                "offset_s": float(row["offset_s"]),
            })
    return events


def _satisfied(events: Sequence[Event], query: Mapping[str, Any]) -> bool:
    temporal = query["filters"]["temporal"]
    holds = PREDICATES[temporal["predicate"]].holds
    tolerance = float(temporal["tolerance_s"])
    a_class, b_class = query_classes(query)
    firsts = [e for e in events if e["class_id"] == a_class]
    seconds = [e for e in events if e["class_id"] == b_class]
    return any(holds(a, b, tolerance) for a in firsts for b in seconds)


def relevant_recordings(query: Mapping[str, Any],
                        ground_truth: Mapping[str, Sequence[Event]]) -> list[str]:
    """Recordings whose annotated events satisfy the query's filters, sorted."""
    source = query["relevance"]["source"]
    if source != GROUND_TRUTH:
        raise ValueError(f"relevance must come from ground truth, got {source!r}")
    return sorted(rid for rid, events in ground_truth.items() if _satisfied(events, query))
