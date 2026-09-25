from pathlib import Path

from ml.captioning.lexicon import CaptionLexicon
from ml.taxonomy import load_taxonomy
from scripts.report_caption_per_class import class_errors, tally

LEXICON = CaptionLexicon.from_taxonomy(
    load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml"))


def timeline(*classes: str) -> dict:
    return {"events": [{"class_id": c, "onset_s": float(i), "offset_s": i + 1.0}
                       for i, c in enumerate(classes)]}


def test_class_errors_separate_omission_unsupported_specific_and_outside() -> None:
    outcome = class_errors(timeline("birds", "voices", "sirens_and_alarms"),
                           "Birds sing near a train, sirens wail, and wind blows.", LEXICON)
    assert outcome["omitted"] == {"voices"}
    assert dict(outcome["unsupported"]) == {"train": 1}
    assert dict(outcome["specific"]) == {"sirens_and_alarms": 1}
    assert dict(outcome["out_of_taxonomy"]) == {"wind": 1}


def test_tally_counts_presence_and_omission_per_branch_and_class() -> None:
    rows = [("x/e2e", timeline("birds", "music"), "Birds sing."),
            ("x/e2e", timeline("birds"), "Birds sing.")]
    table = tally(rows, LEXICON)["x/e2e"]
    assert table["present"] == {"birds": 2, "music": 1}
    assert table["omitted"] == {"music": 1}
