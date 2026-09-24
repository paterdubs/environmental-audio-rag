from __future__ import annotations

import math

from scripts.report_median_filter_ablation import class_f1


def _result(f_measure: float | None) -> dict:
    return {"per_class": {"a": {"f_measure": {"f_measure": f_measure}}}}


def test_class_f1_extracts_value() -> None:
    assert class_f1(_result(0.75), "a") == 0.75


def test_class_f1_returns_none_for_missing_class() -> None:
    assert class_f1(_result(0.75), "b") is None


def test_class_f1_returns_none_for_nan() -> None:
    assert class_f1(_result(math.nan), "a") is None
