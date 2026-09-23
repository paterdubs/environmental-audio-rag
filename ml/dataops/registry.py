"""Khoá định danh của từng dataset khi chia split và khi chạy cổng rò rỉ.

Hai dataset đặt tên item theo hai cách khác nhau, và **đó là sự thật của dữ
liệu, không phải lựa chọn tuỳ tiện**:

* DataSED công bố theo *recording* — `S-0001` là một bản thu 60 giây có
  annotation riêng. `recording_id` tồn tại độc lập với đường dẫn file.
* DataSEC công bố theo *clip* rời, xếp trong cây thư mục theo lớp. Archive
  **không** cho biết clip nào cắt từ bản thu nào. Ở đây `file_id` chính là đơn
  vị duy nhất có thật.

Hệ quả: DataSEC **không có** `recording_id`, và module này không bịa ra một cái.
Quan hệ nguồn gốc giữa các clip DataSEC là thứ cổng D3 *đo được* — nó đã nằm
trong `leakage_group`. Thêm một lớp `recording_id` suy đoán bên cạnh sẽ là một
tuyên bố về nguồn gốc mà không ai đo, và là namespace thứ ba trong một repo đã
hai lần hỏng vì lệch namespace. Xem
[ADR-0010](../../docs/decisions/ADR-0010-dinh-danh-datasec-va-cong-freeze.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from ml.taxonomy import Taxonomy

#: Reason code trong `exclusions.csv` loại clip khỏi **corpus pretraining**.
#: Đây là ràng buộc cứng của RQ1: clip DataSEC trùng dev/test DataSED mà lọt vào
#: pretraining thì phép đo transfer mất nghĩa.
CROSS_DATASET_REASONS = ("exclude_cross_dataset_leak", "exclude_cross_dataset_unsure")

#: Loại trùng nội bộ. **Không** đồng nghĩa với "xoá khỏi split" — xem
#: `DatasetKeys.excluded_must_be_absent`.
WITHIN_DATASET_REASON = "exclude_duplicate"


@dataclass(frozen=True)
class DatasetKeys:
    """Cách một dataset tự đặt tên, và split của nó mang nghĩa gì."""

    dataset: str
    item_col: str
    """Cột khoá trong file split. DataSED: `recording_id`. DataSEC: `file_id`."""

    manifest: str
    item_col_in_manifest: str
    hash_col: str
    """Tên cột hash nội dung — DataSED ghi `content_sha256`, DataSEC ghi `sha256`."""

    excluded_must_be_absent: tuple[str, ...]
    """Reason code mà file mang nó **không được** có mặt trong split này.

    Rỗng không có nghĩa là bỏ qua: với benchmark, trùng nội bộ được xử lý bằng
    cách buộc cùng `leakage_group` chứ không phải bằng cách xoá — xoá đi thì
    benchmark teo lại. Bất biến tương ứng được kiểm riêng.
    """

    corpus: str
    """`benchmark` hoặc `pretraining` — quyết định nghĩa của việc loại trừ."""

    label_source: Literal["events_csv", "directory"]
    """DataSED công bố nhãn bằng bảng event; DataSEC bằng cây thư mục."""

    coverage_level: Literal["polyphonic", "coarse_and_subclass"]
    """Tập lớp mà kiểm phủ đòi phải có mặt ở **mọi** split."""

    label_modes: tuple[str, ...]
    """Chế độ nhãn hợp lệ. Phần tử đầu là mặc định."""

    split_ratio: tuple[float, float, float]
    """train/validation/test. DataSED 60/20/20 (ADR-0008), DataSEC 70/15/15 (DATA_PLAN §8.3)."""


DATASETS: dict[str, DatasetKeys] = {
    "datased": DatasetKeys(
        dataset="datased",
        item_col="recording_id",
        manifest="datased_recordings.csv",
        item_col_in_manifest="recording_id",
        hash_col="content_sha256",
        excluded_must_be_absent=(),
        corpus="benchmark",
        label_source="events_csv",
        coverage_level="polyphonic",
        label_modes=("polyphonic", "monophonic"),
        split_ratio=(0.6, 0.2, 0.2),
    ),
    "datasec": DatasetKeys(
        dataset="datasec",
        item_col="file_id",
        manifest="datasec_inventory.csv",
        item_col_in_manifest="file_id",
        hash_col="sha256",
        excluded_must_be_absent=(*CROSS_DATASET_REASONS, WITHIN_DATASET_REASON),
        corpus="pretraining",
        label_source="directory",
        coverage_level="coarse_and_subclass",
        label_modes=("classification",),
        split_ratio=(0.7, 0.15, 0.15),
    ),
}


def coverage_labels(dataset: str, taxonomy: Taxonomy) -> list[str]:
    """Tập lớp mà kiểm phủ của cổng D4 đòi phải có mặt ở mọi split.

    Hai dataset đòi hai tập khác nhau, và dùng nhầm thì **không có gì báo lỗi**:

    * DataSED — **21** `polyphonic_class_ids`. `wind_turbine` nằm ngoài nhãn
      polyphonic nên đòi nó sẽ làm trượt một split đúng.
    * DataSEC — **22** coarse + **28** subclass. Đây là dataset phân loại, mọi
      lớp đều có clip; dùng 21 ở đây sẽ báo thiếu `wind_turbine` ở mọi split.
    """
    keys = keys_for(dataset)
    if keys.coverage_level == "polyphonic":
        return list(taxonomy.polyphonic_class_ids)
    return [
        *taxonomy.class_ids,
        *(subclass for item in taxonomy.classes for subclass in item.subclasses),
    ]


def keys_for(dataset: str) -> DatasetKeys:
    try:
        return DATASETS[dataset]
    except KeyError:
        raise SystemExit(
            f"Dataset {dataset!r} chưa khai báo trong ml/dataops/registry.py. "
            f"Đã biết: {sorted(DATASETS)}."
        ) from None


def _manifest(keys: DatasetKeys, manifests: Path) -> pd.DataFrame:
    path = manifests / keys.manifest
    if not path.exists():
        raise SystemExit(f"Thiếu {path}: không suy được file_id cho {keys.dataset}.")
    frame = pd.read_csv(path)
    missing = {keys.item_col_in_manifest, "file_id"}.difference(frame.columns)
    if missing:
        raise SystemExit(f"{path} thiếu cột {sorted(missing)}.")
    return frame


def file_id_by_item(dataset: str, manifests: Path) -> dict[str, str]:
    """`item_col` → `file_id`. Mọi khoá bên trong cổng rò rỉ phải là `file_id`.

    Với DataSEC ánh xạ này là đồng nhất, nhưng vẫn đi qua manifest: item không
    có trong manifest thì phải vỡ ở đây, chứ không lặng lẽ biến thành một phép
    giao rỗng ở tầng trên. Một cổng giao rỗng thì **luôn** báo pass — đã xảy ra
    thật hai lần trong repo này.
    """
    keys = keys_for(dataset)
    frame = _manifest(keys, manifests)
    mapping = dict(
        zip(
            frame[keys.item_col_in_manifest].astype(str),
            frame["file_id"].astype(str),
            strict=True,
        )
    )
    foreign = [value for value in mapping.values() if not value.startswith(f"{dataset}:")]
    if foreign:
        raise SystemExit(
            f"{keys.manifest}: {len(foreign)} file_id không mang tiền tố {dataset!r}, "
            f"ví dụ {foreign[0]!r}."
        )
    return mapping


def content_hash_by_file_id(dataset: str, manifests: Path) -> dict[str, str]:
    keys = keys_for(dataset)
    frame = _manifest(keys, manifests)
    if keys.hash_col not in frame.columns:
        raise SystemExit(f"{keys.manifest} thiếu cột hash {keys.hash_col!r}.")
    return dict(
        zip(frame["file_id"].astype(str), frame[keys.hash_col].astype(str), strict=True)
    )
