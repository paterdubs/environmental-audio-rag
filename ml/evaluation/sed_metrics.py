"""Thin adapters for the project's standard SED metric libraries.

The libraries are optional in the development environment.  We fail with an
actionable error instead of silently substituting a non-standard metric.
"""

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np


class MissingMetricDependency(RuntimeError):
    """Raised when a standards-based metric dependency is not installed."""


def _patch_psds_eval_for_numpy2() -> None:
    """Fix a numpy-2.x incompatibility in ``psds_eval`` 0.5.3's internal ``_auc``.

    ``PSDSEval._auc`` calls ``int(np.argwhere(_x == max_x))``. NumPy 2.x removed
    implicit scalar conversion for arrays with ``ndim > 0`` (even when
    ``size == 1``), so this raises ``TypeError: only 0-dimensional arrays can be
    converted to Python scalars`` on every real PSDS-1/PSDS-2 run with
    ``max_efpr`` outside the observed FPR range (H1, 2026-09-23) — not a data or
    fixture issue, reproduced with three independent fixtures. ``psds_eval`` is
    unmaintained (last release predates NumPy 2.0) and this is its only call
    site of that pattern. Patching one line via ``.item()`` is not
    reimplementing the metric — the AUC algorithm itself is untouched, only the
    NumPy-version-specific scalar extraction changes. Idempotent: safe to call
    more than once (e.g. if both `event_based_f1`-adjacent and `psds_score`
    import paths trigger it).
    """
    from psds_eval import psds as psds_module

    if getattr(psds_module.PSDSEval._auc, "_numpy2_patched", False):
        return

    def fixed_auc(x, y, max_x=None, decreasing_y=False):
        # Faithful copy of psds_eval.psds.PSDSEval._auc (0.5.3), with the one
        # broken line replaced. See docstring above for why.
        from psds_eval.psds import PSDSEvalError

        if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
            raise PSDSEvalError("x and y must be provided as a numpy.ndarray")
        if x.ndim > 1 or y.ndim > 1:
            raise PSDSEvalError("x or y are not 1-dimensional numpy.ndarray")
        if x.size != y.size:
            raise PSDSEvalError(f"x and y must be of equal length {x.size} != {y.size}")
        if np.any(np.diff(x) < 0):
            raise PSDSEvalError("non-decreasing property not verified for x")
        if not decreasing_y and np.any(np.diff(y) < 0):
            raise PSDSEvalError("non-decreasing property not verified for y")
        _x = np.array(x)
        _y = np.array(y)
        if max_x is None:
            max_x = _x.max()
        if max_x not in _x:
            _x = np.sort(np.concatenate([_x, [max_x]]))
            max_i = int(np.argwhere(_x == max_x).item())  # <- the fix
            _y = np.concatenate([_y[:max_i], [_y[max_i - 1]], _y[max_i:]])
        valid_idx = _x <= max_x
        dx = np.diff(_x[valid_idx])
        _y = np.array(_y[valid_idx])[:-1]
        if dx.size != _y.size:
            raise PSDSEvalError(f"{dx.size} != {_y.size}")
        return np.sum(dx * _y)

    fixed_auc._numpy2_patched = True
    psds_module.PSDSEval._auc = staticmethod(fixed_auc)


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
    _patch_psds_eval_for_numpy2()
    evaluator = PSDSEval(ground_truth=ground_truth, metadata=metadata, **dict(scenario))
    for operating_point in operating_points:
        evaluator.add_operating_point(*operating_point)
    result = evaluator.psds(
        alpha_ct=scenario.get("alpha_ct", 0.0),
        alpha_st=scenario.get("alpha_st", 1.0),
        max_efpr=scenario.get("max_efpr", 100.0),
    )
    # `.psds()` returns the `PSDS` namedtuple (value, plt, alpha_st, ...), not a
    # bare number — `float(result)` raised TypeError on every call before this
    # fix (H1, 2026-09-23; never exercised end-to-end until now).
    return float(result.value)
