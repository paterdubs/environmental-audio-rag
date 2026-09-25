import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.retrieval.answer import answer, supporting_events, unsupported_claims
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
EN = CaptionLexicon.from_taxonomy(TAXONOMY)
VI = CaptionLexicon.from_taxonomy(TAXONOMY, config=VI_LEXICON_CONFIG)
LABEL = {c.class_id: c.source_label.lower() for c in TAXONOMY.classes}
SCHEMA = json.loads((ROOT / "contracts/retrieval_result.schema.json").read_text("utf-8"))


def ev(event_id, class_id, onset, offset):
    return {"event_id": event_id, "class_id": class_id, "onset_s": onset, "offset_s": offset}


EVENTS = {
    "datased:S-1": [ev(1, "crows_seagulls_magpies", 2.0, 4.0), ev(2, "birds", 5.0, 30.0)],
    "datased:S-2": [ev(3, "birds", 1.0, 2.0)],
}
BEFORE = {"temporal": {"predicate": "before", "a": "crows_seagulls_magpies", "b": "birds",
                       "tolerance_s": 0.0}}


def test_supporting_events_per_filter_type() -> None:
    assert [e["event_id"] for e in supporting_events(EVENTS["datased:S-1"], BEFORE)] == [1, 2]
    long_birds = {"duration": {"class_id": "birds", "min_s": 10.0}}
    assert [e["event_id"] for e in supporting_events(EVENTS["datased:S-1"], long_birds)] == [2]
    assert supporting_events(EVENTS["datased:S-2"], long_birds) is None


def test_answers_cite_only_matching_recordings_and_pass_the_checker_in_both_languages() -> None:
    for language, lexicon, name in (("en", EN, LABEL.__getitem__),
                                    ("vi", VI, VI.canonical_phrase)):
        result = answer("q", BEFORE, "hybrid", ["datased:S-2", "datased:S-1"], EVENTS,
                        language, name, k=10)
        assert list(Draft202012Validator(SCHEMA).iter_errors(result)) == []
        assert {e["recording_id"] for e in result["evidence"]} == {"datased:S-1"}
        assert unsupported_claims(result, lexicon) == []  # VI crows phrase contains a comma


def test_checker_catches_tampered_times_unknown_class_and_g3() -> None:
    result = answer("q", BEFORE, "hybrid", ["datased:S-1"], EVENTS, "en", LABEL.__getitem__, 10)
    tampered = {**result, "answer": result["answer"].replace("5.0–30.0", "6.0–30.0")}
    assert unsupported_claims(tampered, EN) == ["datased:S-1:birds:6.0-30.0"]
    unknown = {**result, "answer": result["answer"] + " In datased:S-1, something at 1.0–2.0 s."}
    assert unsupported_claims(unknown, EN) == ["datased:S-1:None:1.0-2.0"]
    alarming = {**result, "answer": result["answer"] + " This is an emergency."}
    assert unsupported_claims(alarming, EN) == ["G3:emergency"]


def test_no_match_returns_empty_evidence_with_the_applied_filters() -> None:
    result = answer("q", {"classes_all": ["train"]}, "structured_only", [], EVENTS, "vi",
                    VI.canonical_phrase, 10)
    assert result["evidence"] == [] and result["answer"].startswith("Không bản ghi")
    assert result["filters_applied"]["hard_filters"] == {"classes_all": ["train"]}
