"""Transparent event-level error accounting for SED diagnostics."""

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EventError:
    recording_id: str
    error_type: str
    reference_label: str | None
    estimated_label: str | None
    reference_index: int | None
    estimated_index: int | None


def _overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        float(left["onset"]) < float(right["offset"])
        and float(right["onset"]) < float(left["offset"])
    )


def classify_event_errors(
    reference: dict[str, list[dict[str, Any]]],
    estimate: dict[str, list[dict[str, Any]]],
) -> tuple[list[EventError], dict[str, Counter[str]]]:
    """Classify insertion, deletion, fragmentation, merging and confusion.

    Matching is intentionally descriptive (temporal overlap plus identical
    label), not a replacement for sed_eval.  Use the output to inspect model
    behavior after the standard metric has been computed.
    """
    errors: list[EventError] = []
    summary: dict[str, Counter[str]] = {}
    for recording_id in sorted(set(reference) | set(estimate)):
        refs = reference.get(recording_id, [])
        preds = estimate.get(recording_id, [])
        counts = summary.setdefault(recording_id, Counter())
        same_matches: dict[int, list[int]] = {}
        for ref_index, ref in enumerate(refs):
            matches = [
                pred_index
                for pred_index, pred in enumerate(preds)
                if pred.get("event_label", pred.get("class_id"))
                == ref.get("event_label", ref.get("class_id"))
                and _overlaps(ref, pred)
            ]
            same_matches[ref_index] = matches
            if not matches:
                errors.append(
                    EventError(
                        recording_id, "deletion", ref.get("event_label"), None, ref_index, None
                    )
                )
                counts["deletion"] += 1
            elif len(matches) > 1:
                counts["fragmentation"] += 1
                errors.append(
                    EventError(
                        recording_id,
                        "fragmentation",
                        ref.get("event_label"),
                        ref.get("event_label"),
                        ref_index,
                        matches[0],
                    )
                )
        matched_predictions = {index for matches in same_matches.values() for index in matches}
        for pred_index, pred in enumerate(preds):
            if pred_index not in matched_predictions:
                overlapping_refs = [index for index, ref in enumerate(refs) if _overlaps(ref, pred)]
                if overlapping_refs:
                    error_type = "confusion"
                    ref_index = overlapping_refs[0]
                    ref_label = refs[ref_index].get("event_label", refs[ref_index].get("class_id"))
                else:
                    error_type = "insertion"
                    ref_index, ref_label = None, None
                errors.append(
                    EventError(
                        recording_id,
                        error_type,
                        ref_label,
                        pred.get("event_label", pred.get("class_id")),
                        ref_index,
                        pred_index,
                    )
                )
                counts[error_type] += 1
        for pred_index, pred in enumerate(preds):
            overlapping_same = [
                index for index, ref in enumerate(refs)
                if _overlaps(ref, pred)
                and ref.get("event_label", ref.get("class_id"))
                == pred.get("event_label", pred.get("class_id"))
            ]
            if len(overlapping_same) > 1:
                counts["merging"] += 1
                errors.append(
                    EventError(
                        recording_id,
                        "merging",
                        refs[overlapping_same[0]].get("event_label"),
                        pred.get("event_label"),
                        overlapping_same[0],
                        pred_index,
                    )
                )
    return errors, summary
