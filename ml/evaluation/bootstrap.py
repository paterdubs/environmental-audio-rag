"""Recording-level bootstrap confidence intervals.

The unit of resampling is deliberately a recording, never an individual
frame or event.  The statistic is supplied by the caller so this utility can
be used for event-F1, PSDS-derived summaries, or per-class metrics.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BootstrapCI:
    estimate: float
    lower: float
    upper: float
    confidence: float
    n_recordings: int
    n_bootstrap: int


def recording_bootstrap(
    recordings: Sequence[object],
    statistic: Callable[[Sequence[object]], float],
    *,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 20260922,
) -> BootstrapCI:
    """Estimate a statistic and percentile CI by recording-level resampling."""
    if len(recordings) < 2:
        raise ValueError("at least two recordings are required for bootstrap")
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    values = list(recordings)
    estimate = float(statistic(values))
    rng = np.random.default_rng(seed)
    samples = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        sample_indices = rng.integers(0, len(values), size=len(values))
        samples[index] = float(statistic([values[i] for i in sample_indices]))
    alpha = (1.0 - confidence) / 2.0
    lower, upper = np.quantile(samples, [alpha, 1.0 - alpha])
    return BootstrapCI(
        estimate=estimate,
        lower=float(lower),
        upper=float(upper),
        confidence=confidence,
        n_recordings=len(values),
        n_bootstrap=n_bootstrap,
    )
