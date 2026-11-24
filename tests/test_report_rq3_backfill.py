import math

import pytest

from scripts.report_rq3_backfill import (
    backfill,
    permutation_pvalue,
    rrf,
    score_queries,
    summarise,
    win_tie_loss,
)


def test_backfill_keeps_filtered_first_and_appends_unseen_vector_results():
    assert backfill(["a", "b"], ["c", "a", "d"]) == ["a", "b", "c", "d"]


def test_backfill_cuts_at_k_and_adds_nothing_when_hybrid_is_full():
    hybrid = [f"h{i}" for i in range(10)]
    assert backfill(hybrid, ["x", "y"]) == hybrid


def test_backfill_of_empty_hybrid_is_vector_list():
    assert backfill([], ["x", "y"]) == ["x", "y"]


def test_rrf_rewards_items_in_both_lists_and_breaks_ties_by_id():
    assert rrf([["b", "a"], ["a", "c"]])[0] == "a"
    assert rrf([["z"], ["y"]]) == ["y", "z"]


def test_permutation_pvalue_is_one_for_zero_effect_and_small_for_consistent_effect():
    assert permutation_pvalue([0.0, 0.0, 0.0]) == 1.0
    assert permutation_pvalue([0.5] * 20, n=2000) < 0.01


def test_win_tie_loss_counts():
    assert win_tie_loss([0.1, 0.0, -0.2, 0.3]) == {"win": 2, "tie": 1, "loss": 1}


def _query(qid: str) -> dict:
    return {"query_id": qid, "group": "single_class", "filters": {"classes_all": ["birds"]},
            "relevance": {"source": "ground_truth"}}


def _stored(qid, mode, retrieved, ndcg):
    return {"query_id": qid, "mode": mode, "language": "en", "retrieved": retrieved,
            "ndcg@10": ndcg}


def test_score_queries_recomputes_relevance_and_scores_backfill():
    gt = {"r1": [{"class_id": "birds", "onset_s": 0.0, "offset_s": 1.0}],
          "r2": [{"class_id": "birds", "onset_s": 0.0, "offset_s": 1.0}], "r3": []}
    ideal = 1 + 1 / math.log2(3)
    per_query = [_stored("q", "structured_only", ["r1"], 1 / ideal),
                 _stored("q", "hybrid", ["r1"], 1 / ideal),
                 _stored("q", "vector_only", ["r3", "r2"], (1 / math.log2(3)) / ideal)]
    rows = score_queries(per_query, {"q": _query("q")}, gt, "en")
    m = rows[0]["metrics"]
    assert m["backfill"]["ndcg@10"] == pytest.approx((1 + 1 / math.log2(4)) / ideal)
    assert m["backfill"]["tier1_share"] == pytest.approx(1 / 3)
    summary = summarise(rows + [{**rows[0], "query_id": "q2"}])
    assert summary["paired_ndcg@10"]["backfill−hybrid"]["win"] == 2


def test_score_queries_rejects_mismatch_with_stored_artifact():
    gt = {"r1": [{"class_id": "birds", "onset_s": 0.0, "offset_s": 1.0}]}
    per_query = [_stored("q", "structured_only", ["r1"], 1.0), _stored("q", "hybrid", ["r1"], 0.5),
                 _stored("q", "vector_only", ["r1"], 1.0)]
    with pytest.raises(ValueError, match="lệch"):
        score_queries(per_query, {"q": _query("q")}, gt, "en")
