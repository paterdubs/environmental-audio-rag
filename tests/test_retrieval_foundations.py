import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ml.retrieval.document_builder import build_document, max_polyphony
from ml.retrieval.query_set import GROUP_SIZES, build_query_set
from ml.retrieval.relevance import validate_query_classes
from ml.retrieval.temporal import PREDICATES, temporal_query
from ml.taxonomy import load_taxonomy


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


CLASS_IDS = load_taxonomy(Path("ml/configs/taxonomy.yaml")).polyphonic_class_ids
FROZEN = Path("data/manifests/retrieval_queryset_v2.json")


def test_frozen_query_set_v2_matches_contract_groups_and_taxonomy():
    queries = json.loads(FROZEN.read_text(encoding="utf-8"))
    schema = json.loads(Path("contracts/query_set.schema.json").read_text())
    assert list(Draft202012Validator(schema).iter_errors(queries)) == []
    assert [q["query_id"] for q in queries] == [f"q-{i:03d}" for i in range(1, 101)]
    assert {g: sum(q["group"] == g for q in queries) for g in GROUP_SIZES} == GROUP_SIZES
    validate_query_classes(queries, CLASS_IDS)
    temporal = {(q["filters"]["temporal"]["predicate"], q["filters"]["temporal"]["a"],
                 q["filters"]["temporal"]["b"]) for q in queries if q["group"] == "temporal"}
    assert not any(("before", b, a) in temporal for p, a, b in temporal if p == "after")


def test_query_selection_sees_only_the_given_train_split():
    def rec(*classes):
        return [{"class_id": c, "onset_s": float(i), "offset_s": i + 40.0}
                for i, c in enumerate(classes)]

    train = {f"r{i}": rec("birds", "music") for i in range(5)} | {"x": rec("voices")}
    queries = build_query_set(train, ("birds", "music", "voices"), str, str.upper)
    singles = [q for q in queries if q["group"] == "single_class"]
    assert [q["filters"]["classes_all"] for q in singles] == [["birds"], ["music"]]
    assert all(q["support_train"] >= 3 for q in queries)  # voices (1 recording) dropped
    assert singles[0]["question_vi"] == "Bản ghi nào có BIRDS?"
    assert build_query_set(train, ("birds", "music", "voices"), str, str.upper) == queries
