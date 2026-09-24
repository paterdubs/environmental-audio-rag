"""Lexicon v2 (ADR-0022 §3): free-text mentions for the RQ2 unconstrained branch."""

from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon, LexiconEntry
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.grounding import collapse_enumerations, evaluate_grounding
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
LEXICON = CaptionLexicon.from_taxonomy(TAXONOMY)


def timeline(*events: tuple[str, float]) -> dict:
    return canonicalize_timeline(
        "datased:S-0001", 60,
        [{"class_id": c, "onset_s": o, "offset_s": o + 1, "score": 0.9} for c, o in events],
        TAXONOMY,
    )


def score(text: str, tl: dict):
    return evaluate_grounding(tl, {"text": text, "evidence": []}, LEXICON)


def test_paraphrases_are_recognised_as_their_class() -> None:
    metrics = score("A propeller aircraft drones while human voices talk.",
                    timeline(("propeller_aircrafts", 0), ("voices", 5)))
    assert metrics.n_mentions == 2
    assert metrics.hallucination_rate == 0
    assert metrics.omission_rate == 0


def test_out_of_taxonomy_source_is_always_a_hallucination() -> None:
    metrics = score("Birds sing over the wind.", timeline(("birds", 0)))
    assert metrics.event_precision == pytest.approx(0.5)


def test_family_phrase_is_supported_when_any_member_is_present() -> None:
    tl = timeline(("propeller_aircrafts", 0))
    assert score("An aircraft passes overhead.", tl).hallucination_rate == 0
    assert score("An aircraft passes overhead.", timeline(("birds", 0))).hallucination_rate == 1


def test_member_enumeration_of_a_grouped_class_is_one_over_specific_mention() -> None:
    tl = timeline(("crows_seagulls_magpies", 0), ("bells", 10))
    text = "Crows, seagulls, and magpies call before bells ring."
    mentions = collapse_enumerations(text, LEXICON.mentions(text))
    metrics = score(text, tl)
    assert [m.kind for m in mentions] == ["specific", "class"]
    assert metrics.temporal_order_accuracy == 1.0
    assert metrics.over_specific_rate == pytest.approx(0.5)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the sudden boom of fireworks", {"thunder_fireworks_gunshot"}),
        ("the chirping of birds", {"birds"}),
        ("chirping birds", {"birds"}),
        ("the ringing of bells", {"bells"}),
        ("mechanical noise from a lawn mower", {"lawn_mower_brush_cutter_olive_shaker"}),
    ],
)
def test_descriptor_of_source_is_one_mention_of_the_shared_class(text, expected) -> None:
    """Found on dev (ADR-0022 §3): counted as two mentions, these zeroed temporal
    order whenever the timeline had a single event of that class."""
    mentions = collapse_enumerations(text, LEXICON.mentions(text))
    assert [set(m.class_ids) for m in mentions] == [expected]


def test_disjoint_neighbours_are_not_merged() -> None:
    text = "chirping birds and crows"
    mentions = collapse_enumerations(text, LEXICON.mentions(text))
    assert [set(m.class_ids) for m in mentions] == [{"birds"}, {"crows_seagulls_magpies"}]


def test_repeated_mention_across_sentences_is_not_collapsed() -> None:
    metrics = score("Birds are audible early. Birds are audible again later.",
                    timeline(("birds", 1)))
    assert metrics.temporal_order_accuracy == 0.0


def test_unsupported_mentions_do_not_poison_temporal_order() -> None:
    metrics = score("Wind blows, then birds sing, then bells ring.",
                    timeline(("birds", 1), ("bells", 9)))
    assert metrics.temporal_order_accuracy == 1.0
    assert metrics.hallucination_rate == pytest.approx(1 / 3)


def test_context_terms_are_reported_separately_from_g3() -> None:
    metrics = score("A peaceful urban park with birds.", timeline(("birds", 0)))
    assert metrics.context_term_rate == 1.0
    assert metrics.forbidden_term_rate == 0.0


def test_saw_as_a_verb_is_not_a_workshop_tool() -> None:
    assert LEXICON.mentions("The recording saw a quiet start.") == ()


def test_template_captions_stay_perfectly_grounded_under_v2() -> None:
    tl = timeline(*[(c, float(i)) for i, c in enumerate(TAXONOMY.polyphonic_class_ids)])
    caption = TemplateCaptioner(LEXICON).caption(tl)
    metrics = evaluate_grounding(tl, caption, LEXICON)
    assert (metrics.hallucination_rate, metrics.omission_rate) == (0, 0)
    assert metrics.temporal_order_accuracy == 1.0
    assert metrics.n_mentions == len(tl["events"])


def test_conflicting_duplicate_phrase_is_rejected() -> None:
    entries = [LexiconEntry("glass", frozenset({"glass_breaking"}), "class"),
               LexiconEntry("glass", frozenset({"bells"}), "class")]
    with pytest.raises(ValueError, match="twice"):
        CaptionLexicon(TAXONOMY, {}, entries)


def test_lexicon_hash_is_pinned_to_its_content() -> None:
    assert LEXICON.version == "caption-lexicon-v2"
    base = CaptionLexicon.from_taxonomy(TAXONOMY, config=None)
    assert base.sha256() != LEXICON.sha256()
