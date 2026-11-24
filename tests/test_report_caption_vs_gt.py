from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.taxonomy import load_taxonomy
from scripts.report_caption_vs_gt import summarise, tier_scores

ROOT = Path(__file__).resolve().parents[1]
LEXICON = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
TEMPLATE = TemplateCaptioner(LEXICON)


def _timeline(rid: str, classes: list[str]) -> dict:
    return {"recording_id": rid, "duration_s": 30.0, "taxonomy_version": "0.1",
            "model_version": "test",
            "events": [{"event_id": i + 1, "class_id": c, "onset_s": 2.0 * i,
                        "offset_s": 2.0 * i + 1.0, "score": 0.9} for i, c in enumerate(classes)]}


def test_caption_faithful_to_prediction_can_still_be_wrong_against_ground_truth():
    gt = {"r1": _timeline("r1", ["birds", "train"]), "r2": _timeline("r2", ["birds"])}
    e2e = {"r1": {"timeline": _timeline("r1", ["birds", "horn"])},
           "r2": {"timeline": _timeline("r2", ["birds"])}}
    scores = tier_scores(gt, None, e2e, lambda row: TEMPLATE.caption(row["timeline"]), LEXICON)
    assert "oracle" not in scores
    assert scores["e2e_vs_pred"]["r1"]["hallucination_rate"] == 0.0
    assert scores["e2e_vs_gt"]["r1"]["hallucination_rate"] == pytest.approx(0.5)
    assert scores["e2e_vs_gt"]["r1"]["omission_rate"] == pytest.approx(0.5)
    summary = summarise(scores)
    assert summary["e2e_vs_gt"]["n"] == 2
    assert summary["e2e_vs_gt"]["hallucination_rate"]["estimate"] == pytest.approx(0.25)


def test_oracle_tier_is_scored_against_ground_truth_when_available():
    gt = {"r1": _timeline("r1", ["birds"]), "r2": _timeline("r2", ["train"])}
    oracle = {rid: {"timeline": tl} for rid, tl in gt.items()}
    e2e = {rid: {"timeline": tl} for rid, tl in gt.items()}
    scores = tier_scores(gt, oracle, e2e, lambda row: TEMPLATE.caption(row["timeline"]), LEXICON)
    assert all(m["hallucination_rate"] == 0.0 for m in scores["oracle"].values())
    assert all(m["omission_rate"] == 0.0 for m in scores["e2e_vs_gt"].values())
