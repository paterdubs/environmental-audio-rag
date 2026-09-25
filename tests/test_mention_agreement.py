import csv
import json
from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon
from ml.evaluation.mention_agreement import (
    agreement,
    extractor_outside,
    extractor_units,
    parse_units,
    unsupported,
)
from ml.taxonomy import load_taxonomy

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml")
LEXICON = CaptionLexicon.from_taxonomy(TAXONOMY)


def test_parse_units_supports_ambiguity_and_none_and_rejects_unknown() -> None:
    units = parse_units("birds; jet_aircrafts|propeller_aircrafts", TAXONOMY.class_ids)
    assert units == {frozenset({"birds"}), frozenset({"jet_aircrafts", "propeller_aircrafts"})}
    assert parse_units("none", TAXONOMY.class_ids) == set()
    with pytest.raises(ValueError, match="none"):
        parse_units("  ", TAXONOMY.class_ids)
    with pytest.raises(ValueError, match="car"):
        parse_units("birds; car", TAXONOMY.class_ids)


def test_extractor_units_match_human_units_for_plain_and_family_mentions() -> None:
    text = "Birds chirp while an aircraft passes overhead in the wind."
    assert extractor_units(text, LEXICON) == {
        frozenset({"birds"}), frozenset({"jet_aircrafts", "propeller_aircrafts"})}
    assert extractor_outside(text, LEXICON)  # "wind" is outside the taxonomy


def test_agreement_counts_units_and_exact_captions() -> None:
    b, v, m = frozenset({"birds"}), frozenset({"voices"}), frozenset({"music"})
    result = agreement([({b, v}, {b, v}), ({b}, {b, m}), ({v, m}, {v})])
    assert (result.true_positive, result.false_positive, result.false_negative) == (4, 1, 1)
    assert result.exact_captions == 1 and result.n_captions == 3
    assert result.precision == pytest.approx(0.8) and result.recall == pytest.approx(0.8)


def test_unsupported_mirrors_the_grounding_rule() -> None:
    b, jet = frozenset({"birds"}), frozenset({"jet_aircrafts", "propeller_aircrafts"})
    assert not unsupported({b, jet}, {"birds", "propeller_aircrafts"}, outside=False)
    assert unsupported({b}, {"voices"}, outside=False)
    assert unsupported(set(), {"voices"}, outside=True)


def _captions(run: Path) -> None:
    (run / "captions").mkdir(parents=True)
    rows = [{"recording_id": f"S-{i:04d}", "level": level,
             "timeline": {"events": [{"event_id": 1, "class_id": "birds", "onset_s": 0.0,
                                      "offset_s": 1.0, "score": 1.0}]},
             "caption": {"text": f"Birds sing ({i}, {level})."}}
            for i in range(6) for level in ("oracle", "e2e")]
    (run / "captions" / "unconstrained_test.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def test_worksheet_build_is_deterministic_and_never_overwrites(tmp_path: Path) -> None:
    import argparse

    import scripts.caption_mention_worksheet as ws

    _captions(tmp_path / "run")
    sheet = tmp_path / "sheet.csv"
    namespace = argparse.Namespace(run_dir=tmp_path / "run", split="test", n=4, worksheet=sheet,
                                   guide=tmp_path / "guide.md")
    ws.build(namespace)
    first = sheet.read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(first.splitlines()))
    assert len(rows) == 4 and {r["level"] for r in rows} == {"oracle", "e2e"}
    assert all(r["classes_mentioned"] == "" for r in rows)  # blind: nothing pre-filled
    with pytest.raises(SystemExit, match="không ghi đè"):
        ws.build(namespace)
    sheet.unlink()
    ws.build(namespace)
    assert sheet.read_text(encoding="utf-8-sig") == first


def _fill(sheet: Path, n_filled: int, value: str = "birds") -> None:
    with sheet.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows[:n_filled]:
        row["classes_mentioned"] = value
    with sheet.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_partially_filled_worksheet_is_scored_on_annotated_rows_only(tmp_path: Path) -> None:
    import argparse

    import scripts.caption_mention_worksheet as ws

    _captions(tmp_path / "run")
    sheet, out = tmp_path / "sheet.csv", tmp_path / "agreement.md"
    args = argparse.Namespace(run_dir=tmp_path / "run", split="test", n=12, worksheet=sheet,
                              output=out, guide=tmp_path / "guide.md")
    ws.build(args)
    _fill(sheet, 10)
    ws.score(args)
    result = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert result["n_captions"] == 10 and result["n_not_annotated"] == 2
    assert result["mentions"]["precision"] == 1.0 and result["mentions"]["recall"] == 1.0
    assert result["hallucination_flag"]["lexicon_False_human_False"] == 10
    bias = result["metric_bias"]["omission_rate"]
    assert bias["lexicon"] == bias["human"] == 0.0 and bias["lexicon_minus_human"][0] == 0.0


def test_scoring_needs_enough_rows_and_refuses_half_filled_rows() -> None:
    from scripts.caption_mention_worksheet import MIN_ANNOTATED, annotated_rows

    blank = {"item_id": "m-1", "classes_mentioned": "", "other_sources": "",
             "over_specific": "", "notes": ""}
    filled = {**blank, "classes_mentioned": "none"}
    rows, pending = annotated_rows([filled] * MIN_ANNOTATED + [blank] * 3)
    assert len(rows) == MIN_ANNOTATED and pending == 3
    with pytest.raises(SystemExit, match="cần ít nhất"):
        annotated_rows([filled] * (MIN_ANNOTATED - 1))
    with pytest.raises(SystemExit, match="thiếu classes_mentioned"):
        annotated_rows([{**blank, "notes": "unsure"}] + [filled] * MIN_ANNOTATED)


def test_human_grounding_counts_outside_sources_as_unsupported() -> None:
    from ml.evaluation.mention_agreement import human_grounding

    metrics = human_grounding({frozenset({"birds"})}, n_outside=1, present={"birds", "voices"})
    assert metrics.hallucination_rate == 0.5 and metrics.omission_rate == 0.5
    assert human_grounding(set(), 0, {"birds"}).omission_rate == 1.0


def test_label_restatement_is_recognised() -> None:
    from ml.evaluation.mention_agreement import label_restatement

    assert label_restatement("cicadas_and_crickets", "A chorus of cicadas and crickets.", LEXICON)
    assert not label_restatement("cicadas_and_crickets", "Crickets chirp.", LEXICON)
