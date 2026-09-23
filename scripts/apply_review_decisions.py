"""Áp quyết định người đã điền trong phiếu duyệt vào `exclusions.csv`.

    .venv/Scripts/python.exe -m scripts.apply_review_decisions

Chỉ đọc `review_worksheet.csv`. Dòng chưa điền `decision` bị bỏ qua và được đếm
lại, nên tiến độ duyệt luôn nhìn thấy được thay vì im lặng coi như xong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ml.dataops.duplicates import Exclusion, alarm_band
from ml.dataops.textio import count_mangled, read_csv_rows
from scripts.apply_cross_exclusions import (
    EXCLUSIONS_CSV,
    MANIFESTS,
    load_existing,
    merge_exclusions,
    write_exclusions,
)

WORKSHEET = MANIFESTS / "review_worksheet.csv"

# `unsure` xử lý như `duplicate`: loại nhầm một clip pretraining rẻ hơn nhiều so
# với giữ lại một rò rỉ vào dev/test của benchmark.
EXCLUDING_DECISIONS = {"duplicate", "unsure"}
VALID_DECISIONS = EXCLUDING_DECISIONS | {"distinct"}


def read_worksheet(path: Path) -> tuple[list[dict], str, int]:
    """Đọc phiếu người đã điền. Trả về `(rows, encoding, số ghi chú mất ký tự)`."""
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Chạy scripts.build_review_worksheet trước.")
    rows, encoding = read_csv_rows(path)
    return rows, encoding, count_mangled(rows, "note")


def validate(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Tách dòng đã quyết định khỏi dòng còn trống, và bác giá trị lạ."""
    decided: list[dict] = []
    pending: list[str] = []
    invalid: list[str] = []
    for row in rows:
        decision = (row.get("decision") or "").strip().lower()
        if not decision:
            pending.append(row["pair_id"])
            continue
        if decision not in VALID_DECISIONS:
            invalid.append(f"{row['pair_id']}={decision!r}")
            continue
        if not (row.get("decided_by") or "").strip():
            invalid.append(f"{row['pair_id']} thiếu decided_by")
            continue
        decided.append({**row, "decision": decision})
    if invalid:
        raise SystemExit(
            "Giá trị không hợp lệ trong phiếu duyệt: "
            + ", ".join(invalid[:10])
            + f"\nHợp lệ: {sorted(VALID_DECISIONS)}, và `decided_by` bắt buộc."
        )
    return decided, pending


def to_exclusions(decided: list[dict]) -> list[Exclusion]:
    """Quyết định của người luôn mang tiền tố `human:` để luật máy không lật được."""
    exclusions: list[Exclusion] = []
    for row in decided:
        if row["decision"] not in EXCLUDING_DECISIONS:
            continue
        decided_by = row["decided_by"].strip()
        exclusions.append(
            Exclusion(
                file_id=row["pretraining_file_id"],
                group_id=row["pair_id"],
                reason_code=(
                    "exclude_cross_dataset_leak"
                    if row["decision"] == "duplicate"
                    else "exclude_cross_dataset_unsure"
                ),
                decided_by=decided_by
                if decided_by.startswith("human:")
                else f"human:{decided_by}",
            )
        )
    return exclusions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worksheet", type=Path, default=WORKSHEET)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    rows, encoding, mangled = read_worksheet(args.worksheet)
    decided, pending = validate(rows)
    fresh = to_exclusions(decided)
    merged, added = merge_exclusions(load_existing(EXCLUSIONS_CSV), fresh)
    write_exclusions(EXCLUSIONS_CSV, merged)

    audit_path = MANIFESTS / "duplicate_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    leaked = len(
        {
            item.file_id
            for item in merged
            if item.reason_code.startswith("exclude_cross_dataset")
        }
    )
    total = audit["files"]["datasec"]
    band, action = alarm_band(leaked, total)
    notes = []
    if pending:
        notes.append(
            f"{len(pending)} cặp xuyên dataset chưa có quyết định người — "
            "tỷ lệ rò rỉ hiện tại là CẬN DƯỚI, không phải giá trị cuối"
        )
    audit["alarm"] = {
        **audit["alarm"],
        "leaked_files": leaked,
        "ratio": leaked / total,
        "band": band,
        "action": action,
        "pending_review_groups": len(pending),
        "notes": notes,
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "worksheet_encoding": encoding,
                "decided": len(decided),
                "pending": len(pending),
                "excluded_by_human": len(fresh),
                "exclusions_added": added,
                "leaked_total": leaked,
                "ratio": round(leaked / total, 6),
                "band": band,
            },
            indent=2,
        )
    )
    if pending:
        print(f"\nCòn {len(pending)} cặp trống, ví dụ: {pending[:5]}")
    if mangled:
        print(
            f"\nCẢNH BÁO: {mangled} ghi chú chứa ký tự '?' — dấu tiếng Việt đã mất khi "
            f"lưu bằng {encoding}. Quyết định không bị ảnh hưởng, nhưng ghi chú đi vào "
            "phụ lục khóa luận, nên viết lại và lưu UTF-8."
        )


if __name__ == "__main__":
    main()
