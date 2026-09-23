"""Cổng D4: năm kiểm rò rỉ bắt buộc trước khi freeze split (DATA_PLAN §8.4).

    .venv/Scripts/python.exe -m scripts.check_leakage datased

Thoát với mã 1 khi bất kỳ kiểm nào trượt, để CI dùng được làm cổng thật.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

from ml.dataops.datasec_labels import labels_by_file_id
from ml.dataops.leakage import (
    CheckResult,
    check_class_coverage,
    check_cross_dataset_exclusions_applied,
    check_duplicate_pairs_within_split,
    check_group_integrity,
    check_hash_integrity,
    check_pretraining_exclusions_absent,
    run_all,
)
from ml.dataops.registry import (
    content_hash_by_file_id,
    coverage_labels,
    file_id_by_item,
    keys_for,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"


def file_id_by_recording(dataset: str) -> dict[str, str]:
    """Khoá item của split → `file_id`. Mọi khoá trong cổng này phải là `file_id`.

    Split DataSED lưu `recording_id` (`S-0233`), cổng D3 lưu `file_id`
    (`datased:<đường dẫn>.wav`). Trộn hai namespace làm mọi phép giao thành rỗng,
    và một cổng giao rỗng thì **luôn** báo pass. Đã xảy ra thật hai lần.

    DataSEC không có `recording_id` nên ánh xạ là đồng nhất — nhưng vẫn phải đi
    qua manifest để item lạ vỡ ra ở đây (ADR-0010).
    """
    return file_id_by_item(dataset, MANIFESTS)


def assert_matches_frozen(split_path: Path) -> None:
    """Split đã đóng băng thì không được đổi mà cổng vẫn im.

    Sinh lại split rồi quên chạy lại cổng là cách im lặng nhất để làm hỏng mọi
    kết quả phía sau: mọi số đã báo cáo đều gắn với một split cụ thể.
    """
    frozen_path = split_path.with_suffix(".frozen.json")
    if not frozen_path.exists():
        return
    expected = json.loads(frozen_path.read_text(encoding="utf-8"))["split_sha256"]
    actual = hashlib.sha256(split_path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(
            f"{split_path.name} khác bản đã đóng băng "
            f"({actual[:16]}… vs {expected[:16]}…).\n"
            "Split đã freeze thì mọi số đã báo cáo gắn với nó. Hoặc khôi phục split cũ, "
            f"hoặc xoá {frozen_path.name} và chạy lại toàn bộ cổng D3/D4 một cách có ý thức."
        )


def load_assignment(split_path: Path, dataset: str) -> tuple[dict[str, str], dict[str, str]]:
    """Trả về `(split theo file_id, nhóm rò rỉ theo file_id)`."""
    if not split_path.exists():
        raise SystemExit(f"Thiếu {split_path}. Chạy scripts.create_splits trước.")
    frame = pd.read_csv(split_path)
    if "leakage_group" not in frame.columns:
        raise SystemExit(
            f"{split_path} thiếu cột 'leakage_group': split được sinh trước khi cổng D3 "
            "được nối vào create_splits. Sinh lại split."
        )
    item_col = keys_for(dataset).item_col
    if item_col not in frame.columns:
        raise SystemExit(f"{split_path} thiếu cột khoá {item_col!r} của {dataset}.")
    mapping = file_id_by_recording(dataset)
    unknown = set(frame[item_col].astype(str)).difference(mapping)
    if unknown:
        raise SystemExit(f"{len(unknown)} {item_col} ngoài manifest, ví dụ {sorted(unknown)[0]}")

    assignment = {
        mapping[str(row[item_col])]: str(row["split"]) for _, row in frame.iterrows()
    }
    groups = {
        mapping[str(row[item_col])]: str(row["leakage_group"]) for _, row in frame.iterrows()
    }
    return assignment, groups


def load_duplicate_groups(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    groups: dict[str, list[str]] = defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[row["group_id"]].append(row["file_id"])
    return dict(groups)


def load_exclusions(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [row["file_id"] for row in csv.DictReader(handle)]


def load_exclusions_for_dataset(path: Path, dataset: str) -> list[str]:
    """`file_id` bị D3 loại khỏi corpus của `dataset`, đúng luật của corpus đó.

    Với DataSEC (pretraining), loại trừ nghĩa là vắng mặt thật — cả nội bộ
    (`exclude_duplicate`) lẫn xuyên dataset (`exclude_cross_dataset_leak`/
    `_unsure`). Dùng chung một luật cho mọi dataset là sai: nó từng làm trượt
    chính split DataSED đã đóng băng (ADR-0010).
    """
    if not path.exists():
        return []
    reasons = set(keys_for(dataset).excluded_must_be_absent)
    with path.open(encoding="utf-8") as handle:
        return [
            row["file_id"]
            for row in csv.DictReader(handle)
            if row["file_id"].startswith(f"{dataset}:") and row["reason_code"] in reasons
        ]


def load_recording_hashes(dataset: str) -> dict[str, str]:
    """Hash nội dung theo `file_id`. Tên cột khác nhau giữa hai manifest."""
    return content_hash_by_file_id(dataset, MANIFESTS)


def load_labels(dataset: str, label_mode: str, taxonomy) -> dict[str, list[str]]:
    """Nhãn theo `file_id`. Hai dataset công bố nhãn theo hai cách khác nhau.

    DataSED có bảng event; DataSEC **không có** file annotation nào — lớp nằm ở
    cây thư mục ([ADR-0011](../docs/decisions/ADR-0011-nhan-va-do-phu-lop-datasec.md)).
    """
    keys = keys_for(dataset)
    if keys.label_source == "directory":
        return labels_by_file_id(MANIFESTS / keys.manifest, taxonomy)
    path = ROOT / "data" / "annotations" / f"{dataset}_{label_mode}_events.csv"
    frame = pd.read_csv(path)
    mapping = file_id_by_recording(dataset)
    labels: dict[str, list[str]] = defaultdict(list)
    for recording_id, class_id in (
        frame[["recording_id", "class_id"]].drop_duplicates().itertuples(index=False, name=None)
    ):
        if recording_id in mapping:
            labels[mapping[recording_id]].append(str(class_id))
    return dict(labels)


def build_checks(
    dataset: str, label_mode: str, allowed_empty: list[str], *, allow_missing_dedup: bool
) -> list[CheckResult]:
    """Kiểm 3 và 5 không kiểm được gì nếu chưa có kết quả D3.

    Không chặn ở đây thì D4 có thể được tuyên bố "pass" mà chưa hề chạy dedup —
    đúng thứ mà cổng này tồn tại để ngăn.
    """
    if not (MANIFESTS / "duplicate_groups.csv").exists() and not allow_missing_dedup:
        raise SystemExit(
            "duplicate_groups.csv chưa tồn tại: cổng D3 chưa chạy. "
            "Kiểm 3 và 5 sẽ pass rỗng. Chạy scripts.find_duplicates detect trước, "
            "hoặc truyền --allow-missing-dedup để ghi nhận rõ trạng thái này."
        )
    split_path = ROOT / "data" / "splits" / f"{dataset}_{label_mode}.csv"
    assert_matches_frozen(split_path)
    assignment, groups = load_assignment(split_path, dataset)
    duplicate_groups = load_duplicate_groups(MANIFESTS / "duplicate_groups.csv")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    expected = coverage_labels(dataset, taxonomy)
    keys = keys_for(dataset)

    if keys.corpus == "pretraining":
        # DataSEC không có dev/test cần bảo vệ — nó *là* corpus pretraining.
        # Kiểm 5 hỏi câu tương ứng: clip đã bị D3 loại có thực sự vắng mặt
        # (ADR-0010 §3), không phải "loại trừ xuyên dataset đã áp lên benchmark".
        excluded = load_exclusions_for_dataset(MANIFESTS / "exclusions.csv", dataset)
        if not excluded:
            raise SystemExit(
                f"exclusions.csv không có dòng {dataset}: nào bị loại. Kiểm 5 sẽ pass rỗng."
            )
        fifth = check_pretraining_exclusions_absent(assignment, excluded)
    else:
        fifth = check_cross_dataset_exclusions_applied(
            assignment, duplicate_groups, load_exclusions(MANIFESTS / "exclusions.csv")
        )

    return [
        check_group_integrity(assignment, groups),
        check_hash_integrity(assignment, load_recording_hashes(dataset) or groups),
        check_duplicate_pairs_within_split(assignment, duplicate_groups),
        check_class_coverage(
            assignment,
            load_labels(dataset, label_mode, taxonomy),
            expected_classes=expected,
            allowed_empty=allowed_empty,
        ),
        fifth,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=("datased", "datasec"))
    parser.add_argument("--label-mode", default=None)
    parser.add_argument(
        "--allow-missing-dedup",
        action="store_true",
        help="Chạy khi chưa có D3. Kiểm 3 và 5 sẽ pass rỗng và báo cáo ghi rõ.",
    )
    parser.add_argument(
        "--allow-empty-class",
        action="append",
        default=[],
        help="Class được phép vắng ở một split. Phải nêu trong báo cáo.",
    )
    args = parser.parse_args()
    dataset_keys = keys_for(args.dataset)
    label_mode = args.label_mode or dataset_keys.label_modes[0]
    if label_mode not in dataset_keys.label_modes:
        raise SystemExit(f"{args.dataset} chỉ nhận label-mode {list(dataset_keys.label_modes)}.")
    # Console Windows mặc định cp1252, không in được tên kiểm bằng tiếng Việt.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    results = build_checks(
        args.dataset,
        label_mode,
        args.allow_empty_class,
        allow_missing_dedup=args.allow_missing_dedup,
    )
    dedup_available = (MANIFESTS / "duplicate_groups.csv").exists()
    report = run_all(results)
    report["dataset"] = args.dataset
    report["label_mode"] = label_mode
    report["dedup_available"] = dedup_available
    if not dedup_available:
        report["warning"] = "Kiểm 3 và 5 pass rỗng: chưa có duplicate_groups.csv"

    destination = MANIFESTS / f"{args.dataset}_leakage_report.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for result in results:
        print(result.summary)
        for violation in result.violations[:5]:
            print(f"    {violation}")
    print(f"\nreport: {destination}")
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
