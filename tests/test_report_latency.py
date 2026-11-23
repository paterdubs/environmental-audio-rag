"""Hàm thuần của script đo độ trễ: chọn mẫu rải đều theo độ dài, trung vị và p95."""

from scripts import report_latency as latency


def _rows(n: int) -> list[dict]:
    return [{"id": f"S-{i}", "duration_s": float(i)} for i in range(n)]


def test_spread_is_deterministic_and_keeps_both_ends():
    rows = _rows(101)
    chosen = latency.spread(rows, 5)
    assert [r["id"] for r in chosen] == ["S-0", "S-25", "S-50", "S-75", "S-100"]
    assert latency.spread(rows, 5) == chosen


def test_spread_returns_everything_when_count_exceeds_rows():
    rows = _rows(3)
    assert latency.spread(rows, 10) == rows


def test_summarise_reports_median_p95_and_max():
    values = [1.0, 2.0, 3.0, 4.0, 100.0]
    summary = latency.summarise(values)
    assert summary["n"] == 5
    assert summary["median"] == 3.0
    assert summary["p95"] == 100.0
    assert summary["max"] == 100.0


def test_percentile_does_not_depend_on_input_order():
    assert latency.percentile([5.0, 1.0, 3.0], 0.5) == 3.0
