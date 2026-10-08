"""Class-balanced window sampling for SED training (ADR-0041 DO-4).

Train windows are drawn with replacement, each with weight `max over its classes of
(1 / share of windows containing that class) ** power`. A window with no event weighs like the
most common class, so silence is not oversampled. `power` 0.5 is fixed before the screening run
(square-root balancing: halfway between uniform windows and fully class-balanced ones).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np

DEFAULT_POWER = 0.5


def class_balanced_weights(window_classes: Sequence[frozenset[str]], *,
                           power: float = DEFAULT_POWER) -> np.ndarray:
    """One float64 weight per window, normalised to mean 1."""
    if not window_classes:
        raise ValueError("no windows to weight")
    if power < 0:
        raise ValueError("power must be >= 0")
    counts = Counter(label for classes in window_classes for label in classes)
    if not counts:
        return np.ones(len(window_classes))
    total = len(window_classes)
    per_class = {label: (total / count) ** power for label, count in counts.items()}
    floor = min(per_class.values())
    weights = np.array([max((per_class[label] for label in classes), default=floor)
                        for classes in window_classes], dtype=np.float64)
    return weights / weights.mean()


def expected_class_share(window_classes: Sequence[frozenset[str]],
                         weights: np.ndarray) -> dict[str, float]:
    """Share of drawn windows containing each class under `weights` (for the run manifest)."""
    probabilities = np.asarray(weights, dtype=np.float64) / float(np.sum(weights))
    shares: Counter[str] = Counter()
    for classes, probability in zip(window_classes, probabilities, strict=True):
        for label in classes:
            shares[label] += probability
    return {label: float(share) for label, share in sorted(shares.items())}
