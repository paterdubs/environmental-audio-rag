"""ADR-0041 DO-4: class-balanced window weights and the jittered crop around a sampled window."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.datasets.features import SedFeatureDataset
from ml.training.sampling import class_balanced_weights, expected_class_share


def test_rare_class_windows_weigh_more_and_silence_weighs_like_the_commonest() -> None:
    classes = [frozenset({"a"})] * 8 + [frozenset({"b"})] * 2 + [frozenset()] * 2
    weights = class_balanced_weights(classes, power=0.5)
    assert weights.mean() == pytest.approx(1.0)
    a, b, silent = weights[0], weights[8], weights[10]
    assert b / a == pytest.approx((12 / 2) ** 0.5 / (12 / 8) ** 0.5)
    assert silent == pytest.approx(a)


def test_window_with_several_classes_takes_its_rarest_weight() -> None:
    classes = [frozenset({"a"})] * 9 + [frozenset({"a", "b"})]
    weights = class_balanced_weights(classes, power=1.0)
    assert weights[9] / weights[0] == pytest.approx((10 / 1) / (10 / 10))


def test_power_zero_is_uniform_and_sampling_raises_rare_share() -> None:
    classes = [frozenset({"a"})] * 9 + [frozenset({"b"})]
    assert np.allclose(class_balanced_weights(classes, power=0.0), 1.0)
    weights = class_balanced_weights(classes, power=0.5)
    uniform = expected_class_share(classes, np.ones(10))
    sampled = expected_class_share(classes, weights)
    assert uniform["b"] == pytest.approx(0.1) and sampled["b"] > uniform["b"]


def _dataset(jitter: int | None, random_crop: bool = True) -> SedFeatureDataset:
    recordings = pd.DataFrame({"recording_id": ["r1", "r2"], "feature_relative_path": ["x", "y"],
                               "frames": [400, 100]})
    events = pd.DataFrame({"recording_id": ["r1", "r1"], "class_id": ["a", "b"],
                           "onset_s": [0.5, 3.2], "offset_s": [1.0, 3.5]})
    return SedFeatureDataset(recordings, events, feature_root=Path("."), class_ids=("a", "b"),
                             frame_rate=100.0, window_frames=100, hop_frames=100,
                             random_crop=random_crop, crop_jitter_frames=jitter)


def test_window_classes_follow_the_nominal_windows() -> None:
    assert _dataset(None).window_classes() == [frozenset({"a"}), frozenset(), frozenset(),
                                               frozenset({"b"}), frozenset()]


def test_jittered_crop_stays_near_its_window_and_inside_the_recording() -> None:
    dataset = _dataset(25)
    np.random.seed(0)
    for index in range(4):  # the four 100-frame windows of r1
        window = dataset.windows[index]
        starts = {dataset._cropped(window).start_frame for _ in range(200)}
        assert min(starts) >= max(window.start_frame - 25, 0)
        assert max(starts) <= min(window.start_frame + 25, 300)
    short = dataset.windows[4]  # r2 fits in one window: never cropped
    assert dataset._cropped(short) == short


def test_jitter_requires_random_crop() -> None:
    with pytest.raises(ValueError, match="random_crop"):
        _dataset(25, random_crop=False)
