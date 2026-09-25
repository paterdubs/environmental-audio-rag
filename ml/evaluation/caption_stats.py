"""Aggregate caption grounding scores (C2) with recording-level uncertainty.

evaluation_protocol Q3: every headline number gets a bootstrap CI whose resampling
unit is the recording. Branch comparisons (RQ2) are *paired*: each bootstrap sample
draws recordings once and scores both branches on the same draw.

Two aggregation choices are explicit rather than implicit:

- ``temporal_order_eligible`` averages order accuracy only over captions with at
  least two mentions. A caption with 0–1 mention scores 1.0 by definition, so the
  plain mean rewards captions that say little.
- ``hallucination_micro`` pools mentions across captions (unsupported / all) next
  to the per-caption (macro) mean.

Order accuracy is the share of mention pairs in onset order (ties count as in
order) — not Kendall's tau; for tie-free data it equals (tau + 1) / 2.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from statistics import mean

from ml.evaluation.bootstrap import BootstrapCI, recording_bootstrap
from ml.evaluation.grounding import GroundingMetrics

Scores = Mapping[str, GroundingMetrics]  # recording_id -> metrics of one caption
PER_CAPTION = ("hallucination_rate", "omission_rate", "temporal_order_accuracy",
               "forbidden_term_rate", "over_specific_rate", "context_term_rate",
               "evidence_coverage", "n_mentions")
CI_METRICS = ("hallucination_rate", "omission_rate", "temporal_order_eligible",
              "over_specific_rate", "context_term_rate", "forbidden_term_rate")
MIN_ORDER_MENTIONS = 2


def aggregate(rows: Sequence[GroundingMetrics], metric: str) -> float:
    """One summary number over captions; NaN when no caption qualifies."""
    if metric == "temporal_order_eligible":
        eligible = [r.temporal_order_accuracy for r in rows if r.n_mentions >= MIN_ORDER_MENTIONS]
        return mean(eligible) if eligible else float("nan")
    if metric == "hallucination_micro":
        mentions = sum(r.n_mentions for r in rows)
        unsupported = sum(r.hallucination_rate * r.n_mentions for r in rows)
        return unsupported / mentions if mentions else 0.0
    return mean(getattr(r, metric) for r in rows)


def summarise(scores: Scores) -> dict[str, float]:
    rows = list(scores.values())
    summary = {"n": len(rows), **{m: aggregate(rows, m) for m in PER_CAPTION}}
    summary["temporal_order_eligible"] = aggregate(rows, "temporal_order_eligible")
    summary["n_temporal_eligible"] = sum(r.n_mentions >= MIN_ORDER_MENTIONS for r in rows)
    summary["hallucination_micro"] = aggregate(rows, "hallucination_micro")
    return summary


def _bootstrap(ids: list[str], statistic: Callable[[Sequence[str]], float]) -> BootstrapCI:
    return recording_bootstrap(ids, statistic)


def metric_ci(scores: Scores, metric: str) -> BootstrapCI:
    ids = sorted(scores)
    return _bootstrap(ids, lambda sample: aggregate([scores[i] for i in sample], metric))


def paired_difference(first: Scores, second: Scores, metric: str) -> BootstrapCI:
    """CI of aggregate(first) − aggregate(second), resampling recordings jointly."""
    if set(first) != set(second):
        raise ValueError("paired comparison needs the same recordings in both branches")
    ids = sorted(first)
    return _bootstrap(ids, lambda sample: (aggregate([first[i] for i in sample], metric)
                                           - aggregate([second[i] for i in sample], metric)))
