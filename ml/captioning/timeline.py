"""Canonicalize post-processed events before captioning.

The canonicalizer deliberately does not infer labels or alter scores.  Invalid
events fail fast; this keeps a bad SED output from becoming an apparently
grounded caption.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from numbers import Real
from typing import Any

from ml.taxonomy import Taxonomy


def canonicalize_timeline(
    recording_id: str,
    duration_s: float,
    events: Iterable[Mapping[str, Any]],
    taxonomy: Taxonomy,
    taxonomy_version: str | None = None,
    model_version: str = "sed-unknown",
) -> dict[str, Any]:
    """Return a validated, stable timeline dictionary.

    Events are sorted by onset, offset, class and original ID.  Existing IDs
    are retained when unique positive integers; otherwise deterministic IDs
    are assigned.  No overlap merging is performed because that is a
    post-processing decision and must remain auditable.
    """
    if not recording_id or ":" not in recording_id:
        raise ValueError("recording_id must contain a dataset prefix")
    if not isinstance(duration_s, Real) or duration_s <= 0:
        raise ValueError("duration_s must be positive")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(events, start=1):
        try:
            class_id = str(raw["class_id"])
            onset = float(raw["onset_s"])
            offset = float(raw["offset_s"])
            score = float(raw["score"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid event at index {index}") from exc
        if class_id not in taxonomy.class_ids:
            raise ValueError(f"class_id is not in taxonomy: {class_id}")
        if not (0 <= onset < offset <= float(duration_s)):
            raise ValueError(f"invalid event bounds at index {index}")
        if not 0 <= score <= 1:
            raise ValueError(f"score must be in [0, 1] at index {index}")
        normalized.append(
            {
                "class_id": class_id,
                "onset_s": onset,
                "offset_s": offset,
                "score": score,
                "_input_id": raw.get("event_id", index),
            }
        )
    normalized.sort(
        key=lambda item: (
            item["onset_s"],
            item["offset_s"],
            item["class_id"],
            str(item["_input_id"]),
        )
    )
    ids = [item["_input_id"] for item in normalized]
    preserve = all(isinstance(value, int) and value > 0 for value in ids) and len(set(ids)) == len(
        ids
    )
    output_events = []
    for new_id, item in enumerate(normalized, start=1):
        output_events.append(
            {
                "event_id": item["_input_id"] if preserve else new_id,
                "class_id": item["class_id"],
                "onset_s": item["onset_s"],
                "offset_s": item["offset_s"],
                "score": item["score"],
            }
        )
    return {
        "recording_id": recording_id,
        "duration_s": float(duration_s),
        "taxonomy_version": taxonomy_version or taxonomy.version,
        "model_version": model_version,
        "events": output_events,
    }
