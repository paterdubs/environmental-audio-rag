from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit


@dataclass(frozen=True)
class SplitConfig:
    train: float = 0.7
    validation: float = 0.15
    test: float = 0.15
    seed: int = 20260922

    def validate(self) -> None:
        values = (self.train, self.validation, self.test)
        if any(value <= 0 for value in values):
            raise ValueError("Every split ratio must be positive")
        if not np.isclose(sum(values), 1.0):
            raise ValueError("Split ratios must sum to 1")


def grouped_multilabel_split(
    rows: pd.DataFrame,
    *,
    item_col: str,
    group_col: str,
    label_col: str,
    config: SplitConfig,
) -> pd.DataFrame:
    """Split items after collapsing leakage groups into multilabel samples."""
    config.validate()
    required = {item_col, group_col, label_col}
    missing = required.difference(rows.columns)
    if missing:
        raise ValueError(f"Missing split columns: {sorted(missing)}")
    if rows.empty:
        raise ValueError("Cannot split an empty manifest")
    if rows[list(required)].isna().any().any():
        raise ValueError("Split keys and labels cannot be null")
    item_groups = rows.groupby(item_col, observed=True)[group_col].nunique()
    if (item_groups > 1).any():
        raise ValueError(f"Each {item_col} must belong to exactly one {group_col}")

    labels = sorted(rows[label_col].astype(str).unique())
    label_index = {label: index for index, label in enumerate(labels)}
    groups = sorted(rows[group_col].astype(str).unique())
    group_index = {group: index for index, group in enumerate(groups)}
    targets = np.zeros((len(groups), len(labels)), dtype=np.uint8)
    for group, label in rows[[group_col, label_col]].itertuples(index=False, name=None):
        targets[group_index[str(group)], label_index[str(label)]] = 1

    indices = np.arange(len(groups))
    holdout_ratio = config.validation + config.test
    first = MultilabelStratifiedShuffleSplit(
        n_splits=1,
        test_size=holdout_ratio,
        random_state=config.seed,
    )
    train_indices, holdout_indices = next(first.split(indices, targets))

    validation_share = config.validation / holdout_ratio
    second = MultilabelStratifiedShuffleSplit(
        n_splits=1,
        test_size=1.0 - validation_share,
        random_state=config.seed + 1,
    )
    validation_local, test_local = next(
        second.split(holdout_indices, targets[holdout_indices])
    )
    split_by_group = {groups[index]: "train" for index in train_indices}
    split_by_group.update(
        {groups[holdout_indices[index]]: "validation" for index in validation_local}
    )
    split_by_group.update({groups[holdout_indices[index]]: "test" for index in test_local})

    result = rows[[item_col, group_col]].drop_duplicates().copy()
    result["split"] = result[group_col].astype(str).map(split_by_group)
    return result.sort_values(item_col).reset_index(drop=True)


def split_summary(
    assignments: pd.DataFrame,
    labels: pd.DataFrame,
    *,
    item_col: str,
    label_col: str,
) -> dict:
    merged = assignments[[item_col, "split"]].merge(
        labels[[item_col, label_col]], on=item_col, validate="one_to_many"
    )
    counts = (
        merged.groupby(["split", label_col], observed=True)
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    return {
        "items": assignments.groupby("split")[item_col].nunique().sort_index().to_dict(),
        "label_occurrences": counts.to_dict(orient="index"),
    }


def write_split(
    assignments: pd.DataFrame,
    path: Path,
    *,
    metadata: dict,
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    assignments.to_csv(path, index=False, lineterminator="\n")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    metadata_path = path.with_suffix(".json")
    metadata_path.write_text(
        json.dumps({**metadata, "sha256": digest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return digest
