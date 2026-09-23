"""Thin adapters for the project's standard SED metric libraries.

The libraries are optional in the development environment.  We fail with an
actionable error instead of silently substituting a non-standard metric.
"""

from collections.abc import Iterable, Mapping
from typing import Any


class MissingMetricDependency(RuntimeError):
    """Raised when a standards-based metric dependency is not installed."""


def _events_by_recording(events: Mapping[str, Iterable[Mapping[str, Any]]]) -> list[dict]:
    rows = []
    for recording_id, recording_events in events.items():
        for event in recording_events:
            row = dict(event)
            row.setdefault("filename", recording_id)
            row.setdefault("event_label", row.get("class_id"))
            rows.append(row)
    return rows


def event_based_f1(
    reference: Mapping[str, Iterable[Mapping[str, Any]]],
    estimate: Mapping[str, Iterable[Mapping[str, Any]]],
    *,
    event_label_list: list[str],
    t_collar: float = 0.2,
    percentage_of_length: float = 0.2,
) -> dict[str, Any]:
    """Evaluate event F1 through :mod:`sed_eval` with the locked protocol."""
    try:
        import sed_eval
    except ImportError as exc:
        raise MissingMetricDependency(
            "event-based F1 requires sed_eval; install the pinned evaluation extras"
        ) from exc
    metric = sed_eval.sound_event.EventBasedMetrics(
        event_label_list=event_label_list,
        t_collar=t_collar,
        percentage_of_length=percentage_of_length,
    )
    metric.evaluate(
        reference_event_list=_events_by_recording(reference),
        estimated_event_list=_events_by_recording(estimate),
    )
    result = metric.results()
    return {
        "f_measure": result["overall"].get("f_measure", {}),
        "overall": result.get("overall", {}),
        "per_class": result.get("class_wise", {}),
        "config": {
            "t_collar": t_collar,
            "percentage_of_length": percentage_of_length,
        },
    }


def psds_score(
    *,
    ground_truth: Any,
    metadata: Any,
    operating_points: Iterable[Any],
    scenario: Mapping[str, float],
) -> float:
    """Run a frozen PSDS scenario through :mod:`psds_eval`.

    ``operating_points`` are passed to the library unchanged because their
    exact representation is defined by psds_eval (and may be DataFrames).
    """
    try:
        from psds_eval import PSDSEval
    except ImportError as exc:
        raise MissingMetricDependency(
            "PSDS requires psds_eval; install the pinned evaluation extras"
        ) from exc
    evaluator = PSDSEval(ground_truth=ground_truth, metadata=metadata, **dict(scenario))
    for operating_point in operating_points:
        evaluator.add_operating_point(*operating_point)
    return float(
        evaluator.psds(
            alpha_ct=scenario.get("alpha_ct", 0.0),
            alpha_st=scenario.get("alpha_st", 1.0),
            max_efpr=scenario.get("max_efpr", 100.0),
        )
    )
