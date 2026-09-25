"""Constrained branch (ADR-0023): same model/prompt as unconstrained + a grammar."""

from pathlib import Path
from typing import Any

import pytest

from ml.captioning.constrained import (
    EMPTY_TEXT,
    SEPARATORS,
    VERBS,
    ConstrainedLLMCaptioner,
    align_evidence,
    build_grammar,
    event_clause,
    longest_caption,
    source_phrase,
)
from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.llm import LLMConfig, UnconstrainedLLMCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.grounding import collapse_enumerations, evaluate_grounding
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
LEXICON = CaptionLexicon.from_taxonomy(TAXONOMY)
CONFIG = LLMConfig.from_yaml(ROOT / "ml" / "configs" / "caption_llm.yaml")


class FakeTransport:
    def __init__(self, text: str):
        self.text = text
        self.bodies: list[dict[str, Any]] = []

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        self.bodies.append(body)
        return {"choices": [{"message": {"content": self.text}, "finish_reason": "stop"}]}


def timeline(*events: tuple[str, float, float]) -> dict:
    return canonicalize_timeline(
        "datased:S-0001", 60,
        [{"class_id": c, "onset_s": on, "offset_s": off, "score": 0.9} for c, on, off in events],
        TAXONOMY,
    )


@pytest.mark.parametrize("class_id", TAXONOMY.polyphonic_class_ids)
def test_every_source_phrase_is_read_back_as_its_own_class(class_id) -> None:
    """If the frozen lexicon misread a grammar phrase, the constrained branch
    would be charged with hallucinations it cannot produce."""
    phrase = source_phrase(class_id)
    mentions = collapse_enumerations(phrase, LEXICON.mentions(phrase))
    assert [(set(m.class_ids), m.kind) for m in mentions] == [({class_id}, "class")]


def test_grammar_admits_only_timeline_events() -> None:
    grammar = build_grammar(timeline(("birds", 1.0, 2.5), ("bells", 5.0, 6.0)))
    assert '"The sound of birds"' in grammar and '"the sound of bells"' in grammar
    assert "from 1.0 to 2.5 seconds" in grammar
    assert "train" not in grammar


def test_one_sentence_can_list_several_events() -> None:
    """Smoke test (ADR-0023): with one event per sentence the model, asked for
    ONE short caption, stopped after a single event."""
    tl = timeline(("birds", 1.0, 2.0), ("bells", 5.0, 6.0), ("train", 8.0, 9.0))
    text = ("The sound of birds can be heard from 1.0 to 2.0 seconds, the sound of bells "
            "from 5.0 to 6.0 seconds, and the sound of train from 8.0 to 9.0 seconds.")
    caption = ConstrainedLLMCaptioner(FakeTransport(text), CONFIG).caption(tl)
    metrics = evaluate_grounding(tl, caption, LEXICON)
    assert len(caption["evidence"]) == 3
    assert (metrics.omission_rate, metrics.temporal_order_accuracy) == (0, 1)


def test_grammar_is_an_ordered_subsequence_without_repeats() -> None:
    """Smoke test (ADR-0023): a free item list let greedy decoding repeat one
    item until max_tokens. Each event may now appear once, in onset order."""
    tl = timeline(("birds", 1.0, 2.0), ("bells", 5.0, 6.0), ("train", 8.0, 9.0))
    lines = build_grammar(tl).splitlines()
    assert lines[0] == 'root ::= (f0 | f1 | f2) "."'
    assert any(line.startswith("f0 ::=") and line.endswith(" r1") for line in lines)
    assert any(line.startswith("r1 ::= (separator") and line.endswith(" r2") for line in lines)
    assert not any(line.startswith("r0 ::=") for line in lines)


def test_empty_timeline_grammar_forces_the_no_event_sentence() -> None:
    assert build_grammar(timeline()) == f'root ::= "{EMPTY_TEXT}"'


def test_request_equals_unconstrained_plus_grammar() -> None:
    tl = timeline(("birds", 1.0, 2.0))
    constrained, free = FakeTransport("x"), FakeTransport("x")
    ConstrainedLLMCaptioner(constrained, CONFIG).caption(tl)
    UnconstrainedLLMCaptioner(free, CONFIG).caption(tl)
    body = dict(constrained.bodies[0])
    assert body.pop("grammar") == build_grammar(tl)
    assert body == free.bodies[0]


def test_evidence_aligns_each_sentence_to_its_event() -> None:
    tl = timeline(("birds", 1.0, 2.0), ("bells", 5.0, 6.0), ("birds", 9.0, 10.0))
    text = ("The sound of bells can be heard from 5.0 to 6.0 seconds. Then, the sound of "
            "birds can be detected from 9.0 to 10.0 seconds.")
    ids = {e["class_id"] + str(e["onset_s"]): e["event_id"] for e in tl["events"]}
    evidence = align_evidence(text, tl)
    assert [item["event_id"] for item in evidence] == [ids["bells5.0"], ids["birds9.0"]]


def test_repeated_sentence_gets_no_second_evidence() -> None:
    tl = timeline(("birds", 1.0, 2.0))
    sentence = "The sound of birds can be heard from 1.0 to 2.0 seconds."
    assert len(align_evidence(f"{sentence} {sentence}", tl)) == 1


def test_grammar_shaped_caption_is_fully_grounded_but_can_omit() -> None:
    tl = timeline(("birds", 1.0, 2.0), ("bells", 5.0, 6.0), ("train", 8.0, 9.0))
    text = ("The sound of birds can be heard from 1.0 to 2.0 seconds, followed by the sound "
            "of train from 8.0 to 9.0 seconds.")
    caption = ConstrainedLLMCaptioner(FakeTransport(text), CONFIG).caption(tl)
    metrics = evaluate_grounding(tl, caption, LEXICON)
    assert metrics.hallucination_rate == 0
    assert metrics.evidence_coverage == 1
    assert metrics.omission_rate == pytest.approx(1 / 3)
    assert metrics.temporal_order_accuracy == 1
    assert (metrics.forbidden_term_rate, metrics.context_term_rate) == (0, 0)


def test_temporal_order_uses_evidence_when_an_earlier_same_class_event_is_omitted() -> None:
    """Found on dev (constrained order 0.86 despite a grammar that forces onset
    order): without evidence the metric pinned the 'birds' mention to the
    earliest unclaimed birds onset (1.0), not the event actually cited (9.0)."""
    tl = timeline(("birds", 1.0, 2.0), ("bells", 5.0, 6.0), ("birds", 9.0, 10.0))
    text = ("The sound of bells can be heard from 5.0 to 6.0 seconds, followed by the sound "
            "of birds from 9.0 to 10.0 seconds.")
    caption = ConstrainedLLMCaptioner(FakeTransport(text), CONFIG).caption(tl)
    assert evaluate_grounding(tl, caption, LEXICON).temporal_order_accuracy == 1.0
    no_evidence = {**caption, "evidence": []}
    assert evaluate_grounding(tl, no_evidence, LEXICON).temporal_order_accuracy == 0.0


def test_longest_caption_lists_every_event_in_order_with_longest_choices() -> None:
    tl = timeline(("birds", 1.0, 2.5), ("bells", 5.0, 6.0), ("birds", 7.0, 8.0))
    text = longest_caption(tl)
    positions = [text.index(event_clause(e)) for e in tl["events"]]
    assert positions == sorted(positions) and text.startswith("The sound of birds")
    assert text.count(max(VERBS, key=len)) == 3 and text.count(max(SEPARATORS, key=len)) == 2
    assert text.endswith(".") and longest_caption(timeline()) == EMPTY_TEXT


def test_request_budget_covers_the_grammar_and_never_drops_below_the_shared_cap() -> None:
    many = timeline(*[("birds", float(i), i + 0.5) for i in range(20)])
    transport = FakeTransport("The sound of birds can be heard from 0.0 to 0.5 seconds.")
    caption = ConstrainedLLMCaptioner(transport, CONFIG).caption(many)
    expected = max(CONFIG.max_tokens, len(longest_caption(many)) + 1)  # chars, not tokens
    assert expected > CONFIG.max_tokens  # 20 events would not fit the old 256 cap
    assert transport.bodies[0]["max_tokens"] == caption["generation"]["token_budget"] == expected
    short = ConstrainedLLMCaptioner(transport, CONFIG).caption(timeline(("birds", 1.0, 2.0)))
    assert short["generation"]["token_budget"] == CONFIG.max_tokens


def test_cover_grammar_makes_the_first_event_of_every_class_mandatory() -> None:
    from ml.captioning.constrained import first_occurrences

    tl = timeline(("birds", 0.0, 2.0), ("bells", 3.0, 4.0), ("birds", 5.0, 6.0),
                  ("music", 7.0, 8.0))
    assert first_occurrences(tl["events"]) == {0, 1, 3}
    rules = dict(line.split(" ::= ", 1) for line in build_grammar(tl, cover=True).splitlines())
    assert rules["root"] == '(f0) "."'  # must start at the earliest event
    assert not rules["r1"].startswith("(") and not rules["r3"].startswith("(")  # mandatory
    assert rules["r2"].startswith("(separator")  # a repeat of birds stays optional
    plain = dict(line.split(" ::= ", 1) for line in build_grammar(tl).splitlines())
    assert plain["root"].startswith("(f0 | f1") and plain["r1"].startswith("(separator")


def test_cover_captioner_sends_the_cover_grammar_and_names_its_version() -> None:
    from ml.captioning.constrained import CoverConstrainedLLMCaptioner

    tl = timeline(("birds", 0.0, 2.0), ("bells", 3.0, 4.0))
    transport = FakeTransport("The sound of birds can be heard from 0.0 to 2.0 seconds, "
                              "and the sound of bells can be heard from 3.0 to 4.0 seconds.")
    caption = CoverConstrainedLLMCaptioner(transport, CONFIG).caption(tl)
    assert transport.bodies[0]["grammar"] == build_grammar(tl, cover=True)
    assert caption["captioner_version"].startswith("caption-grammar-cover-v1+")
    assert evaluate_grounding(tl, caption, LEXICON).omission_rate == 0
