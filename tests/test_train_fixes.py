"""ADR-0041 DO-2 / DO-3: train-side label fixes."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.datasets.features import SedFeatureDataset
from ml.datasets.train_fixes import apply_train_fixes, duplicate_groups

TRAIN = pd.DataFrame([
    {"recording_id": "S-0001", "content_sha256": "a", "split": "train"},
    {"recording_id": "S-0002", "content_sha256": "dup", "split": "train"},
    {"recording_id": "S-0003", "content_sha256": "dup", "split": "train"},
    {"recording_id": "S-0704", "content_sha256": "w", "split": "train"},
])
EVENTS = pd.DataFrame([
    {"recording_id": "S-0001", "class_id": "birds", "onset_s": 0.0, "offset_s": 1.0},
    {"recording_id": "S-0002", "class_id": "horn", "onset_s": 0.0, "offset_s": 1.0},
    {"recording_id": "S-0003", "class_id": "horn", "onset_s": 0.5, "offset_s": 1.5},
    {"recording_id": "S-9999", "class_id": "birds", "onset_s": 0.0, "offset_s": 1.0},  # dev
])


def test_unannotated_recordings_leave_the_train_set():
    kept, _, report = apply_train_fixes(TRAIN, EVENTS, {"S-0704", "S-0705"},
                                        drop_unannotated=True, merge_duplicates=False)
    assert "S-0704" not in set(kept["recording_id"])
    assert report.dropped_unannotated == ("S-0704",)


def test_duplicates_merge_into_one_copy_with_half_weight_annotations():
    kept, weighted, report = apply_train_fixes(TRAIN, EVENTS, set(),
                                               drop_unannotated=False, merge_duplicates=True)
    assert set(kept["recording_id"]) == {"S-0001", "S-0002", "S-0704"}
    horn = weighted[weighted["class_id"] == "horn"]
    assert list(horn["recording_id"]) == ["S-0002", "S-0002"]
    assert list(horn["weight"]) == [0.5, 0.5]
    assert weighted.loc[weighted["recording_id"] == "S-0001", "weight"].tolist() == [1.0]
    assert "S-9999" not in set(weighted["recording_id"])  # only train events remain
    assert report.merged_duplicates == (("S-0002", "S-0003"),)


def test_disabled_fixes_change_nothing_but_add_unit_weights():
    kept, weighted, report = apply_train_fixes(TRAIN, EVENTS, {"S-0704"},
                                               drop_unannotated=False, merge_duplicates=False)
    assert kept.equals(TRAIN)
    assert set(weighted["weight"]) == {1.0}
    assert report.dropped_unannotated == () and report.merged_duplicates == ()


def test_fixes_refuse_non_train_rows():
    with pytest.raises(ValueError, match="train"):
        apply_train_fixes(TRAIN.assign(split="validation"), EVENTS, set(),
                          drop_unannotated=True, merge_duplicates=True)


def test_duplicate_groups_are_sorted_and_only_size_two_or_more():
    assert duplicate_groups(TRAIN) == [("S-0002", "S-0003")]


def test_soft_targets_sum_annotations_and_cap_at_one(tmp_path: Path):
    """Both annotators mark 0.5–1.0 s → 1.0; only one marks it → 0.5; hard labels unchanged."""
    np.save(tmp_path / "r.npy", np.zeros((4, 200), dtype=np.float32))
    recordings = pd.DataFrame([{"recording_id": "r", "feature_relative_path": "r.npy",
                                "frames": 200}])
    events = pd.DataFrame([
        {"recording_id": "r", "class_id": "horn", "onset_s": 0.0, "offset_s": 1.0, "weight": 0.5},
        {"recording_id": "r", "class_id": "horn", "onset_s": 0.5, "offset_s": 1.5, "weight": 0.5},
    ])
    common = {"feature_root": tmp_path, "class_ids": ("birds", "horn"), "frame_rate": 100.0,
              "window_frames": 200, "hop_frames": 200}
    target = SedFeatureDataset(recordings, events, **common)[0][1][:, 1].numpy()
    assert np.allclose(target[:50], 0.5) and np.allclose(target[50:100], 1.0)
    assert np.allclose(target[100:150], 0.5) and np.allclose(target[150:], 0.0)

    hard = SedFeatureDataset(recordings, events.drop(columns="weight"), **common)
    assert set(np.unique(hard[0][1][:, 1].numpy())) == {0.0, 1.0}
