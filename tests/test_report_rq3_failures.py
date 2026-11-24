from scripts.report_rq3_failures import classify, parser_divergence


def test_short_structured_list_attributes_missing_relevant_to_sed():
    counts = classify({"a", "b", "c"}, structured=["a", "x"], hybrid=["a", "x"])
    assert counts["hit"] == 1
    assert counts["sed_miss"] == 2
    assert counts["sed_false_match"] == 1
    assert counts["retrieved"] == 2


def test_full_structured_list_cannot_separate_cut_from_miss():
    full = [f"r{i}" for i in range(10)]
    counts = classify({"r0", "z"}, structured=full, hybrid=full)
    assert counts["hit"] == 1
    assert counts["beyond_top10_or_miss"] == 1
    assert counts["sed_miss"] == 0


def test_parser_divergence_counts_queries_with_different_hybrid_lists():
    def row(q, retrieved):
        return {"query_id": q, "mode": "hybrid", "language": "en", "retrieved": retrieved}
    gold = [row("q1", ["a"]), row("q2", ["b"])]
    parsed = [row("q1", ["a"]), row("q2", [])]
    assert parser_divergence(gold, parsed) == {"n": 2, "different": 1}
