import unicodedata
from pathlib import Path

import pytest

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon, ForbiddenTermError
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.grounding import evaluate_grounding
from ml.taxonomy import load_taxonomy

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml")
EN = CaptionLexicon.from_taxonomy(TAXONOMY)
VI = CaptionLexicon.from_taxonomy(TAXONOMY, config=VI_LEXICON_CONFIG)
FROZEN_EN_SHA = "6f5634bb7837817c94dd16fe0c0b07a6eae15996fe93064c325599d3321edc73"


def timeline(*events: tuple[str, float, float]) -> dict:
    return {"recording_id": "datased:S-0001", "duration_s": 60.0, "taxonomy_version": "0.1",
            "model_version": "x",
            "events": [{"event_id": i + 1, "class_id": c, "onset_s": on, "offset_s": off,
                        "score": 0.9} for i, (c, on, off) in enumerate(events)]}


def test_every_class_has_an_english_and_a_vietnamese_phrase() -> None:
    for lexicon in (EN, VI):
        named = {cid for e in lexicon.entries if e.kind == "class" for cid in e.class_ids}
        assert named == set(TAXONOMY.class_ids), lexicon.language
    assert all(VI.canonical_phrase(cid) for cid in TAXONOMY.class_ids)


def test_every_vietnamese_class_phrase_is_a_whole_noun_phrase() -> None:
    """An unquoted comma in a YAML flow list splits one phrase into fragments."""
    phrases = [e.phrase for e in VI.entries if e.kind == "class"]
    fragments = [p for p in phrases if not p.startswith(("tiếng ", "âm thanh "))]
    assert fragments == []


def test_vietnamese_lexicon_leaves_the_frozen_english_hash_untouched() -> None:
    assert EN.language == "en" and EN.sha256() == FROZEN_EN_SHA
    assert VI.language == "vi" and VI.sha256() != FROZEN_EN_SHA


def test_vietnamese_template_is_perfectly_grounded() -> None:
    tl = timeline(("birds", 0.0, 17.6), ("sirens_and_alarms", 3.0, 5.0),
                  ("birds", 20.0, 25.0), ("thunder_fireworks_gunshot", 30.0, 30.4),
                  ("crows_seagulls_magpies", 40.0, 42.0), ("vehicle_idling", 50.0, 58.0))
    caption = TemplateCaptioner(VI).caption(tl, language="vi")
    metrics = evaluate_grounding(tl, caption, VI)
    assert metrics.hallucination_rate == 0 and metrics.omission_rate == 0
    assert metrics.temporal_order_accuracy == 1.0 and metrics.evidence_coverage == 1.0
    assert metrics.forbidden_term_rate == 0 and metrics.over_specific_rate == 0
    assert metrics.n_mentions == 6
    for item in caption["evidence"]:  # spans index the sentence of their own event
        start, end = item["mention_span"]
        assert caption["text"][start:end].startswith("Có thể nghe thấy")


def test_vietnamese_grouped_classes_keep_hedging_and_subclass_is_over_specific() -> None:
    text = TemplateCaptioner(VI).caption(
        timeline(("thunder_fireworks_gunshot", 1.0, 1.5)), language="vi")["text"]
    assert "âm thanh dạng xung giống tiếng sấm, pháo hoa hoặc tiếng súng" in text
    assert [m.kind for m in VI.mentions(text)] == ["class"]
    assert [m.kind for m in VI.mentions("Có tiếng súng.")] == ["specific"]


def test_vietnamese_numbers_use_decimal_comma_and_empty_is_not_silence() -> None:
    text = TemplateCaptioner(VI).caption(timeline(("music", 1.5, 2.0)), language="vi")["text"]
    assert text == "Có thể nghe thấy tiếng nhạc từ 1,5 đến 2,0 giây."
    empty = TemplateCaptioner(VI).caption(timeline(), language="vi")["text"]
    assert "Không phát hiện" in empty and "im lặng" not in empty


def test_vietnamese_g3_keeps_diacritics() -> None:
    assert VI.forbidden_terms("Có dấu hiệu tội phạm.") == ("tội phạm",)
    assert VI.forbidden_terms("Tiếng chim lan tới phạm vi rộng.") == ()  # "toi pham" if folded
    assert VI.forbidden_terms("Mối đe doạ.") == ("đe doạ",)
    with pytest.raises(ForbiddenTermError):
        VI.assert_safe("Có một vụ đột nhập.")


def test_language_must_match_the_lexicon_and_text_must_be_nfc() -> None:
    with pytest.raises(ValueError, match="needs a 'vi' lexicon"):
        TemplateCaptioner(EN).caption(timeline(("music", 1.0, 2.0)), language="vi")
    with pytest.raises(ValueError, match="NFC"):
        VI.mentions(unicodedata.normalize("NFD", "Có thể nghe thấy tiếng nhạc."))


def test_english_template_text_is_unchanged() -> None:
    caption = TemplateCaptioner(EN).caption(timeline(("birds", 0.0, 17.6)))
    assert caption["text"] == "A birds is audible from 0.0 to 17.6 seconds."
