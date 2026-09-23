"""Sinh measurement Markdown cho cổng D3 từ artifact đã ghi.

Usage:
    python -m scripts.report_duplicates

Đọc `duplicate_audit.json`, `threshold_calibration.json`, `duplicate_groups.csv`
và inventory. Không nhận số nào từ tay người.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from ml.dataops.datasec_labels import labels_by_file_id
from ml.dataops.textio import read_csv_rows
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
INTERIM = ROOT / "data" / "interim" / "dedup"
MEASUREMENTS = ROOT / "docs" / "measurements"

BAND_NOTE = {
    "clean": "RQ1 hợp lệ như thiết kế",
    "minor": "Loại, ghi số vào báo cáo, RQ1 vẫn hợp lệ",
    "material": "Loại, **chạy lại nhánh C**, nêu rõ trong Hạn chế",
    "invalidating": "**Δ transfer không còn diễn giải được như transfer.** "
    "RQ1 chuyển thành kết quả âm tính",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Thiếu artifact: {path}. Chạy scripts.find_duplicates trước.")
    return json.loads(path.read_text(encoding="utf-8"))


def read_groups(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def group_stats(rows: list[dict]) -> dict:
    members_by_group: dict[str, list[dict]] = {}
    for row in rows:
        members_by_group.setdefault(row["group_id"], []).append(row)
    sizes = Counter(len(members) for members in members_by_group.values())
    return {
        "groups": len(members_by_group),
        "members": len(rows),
        "sizes": dict(sorted(sizes.items())),
        "cross": sum(
            1
            for members in members_by_group.values()
            if members[0]["cross_dataset"] == "true"
        ),
        "largest": max((len(members) for members in members_by_group.values()), default=0),
    }


def calibration_section(calibration: dict) -> list[str]:
    separation = calibration["separation"]
    positives, negatives = calibration["positives"], calibration["negatives"]
    return [
        "## Hiệu chuẩn ngưỡng T3",
        "",
        f"Positive: {positives.get('count', 0)} cặp T1 byte-identical. "
        f"Negative: {negatives.get('count', 0)} cặp ngẫu nhiên khác nhãn "
        f"(seed {calibration['seed']}).",
        "",
        "| Đại lượng | Giá trị |",
        "|---|---:|",
        f"| positive min | {separation['positive_min']:.6f} |",
        f"| negative max | {separation['negative_max']:.6f} |",
        f"| negative p99 | {negatives['p99']:.6f} |",
        f"| negative p99.9 | {separation['negative_p999']:.6f} |",
        f"| negative ≥ {calibration['default_thresholds']['review_min']} | "
        f"{calibration['negative_above_review_min']} / {negatives['count']} |",
        f"| negative ≥ {calibration['default_thresholds']['duplicate_min']} | "
        f"**{calibration['negative_above_duplicate_min']}** / {negatives['count']} |",
        f"| hai phân bố tách được | **{'có' if separation['separated'] else 'KHÔNG'}** |",
        "",
        f"`standardizer_sha256`: `{calibration['standardizer_sha256'][:16]}…`",
        "",
    ]


def alarm_section(audit: dict) -> list[str]:
    alarm = audit["alarm"]
    lines = [
        "## Ngưỡng báo động xuyên dataset — DATA_PLAN §7.6",
        "",
        f"- Clip pretraining trùng dev/test benchmark: **{alarm['leaked_files']}** "
        f"/ {alarm['total_files']} = **{alarm['ratio'] * 100:.3f}%**",
        f"- Dải: **{alarm['band']}** — {BAND_NOTE.get(alarm['band'], alarm['action'])}",
        "",
    ]
    if audit.get("cross_dataset_exclusions_pending_split"):
        lines += [
            "> ⚠️ Con số trên tính **trước khi freeze split**. Luật loại trừ xuyên"
            " dataset chỉ áp được sau khi biết recording DataSED nào rơi vào"
            " dev/test, nên đây là kết quả **chưa kết luận được**, không phải 0 thật.",
            "",
        ]
    for note in alarm.get("notes", []):
        lines += [f"> ⚠️ {note}", ""]
    return lines


def coverage_section(audit: dict) -> list[str]:
    unreachable = audit.get("unreachable_by_tier3", {})
    lines = [
        "## Độ phủ của cổng",
        "",
        "| Dataset | File | Ngoài tầm T3 (< 1 s) | Độ phủ |",
        "|---|---:|---:|---:|",
    ]
    for dataset, total in audit["files"].items():
        missing = len(unreachable.get(dataset, []))
        lines.append(
            f"| `{dataset}` | {total} | {missing} | {(total - missing) / total * 100:.1f}% |"
        )
    lines += [
        "",
        "File ngắn hơn sàn chồng lấp 1 s không được T3 kết luận gì "
        "([ADR-0007 §6](../decisions/ADR-0007-fingerprint-va-luat-dedup.md)).",
        "",
    ]
    return lines


def short_clip_class_section(
    audit: dict, labels: dict[str, list[str]], class_ids: tuple[str, ...]
) -> list[str]:
    """Report T3's short-clip blind spot by coarse class, with no silent ID mismatch."""
    unreachable = list(audit.get("unreachable_by_tier3", {}).get("datasec", []))
    if not unreachable:
        raise SystemExit("duplicate_audit.json has no DataSEC short-clip list")
    matched = set(unreachable).intersection(labels)
    missing = sorted(set(unreachable).difference(labels))
    if missing:
        raise SystemExit(f"Short-clip IDs missing labels: {missing[:3]}")
    if not matched:
        raise SystemExit("Short-clip/label intersection is empty")
    short_counts = Counter(labels[file_id][0] for file_id in unreachable)
    total_counts = Counter(values[0] for values in labels.values())
    lines = [
        "## Phân bố clip DataSEC < 1 s",
        "",
        f"Danh sách `unreachable_by_tier3.datasec` có **{len(unreachable)}** file; "
        f"giao với nhãn DataSEC là **{len(matched)}** file.",
        "",
        "| Coarse class | Clip < 1 s / tổng clip lớp |",
        "|---|---:|",
    ]
    lines.extend(
        f"| `{class_id}` | {short_counts[class_id]} / {total_counts[class_id]} |"
        for class_id in class_ids
    )
    return [*lines, ""]


def read_worksheet(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows, _ = read_csv_rows(path)
    return rows


def decision_section(rows: list[dict], audit: dict) -> list[str]:
    """Nhật ký quyết định của người — vật liệu phụ lục khóa luận.

    Ghi chú của người duyệt là bằng chứng duy nhất giải thích **vì sao** một cặp
    similarity 0.89 bị coi là cùng nguồn còn cặp 0.91 thì không. Không có nó, phần
    duy nhất của cổng D3 do người quyết định trở thành một hộp đen.
    """
    pending = audit["review_queue_cross_dataset"] - len(
        [row for row in rows if (row.get("decision") or "").strip()]
    )
    if not rows:
        return [
            f"> {audit['review_queue_cross_dataset']} cặp xuyên dataset **chưa** có"
            " quyết định. Chỉ nhóm này ảnh hưởng RQ1. Chạy"
            " `scripts.build_review_worksheet` để sinh phiếu.",
            "",
        ]

    counts: dict[str, int] = {}
    for row in rows:
        decision = (row.get("decision") or "").strip().lower() or "(trống)"
        counts[decision] = counts.get(decision, 0) + 1

    reviewers = sorted({row["decided_by"] for row in rows if row.get("decided_by")})
    lines = [
        "## Quyết định của người",
        "",
        f"Người duyệt: {', '.join(reviewers) or '—'}",
        "",
        "| Quyết định | Cặp |",
        "|---|---:|",
        *[f"| `{key}` | {value} |" for key, value in sorted(counts.items())],
        "",
    ]
    if pending > 0:
        lines += [f"> ⚠️ Còn **{pending}** cặp chưa có quyết định.", ""]

    lines += [
        "### Nhật ký",
        "",
        "| # | Sim | Chồng lấp | Clip pretraining | Recording benchmark | Quyết định | Ghi chú |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in sorted(rows, key=lambda item: -float(item["similarity"])):
        lines.append(
            f"| {row['pair_id']} | {float(row['similarity']):.4f} "
            f"| {float(row['overlap_s']):.1f} s "
            f"| `{row['pretraining_file_id'].split('/')[-1]}` "
            f"| `{row['benchmark_file_id'].split('/')[-1]}` "
            f"| `{(row.get('decision') or '—').strip()}` "
            f"| {(row.get('note') or '').strip() or '—'} |"
        )
    lines.append("")
    return lines


def build_report(
    audit: dict, calibration: dict, stats: dict, short_clip_lines: list[str] | None = None
) -> str:
    tiers = audit["pairs_by_tier"]
    lines = [
        "# Cổng D3 — audit trùng lặp",
        "",
        f"**Sinh tự động** `scripts.report_duplicates` — "
        f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Cấu hình đã dùng",
        "",
        "| | |",
        "|---|---|",
        f"| `duplicate_min` | {audit['thresholds']['duplicate_min']} |",
        f"| `review_min` | {audit['thresholds']['review_min']} |",
        f"| `min_overlap_s` | {audit['thresholds']['min_overlap_s']} |",
        f"| `fingerprint_sha256` | `{audit['fingerprint_sha256'][:16]}…` |",
        f"| `standardizer_sha256` | `{audit['standardizer_sha256'][:16]}…` |",
        "",
        "## Cặp khớp theo tầng",
        "",
        "| Tầng | Cặp |",
        "|---|---:|",
    ]
    for tier in ("T1", "T2", "T3"):
        lines.append(f"| {tier} | {tiers.get(tier, 0)} |")
    lines += [
        "",
        "## Nhóm trùng lặp",
        "",
        "Nhóm chỉ được tạo từ cạnh `duplicate`. Cạnh `review` **không** gom nhóm —"
        " xem [ADR-0007](../decisions/ADR-0007-fingerprint-va-luat-dedup.md).",
        "",
        f"- Tổng nhóm: **{stats['groups']}** gồm {stats['members']} file",
        f"- Nhóm xuyên dataset: **{stats['cross']}**",
        f"- Nhóm lớn nhất: {stats['largest']} file",
        f"- Phân bố cỡ nhóm: {stats['sizes'] or '(không có nhóm)'}",
        "",
        "## Cặp ở dải review",
        "",
        f"- Tổng: **{audit['review_pairs']}**",
        f"- **Phải có quyết định của người** (xuyên dataset): "
        f"**{audit['review_queue_cross_dataset']}** → `review_queue_cross_dataset.csv`",
        f"- Ràng buộc \"cùng split\" (nội bộ, không xoá gì): "
        f"**{audit['split_cohesion_pairs']}** → `split_cohesion_pairs.csv`",
        "",
    ]
    lines += decision_section(read_worksheet(MANIFESTS / "review_worksheet.csv"), audit)
    sections = lines + alarm_section(audit) + calibration_section(calibration)
    sections += coverage_section(audit)
    return "\n".join(sections + (short_clip_lines or []))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    audit = read_json(MANIFESTS / "duplicate_audit.json")
    calibration = read_json(INTERIM / "threshold_calibration.json")
    stats = group_stats(read_groups(MANIFESTS / "duplicate_groups.csv"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    labels = labels_by_file_id(MANIFESTS / "datasec_inventory.csv", taxonomy)
    short_clip_lines = short_clip_class_section(audit, labels, taxonomy.class_ids)

    MEASUREMENTS.mkdir(parents=True, exist_ok=True)
    destination = MEASUREMENTS / f"dedup_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    destination.write_text(
        build_report(audit, calibration, stats, short_clip_lines) + "\n", encoding="utf-8"
    )
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
