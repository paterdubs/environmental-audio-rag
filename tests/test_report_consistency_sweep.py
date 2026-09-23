from __future__ import annotations

from pathlib import Path

from scripts.report_consistency_sweep import Candidate, select_candidate


def candidate(weight: float, coarse: float, parent: float, supported: float) -> Candidate:
    return Candidate(Path(f"run-{weight}"), weight, 1, coarse, supported, parent)


def test_selection_rejects_primary_metric_regression_before_parent_metric() -> None:
    selection = select_candidate(
        [
            candidate(0.0, 0.80, 0.90, 0.70),
            candidate(0.5, 0.79, 0.99, 0.95),
            candidate(1.0, 0.77, 1.00, 1.00),
        ],
        {
            "coarse_guardrail_drop": 0.02,
            "parent_consistency_tie": 0.005,
            "default_consistency_weight": 0.5,
        },
    )

    assert selection.selected.weight == 0.5
    assert [item.weight for item in selection.eligible] == [0.0, 0.5]


def test_selection_breaks_near_parent_tie_with_supported_subclass_score() -> None:
    selection = select_candidate(
        [
            candidate(0.0, 0.80, 0.90, 0.70),
            candidate(0.25, 0.81, 0.96, 0.80),
            candidate(0.5, 0.81, 0.964, 0.90),
        ],
        {
            "coarse_guardrail_drop": 0.02,
            "parent_consistency_tie": 0.005,
            "default_consistency_weight": 0.5,
        },
    )

    assert selection.selected.weight == 0.5
