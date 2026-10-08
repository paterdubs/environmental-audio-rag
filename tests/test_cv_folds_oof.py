"""ADR-0041 tầng C: fold train ∪ dev, relabel cho train_sed, ghép OOF."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.evaluation.predictions import PredictionArtifact
from ml.taxonomy import load_taxonomy
from scripts.build_oof import concatenate, fold_of_members
from scripts.make_cv_folds import assign_group_folds

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml" / "configs" / "taxonomy.yaml")
CLASS_IDS = TAXONOMY.polyphonic_class_ids


def _artifact(recordings: list[str]) -> PredictionArtifact:
    shape = (len(recordings), 4, len(CLASS_IDS))
    return PredictionArtifact(
        logits=np.zeros(shape, dtype=np.float32), targets=np.zeros(shape, dtype=np.uint8),
        recording_ids=np.array(recordings), frame_offsets_s=np.zeros(len(recordings)),
        mask=np.ones(shape[:2], dtype=bool), class_ids=CLASS_IDS, split="dev",
        model_version="sed-v1.0", frame_hop_s=0.01, taxonomy_sha256=TAXONOMY.checksum)


FOLDS = pd.DataFrame({"recording_id": ["a", "b", "c", "d"], "fold": [0, 0, 1, 1]})


def test_group_folds_spread_rare_classes_and_balance_sizes():
    # columns: recordings, class0 (rare, 2 groups), class1 (common)
    counts = np.array([[1, 1, 0], [1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1]])
    folds = assign_group_folds([f"g{i}" for i in range(6)], counts, 2)
    assert folds[0] != folds[1]  # the two rare-class groups land in different folds
    assert sorted(np.bincount(folds)) == [3, 3]


def test_oof_members_must_each_cover_exactly_one_fold():
    assert fold_of_members([_artifact(["c", "d"]), _artifact(["a", "b"])], FOLDS) == [1, 0]
    with pytest.raises(ValueError, match="đúng một fold"):
        fold_of_members([_artifact(["a"]), _artifact(["c", "d"])], FOLDS)
    with pytest.raises(ValueError, match="thiếu hoặc lặp"):
        fold_of_members([_artifact(["a", "b"]), _artifact(["a", "b"])], FOLDS)


def test_oof_concatenation_keeps_every_window_and_refuses_mixed_weighting():
    merged = concatenate([_artifact(["a", "b"]), _artifact(["c", "d"])])
    assert list(merged.recording_ids) == ["a", "b", "c", "d"]
    assert merged.model_version == "sed-oof-v1.0"
    with pytest.raises(ValueError, match="window_weighting"):
        concatenate([_artifact(["a", "b"]),
                     replace(_artifact(["c", "d"]), window_weighting="triangular:0.3")])


def test_cv_fold_relabel_keeps_test_and_excludes_unfolded(monkeypatch, tmp_path):
    import scripts.train_sed as train_sed

    path = tmp_path / "folds.csv"
    FOLDS.to_csv(path, index=False)
    monkeypatch.setattr(train_sed, "CV_FOLDS_PATH", path)
    joined = pd.DataFrame({"recording_id": ["a", "b", "c", "d", "e", "t"],
                           "split": ["train", "validation", "train", "validation", "train",
                                     "test"]})
    relabeled = train_sed.apply_cv_fold(joined, 1)
    assert relabeled["split"].tolist() == ["train", "train", "validation", "validation",
                                           "excluded", "test"]
    assert train_sed.apply_cv_fold(joined, None) is joined
