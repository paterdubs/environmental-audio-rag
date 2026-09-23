from __future__ import annotations

import numpy as np

from ml.dataops.fingerprint import FingerprintConfig
from scripts.find_duplicates import cropped_similarity, short_calibration_report


def test_cropped_similarity_requires_the_requested_duration() -> None:
    config = FingerprintConfig()
    matrix = np.ones((1, config.dimensions), dtype=np.float32)

    assert cropped_similarity(matrix, matrix, 1.5, config) is None


def test_short_calibration_report_does_not_claim_a_failed_threshold_is_kept() -> None:
    report = short_calibration_report(
        {
            "fingerprint_sha256": "fingerprint",
            "standardizer_sha256": "standardizer",
            "positive_pairs": {"tier1": 24, "cross_dataset": 2, "total": 26},
            "sample_pairs": 5000,
            "seed": 20260922,
            "durations": {
                "1.0": {
                    "frames": 1,
                    "positive_min": 0.98,
                    "negative_max": 0.97,
                    "separated_at_threshold": False,
                }
            },
            "short_duplicate_min": 0.99,
            "keep_short_duplicate_min": False,
        }
    )

    assert "not changed automatically" in report
    assert "| 1.0 | 1 | 0.980000 | 0.970000 | no |" in report
