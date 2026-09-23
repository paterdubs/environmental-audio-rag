"""Đóng băng split sau khi cổng D4 pass (DATA_PLAN §8.4, nghiệm thu W1).

    .venv/Scripts/python.exe -m scripts.freeze_split datased

Ghi `<split>.frozen.json` chứa SHA-256 của file split tại thời điểm đóng băng.
Từ đó `scripts.check_leakage` **từ chối chạy** nếu split hiện tại khác bản đã
đóng băng — sinh lại split mà quên chạy lại cổng là cách im lặng nhất để làm hỏng
mọi kết quả phía sau.

Chỉ đóng băng được khi D4 đã pass và không còn cặp nào chờ người quyết định.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from ml.dataops.registry import file_id_by_item, keys_for

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
SPLITS = ROOT / "data" / "splits"


def split_paths(dataset: str, label_mode: str) -> tuple[Path, Path, Path]:
    stem = f"{dataset}_{label_mode}"
    return SPLITS / f"{stem}.csv", SPLITS / f"{stem}.json", SPLITS / f"{stem}.frozen.json"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_gates_passed(dataset: str) -> tuple[dict, dict]:
    leakage_path = MANIFESTS / f"{dataset}_leakage_report.json"
    audit_path = MANIFESTS / "duplicate_audit.json"
    for path in (leakage_path, audit_path):
        if not path.exists():
            raise SystemExit(f"Thiếu {path}: chưa chạy đủ cổng D3/D4.")

    leakage = json.loads(leakage_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if not leakage.get("passed"):
        raise SystemExit("Cổng D4 chưa pass: không đóng băng split.")
    if not leakage.get("dedup_available"):
        raise SystemExit("Báo cáo D4 được sinh khi chưa có D3 (pass rỗng): chạy lại.")
    if audit.get("cross_dataset_exclusions_pending_split"):
        raise SystemExit("Chưa áp loại trừ xuyên dataset: chạy scripts.apply_cross_exclusions.")
    pending = audit.get("alarm", {}).get("pending_review_groups", 0)
    if pending:
        raise SystemExit(f"Còn {pending} cặp chờ người quyết định: không đóng băng split.")
    return leakage, audit


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def split_membership(dataset: str, csv_path: Path) -> tuple[dict[str, str], set[str]]:
    """`file_id` → `leakage_group` của split, và tập `file_id` có mặt."""
    item_col = keys_for(dataset).item_col
    mapping = file_id_by_item(dataset, MANIFESTS)
    groups: dict[str, str] = {}
    for row in _read_rows(csv_path):
        file_id = mapping.get(row[item_col])
        if file_id is None:
            raise SystemExit(f"{row[item_col]!r} không có trong manifest {dataset}.")
        groups[file_id] = row.get("leakage_group", "")
    return groups, set(groups)


def require_exclusion_policy(dataset: str, csv_path: Path) -> dict:
    """Loại trừ của D3 nghĩa gì với split này — phụ thuộc corpus, không phải một luật chung.

    `exclusions.csv` gộp hai động từ khác nhau dưới một tên. Với **benchmark**
    DataSED, `exclude_duplicate` nghĩa là "buộc cùng split", không phải "xoá":
    xoá đi thì benchmark teo lại, và đã đo được cả 13 file vẫn nằm trong split
    đã đóng băng. Với **corpus pretraining** DataSEC, loại trừ nghĩa là vắng mặt
    thật — clip trùng dev/test của benchmark mà lọt vào pretraining thì RQ1 mất
    nghĩa ([ADR-0010](../docs/decisions/ADR-0010-dinh-danh-datasec-va-cong-freeze.md)).
    """
    keys = keys_for(dataset)
    rows = [
        row
        for row in _read_rows(MANIFESTS / "exclusions.csv")
        if row["file_id"].startswith(f"{dataset}:")
    ]
    if not rows:
        return {"corpus": keys.corpus, "checked": 0, "must_be_absent": 0, "grouped": 0}

    groups, present = split_membership(dataset, csv_path)
    if not present:
        raise SystemExit(f"Split {dataset} rỗng sau khi phân giải file_id: kiểm sẽ pass rỗng.")

    must_be_absent = [row for row in rows if row["reason_code"] in keys.excluded_must_be_absent]
    leaked = sorted(row["file_id"] for row in must_be_absent if row["file_id"] in present)
    if leaked:
        raise SystemExit(
            f"{len(leaked)} file đã bị D3 loại vẫn nằm trong split {dataset}, "
            f"ví dụ {leaked[0]!r}. Sinh lại split sau khi áp loại trừ."
        )

    grouped = [row for row in rows if row["reason_code"] not in keys.excluded_must_be_absent]
    _require_same_leakage_group(grouped, groups)
    return {
        "corpus": keys.corpus,
        "checked": len(rows),
        "must_be_absent": len(must_be_absent),
        "grouped": len(grouped),
    }


def _require_same_leakage_group(rows: list[dict[str, str]], groups: dict[str, str]) -> None:
    """File trùng nội bộ được giữ lại thì phải cùng `leakage_group` với anh em của nó."""
    members: dict[str, list[str]] = defaultdict(list)
    for row in _read_rows(MANIFESTS / "duplicate_groups.csv"):
        members[row["group_id"]].append(row["file_id"])
    for row in rows:
        present = [item for item in members[row["group_id"]] if item in groups]
        distinct = {groups[item] for item in present}
        if len(distinct) > 1:
            raise SystemExit(
                f"Nhóm trùng {row['group_id']} trải trên {len(distinct)} leakage_group: "
                "split không phản ánh ràng buộc D3."
            )


def build_record(dataset: str, label_mode: str) -> dict:
    csv_path, metadata_path, _ = split_paths(dataset, label_mode)
    if not csv_path.exists():
        raise SystemExit(f"Thiếu {csv_path}. Chạy scripts.create_splits trước.")
    leakage, audit = require_gates_passed(dataset)
    exclusions = require_exclusion_policy(dataset, csv_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    digest = sha256_of(csv_path)
    if metadata.get("sha256") != digest:
        raise SystemExit(
            f"{csv_path.name} đã đổi sau khi sinh metadata "
            f"({digest[:16]}… vs {metadata['sha256'][:16]}…). Sinh lại split."
        )
    return {
        "dataset": dataset,
        "label_mode": label_mode,
        "frozen_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "split_sha256": digest,
        "taxonomy_sha256": metadata["taxonomy_sha256"],
        "config": metadata["config"],
        "items": metadata["summary"]["items"],
        "leakage_groups": metadata["leakage_groups"],
        "gates": {
            "d4_passed": leakage["passed"],
            "dedup_available": leakage["dedup_available"],
            "fingerprint_sha256": audit["fingerprint_sha256"],
            "standardizer_sha256": audit["standardizer_sha256"],
            "alarm_band": audit["alarm"]["band"],
            "leaked_pretraining_clips": audit["alarm"]["leaked_files"],
            # Con số trên đếm clip **DataSEC** trùng dev/test DataSED. Nó là một
            # dữ kiện toàn cục của cổng D3, không phải thuộc tính của split đang
            # đóng băng — ghi rõ phạm vi để bản ghi của DataSED không bị đọc
            # nhầm thành "DataSED rò rỉ 11 file".
            "leaked_clips_scope": "datasec clips overlapping datased dev/test",
            "exclusion_policy": exclusions,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=("datased", "datasec"))
    parser.add_argument("--label-mode", default=None)
    args = parser.parse_args()
    dataset_keys = keys_for(args.dataset)
    label_mode = args.label_mode or dataset_keys.label_modes[0]
    if label_mode not in dataset_keys.label_modes:
        raise SystemExit(f"{args.dataset} chỉ nhận label-mode {list(dataset_keys.label_modes)}.")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    record = build_record(args.dataset, label_mode)
    _, _, frozen_path = split_paths(args.dataset, label_mode)
    frozen_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"\nĐã đóng băng → {frozen_path}")


if __name__ == "__main__":
    main()
