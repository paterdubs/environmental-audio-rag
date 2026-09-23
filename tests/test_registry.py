"""Test cho khoá định danh theo dataset (ADR-0010).

DataSED đặt tên item bằng `recording_id`, DataSEC bằng chính `file_id`. Trộn hai
namespace làm mọi phép giao thành rỗng, và cổng giao rỗng thì luôn báo pass.
"""

from pathlib import Path

import pytest

from ml.dataops.registry import (
    content_hash_by_file_id,
    coverage_labels,
    file_id_by_item,
    keys_for,
)
from ml.taxonomy import load_taxonomy

DATASED_HEADER = "recording_id,file_id,content_sha256\n"
DATASEC_HEADER = "file_id,relative_path,sha256\n"
TAXONOMY_PATH = Path(__file__).resolve().parents[1] / "ml" / "configs" / "taxonomy.yaml"


def _datased(tmp_path: Path, body: str = "S-0001,datased:SED_wav/S-0001.wav,aa\n") -> Path:
    (tmp_path / "datased_recordings.csv").write_text(DATASED_HEADER + body, encoding="utf-8")
    return tmp_path


def _datasec(tmp_path: Path, body: str = "datasec:DATASEC/Bells/Bells-0001.wav,x,bb\n") -> Path:
    (tmp_path / "datasec_inventory.csv").write_text(DATASEC_HEADER + body, encoding="utf-8")
    return tmp_path


def test_datasec_has_no_recording_id_layer() -> None:
    """Archive DataSEC chỉ phát hành clip rời — bịa `recording_id` là bịa nguồn gốc."""
    assert keys_for("datasec").item_col == "file_id"
    assert keys_for("datased").item_col == "recording_id"


def test_datasec_mapping_is_identity(tmp_path) -> None:
    mapping = file_id_by_item("datasec", _datasec(tmp_path))

    file_id = "datasec:DATASEC/Bells/Bells-0001.wav"
    assert mapping == {file_id: file_id}


def test_datased_mapping_crosses_two_namespaces(tmp_path) -> None:
    mapping = file_id_by_item("datased", _datased(tmp_path))

    assert mapping == {"S-0001": "datased:SED_wav/S-0001.wav"}


def test_hash_column_name_differs_between_manifests(tmp_path) -> None:
    """DataSED ghi `content_sha256`, DataSEC ghi `sha256` — đọc cứng một tên là hỏng một bên."""
    _datased(tmp_path)
    _datasec(tmp_path)

    assert content_hash_by_file_id("datased", tmp_path) == {"datased:SED_wav/S-0001.wav": "aa"}
    assert content_hash_by_file_id("datasec", tmp_path) == {
        "datasec:DATASEC/Bells/Bells-0001.wav": "bb"
    }


def test_foreign_prefix_is_rejected(tmp_path) -> None:
    """`file_id` sai tiền tố phải vỡ ở đây, không biến thành phép giao rỗng ở tầng trên."""
    _datasec(tmp_path, "datased:DATASEC/Bells/Bells-0001.wav,x,bb\n")

    with pytest.raises(SystemExit, match="tiền tố"):
        file_id_by_item("datasec", tmp_path)


def test_missing_manifest_names_the_file(tmp_path) -> None:
    with pytest.raises(SystemExit, match="datasec_inventory.csv"):
        file_id_by_item("datasec", tmp_path)


def test_unknown_dataset_lists_what_is_known() -> None:
    with pytest.raises(SystemExit, match="datased"):
        keys_for("audioset")


def test_manifest_missing_a_required_column(tmp_path) -> None:
    body = "relative_path,sha256\nx,bb\n"
    (tmp_path / "datasec_inventory.csv").write_text(body, encoding="utf-8")

    with pytest.raises(SystemExit, match="file_id"):
        file_id_by_item("datasec", tmp_path)


# ---------- tập lớp của kiểm phủ (ADR-0011) ----------


def test_coverage_uses_21_polyphonic_classes_for_the_benchmark() -> None:
    """`wind_turbine` ngoài nhãn polyphonic — đòi nó sẽ làm trượt một split đúng."""
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    labels = coverage_labels("datased", taxonomy)

    assert len(labels) == 21
    assert "wind_turbine" not in labels


def test_coverage_uses_22_coarse_plus_28_subclass_for_pretraining() -> None:
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    labels = coverage_labels("datasec", taxonomy)

    assert len(labels) == 50
    assert "wind_turbine" in labels and "magpies" in labels


def test_label_source_differs_between_datasets() -> None:
    assert keys_for("datased").label_source == "events_csv"
    assert keys_for("datasec").label_source == "directory"
