import json
import math
from pathlib import Path

import pytest

from ml.retrieval import store
from ml.retrieval.relevance import satisfied

ROOT = Path(__file__).parents[1]


def test_filter_sql_combines_every_filter_with_named_parameters() -> None:
    where, params = store.filter_sql({
        "classes_all": ["birds", "voices"],
        "temporal": {"predicate": "before", "a": "birds", "b": "voices", "tolerance_s": 0.5},
        "duration": {"class_id": "birds", "min_s": 10.0}})
    assert where.count(" AND EXISTS") == 2 and "d.class_ids @> %(classes_all)s" in where
    assert "a.offset_s <= b.onset_s + %(tol)s" in where and ":tolerance_s" not in where
    assert params == {"classes_all": ["birds", "voices"], "ta": "birds", "tb": "voices",
                      "tol": 0.5, "dc": "birds", "dmin": 10.0}
    with pytest.raises(ValueError, match="hard filter"):
        store.filter_sql({})


def test_rank_metrics() -> None:
    from scripts.evaluate_retrieval import rank_metrics

    m = rank_metrics(["x", "a", "y", "b"], {"a", "b"}, [True, True, False, True])
    assert m["recall@1"] == 0 and m["recall@5"] == 1.0 and m["mrr"] == 0.5
    ideal = 1 + 1 / math.log2(3)
    assert m["ndcg@10"] == pytest.approx((1 / math.log2(3) + 1 / math.log2(5)) / ideal)
    assert m["filter_exactness"] == 0.75


def test_embedding_revision_is_read_from_refs_main(tmp_path: Path) -> None:
    from ml.retrieval.embedding import _revision

    ref = tmp_path / "models--BAAI--bge-m3" / "refs"
    ref.mkdir(parents=True)
    (ref / "main").write_text("abc123\n", encoding="utf-8")
    assert _revision(tmp_path) == "abc123"
    with pytest.raises(RuntimeError, match="not cached"):
        _revision(tmp_path / "missing")


def _connect_or_skip():
    try:
        conn = store.connect()
    except Exception as exc:  # no database in CI
        pytest.skip(f"PostgreSQL not available: {exc}")
    if conn.execute("SELECT to_regclass('retrieval_documents')").fetchone()[0] is None:
        pytest.skip("event store not loaded")
    return conn


@pytest.mark.parametrize("split", ["validation", "test"])
def test_sql_filters_select_exactly_what_the_python_semantics_select(split) -> None:
    """Integration: for every frozen query, SQL hard filters on the indexed events return the
    same recordings as `relevance.satisfied` — sound AND complete, not just a subset."""
    conn = _connect_or_skip()
    indexed = store.indexed_events(conn, split)
    corpus = [row[0] for row in conn.execute(
        "SELECT recording_id FROM recordings WHERE split = %s", (split,))]
    queries = json.loads((ROOT / "data/manifests/retrieval_queryset_v2.json").read_text("utf-8"))
    for query in queries:
        where, params = store.filter_sql(query["filters"])
        sql = sorted(row[0] for row in conn.execute(
            "SELECT d.recording_id FROM retrieval_documents d JOIN recordings r "
            "USING (recording_id) WHERE r.split = %(split)s AND " + where,
            {**params, "split": split}))
        python = sorted(rid for rid in corpus if satisfied(indexed.get(rid, []), query["filters"]))
        assert sql == python, query["query_id"]
