import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ml.retrieval.document_builder import build_document, max_polyphony
from ml.retrieval.query_set import build_query_set
from ml.retrieval.temporal import PREDICATES, temporal_query


def timeline():
    return {"recording_id": "datased:S-1", "duration_s": 10, "events": [
        {"event_id": 2, "class_id": "bells", "onset_s": 5, "offset_s": 7, "score": .8},
        {"event_id": 1, "class_id": "birds", "onset_s": 0, "offset_s": 6, "score": .9},
    ]}


def test_document_is_sorted_and_denormalized():
    document = build_document("Bird calls are audible.", timeline())
    assert document["class_ids"] == ["bells", "birds"]
    assert document["total_events"] == 2
    assert document["max_polyphony"] == 2
    assert "birds 0.000-6.000s" in document["text"]


def test_half_open_polyphony_and_temporal_sql():
    assert max_polyphony([{"onset_s": 0, "offset_s": 1}, {"onset_s": 1, "offset_s": 2}]) == 1
    assert len(PREDICATES) == 4
    assert ":tolerance_s" in temporal_query("before")
    assert "a.onset_s < b.offset_s" in temporal_query("overlaps")


def test_query_set_is_100_and_result_independent():
    queries = build_query_set()
    assert len(queries) == 100
    assert [q["query_id"] for q in queries] == [f"q-{i:03d}" for i in range(1, 101)]
    assert all(q["relevance"]["source"] == "temporal_filter" for q in queries)


def test_query_set_contract_accepts_generated_fixture():
    schema = json.loads(Path("contracts/query_set.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(build_query_set()))
    assert errors == []
