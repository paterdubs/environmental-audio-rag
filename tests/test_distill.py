import numpy as np
import pandas as pd
import pytest

from ml.datasets.features import SedFeatureDataset
from ml.training.distill import average_teachers


def _dataset(tmp_path):
    np.save(tmp_path / "r.npy", np.zeros((4, 10), dtype=np.float32))
    recordings = pd.DataFrame({"recording_id": ["r"], "feature_relative_path": ["r.npy"],
                               "frames": [10]})
    events = pd.DataFrame({"recording_id": ["r"], "class_id": ["a"], "onset_s": [0.0],
                           "offset_s": [0.5]})
    return SedFeatureDataset(recordings, events, feature_root=tmp_path, class_ids=("a", "b"),
                             frame_rate=10.0, window_frames=10, hop_frames=10)


def test_soft_targets_mix_hard_label_with_teacher(tmp_path):
    dataset = _dataset(tmp_path)
    teacher = np.full((10, 2), 0.2, dtype=np.float32)
    dataset.set_soft_targets({"r": teacher}, hard_weight=0.5)
    _, target, _ = dataset[0]
    assert np.allclose(target[:5, 0], 0.6) and np.allclose(target[5:, 0], 0.1)
    assert np.allclose(target[:, 1], 0.1)


def test_soft_targets_refuse_missing_recording(tmp_path):
    with pytest.raises(ValueError):
        _dataset(tmp_path).set_soft_targets({"other": np.zeros((10, 2))}, hard_weight=0.5)


def test_average_teachers_truncates_to_common_frames():
    first = {"r": np.ones((5, 2)), "only_first": np.ones((3, 2))}
    second = {"r": np.zeros((4, 2))}
    averaged = average_teachers([first, second])
    assert set(averaged) == {"r"} and averaged["r"].shape == (4, 2)
    assert np.allclose(averaged["r"], 0.5)
