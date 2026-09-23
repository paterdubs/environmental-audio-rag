"""SQL temporal predicates used by structured retrieval."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalPredicate:
    name: str
    condition: str

    def sql(self) -> str:
        return f"a.recording_id = b.recording_id AND {self.condition}"


PREDICATES = {
    "before": TemporalPredicate("before", "a.offset_s <= b.onset_s + :tolerance_s"),
    "after": TemporalPredicate("after", "a.onset_s >= b.offset_s - :tolerance_s"),
    "overlaps": TemporalPredicate(
        "overlaps", "a.onset_s < b.offset_s AND b.onset_s < a.offset_s"
    ),
    "within": TemporalPredicate(
        "within", "a.onset_s >= b.onset_s AND a.offset_s <= b.offset_s"
    ),
}


def temporal_query(predicate: str) -> str:
    """Return parameterized PostgreSQL SQL for a class-pair self-join."""
    try:
        selected = PREDICATES[predicate]
    except KeyError as exc:
        raise ValueError(f"unknown temporal predicate: {predicate}") from exc
    return (
        "SELECT DISTINCT a.recording_id FROM events a JOIN events b ON "
        f"{selected.sql()} WHERE a.class_id = :class_a AND b.class_id = :class_b "
        "AND a.provenance = 'prediction' AND b.provenance = 'prediction'"
    )
