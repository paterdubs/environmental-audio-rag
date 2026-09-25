import json
import math
from pathlib import Path

import pytest

from ml.evaluation.caption_stats import aggregate, metric_ci, paired_difference, summarise
from ml.evaluation.grounding import GroundingMetrics


def score(hallucination=0.0, omission=0.0, order=1.0, mentions=3) -> GroundingMetrics:
    return GroundingMetrics(event_precision=1 - hallucination, event_recall=1 - omission,
                            hallucination_rate=hallucination, omission_rate=omission,
                            temporal_order_accuracy=order, evidence_coverage=1.0,
                            forbidden_term_rate=0.0, n_mentions=mentions)


def test_order_accuracy_excludes_captions_with_fewer_than_two_mentions() -> None:
    rows = [score(order=0.5, mentions=4), score(order=1.0, mentions=1),
            score(order=1.0, mentions=0)]
    assert aggregate(rows, "temporal_order_accuracy") == pytest.approx(2.5 / 3)
    assert aggregate(rows, "temporal_order_eligible") == 0.5
    assert math.isnan(aggregate([score(mentions=1)], "temporal_order_eligible"))
    assert summarise(dict(enumerate(rows)))["n_temporal_eligible"] == 1


def test_micro_hallucination_pools_mentions() -> None:
    rows = [score(hallucination=0.5, mentions=2), score(hallucination=0.0, mentions=8)]
    assert aggregate(rows, "hallucination_rate") == 0.25
    assert aggregate(rows, "hallucination_micro") == pytest.approx(1 / 10)


def test_paired_difference_is_zero_for_identical_branches_and_signed_otherwise() -> None:
    a = {f"r{i}": score(omission=0.1 * (i % 3)) for i in range(20)}
    worse = {rid: score(omission=m.omission_rate + 0.2) for rid, m in a.items()}
    same = paired_difference(a, a, "omission_rate")
    assert same.estimate == same.lower == same.upper == 0.0
    diff = paired_difference(worse, a, "omission_rate")
    assert diff.estimate == pytest.approx(0.2) and diff.lower == pytest.approx(0.2)


def test_paired_difference_refuses_different_recordings() -> None:
    with pytest.raises(ValueError, match="same recordings"):
        paired_difference({"r1": score(), "r2": score()}, {"r1": score(), "r3": score()},
                          "omission_rate")


def test_ci_brackets_the_estimate_and_is_deterministic() -> None:
    scores = {f"r{i}": score(hallucination=0.1 * (i % 4)) for i in range(30)}
    first, second = metric_ci(scores, "hallucination_rate"), metric_ci(scores, "hallucination_rate")
    assert first == second and first.lower <= first.estimate <= first.upper


def _write_branch(captions: Path, branch: str, timeline: dict) -> None:
    row = {"recording_id": "S-0001", "level": "oracle", "timeline": timeline,
           "caption": {"text": "Birds can be heard.", "evidence": []}}
    path = captions / f"{branch}_dev.jsonl"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    path.with_suffix(".meta.json").write_text(json.dumps({"output_sha256": "0" * 64}),
                                             encoding="utf-8")


def test_score_sources_stops_when_branches_saw_different_timelines(tmp_path: Path) -> None:
    from ml.captioning.lexicon import CaptionLexicon
    from ml.taxonomy import load_taxonomy
    from scripts.score_captions import score_sources

    lexicon = CaptionLexicon.from_taxonomy(
        load_taxonomy(Path(__file__).parents[1] / "ml/configs/taxonomy.yaml"))
    base = {"recording_id": "datased:S-0001", "duration_s": 10.0, "events": [
        {"event_id": 1, "class_id": "birds", "onset_s": 0.0, "offset_s": 2.0, "score": 1.0}]}
    shifted = {**base, "events": [{**base["events"][0], "onset_s": 0.5}]}
    _write_branch(tmp_path, "unconstrained", base)
    _write_branch(tmp_path, "constrained", shifted)
    sources = [tmp_path / "unconstrained_dev.jsonl", tmp_path / "constrained_dev.jsonl"]
    with pytest.raises(SystemExit, match="khác nhánh trước"):
        score_sources(sources, lexicon)
    scored, _ = score_sources(sources[:1], lexicon)  # template scored on the same timeline
    assert set(scored) == {("unconstrained", "oracle"), ("template", "oracle")}


def test_test_split_scoring_requires_the_frozen_lexicon() -> None:
    from scripts.generate_llm_captions import check_test_gate

    check_test_gate("dev", "a" * 64, None)  # dev is free
    check_test_gate("test", "a" * 64, "a" * 64)
    with pytest.raises(SystemExit, match="đóng băng"):
        check_test_gate("test", "a" * 64, "b" * 64)
