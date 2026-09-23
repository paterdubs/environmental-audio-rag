"""Test cho trình đọc file do người sửa.

Excel trên Windows tiếng Việt lưu CSV bằng cp1252 và thay ký tự ngoài bảng mã
bằng `?`. Đã xảy ra thật: 29/35 ghi chú mất dấu.
"""

import pytest

from ml.dataops.textio import count_mangled, read_csv_rows, read_text_any

VIETNAMESE = "vọng âm và độ xa giống nhau"
HEADER = "pair_id,note\n"


def test_reads_plain_utf8_without_claiming_a_bom(tmp_path) -> None:
    """`utf-8-sig` giải mã được cả file không BOM — báo tên nó là báo sai."""
    path = tmp_path / "a.csv"
    path.write_text(HEADER + f"rev-001,{VIETNAMESE}\n", encoding="utf-8")

    text, encoding = read_text_any(path)

    assert encoding == "utf-8"
    assert VIETNAMESE in text


def test_reads_utf8_with_bom_and_reports_it(tmp_path) -> None:
    path = tmp_path / "b.csv"
    path.write_text(HEADER + f"rev-001,{VIETNAMESE}\n", encoding="utf-8-sig")

    text, encoding = read_text_any(path)

    assert encoding == "utf-8-sig"
    assert not text.startswith("﻿")


def test_reads_cp1252_excel_output(tmp_path) -> None:
    path = tmp_path / "c.csv"
    path.write_bytes((HEADER + "rev-001,vong am va do xa\n").encode("cp1252"))

    _, encoding = read_text_any(path)

    assert encoding in {"utf-8", "cp1252"}  # ASCII thuần giải mã được bằng cả hai


def test_cp1252_with_high_bytes_is_not_utf8(tmp_path) -> None:
    path = tmp_path / "d.csv"
    path.write_bytes(HEADER.encode() + b"rev-001,v\xe2ng \xe2m\n")

    _, encoding = read_text_any(path)

    assert encoding == "cp1252"


def test_csv_rows_parse_with_detected_encoding(tmp_path) -> None:
    path = tmp_path / "e.csv"
    path.write_text(HEADER + f"rev-001,{VIETNAMESE}\n", encoding="utf-8")

    rows, encoding = read_csv_rows(path)

    assert rows == [{"pair_id": "rev-001", "note": VIETNAMESE}]
    assert encoding == "utf-8"


def test_count_mangled_flags_replacement_marks() -> None:
    rows = [
        {"note": "v?ng âm và ?? xa"},
        {"note": VIETNAMESE},
        {"note": ""},
        {},
    ]
    assert count_mangled(rows, "note") == 1


def test_count_mangled_on_absent_column_is_zero() -> None:
    assert count_mangled([{"note": "x"}], "decision") == 0


def test_unreadable_bytes_still_decode(tmp_path) -> None:
    """latin-1 giải mã được mọi chuỗi byte — không được ném lỗi ở bước cuối."""
    path = tmp_path / "f.csv"
    path.write_bytes(HEADER.encode() + bytes(range(128, 256)) + b"\n")

    _, encoding = read_text_any(path)

    assert encoding in {"cp1252", "latin-1"}


def test_empty_file_is_not_an_error(tmp_path) -> None:
    path = tmp_path / "g.csv"
    path.write_bytes(b"")

    rows, _ = read_csv_rows(path)

    assert rows == []


def test_utf8_is_preferred_over_lossy_fallback(tmp_path) -> None:
    """Chuỗi UTF-8 hợp lệ không được rơi xuống cp1252, nếu không sẽ ra mojibake."""
    path = tmp_path / "h.csv"
    path.write_text(HEADER + "rev-001,pháo hoa\n", encoding="utf-8")

    rows, _ = read_csv_rows(path)

    assert rows[0]["note"] == "pháo hoa"


def test_reader_rejects_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        read_text_any(tmp_path / "khong-ton-tai.csv")
