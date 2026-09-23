"""Test cho kiểm 5 khi cổng D4 áp lên DataSEC (ADR-0010/0011).

DataSEC là corpus pretraining, không phải benchmark có dev/test cần bảo vệ.
Kiểm 5 gốc (`check_cross_dataset_exclusions_applied`) không áp dụng được — nó
hỏi về "loại trừ xuyên dataset đã áp lên benchmark", một khái niệm DataSEC
không có. `scripts.check_leakage` phải rẽ nhánh theo `corpus` của registry.
"""

from pathlib import Path

from scripts.check_leakage import load_exclusions_for_dataset

HEADER = "file_id,group_id,reason_code,decided_by\n"


def _write(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "exclusions.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return path


def test_pretraining_keeps_both_internal_and_cross_dataset_reasons(tmp_path) -> None:
    """Với DataSEC, cả `exclude_duplicate` lẫn `exclude_cross_dataset_leak` đều phải vắng mặt."""
    path = _write(
        tmp_path,
        "datasec:a.wav,dup-0001,exclude_duplicate,rule:within_dataset_representative\n"
        "datasec:b.wav,dup-0002,exclude_cross_dataset_leak,human:patphh\n"
        "datasec:c.wav,dup-0003,exclude_cross_dataset_unsure,human:patphh\n",
    )

    result = load_exclusions_for_dataset(path, "datasec")

    assert sorted(result) == ["datasec:a.wav", "datasec:b.wav", "datasec:c.wav"]


def test_benchmark_keeps_no_reason_must_be_absent(tmp_path) -> None:
    """DataSED không có reason code nào bắt buộc vắng mặt — trùng nội bộ được giữ."""
    path = _write(
        tmp_path, "datased:a.wav,dup-0001,exclude_duplicate,rule:within_dataset_representative\n"
    )

    assert load_exclusions_for_dataset(path, "datased") == []


def test_foreign_dataset_rows_are_ignored(tmp_path) -> None:
    """Loại trừ của DataSED không lẫn vào kiểm của DataSEC."""
    path = _write(
        tmp_path,
        "datased:a.wav,dup-0001,exclude_duplicate,rule:within_dataset_representative\n"
        "datasec:b.wav,dup-0002,exclude_cross_dataset_leak,human:patphh\n",
    )

    assert load_exclusions_for_dataset(path, "datasec") == ["datasec:b.wav"]


def test_missing_file_yields_empty_list(tmp_path) -> None:
    assert load_exclusions_for_dataset(tmp_path / "khong-ton-tai.csv", "datasec") == []
