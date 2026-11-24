from pathlib import Path

import pytest

from ml.captioning.grouped import GroupedTemplateCaptioner
from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.evaluation.grounding import evaluate_grounding
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
EN = CaptionLexicon.from_taxonomy(TAXONOMY)
VI = CaptionLexicon.from_taxonomy(TAXONOMY, config=VI_LEXICON_CONFIG)


def ev(event_id, class_id, onset, offset, score):
    return {"event_id": event_id, "class_id": class_id, "onset_s": onset, "offset_s": offset,
            "score": score}


TIMELINE = {"recording_id": "datased:S-1", "events": [
    ev(1, "birds", 0.0, 5.0, 0.9), ev(2, "train", 3.0, 9.0, 0.2), ev(3, "birds", 12.0, 20.0, 0.95)]}


def test_groups_repeated_class_with_count_and_span_in_onset_order():
    text = GroupedTemplateCaptioner(EN).caption(TIMELINE)["text"]
    assert text == "Detected: birds, 2 times, 0.0–20.0 s. Detected: train, 3.0–9.0 s."


def test_hedges_only_classes_whose_best_score_is_below_threshold():
    en = GroupedTemplateCaptioner(EN, hedge_threshold=0.5).caption(TIMELINE)["text"]
    assert en.endswith("Possible (low confidence): train, 3.0–9.0 s.")
    assert en.startswith("Detected: birds")
    vi = GroupedTemplateCaptioner(VI, hedge_threshold=0.5).caption(TIMELINE, "vi")["text"]
    assert vi == ("Phát hiện: tiếng chim, 2 lần, 0,0–20,0 giây. "
                  "Có thể có (độ tin cậy thấp): tiếng tàu hỏa, 3,0–9,0 giây.")


def test_grouped_caption_keeps_zero_hallucination_and_omission_and_order():
    caption = GroupedTemplateCaptioner(EN, hedge_threshold=0.5).caption(TIMELINE)
    metrics = evaluate_grounding(TIMELINE, caption, EN)
    assert metrics.hallucination_rate == 0.0 and metrics.omission_rate == 0.0
    assert metrics.temporal_order_accuracy == 1.0 and metrics.evidence_coverage == 1.0


def test_empty_timeline_and_language_mismatch():
    empty = {"recording_id": "datased:S-2", "events": []}
    assert GroupedTemplateCaptioner(EN).caption(empty)["text"].startswith("No target sound")
    with pytest.raises(ValueError):
        GroupedTemplateCaptioner(EN).caption(TIMELINE, "vi")


def test_serving_threshold_matches_the_dev_measurement():
    import json

    from ml.inference.pipeline import serving_hedge_threshold

    measured = ROOT / "docs/measurements/grouped_captions_dev_20261124.json"
    expected = json.loads(measured.read_text(encoding="utf-8"))["hedge_threshold"]
    assert serving_hedge_threshold() == expected
