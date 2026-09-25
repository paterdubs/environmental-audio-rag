import random
import sqlite3
from pathlib import Path

import pytest

from ml.retrieval.relevance import (
    load_ground_truth,
    relevant_recordings,
    validate_query_classes,
)
from ml.retrieval.temporal import PREDICATES, temporal_query


def query(predicate: str, a: str, b: str, tolerance: float = 0.0,
          source: str = "ground_truth") -> dict:
    return {"query_id": "q-001", "question": "?",
            "filters": {"temporal": {"predicate": predicate, "a": a, "b": b,
                                     "tolerance_s": tolerance}},
            "relevance": {"type": "recording_ids", "source": source}}


def event(class_id: str, onset: float, offset: float) -> dict:
    return {"class_id": class_id, "onset_s": onset, "offset_s": offset}


GROUND_TRUTH = {
    "datased:S-1": [event("birds", 0.0, 2.0), event("voices", 3.0, 5.0)],
    "datased:S-2": [event("voices", 0.0, 2.0), event("birds", 3.0, 5.0)],
    "datased:S-3": [event("birds", 0.0, 10.0), event("voices", 2.0, 4.0)],
}


@pytest.mark.parametrize(("predicate", "expected"), [
    ("before", ["datased:S-1"]),
    ("after", ["datased:S-2"]),
    ("overlaps", ["datased:S-3"]),
    ("within", []),
])
def test_relevance_is_computed_from_ground_truth_events(predicate, expected) -> None:
    assert relevant_recordings(query(predicate, "birds", "voices"), GROUND_TRUTH) == expected


def test_relevance_refuses_a_non_ground_truth_source() -> None:
    with pytest.raises(ValueError, match="ground truth"):
        relevant_recordings(query("before", "birds", "voices", source="temporal_filter"),
                            GROUND_TRUTH)


def test_unknown_class_ids_are_rejected_instead_of_filtering_to_nothing() -> None:
    with pytest.raises(ValueError, match=r"\['car', 'dog'\]"):
        validate_query_classes([query("before", "car", "dog")], ("birds", "voices"))


def test_ground_truth_loader_uses_canonical_recording_ids(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    path.write_text("event_id,recording_id,class_id,onset_s,offset_s\n"
                    "1,S-0001,birds,0.5,1.5\n", encoding="utf-8")
    assert load_ground_truth(path) == {"datased:S-0001": [event("birds", 0.5, 1.5)]}


def test_python_predicates_match_the_sql_filter_on_sqlite() -> None:
    """Relevance (Python) and retrieval (SQL) must share semantics, ties included."""
    rng = random.Random(20260922)
    ground_truth: dict[str, list[dict]] = {}
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE events (recording_id TEXT, class_id TEXT, onset_s REAL, "
               "offset_s REAL, provenance TEXT)")
    for r in range(60):
        rid = f"datased:S-{r:04d}"
        for _ in range(rng.randint(1, 5)):
            onset = rng.randint(0, 20) * 0.5  # half-second grid → exact ties occur
            item = event(rng.choice(("birds", "voices", "music")), onset,
                         onset + rng.randint(1, 8) * 0.5)
            ground_truth.setdefault(rid, []).append(item)
            db.execute("INSERT INTO events VALUES (?, ?, ?, ?, 'prediction')",
                       (rid, item["class_id"], item["onset_s"], item["offset_s"]))
    for name in PREDICATES:
        for a, b in (("birds", "voices"), ("voices", "music"), ("music", "birds")):
            for tolerance in (0.0, 0.5):
                params = {"class_a": a, "class_b": b, "tolerance_s": tolerance}
                sql = sorted(r for (r,) in db.execute(temporal_query(name), params))
                python = relevant_recordings(query(name, a, b, tolerance), ground_truth)
                assert python == sql, (name, a, b, tolerance)
