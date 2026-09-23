"""Temperature scaling and reliability measurements for frozen classifiers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch.nn import functional as functional


@dataclass(frozen=True)
class CalibrationBin:
    """One equal-width confidence bin used in expected calibration error."""

    lower: float
    upper: float
    count: int
    confidence: float
    accuracy: float


@dataclass(frozen=True)
class TemperatureFit:
    """A dev-only scalar temperature with its NLL before and after fitting."""

    temperature: float
    nll_before: float
    nll_after: float


def _validate(logits: np.ndarray, targets: np.ndarray) -> None:
    if logits.ndim != 2 or targets.ndim != 1 or len(logits) != len(targets):
        raise ValueError("logits must be [items, classes] and targets must be matching [items]")
    if not len(targets):
        raise ValueError("calibration requires at least one item")
    if not np.isfinite(logits).all() or (targets < 0).any() or (targets >= logits.shape[1]).any():
        raise ValueError("logits must be finite and targets must be valid class indices")


def fit_temperature(
    logits: np.ndarray,
    targets: np.ndarray,
    *,
    max_iterations: int,
    learning_rate: float,
) -> TemperatureFit:
    """Fit one positive temperature by minimizing cross-entropy on dev logits only."""
    _validate(logits, targets)
    if max_iterations < 1 or learning_rate <= 0:
        raise ValueError("temperature optimizer settings must be positive")
    values = torch.as_tensor(logits, dtype=torch.float64)
    labels = torch.as_tensor(targets, dtype=torch.long)
    log_temperature = torch.zeros((), dtype=torch.float64, requires_grad=True)
    optimizer = torch.optim.LBFGS(
        [log_temperature], lr=learning_rate, max_iter=max_iterations, line_search_fn="strong_wolfe"
    )

    def closure() -> torch.Tensor:
        optimizer.zero_grad()
        loss = functional.cross_entropy(values / log_temperature.exp(), labels)
        loss.backward()
        return loss

    nll_before = float(functional.cross_entropy(values, labels))
    optimizer.step(closure)
    temperature = float(log_temperature.detach().exp())
    nll_after = float(functional.cross_entropy(values / temperature, labels))
    return TemperatureFit(temperature, nll_before, nll_after)


def calibration_bins(
    logits: np.ndarray, targets: np.ndarray, *, temperature: float, bins: int
) -> list[CalibrationBin]:
    """Partition maximum softmax confidence into equal bins without dropping empty bins."""
    _validate(logits, targets)
    if temperature <= 0 or bins < 1:
        raise ValueError("temperature and bins must be positive")
    scaled = logits / temperature
    probabilities = np.exp(scaled - scaled.max(axis=1, keepdims=True))
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    prediction = probabilities.argmax(axis=1)
    confidence = probabilities[np.arange(len(prediction)), prediction]
    correct = prediction == targets
    edges = np.linspace(0.0, 1.0, bins + 1)
    output: list[CalibrationBin] = []
    for index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        selected = (confidence >= lower) & (confidence <= upper)
        if index:
            selected &= confidence > lower
        count = int(selected.sum())
        output.append(
            CalibrationBin(
                float(lower),
                float(upper),
                count,
                float(confidence[selected].mean()) if count else float("nan"),
                float(correct[selected].mean()) if count else float("nan"),
            )
        )
    return output


def expected_calibration_error(rows: list[CalibrationBin]) -> float:
    """Calculate standard confidence-weighted ECE from a complete bin partition."""
    total = sum(row.count for row in rows)
    if total < 1:
        raise ValueError("ECE requires at least one non-empty bin")
    return float(
        sum(row.count / total * abs(row.accuracy - row.confidence) for row in rows if row.count)
    )
