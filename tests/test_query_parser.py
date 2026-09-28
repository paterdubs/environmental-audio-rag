from pathlib import Path

import pytest

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.retrieval.query_parser import (
    ParserConfig,
    QueryParser,
    QueryParserInvalid,
    filter_json_schema,
)
from ml.retrieval.temporal import PREDICATES
from ml.taxonomy import load_taxonomy
from scripts.evaluate_query_parser import normalise, samples, summarise

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
VI = CaptionLexicon.from_taxonomy(TAXONOMY, config=VI_LEXICON_CONFIG)
LABELS = {item.class_id: {"en": item.source_label.lower(),
                          "vi": VI.canonical_phrase(item.class_id)}
          for item in TAXONOMY.classes if item.class_id in TAXONOMY.polyphonic_class_ids}
CONFIG = ParserConfig("fake", "http://unused", 0.0, 20260922, 128, False, 1.0)


class FakeTransport:
    def __init__(self, content):
        self.content = content
        self.body = None

    def complete(self, body):
        self.body = body
        return {"choices": [{"message": {"content": self.content}}]}


def test_schema_and_request_are_derived_from_taxonomy_and_predicates() -> None:
    schema = filter_json_schema(TAXONOMY.polyphonic_class_ids)
    temporal = schema["oneOf"][1]["properties"]["temporal"]
    duration = schema["oneOf"][2]["properties"]["duration"]
    assert temporal["properties"]["predicate"]["enum"] == list(PREDICATES)
    assert duration["properties"]["class_id"]["enum"] == list(TAXONOMY.polyphonic_class_ids)
    transport = FakeTransport('{"classes_all":["birds"]}')
    result = QueryParser(transport, CONFIG, LABELS).parse("bird sounds?", "en")
    assert result.filters.as_dict() == {"classes_all": ["birds"]}
    assert transport.body["temperature"] == 0.0 and transport.body["seed"] == 20260922
    assert transport.body["response_format"]["type"] == "json_object"
    assert transport.body["json_schema"] == schema


def test_parser_rejects_unknown_class_even_if_fake_server_ignores_grammar() -> None:
    parser = QueryParser(FakeTransport('{"classes_all":["car"]}'), CONFIG, LABELS)
    with pytest.raises(QueryParserInvalid, match="ngoài 21 lớp"):
        parser.parse("car", "en")


@pytest.mark.parametrize("content", ["not json", "{}", '{"classes_all":["birds"],"x":1}'])
def test_parser_rejects_malformed_empty_and_extra_fields(content: str) -> None:
    with pytest.raises(QueryParserInvalid, match="không hợp lệ"):
        QueryParser(FakeTransport(content), CONFIG, LABELS).parse("q", "vi")


def test_locked_evaluation_sets_and_metrics() -> None:
    rows = samples("all")
    assert len(rows) == 240
    assert sum(row["dataset"] == "template" for row in rows) == 200
    assert sum(row["dataset"] == "paraphrase" for row in rows) == 40
    gold = {"classes_all": ["voices", "music"]}
    assert normalise(gold) == normalise({"classes_all": ["music", "voices"]})
    scored = [{"gold": gold, "predicted": gold, "error": None, "exact": True},
              {"gold": {"classes_all": ["birds"]}, "predicted": None,
               "error": "bad", "exact": False}]
    summary = summarise(scored)
    assert summary["exact_match"] == 0.5 and summary["class_recall"] == pytest.approx(2 / 3)
