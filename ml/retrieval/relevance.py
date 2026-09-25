"""Relevance judgments from ground-truth events (evaluation_protocol §9.1).

Retrieval only ever sees *predicted* events. A query's relevant set is computed here
from *annotations*, with the same predicate semantics as the SQL filter
(`ml.retrieval.temporal`), so Recall@k/MRR measure the whole pipeline (SED errors
included) instead of the filter agreeing with itself. Filter exactness (§9.2) is the
metric that is computed against the indexed predictions, not this module.

A query's ``filters`` may combine (all must hold):

- ``classes_all``: every listed class has at least one event;
- ``temporal``: ``{predicate, a, b, tolerance_s}`` holds for some event pair;
- ``duration``: ``{class_id, min_s}`` — some event of the class lasts longer than ``min_s``.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ml.retrieval.temporal import PREDICATES, Event

GROUND_TRUTH = "ground_truth"
DATASET_PREFIX = "datased:"


def query_classes(query: Mapping[str, Any]) -> set[str]:
    filters = query["filters"]
    classes = set(filters.get("classes_all", ()))
    if "temporal" in filters:
        classes |= {str(filters["temporal"]["a"]), str(filters["temporal"]["b"])}
    if "duration" in filters:
        classes.add(str(filters["duration"]["class_id"]))
    return classes


def validate_query_classes(queries: Iterable[Mapping[str, Any]],
                           class_ids: Sequence[str]) -> None:
    """Refuse unknown class ids: they would filter to an empty set without any error."""
    unknown = sorted({c for q in queries for c in query_classes(q)} - set(class_ids))
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


def _temporal(events: Sequence[Event], temporal: Mapping[str, Any]) -> bool:
    holds = PREDICATES[temporal["predicate"]].holds
    tolerance = float(temporal["tolerance_s"])
    firsts = [e for e in events if e["class_id"] == temporal["a"]]
    seconds = [e for e in events if e["class_id"] == temporal["b"]]
    return any(holds(a, b, tolerance) for a in firsts for b in seconds)


def satisfied(events: Sequence[Event], filters: Mapping[str, Any]) -> bool:
    """Whether a recording's events satisfy every condition in `filters`."""
    if not filters:
        raise ValueError("a query needs at least one filter")
    present = {e["class_id"] for e in events}
    if not set(filters.get("classes_all", ())) <= present:
        return False
    if "temporal" in filters and not _temporal(events, filters["temporal"]):
        return False
    if "duration" in filters:
        rule = filters["duration"]
        if not any(e["class_id"] == rule["class_id"]
                   and e["offset_s"] - e["onset_s"] > float(rule["min_s"]) for e in events):
            return False
    return True


def relevant_recordings(query: Mapping[str, Any],
                        ground_truth: Mapping[str, Sequence[Event]]) -> list[str]:
    """Recordings whose annotated events satisfy the query's filters, sorted."""
    source = query["relevance"]["source"]
    if source != GROUND_TRUTH:
        raise ValueError(f"relevance must come from ground truth, got {source!r}")
    return sorted(rid for rid, events in ground_truth.items()
                  if satisfied(events, query["filters"]))
