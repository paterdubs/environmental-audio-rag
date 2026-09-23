from __future__ import annotations

import numpy as np

from ml.dataops.fmax_separation import (
    describe_scores,
    exceeds_global_negative_guard,
    top_centroid_classes,
)


def test_top_centroid_classes_uses_value_then_class_id_for_a_stable_ranking() -> None:
    assert top_centroid_classes({"birds": 2000.0, "bells": 2000.0, "voices": 1000.0}, 2) == [
        "bells",
        "birds",
    ]


def test_global_negative_guard_fails_when_the_p99_exceeds_the_locked_margin() -> None:
    scores = describe_scores(np.asarray([0.1, 0.2, 0.95]))

    assert exceeds_global_negative_guard(scores, global_max=0.92, allowed_excess=0.01)
