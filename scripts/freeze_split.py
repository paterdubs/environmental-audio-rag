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
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

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


def build_record(dataset: str, label_mode: str) -> dict:
    csv_path, metadata_path, _ = split_paths(dataset, label_mode)
    if not csv_path.exists():
        raise SystemExit(f"Thiếu {csv_path}. Chạy scripts.create_splits trước.")
    leakage, audit = require_gates_passed(dataset)
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
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=("datased",))
    parser.add_argument("--label-mode", choices=("polyphonic", "monophonic"), default="polyphonic")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    record = build_record(args.dataset, args.label_mode)
    _, _, frozen_path = split_paths(args.dataset, args.label_mode)
    frozen_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"\nĐã đóng băng → {frozen_path}")


if __name__ == "__main__":
    main()
