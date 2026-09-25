from pathlib import Path

import pytest

from ml.captioning.constrained import source_phrase
from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.taxonomy import load_taxonomy
from scripts.report_grouped_class_wording import GROUPED, classify, tally

LEXICON = CaptionLexicon.from_taxonomy(
    load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml")
)


def timeline(class_id: str) -> dict:
    return {"recording_id": "datased:S-0001", "duration_s": 10.0, "taxonomy_version": "0.1",
            "model_version": "x",
            "events": [{"event_id": 1, "class_id": class_id, "onset_s": 1.0,
                        "offset_s": 2.0, "score": 0.9}]}


@pytest.mark.parametrize("class_id", GROUPED)
def test_template_and_constrained_phrases_stay_at_grouped_level(class_id: str) -> None:
    template_text = TemplateCaptioner(LEXICON).caption(timeline(class_id))["text"]
    constrained_text = f"{source_phrase(class_id).capitalize()} can be heard."
    assert classify(template_text, class_id, LEXICON) == ("class", [])
    assert classify(constrained_text, class_id, LEXICON) == ("class", [])


@pytest.mark.parametrize(("text", "class_id", "expected"), [
    ("A gunshot is heard.", "thunder_fireworks_gunshot", ("specific", ["gunshot"])),
    ("An ambulance siren wails.", "sirens_and_alarms", ("specific", ["siren"])),
    ("A loud boom echoes.", "thunder_fireworks_gunshot", ("family", [])),
    ("thunder, fireworks, and gunshots", "thunder_fireworks_gunshot",
     ("specific", ["thunder", "fireworks", "gunshots"])),
    ("a burst of thunder, fireworks, or a gunshot", "thunder_fireworks_gunshot",
     ("disjunction", ["thunder", "fireworks", "gunshot"])),
    ("distant thunder or fireworks", "thunder_fireworks_gunshot",
     ("disjunction", ["thunder", "fireworks"])),
    ("a gunshot or gunshots", "thunder_fireworks_gunshot",
     ("specific", ["gunshot", "gunshots"])),
    ("a sudden thunder-like gunshot", "thunder_fireworks_gunshot",
     ("specific", ["thunder", "gunshot"])),
    ("Birds sing.", "sirens_and_alarms", ("absent", [])),
])
def test_classify_flags_subclass_named_as_fact(text, class_id, expected) -> None:
    assert classify(text, class_id, LEXICON) == expected


def test_tally_counts_only_grouped_classes_present_in_timeline() -> None:
    rows = [("x/oracle", timeline("sirens_and_alarms"), "Sirens wail."),
            ("x/oracle", timeline("birds"), "A gunshot is heard.")]
    result = tally(rows, LEXICON)
    assert result["counts"] == {"x/oracle": {"sirens_and_alarms": {"specific": 1}}}
    assert result["specific_phrases"] == {"x/oracle": {"sirens": 1}}
