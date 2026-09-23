"""Test cho nhãn DataSEC suy từ cây thư mục (ADR-0011).

DataSEC không phát hành file annotation nào — lớp của một clip nằm ở chính đường
dẫn. Cổng D4 phải đọc được nguồn nhãn đó mà không cần torch.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from ml.dataops.datasec_labels import labels_by_file_id, path_labels
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")

HEADER = "file_id,relative_path\n"
WITH_SUBCLASS = "DATASEC/Sirens and alarms/Sirens/Sirens-0046.wav"
WITHOUT_SUBCLASS = "DATASEC/Bells/Bells-0001.wav"
PROBE = "import sys, scripts.check_leakage; sys.exit('torch' in sys.modules)"


def test_path_with_a_subclass_folder_yields_both_levels() -> None:
    assert path_labels(WITH_SUBCLASS, TAXONOMY) == ("sirens_and_alarms", "sirens")


def test_path_without_a_subclass_folder_yields_only_coarse() -> None:
    """12 lớp coarse không có subclass — `None` chứ không phải chuỗi rỗng."""
    assert path_labels(WITHOUT_SUBCLASS, TAXONOMY) == ("bells", None)


def test_path_outside_the_taxonomy_is_rejected() -> None:
    with pytest.raises(ValueError, match="Cannot map DataSEC path"):
        path_labels("DATASEC/Khong co lop nay/x.wav", TAXONOMY)


def test_subclass_outside_its_parent_is_rejected() -> None:
    """Subclass hợp lệ nhưng nằm dưới lớp cha khác là lỗi cây thư mục, không phải nhãn mới."""
    with pytest.raises(ValueError, match="Unknown subclass"):
        path_labels("DATASEC/Bells/Sirens/x.wav", TAXONOMY)


def test_labels_keep_both_levels_for_the_coverage_check(tmp_path) -> None:
    path = tmp_path / "inventory.csv"
    path.write_text(
        HEADER + f"datasec:{WITH_SUBCLASS},{WITH_SUBCLASS}\n"
        f"datasec:{WITHOUT_SUBCLASS},{WITHOUT_SUBCLASS}\n",
        encoding="utf-8",
    )

    labels = labels_by_file_id(path, TAXONOMY)

    assert labels[f"datasec:{WITH_SUBCLASS}"] == ["sirens_and_alarms", "sirens"]
    assert labels[f"datasec:{WITHOUT_SUBCLASS}"] == ["bells"]


def test_inventory_missing_a_column_names_it(tmp_path) -> None:
    path = tmp_path / "inventory.csv"
    path.write_text("file_id\ndatasec:x\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="relative_path"):
        labels_by_file_id(path, TAXONOMY)


def test_the_real_inventory_covers_every_taxonomy_label() -> None:
    """50 nhãn = 22 coarse + 28 subclass. Thiếu một nhãn là cây thư mục đã đổi."""
    labels = labels_by_file_id(ROOT / "data" / "manifests" / "datasec_inventory.csv", TAXONOMY)
    observed = {label for values in labels.values() for label in values}

    expected = set(TAXONOMY.class_ids) | {
        subclass for item in TAXONOMY.classes for subclass in item.subclasses
    }
    assert observed == expected


def test_the_leakage_gate_does_not_need_torch() -> None:
    """Cổng dữ liệu phụ thuộc torch là cổng có thể bị bỏ qua khi torch không nạp được."""
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=ROOT,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
