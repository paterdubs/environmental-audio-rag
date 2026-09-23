from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.datasets.datasec import (
    ClassBalancedSampler,
    DataSECFeatureDataset,
    DataSECLabelSpace,
    build_datasec_manifest,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")


def test_manifest_maps_coarse_and_subclass_from_audited_path() -> None:
    rows = pd.DataFrame(
        {
            "file_id": ["datasec:a.wav", "datasec:b.wav"],
            "relative_path": [
                "DATASEC/Bells/Bells-0001.wav",
                "DATASEC/Workshop/Drill/Drill-0001.wav",
            ],
        }
    )
    result = build_datasec_manifest(rows, TAXONOMY)
    assert result["class_id"].tolist() == ["bells", "workshop"]
    assert result["subclass_id"].tolist() == [None, "drill"]


def test_manifest_rejects_unknown_label() -> None:
    rows = pd.DataFrame({"file_id": ["x"], "relative_path": ["DATASEC/Unknown/x.wav"]})
    with pytest.raises(ValueError, match="Cannot map"):
        build_datasec_manifest(rows, TAXONOMY)


def test_feature_dataset_returns_ignored_subclass_and_config_order(tmp_path: Path) -> None:
    np.save(tmp_path / "a.npy", np.ones((4, 3), dtype=np.float32))
    rows = pd.DataFrame(
        {
            "feature_relative_path": ["a.npy", "a.npy"],
            "class_id": ["bells", "workshop"],
            "subclass_id": [None, "drill"],
        }
    )
    dataset = DataSECFeatureDataset(
        rows,
        feature_root=tmp_path,
        label_space=DataSECLabelSpace.from_taxonomy(TAXONOMY),
        frames=5,
    )
    x, coarse, subclass = dataset[0]
    assert x.shape == (1, 4, 5)
    assert coarse.item() == 0
    assert subclass.item() == -1
    assert dataset[1][2].item() == dataset.subclass_index["drill"]


def test_balanced_sampler_equalizes_classes_and_is_reproducible() -> None:
    sampler = ClassBalancedSampler([0, 0, 0, 1], num_samples=400, seed=7)
    first = list(iter(sampler))
    second = list(iter(sampler))
    assert first == second
    assert abs(sum(index < 3 for index in first) - sum(index == 3 for index in first)) < 60
    assert set(first).issubset({0, 1, 2, 3})


def test_balanced_sampler_ignores_unannotated_subclasses() -> None:
    sampler = ClassBalancedSampler([-1, 0, 1], num_samples=20, ignore_index=-1)
    assert all(index in (1, 2) for index in sampler)
