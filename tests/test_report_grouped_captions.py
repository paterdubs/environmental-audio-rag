import pytest

from scripts.report_grouped_captions import hedge_threshold, precision_gap


def test_hedge_threshold_is_the_lower_tercile_of_event_scores():
    timelines = [{"events": [{"score": s} for s in (0.1, 0.2, 0.3)]},
                 {"events": [{"score": s} for s in (0.4, 0.5, 0.6)]}]
    assert hedge_threshold(timelines) == pytest.approx(0.2666666, abs=1e-6)


def test_precision_gap_compares_unhedged_with_hedged_clauses():
    per_rec = [[(False, True), (True, False)], [(False, True), (True, True)]]
    gap = precision_gap(per_rec, n=200)
    counts = (gap["plain"], gap["plain_correct"], gap["hedged"], gap["hedged_correct"])
    assert counts == (2, 2, 2, 1)
    assert gap["estimate"] == pytest.approx(0.5)
    assert gap["n_valid_draws"] > 0
