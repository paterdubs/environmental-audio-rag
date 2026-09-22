"""Generate docs/data_inventory.md from committed manifests.

Usage:
    python -m scripts.report_data_inventory
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
REFERENCE = ROOT / "data" / "reference"
OUTPUT = ROOT / "docs" / "data_inventory.md"


def load(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def licence_of(dataset: str) -> tuple[str, str]:
    matches = sorted(REFERENCE.glob(f"zenodo_{dataset}_*.json"))
    if not matches:
        return "(not recorded)", "(not recorded)"
    metadata = json.loads(matches[-1].read_text(encoding="utf-8"))["metadata"]
    licence = metadata.get("license") or {}
    return str(licence.get("id", "(not recorded)")), str(metadata.get("doi", "(not recorded)"))


def archive_section(dataset: str, audit: dict) -> list[str]:
    licence, doi = licence_of(dataset)
    return [
        "",
        f"### `{dataset}` — archive",
        "",
        "| Trường | Giá trị |",
        "|---|---:|",
        f"| Record DOI | `{doi}` |",
        f"| License | `{licence}` |",
        f"| Archive | `{audit['archive_name']}` |",
        f"| Bytes | {audit['bytes_actual']:,} |",
        f"| MD5 | `{audit['md5_actual']}` |",
        f"| MD5 khớp contract | {audit['md5_match']} |",
        f"| ZIP entries | {audit['entries']:,} |",
        f"| File audio | {audit['audio_files']:,} |",
        f"| Giải nén (GiB) | {audit['uncompressed_bytes'] / 2**30:.2f} |",
        f"| Bảng annotation | {len(audit['annotation_files'])} |",
        f"| LICENSE/README trong archive | {len(audit['documentation_files'])} |",
        f"| Coarse label trong layout | {audit['coarse_labels']} |",
        f"| Subclass label trong layout | {audit['subclass_labels']} |",
        f"| Nhãn ngoài taxonomy | {len(audit['unmapped_labels'])} |",
        f"| **Verdict** | **{audit['verdict']}** |",
    ]


def class_distribution(audit: dict) -> list[str]:
    labels = audit["labels"]
    if not labels:
        return []
    total = sum(node["files"] for node in labels)
    ranked = sorted(labels, key=lambda node: -node["files"])
    lines = [
        "",
        f"### `{audit['dataset']}` — phân bố lớp",
        "",
        "| Coarse class | Files | Share | Subclass (files) |",
        "|---|---:|---:|---|",
    ]
    for node in ranked:
        subs = node["subclasses"]
        rendered = ", ".join(f"`{k}` {v}" for k, v in subs.items()) if subs else "—"
        share = 100 * node["files"] / total
        lines.append(
            f"| `{node['canonical_class_id']}` | {node['files']:,} "
            f"| {share:.1f}% | {rendered} |"
        )
    lines.append(f"| **Tổng** | **{total:,}** | 100% | |")

    biggest, smallest = ranked[0], ranked[-1]
    top2 = ranked[0]["files"] + ranked[1]["files"]
    subs = [
        (count, f"{node['canonical_class_id']}/{name}")
        for node in labels
        for name, count in node["subclasses"].items()
    ]
    lines.extend(
        [
            "",
            "**Chỉ số lệch lớp:**",
            "",
            f"- Lớn nhất: `{biggest['canonical_class_id']}` {biggest['files']:,} "
            f"({100 * biggest['files'] / total:.1f}%)",
            f"- Nhỏ nhất: `{smallest['canonical_class_id']}` {smallest['files']:,} "
            f"({100 * smallest['files'] / total:.1f}%)",
            f"- Tỉ lệ lệch coarse: **{biggest['files'] / smallest['files']:.1f} : 1**",
            f"- Hai lớp lớn nhất chiếm: **{100 * top2 / total:.1f}%**",
        ]
    )
    if subs:
        low = sorted(v for v, _ in subs if v < 25)
        names = [name for value, name in sorted(subs) if value < 25]
        lines.append(f"- Subclass: {len(subs)} node, nhỏ nhất {min(subs)[0]} file")
        if names:
            lines.append(
                f"- **Subclass dưới 25 file ({len(low)}):** "
                + ", ".join(f"`{name}`" for name in names)
            )
    return lines


def audio_section(dataset: str, summary: dict) -> list[str]:
    duplicates = summary.get("exact_duplicate_groups", [])
    return [
        "",
        f"### `{dataset}` — inventory audio",
        "",
        "| Trường | Giá trị |",
        "|---|---:|",
        f"| File | {summary['files']:,} |",
        f"| Tổng thời lượng (giờ) | {summary['hours']:.4f} |",
        f"| Bytes | {summary['bytes']:,} |",
        f"| Sample rate | {summary['sample_rates']} |",
        f"| Channels | {summary['channels']} |",
        f"| Nhóm exact duplicate (T1) | {len(duplicates)} |",
    ]


def main() -> None:
    lines = [
        "# data_inventory.md — Inventory dữ liệu",
        "",
        "> **Sinh tự động** bởi `python -m scripts.report_data_inventory` từ",
        "> `data/manifests/` và `data/reference/`. **Không sửa số bằng tay.**",
        "",
        f"- Sinh lúc: `{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
    ]

    audits = {}
    for dataset in ("datasec", "datased"):
        audit = load(MANIFESTS / f"{dataset}_archive_audit.json")
        if audit:
            audits[dataset] = audit
    if audits:
        first = next(iter(audits.values()))
        lines.append(f"- Taxonomy: `{first['taxonomy_version']}` / `{first['taxonomy_sha256']}`")

    lines.append("")
    lines.append("## 1. Archive")
    for dataset, audit in audits.items():
        lines.extend(archive_section(dataset, audit))

    lines.append("")
    lines.append("## 2. Phân bố lớp")
    for audit in audits.values():
        lines.extend(class_distribution(audit))
    if not any(a["labels"] for a in audits.values()):
        lines.append("")
        lines.append("Chưa có dataset nào mã hóa nhãn trong cây thư mục.")

    lines.append("")
    lines.append("## 3. Inventory audio")
    found = False
    for dataset in ("datasec", "datased"):
        summary = load(MANIFESTS / f"{dataset}_inventory_summary.json")
        if summary:
            lines.extend(audio_section(dataset, summary))
            found = True
        else:
            lines.extend(
                [
                    "",
                    f"### `{dataset}` — inventory audio",
                    "",
                    "○ Chưa giải nén, nên chưa có duration, sample rate hay hash từng file.",
                ]
            )
    if not found:
        lines.append("")
        lines.append("○ Chưa có inventory nào.")

    lines.extend(
        [
            "",
            "## 4. Ranh giới",
            "",
            "Archive audit chỉ đọc central directory của ZIP: nó xác nhận toàn vẹn,",
            "số file audio và độ phủ tên nhãn. Nó **không** mở file audio nào, nên",
            "không nói gì về sample rate, duration, khả năng decode, tính hợp lệ của",
            "annotation hay duplicate. Những mục đó thuộc cổng D1–D3.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
