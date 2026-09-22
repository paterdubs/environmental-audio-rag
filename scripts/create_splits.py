from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ml.dataops.splits import (
    SplitConfig,
    grouped_multilabel_split,
    split_summary,
    write_split,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]


def datased_rows(mode: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    recordings = pd.read_csv(ROOT / "data" / "manifests" / "datased_recordings.csv")
    events = pd.read_csv(ROOT / "data" / "annotations" / f"datased_{mode}_events.csv")
    labels = events[["recording_id", "class_id"]].drop_duplicates()
    missing = sorted(set(recordings["recording_id"]).difference(labels["recording_id"]))
    if missing:
        labels = pd.concat(
            [
                labels,
                pd.DataFrame(
                    {"recording_id": missing, "class_id": "__no_target_event__"}
                ),
            ],
            ignore_index=True,
        )
    rows = labels.merge(
        recordings[["recording_id", "content_sha256"]],
        on="recording_id",
        validate="many_to_one",
    )
    return rows, labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic leakage-safe splits")
    parser.add_argument("dataset", choices=("datased",))
    parser.add_argument("--label-mode", choices=("polyphonic", "monophonic"), default="polyphonic")
    parser.add_argument("--seed", type=int, default=20260922)
    args = parser.parse_args()
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")

    rows, labels = datased_rows(args.label_mode)
    config = SplitConfig(train=0.6, validation=0.2, test=0.2, seed=args.seed)
    assignments = grouped_multilabel_split(
        rows,
        item_col="recording_id",
        group_col="content_sha256",
        label_col="class_id",
        config=config,
    )
    if assignments.groupby("content_sha256")["split"].nunique().max() != 1:
        raise RuntimeError("Content group leakage detected")
    summary = split_summary(
        assignments,
        labels,
        item_col="recording_id",
        label_col="class_id",
    )
    output = ROOT / "data" / "splits" / f"datased_{args.label_mode}.csv"
    metadata = {
        "dataset": "datased",
        "label_mode": args.label_mode,
        "config": asdict(config),
        "taxonomy_version": taxonomy.version,
        "taxonomy_sha256": taxonomy.checksum,
        "summary": summary,
    }
    digest = write_split(assignments, output, metadata=metadata)
    print(json.dumps({**metadata, "sha256": digest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
