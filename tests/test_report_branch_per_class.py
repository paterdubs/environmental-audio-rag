from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_branch_per_class import compare, load_per_class


def test_compare_uses_nan_as_missing_not_zero() -> None:
    result = compare([{"a": 0.2, "b": float("nan")}], [{"a": 0.4, "b": float("nan")}])
    assert result["a"]["mean_b"] == pytest.approx(0.2)
    assert result["a"]["delta"] == pytest.approx(0.2)
    assert result["a"]["n_pairs_c_gt_b"] == 1
    assert result["a"]["n_pairs"] == 1
    assert result["b"]["mean_b"] != result["b"]["mean_b"]
    assert result["b"]["n_pairs_c_gt_b"] == 0
    assert result["b"]["n_pairs"] == 0


def test_all_pairs_are_order_invariant_and_support_unequal_counts() -> None:
    branch_b = [{"a": 0.1}, {"a": 0.2}, {"a": 0.3}]
    branch_c = [{"a": 0.4}, {"a": 0.05}, {"a": 0.25}, {"a": 0.35}, {"a": 0.15}]
    forward = compare(branch_b, branch_c)
    reversed_order = compare(list(reversed(branch_b)), list(reversed(branch_c)))
    assert forward["a"]["mean_b"] == pytest.approx(reversed_order["a"]["mean_b"])
    assert forward["a"]["mean_c"] == pytest.approx(reversed_order["a"]["mean_c"])
    assert forward["a"]["delta"] == pytest.approx(reversed_order["a"]["delta"])
    assert forward["a"]["n_pairs_c_gt_b"] == reversed_order["a"]["n_pairs_c_gt_b"]
    assert forward["a"]["n_pairs"] == 15
    assert forward["a"]["n_pairs_c_gt_b"] == 9
    assert isinstance(forward["a"]["n_pairs_c_gt_b"], int)


def test_load_per_class_reads_nested_f_measure(tmp_path: Path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "manifest.json").write_text(json.dumps({"complete": True}), encoding="utf-8")
    (run / "evaluation.json").write_text(json.dumps({"event_based_f1_per_class": {
        "a": {"f_measure": 0.5}, "b": {"f_measure": None}}}), encoding="utf-8")
    values = load_per_class(run)
    assert values["a"] == 0.5
    assert values["b"] != values["b"]
