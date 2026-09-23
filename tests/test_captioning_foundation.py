from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon, ForbiddenTermError
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.grounding import evaluate_grounding
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).parents[1]


@pytest.fixture()
def taxonomy():
    return load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")


def test_canonicalizer_sorts_and_rejects_unknown(taxonomy):
    timeline = canonicalize_timeline(
        "datased:S-0001",
        10,
        [
            {"event_id": 2, "class_id": "birds", "onset_s": 4, "offset_s": 5, "score": 0.8},
            {"event_id": 1, "class_id": "bells", "onset_s": 1, "offset_s": 2, "score": 0.9},
        ],
        taxonomy,
    )
    assert [event["class_id"] for event in timeline["events"]] == ["bells", "birds"]
    with pytest.raises(ValueError, match="not in taxonomy"):
        canonicalize_timeline(
            "datased:S-0001",
            10,
            [{"class_id": "sirens", "onset_s": 1, "offset_s": 2, "score": 1}],
            taxonomy,
        )


def test_template_has_zero_hallucination_and_explicit_evidence(taxonomy):
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    timeline = canonicalize_timeline(
        "datased:S-0001",
        10,
        [{"event_id": 7, "class_id": "birds", "onset_s": 1, "offset_s": 2, "score": 0.9}],
        taxonomy,
    )
    caption = TemplateCaptioner(lexicon).caption(timeline)
    metrics = evaluate_grounding(timeline, caption, lexicon)
    assert metrics.hallucination_rate == 0
    assert metrics.omission_rate == 0
    assert metrics.evidence_coverage == 1


def test_grouped_class_keeps_ambiguity_and_g3_is_enforced(taxonomy):
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    timeline = canonicalize_timeline(
        "datased:S-0001",
        10,
        [{"class_id": "sirens_and_alarms", "onset_s": 1, "offset_s": 2, "score": 0.9}],
        taxonomy,
    )
    caption = TemplateCaptioner(lexicon).caption(timeline)
    assert "siren- or alarm-like" in caption["text"]
    assert lexicon.mentions(caption["text"])[0].class_id == "sirens_and_alarms"
    with pytest.raises(ForbiddenTermError):
        lexicon.assert_safe("An emergency vehicle is audible.")


def test_empty_timeline_is_not_called_silence(taxonomy):
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    timeline = canonicalize_timeline("datased:S-0001", 10, [], taxonomy)
    caption = TemplateCaptioner(lexicon).caption(timeline)
    assert "silent" not in caption["text"].lower()
