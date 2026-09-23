"""Nhãn DataSEC suy từ cây thư mục, không phụ thuộc torch.

DataSED phát hành nhãn dưới dạng bảng event (`datased_<mode>_events.csv`).
DataSEC **không có** file như vậy: lớp của một clip nằm ở chính đường dẫn của nó,
`DATASEC/<Coarse>/[<Subclass>/]<tên>.wav`.

Logic này từng nằm trong `ml/datasets/datasec.py`, mà module đó import `torch` ở
cấp module. Cổng D4 phải chạy được **không** cần torch: nó là cổng dữ liệu, và
trong chính môi trường này torch đã một lần không khởi tạo được (`0x8007000e`).
Một cổng phụ thuộc vào thứ có thể không nạp được là một cổng có thể bị bỏ qua.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.taxonomy import Taxonomy, normalize_text


def path_labels(relative_path: str, taxonomy: Taxonomy) -> tuple[str, str | None]:
    """`(coarse, subclass|None)` suy từ đường dẫn tương đối của clip."""
    parts = [normalize_text(part) for part in Path(relative_path).parts]
    aliases = taxonomy.alias_to_id
    coarse_index = next(
        (index for index, part in enumerate(parts) if part in aliases), None
    )
    if coarse_index is None:
        raise ValueError(f"Cannot map DataSEC path to taxonomy: {relative_path}")
    coarse = aliases[parts[coarse_index]]
    subclass = None
    if coarse_index + 1 < len(parts) - 1:
        candidate = parts[coarse_index + 1]
        item = next(value for value in taxonomy.classes if value.class_id == coarse)
        valid = {normalize_text(value): value for value in item.subclasses}
        if candidate not in valid:
            raise ValueError(f"Unknown subclass {candidate!r} under {coarse!r}")
        subclass = valid[candidate]
    return coarse, subclass


def labels_by_file_id(inventory: Path, taxonomy: Taxonomy) -> dict[str, list[str]]:
    """`file_id` → nhãn của clip, gồm coarse và subclass nếu có.

    Trả về **cả hai mức** vì cổng phủ lớp của DataSEC kiểm cả 22 coarse lẫn 28
    subclass: một subclass biến mất khỏi một split là một khiếm khuyết thật, và
    đo được là nó không bị buộc phải xảy ra (mọi subclass trải trên ≥ 16
    `leakage_group`).
    """
    frame = pd.read_csv(inventory)
    missing = {"file_id", "relative_path"}.difference(frame.columns)
    if missing:
        raise SystemExit(f"{inventory} thiếu cột {sorted(missing)}.")
    labels: dict[str, list[str]] = {}
    for file_id, relative_path in frame[["file_id", "relative_path"]].itertuples(
        index=False, name=None
    ):
        coarse, subclass = path_labels(str(relative_path), taxonomy)
        labels[str(file_id)] = [coarse] if subclass is None else [coarse, subclass]
    return labels
