from __future__ import annotations

import numpy as np

from ml.evaluation.calibration import calibration_bins, expected_calibration_error, fit_temperature
from scripts.calibrate_classifier import reliability_plot


def test_calibration_bins_account_for_every_item_and_ece() -> None:
    logits = np.log(np.asarray([[0.9, 0.1], [0.6, 0.4], [0.55, 0.45]]))
    targets = np.asarray([0, 1, 0])

    rows = calibration_bins(logits, targets, temperature=1.0, bins=2)

    assert sum(row.count for row in rows) == 3
    assert np.isclose(expected_calibration_error(rows), 1 / 60)


def test_temperature_fitting_reduces_dev_nll_without_changing_argmax_order() -> None:
    logits = np.asarray([[4.0, 0.0], [4.0, 0.0], [0.0, 4.0], [0.0, 4.0]])
    targets = np.asarray([0, 1, 1, 1])

    fit = fit_temperature(logits, targets, max_iterations=100, learning_rate=0.1)

    assert fit.temperature > 0
    assert fit.nll_after <= fit.nll_before
    assert np.array_equal(logits.argmax(axis=1), (logits / fit.temperature).argmax(axis=1))


def test_reliability_plot_writes_a_png_without_optional_plotting_packages(tmp_path) -> None:
    rows = calibration_bins(
        np.log(np.asarray([[0.9, 0.1], [0.6, 0.4]])), np.asarray([0, 1]), temperature=1.0, bins=2
    )
    output = tmp_path / "reliability.png"

    reliability_plot(rows, output)

    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
