"""Train-side label fixes of phase O (ADR-0041 DO-2, DO-3) — torch-free, dev/test untouched.

DO-2: recordings without polyphonic ground truth (the `wind_turbine` set S-0704…S-0717, PLAN
debt #25) were trained as "no event anywhere", although their monophonic labels show vehicles,
thunder, crows… in them. They are dropped from the training set; ADR-0034 already drops them
from scoring.

DO-3: byte-identical recordings were annotated twice, independently. Training on both copies
shows the model one audio with two conflicting targets, at double weight. Each group keeps one
copy whose events are the union of every annotation, each weighted 1/k, so a span both
annotators marked gets target 1 and a span only one marked gets 1/2 (soft labels from
annotator disagreement, as in RealDESED).

Raw annotations and the frozen split are never modified; this only shapes the train dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

UNANNOTATED_PATH = Path("data") / "manifests" / "datased_polyphonic_unannotated.csv"


@dataclass(frozen=True)
class TrainFixReport:
    dropped_unannotated: tuple[str, ...]
    merged_duplicates: tuple[tuple[str, ...], ...]  # (kept, dropped...) per group

    def as_manifest(self) -> dict[str, object]:
        return {"dropped_unannotated": list(self.dropped_unannotated),
                "merged_duplicates": [list(group) for group in self.merged_duplicates]}


def duplicate_groups(recordings: pd.DataFrame) -> list[tuple[str, ...]]:
    """Groups (sorted recording_ids) of identical audio, by content hash, size ≥ 2."""
    groups = recordings.groupby("content_sha256")["recording_id"].apply(sorted)
    return [tuple(ids) for ids in groups if len(ids) > 1]


def apply_train_fixes(train: pd.DataFrame, events: pd.DataFrame, unannotated: set[str], *,
                      drop_unannotated: bool, merge_duplicates: bool
                      ) -> tuple[pd.DataFrame, pd.DataFrame, TrainFixReport]:
    """Return (train recordings, events with a `weight` column, report).

    `train` must hold only train-split rows with `recording_id` and `content_sha256`.
    """
    if set(train.get("split", pd.Series(["train"]))) - {"train"}:
        raise ValueError("apply_train_fixes only shapes the train split")
    dropped = tuple(sorted(set(train["recording_id"]) & unannotated)) if drop_unannotated else ()
    kept = train[~train["recording_id"].isin(dropped)]
    weighted = events.assign(weight=1.0)
    merged: list[tuple[str, ...]] = []
    if merge_duplicates:
        for group in duplicate_groups(kept):
            keep_id, others = group[0], set(group[1:])
            mask = weighted["recording_id"].isin(group)
            weighted.loc[mask, "weight"] = 1.0 / len(group)
            weighted.loc[mask, "recording_id"] = keep_id
            kept = kept[~kept["recording_id"].isin(others)]
            merged.append(group)
    weighted = weighted[weighted["recording_id"].isin(set(kept["recording_id"]))]
    return kept, weighted.reset_index(drop=True), TrainFixReport(dropped, tuple(merged))


def load_unannotated(root: Path) -> set[str]:
    return set(pd.read_csv(root / UNANNOTATED_PATH)["recording_id"].astype(str))
