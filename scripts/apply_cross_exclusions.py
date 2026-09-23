"""Mắt nối giữa D3 và D4: áp luật loại trừ xuyên dataset **sau** khi có split.

    .venv/Scripts/python.exe -m scripts.apply_cross_exclusions datased

Luật của [DATA_PLAN §7.5](../docs/DATA_PLAN.md) không áp được lúc `find_duplicates`
chạy, vì nó cần biết recording DataSED nào rơi vào dev/test — mà split lại phải
sinh **sau** D3. Script này chạy giữa hai bước đó.

Thứ tự đúng của cổng:

    find_duplicates detect  →  create_splits  →  apply_cross_exclusions  →  check_leakage
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

from ml.dataops.duplicates import (
    DuplicateGroup,
    Exclusion,
    alarm_band,
    cross_dataset_exclusions,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
GROUPS_CSV = MANIFESTS / "duplicate_groups.csv"
EXCLUSIONS_CSV = MANIFESTS / "exclusions.csv"


def load_groups(path: Path) -> list[DuplicateGroup]:
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Chạy scripts.find_duplicates detect trước.")
    members: dict[str, list[str]] = defaultdict(list)
    attributes: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            members[row["group_id"]].append(row["file_id"])
            attributes[row["group_id"]] = row
    return [
        DuplicateGroup(
            group_id=group_id,
            members=tuple(sorted(files)),
            tiers=tuple(attributes[group_id]["tiers"].split("|")),  # type: ignore[arg-type]
            min_similarity=float(attributes[group_id]["min_similarity"]),
            cross_dataset=attributes[group_id]["cross_dataset"] == "true",
            needs_review=attributes[group_id]["needs_review"] == "true",
        )
        for group_id, files in sorted(members.items())
    ]


def load_split(path: Path, dataset: str) -> dict[str, str]:
    """Ánh xạ `file_id` → split, đi qua manifest recording để lấy đúng `file_id`.

    Split lưu `recording_id` (`S-0233`) còn cổng D3 dùng `file_id` đầy đủ
    (`datased:<đường dẫn>.wav`). Ghép `f"{dataset}:{recording_id}"` cho ra một
    khoá **không khớp gì cả**, và luật loại trừ im lặng trả về rỗng. Đã xảy ra
    thật: `S-0233` nằm ở validation, trùng similarity 1.000000 với một clip
    DataSEC, mà báo cáo vẫn ghi "0 clip rò rỉ".
    """
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Chạy scripts.create_splits trước.")
    frame = pd.read_csv(path)
    if "file_id" in frame.columns:
        return {str(row["file_id"]): str(row["split"]) for _, row in frame.iterrows()}

    recordings_path = MANIFESTS / f"{dataset}_recordings.csv"
    if not recordings_path.exists():
        raise SystemExit(f"Thiếu {recordings_path}: không suy được file_id từ recording_id.")
    recordings = pd.read_csv(recordings_path)
    by_recording = dict(zip(recordings["recording_id"], recordings["file_id"], strict=True))
    unknown = set(frame["recording_id"]).difference(by_recording)
    if unknown:
        raise SystemExit(
            f"{len(unknown)} recording_id không có trong manifest, ví dụ {sorted(unknown)[0]}"
        )
    return {
        str(by_recording[row["recording_id"]]): str(row["split"]) for _, row in frame.iterrows()
    }


def assert_split_covers_groups(
    groups: list[DuplicateGroup], split: dict[str, str], *, benchmark: str = "datased"
) -> None:
    """Chặn lệch namespace: nhóm xuyên dataset phải khớp được split.

    Không có kiểm này thì một khoá sai cho ra "0 clip rò rỉ" — kết quả trông
    giống hệt "sạch thật".
    """
    members = {
        member
        for group in groups
        if group.cross_dataset
        for member in group.members
        if member.startswith(f"{benchmark}:")
    }
    if members and not members & set(split):
        raise SystemExit(
            f"Namespace mismatch: {len(members)} recording {benchmark} trong nhóm xuyên "
            f"dataset không khớp khoá split nào. Ví dụ nhóm có {sorted(members)[0]!r}, "
            f"split có {sorted(split)[0]!r}."
        )


def load_existing(path: Path) -> list[Exclusion]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [
            Exclusion(
                file_id=row["file_id"],
                group_id=row["group_id"],
                reason_code=row["reason_code"],
                decided_by=row["decided_by"],
            )
            for row in csv.DictReader(handle)
        ]


def merge_exclusions(
    existing: list[Exclusion], fresh: list[Exclusion]
) -> tuple[list[Exclusion], int]:
    """Gộp, giữ quyết định của người nguyên vẹn.

    Dòng `decided_by: human:…` **không bao giờ** bị ghi đè bởi một luật tự động.
    Một quyết định đã có người ký tên thì máy không được lật.
    """
    by_file = {item.file_id: item for item in existing}
    added = 0
    for item in fresh:
        current = by_file.get(item.file_id)
        if current is not None and current.decided_by.startswith("human:"):
            continue
        if current is None:
            added += 1
        by_file[item.file_id] = item
    return sorted(by_file.values(), key=lambda item: item.file_id), added


def write_exclusions(path: Path, exclusions: list[Exclusion]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file_id", "group_id", "reason_code", "decided_by"])
        for item in exclusions:
            writer.writerow([item.file_id, item.group_id, item.reason_code, item.decided_by])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=("datased",))
    parser.add_argument("--label-mode", choices=("polyphonic", "monophonic"), default="polyphonic")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    groups = load_groups(GROUPS_CSV)
    split = load_split(
        ROOT / "data" / "splits" / f"{args.dataset}_{args.label_mode}.csv", args.dataset
    )
    assert_split_covers_groups(groups, split)
    fresh = cross_dataset_exclusions(groups, datased_split=split)
    merged, added = merge_exclusions(load_existing(EXCLUSIONS_CSV), fresh)
    write_exclusions(EXCLUSIONS_CSV, merged)

    audit_path = MANIFESTS / "duplicate_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    leaked = len({item.file_id for item in fresh})
    total = audit["files"]["datasec"]
    band, action = alarm_band(leaked, total)
    audit["cross_dataset_exclusions_pending_split"] = False
    audit["alarm"] = {
        **audit["alarm"],
        "leaked_files": leaked,
        "ratio": leaked / total,
        "band": band,
        "action": action,
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "cross_dataset_groups": sum(1 for group in groups if group.cross_dataset),
                "leaked_pretraining_clips": leaked,
                "ratio": round(leaked / total, 6),
                "exclusions_added": added,
                "exclusions_total": len(merged),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
