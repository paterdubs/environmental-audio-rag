from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ml.dataops.datasec_labels import labels_by_file_id
from ml.dataops.grouping import build_leakage_groups, group_size_histogram, largest_group
from ml.dataops.registry import keys_for
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
        recordings[["recording_id", "file_id", "content_sha256"]],
        on="recording_id",
        validate="many_to_one",
    )
    rows["leakage_group"] = _leakage_group_column(rows)
    return rows, labels


def datasec_rows(taxonomy) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clip DataSEC ở dạng dài `(file_id, class_id)`, đã loại theo cổng D3.

    Khoá item là `file_id`: DataSEC không có `recording_id` và không được bịa ra
    ([ADR-0010](../docs/decisions/ADR-0010-dinh-danh-datasec-va-cong-freeze.md)).
    Mỗi clip sinh 1–2 dòng — coarse, và subclass nếu có — để bộ chia phân tầng
    trên **cả hai mức**, đúng tập mà cổng D4 sẽ đòi phủ (ADR-0011 §3).
    """
    keys = keys_for("datasec")
    manifests = ROOT / "data" / "manifests"
    inventory = pd.read_csv(manifests / keys.manifest)
    excluded = read_excluded_file_ids(manifests / "exclusions.csv", "datasec")
    kept = inventory[~inventory["file_id"].isin(excluded)]
    if len(kept) == len(inventory):
        raise SystemExit(
            "Không loại được clip nào của datasec khỏi split. exclusions.csv có "
            f"{len(excluded)} dòng nhưng không khớp file_id nào — lỗi lệch namespace."
        )

    labels_by_clip = labels_by_file_id(manifests / keys.manifest, taxonomy)
    pairs = [
        (str(file_id), label)
        for file_id in kept["file_id"].astype(str)
        for label in labels_by_clip[str(file_id)]
    ]
    labels = pd.DataFrame(pairs, columns=["file_id", "class_id"])
    rows = labels.merge(
        kept[["file_id", keys.hash_col]].rename(columns={keys.hash_col: "content_sha256"}),
        on="file_id",
        validate="many_to_one",
    )
    rows["leakage_group"] = _leakage_group_column(rows)
    return rows, labels


def read_excluded_file_ids(path: Path, dataset: str) -> set[str]:
    """`file_id` bị cổng D3 loại khỏi corpus của `dataset`.

    Với corpus pretraining, loại trừ nghĩa là **vắng mặt thật** — khác với
    benchmark, nơi trùng nội bộ chỉ bị buộc cùng split (ADR-0010 §3).
    """
    if not path.exists():
        raise SystemExit(f"Thiếu {path}: cổng D3 chưa chạy xong.")
    reasons = set(keys_for(dataset).excluded_must_be_absent)
    with path.open(encoding="utf-8") as handle:
        return {
            row["file_id"]
            for row in csv.DictReader(handle)
            if row["file_id"].startswith(f"{dataset}:") and row["reason_code"] in reasons
        }


def _leakage_group_column(rows: pd.DataFrame) -> pd.Series:
    """Khoá nhóm hợp nhất ba nguồn ràng buộc của cổng D3.

    `content_sha256` một mình chỉ chặn được trùng byte (T1/T2). Cặp T3 và cặp ở
    dải review phải được hợp nhất **trước** khi chia, nếu không kiểm 3 của
    [DATA_PLAN §8.4](../docs/DATA_PLAN.md) sẽ trượt — và trượt sau khi đã chia thì
    chỉ còn cách chia lại.
    """
    manifests = ROOT / "data" / "manifests"
    file_ids = list(rows["file_id"].astype(str))
    content = dict(zip(file_ids, rows["content_sha256"].astype(str), strict=True))
    groups = build_leakage_groups(
        file_ids,
        content_key=content,
        duplicate_groups=read_duplicate_groups(manifests / "duplicate_groups.csv"),
        cohesion_pairs=read_cohesion_pairs(manifests / "split_cohesion_pairs.csv"),
    )
    return pd.Series([groups[file_id] for file_id in file_ids], index=rows.index)


def read_duplicate_groups(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        raise SystemExit(
            f"Thiếu {path}: cổng D3 chưa chạy. Split sinh trước D3 sẽ phải sinh lại. "
            "Chạy scripts.find_duplicates detect trước."
        )
    groups: dict[str, list[str]] = defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[row["group_id"]].append(row["file_id"])
    return dict(groups)


def read_cohesion_pairs(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [(row["left_file_id"], row["right_file_id"]) for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic leakage-safe splits")
    parser.add_argument("dataset", choices=("datased", "datasec"))
    parser.add_argument("--label-mode", default=None)
    parser.add_argument("--seed", type=int, default=20260922)
    args = parser.parse_args()
    keys = keys_for(args.dataset)
    label_mode = args.label_mode or keys.label_modes[0]
    if label_mode not in keys.label_modes:
        raise SystemExit(f"{args.dataset} chỉ nhận label-mode {list(keys.label_modes)}.")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")

    if args.dataset == "datasec":
        rows, labels = datasec_rows(taxonomy)
    else:
        rows, labels = datased_rows(label_mode)
    train, validation, test = keys.split_ratio
    config = SplitConfig(train=train, validation=validation, test=test, seed=args.seed)
    assignments = grouped_multilabel_split(
        rows,
        item_col=keys.item_col,
        group_col="leakage_group",
        label_col="class_id",
        config=config,
    )
    if assignments.groupby("leakage_group")["split"].nunique().max() != 1:
        raise RuntimeError("Leakage group spans more than one split")
    summary = split_summary(
        assignments,
        labels,
        item_col=keys.item_col,
        label_col="class_id",
    )
    output = ROOT / "data" / "splits" / f"{args.dataset}_{label_mode}.csv"
    metadata = {
        "dataset": args.dataset,
        "label_mode": label_mode,
        "config": asdict(config),
        "taxonomy_version": taxonomy.version,
        "taxonomy_sha256": taxonomy.checksum,
        "leakage_groups": {
            "source": "content_sha256 + duplicate_groups.csv + split_cohesion_pairs.csv",
            "groups": int(rows["leakage_group"].nunique()),
            "largest": largest_group(
                dict(zip(rows[keys.item_col], rows["leakage_group"], strict=True))
            ),
            "size_histogram": group_size_histogram(
                dict(zip(rows[keys.item_col], rows["leakage_group"], strict=True))
            ),
        },
        "summary": summary,
    }
    digest = write_split(assignments, output, metadata=metadata)
    print(json.dumps({**metadata, "sha256": digest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
