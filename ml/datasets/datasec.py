"""DataSEC hierarchical dataset and class-balanced sampling utilities.

The label source of truth is the directory layout audited in the DataSEC
manifest.  This module deliberately does not infer labels from audio content.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch
from torch import Tensor
from torch.utils.data import Dataset, Sampler

from ml.dataops.datasec_labels import path_labels as _path_labels
from ml.datasets.features import _fit_frames
from ml.taxonomy import Taxonomy, load_taxonomy


@dataclass(frozen=True)
class DataSECLabelSpace:
    """Config-driven coarse and subclass label order."""

    coarse_ids: tuple[str, ...]
    subclass_ids: tuple[str, ...]

    @classmethod
    def from_taxonomy(cls, taxonomy: Taxonomy) -> DataSECLabelSpace:
        return cls(
            coarse_ids=taxonomy.class_ids,
            subclass_ids=tuple(
                subclass for item in taxonomy.classes for subclass in item.subclasses
            ),
        )


def build_datasec_manifest(
    inventory: pd.DataFrame | Path,
    taxonomy: Taxonomy | Path,
) -> pd.DataFrame:
    """Add canonical coarse/subclass IDs to an audited inventory CSV."""
    rows = pd.read_csv(inventory) if isinstance(inventory, Path) else inventory.copy()
    if "relative_path" not in rows.columns:
        raise ValueError("DataSEC inventory requires relative_path")
    taxonomy = load_taxonomy(taxonomy) if isinstance(taxonomy, Path) else taxonomy
    labels = [_path_labels(str(path), taxonomy) for path in rows["relative_path"]]
    rows["class_id"] = [item[0] for item in labels]
    rows["subclass_id"] = [item[1] for item in labels]
    rows["clip_id"] = rows["file_id"].astype(str)
    return rows


class DataSECFeatureDataset(Dataset[tuple[Tensor, Tensor, Tensor]]):
    """Feature-backed DataSEC dataset yielding ``(x, coarse, subclass)``.

    Subclass targets are ``-1`` for the 12 coarse classes with no subclass
    annotation.  This makes the ignored target explicit for a hierarchical
    loss instead of silently pretending those clips belong to a class.
    """

    def __init__(
        self,
        rows: pd.DataFrame,
        *,
        feature_root: Path,
        label_space: DataSECLabelSpace,
        frames: int = 250,
        random_crop: bool = False,
    ) -> None:
        required = {"feature_relative_path", "class_id", "subclass_id"}
        if missing := required.difference(rows.columns):
            raise ValueError(f"DataSEC manifest missing: {sorted(missing)}")
        self.rows = rows.reset_index(drop=True)
        self.feature_root = feature_root
        self.coarse_index = {value: i for i, value in enumerate(label_space.coarse_ids)}
        self.subclass_index = {value: i for i, value in enumerate(label_space.subclass_ids)}
        unknown = set(self.rows["class_id"]).difference(self.coarse_index)
        if unknown:
            raise ValueError(f"Unknown coarse IDs: {sorted(unknown)}")
        subclasses = set(self.rows["subclass_id"].dropna()) - set(self.subclass_index)
        if subclasses:
            raise ValueError(f"Unknown subclass IDs: {sorted(subclasses)}")
        self.frames = frames
        self.random_crop = random_crop

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor, Tensor]:
        row = self.rows.iloc[index]
        feature = np.load(
            self.feature_root / str(row["feature_relative_path"]),
            mmap_mode="r",
            allow_pickle=False,
        )
        fitted = _fit_frames(feature, self.frames, random_crop=self.random_crop)
        coarse = self.coarse_index[str(row["class_id"])]
        subclass_value = row["subclass_id"]
        subclass = -1 if pd.isna(subclass_value) else self.subclass_index[str(subclass_value)]
        return (
            torch.from_numpy(fitted).unsqueeze(0),
            torch.tensor(coarse, dtype=torch.long),
            torch.tensor(subclass, dtype=torch.long),
        )

    def labels(self, level: Literal["coarse", "subclass"] = "coarse") -> list[int]:
        if level == "coarse":
            return [self.coarse_index[str(value)] for value in self.rows["class_id"]]
        return [
            -1 if pd.isna(value) else self.subclass_index[str(value)]
            for value in self.rows["subclass_id"]
        ]

    def low_support(self, minimum: int = 10) -> dict[str, int]:
        counts = Counter(str(value) for value in self.rows["subclass_id"].dropna())
        return {label: count for label, count in counts.items() if count < minimum}


class ClassBalancedSampler(Sampler[int]):
    """Sample each observed class with equal probability.

    Empty/ignored subclass labels (``-1``) are excluded.  A class with fewer
    examples is sampled with replacement, which is intentional for pretraining.
    """

    def __init__(
        self,
        labels: list[int] | tuple[int, ...] | np.ndarray,
        *,
        num_samples: int | None = None,
        seed: int = 20260922,
        ignore_index: int | None = None,
    ) -> None:
        values = [
            int(value)
            for value in labels
            if ignore_index is None or int(value) != ignore_index
        ]
        if not values:
            raise ValueError("Cannot balance an empty label set")
        self.indices_by_class = {
            label: np.asarray(
                [i for i, value in enumerate(labels) if int(value) == label],
                dtype=np.int64,
            )
            for label in sorted(set(values))
        }
        self.num_samples = len(values) if num_samples is None else int(num_samples)
        if self.num_samples < 1:
            raise ValueError("num_samples must be positive")
        self.seed = seed
        self.epoch = 0

    def __len__(self) -> int:
        return self.num_samples

    def set_epoch(self, epoch: int) -> None:
        self.epoch = int(epoch)

    def __iter__(self):
        generator = np.random.default_rng(self.seed + self.epoch)
        classes = np.asarray(list(self.indices_by_class), dtype=np.int64)
        chosen = generator.choice(classes, size=self.num_samples, replace=True)
        return iter(
            int(generator.choice(self.indices_by_class[int(label)])) for label in chosen
        )


def make_class_balanced_sampler(
    dataset: DataSECFeatureDataset,
    *,
    level: Literal["coarse", "subclass"] = "coarse",
    num_samples: int | None = None,
    seed: int = 20260922,
) -> ClassBalancedSampler:
    return ClassBalancedSampler(
        dataset.labels(level),
        num_samples=num_samples,
        seed=seed,
        ignore_index=-1 if level == "subclass" else None,
    )
