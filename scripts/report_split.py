"""Report config-ordered class counts for a frozen split candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

from ml.dataops.datasec_labels import labels_by_file_id
from ml.dataops.textio import read_csv_rows
from ml.taxonomy import Taxonomy, load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
SPLIT_ORDER = ("train", "validation", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report DataSEC split class distribution")
    parser.add_argument("dataset", choices=("datasec",))
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown destination; without it, write to stdout.",
    )
    return parser.parse_args()


def _csv_frame(path: Path, required: set[str]) -> pd.DataFrame:
    rows, _ = read_csv_rows(path)
    frame = pd.DataFrame(rows)
    missing = required.difference(frame.columns)
    if missing:
        raise SystemExit(f"{path} thiếu cột {sorted(missing)}.")
    if frame.empty:
        raise SystemExit(f"{path} rỗng; không thể báo cáo split.")
    return frame


def _split_assignments(path: Path) -> pd.DataFrame:
    assignments = _csv_frame(path, {"file_id", "split"})
    if assignments["file_id"].duplicated().any():
        raise SystemExit(f"{path} có file_id lặp; mỗi clip phải có đúng một split.")
    unknown = set(assignments["split"]).difference(SPLIT_ORDER)
    if unknown:
        raise SystemExit(f"{path} có split không hợp lệ: {sorted(unknown)}.")
    foreign = assignments[~assignments["file_id"].str.startswith("datasec:")]
    if not foreign.empty:
        raise SystemExit(f"{path} có file_id ngoài namespace datasec.")
    return assignments


def _class_counts(assignments: pd.DataFrame, taxonomy: Taxonomy) -> pd.DataFrame:
    labels = labels_by_file_id(
        ROOT / "data" / "manifests" / "datasec_inventory.csv", taxonomy
    )
    missing = set(assignments["file_id"]).difference(labels)
    if missing:
        raise SystemExit(
            "Split có file_id không có trong inventory; phép giao không được rỗng. "
            f"Ví dụ: {sorted(missing)[0]!r}."
        )
    long_rows = [
        {"file_id": file_id, "class_id": class_id}
        for file_id in assignments["file_id"]
        for class_id in labels[file_id]
    ]
    merged = assignments.merge(pd.DataFrame(long_rows), on="file_id", validate="one_to_many")
    ordered_labels = [
        *taxonomy.class_ids,
        *(subclass for item in taxonomy.classes for subclass in item.subclasses),
    ]
    counts = pd.crosstab(merged["class_id"], merged["split"])
    counts = counts.reindex(index=ordered_labels, columns=SPLIT_ORDER, fill_value=0)
    if (counts.sum(axis=1) == 0).any():
        missing_labels = counts.index[counts.sum(axis=1) == 0].tolist()
        raise SystemExit(f"Split không phủ nhãn: {missing_labels}.")
    return counts.astype(int)


def _markdown_table(counts: pd.DataFrame) -> list[str]:
    rows = ["| class_id | train | validation | test | total |", "|---|---:|---:|---:|---:|"]
    for class_id, values in counts.iterrows():
        total = int(values.sum())
        rows.append(
            f"| `{class_id}` | {int(values['train'])} | {int(values['validation'])} "
            f"| {int(values['test'])} | {total} |"
        )
    return rows


def render_report(assignments: pd.DataFrame, taxonomy: Taxonomy, metadata: dict) -> str:
    counts = _class_counts(assignments, taxonomy)
    coarse = counts.loc[list(taxonomy.class_ids)]
    subclasses = counts.loc[[subclass for item in taxonomy.classes for subclass in item.subclasses]]
    low_support = subclasses[subclasses.sum(axis=1) < 25]
    split_items = assignments["split"].value_counts().reindex(SPLIT_ORDER, fill_value=0)
    split_sha256 = hashlib.sha256(
        (ROOT / "data" / "splits" / "datasec_classification.csv").read_bytes()
    ).hexdigest()
    if metadata.get("sha256") != split_sha256:
        raise SystemExit("SHA-256 split không khớp metadata; từ chối báo cáo số lẫn nguồn.")
    if metadata.get("taxonomy_sha256") != taxonomy.checksum:
        raise SystemExit("SHA-256 taxonomy không khớp metadata split.")

    lines = [
        "# Phân bố lớp split DataSEC",
        "",
        "Báo cáo sinh tự động từ `data/splits/datasec_classification.csv`; ",
        "không dùng để chọn lại split hoặc tuning trên test.",
        "",
        f"- Split SHA-256: `{split_sha256}`",
        f"- Taxonomy SHA-256: `{taxonomy.checksum}`",
        "- Số clip: " + " · ".join(f"{name}={int(split_items[name])}" for name in SPLIT_ORDER),
        "",
        "## 22 lớp coarse",
        "",
        *_markdown_table(coarse),
        "",
        "## 28 subclass",
        "",
        *_markdown_table(subclasses),
        "",
        "## Subclass low-support (tổng < 25)",
        "",
        "Các số là số tuyệt đối, không báo tỷ lệ vì mẫu dev/test quá nhỏ.",
        "",
        *_markdown_table(low_support),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    split_path = ROOT / "data" / "splits" / f"{args.dataset}_classification.csv"
    metadata_path = split_path.with_suffix(".json")
    assignments = _split_assignments(split_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    report = render_report(assignments, taxonomy, metadata)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        # Windows console có thể là cp1252; báo cáo chứa tiếng Việt nên ghi UTF-8 trực tiếp.
        sys.stdout.buffer.write(report.encode("utf-8"))


if __name__ == "__main__":
    main()
