"""Đọc file CSV do **người** sửa, không giả định encoding.

Excel trên Windows tiếng Việt lưu lại CSV bằng cp1252 chứ không phải UTF-8, và
mọi ký tự ngoài bảng mã bị thay bằng `?`. Đọc thẳng bằng UTF-8 thì `UnicodeDecodeError`
làm hỏng cả bước áp quyết định — mà quyết định thì đã bỏ công nghe xong rồi.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
REPLACEMENT_MARK = "?"


def read_text_any(path: Path) -> tuple[str, str]:
    """Trả về `(nội dung, tên encoding đã dùng)`. `latin-1` luôn giải mã được.

    `utf-8-sig` giải mã được cả file **không** có BOM, nên thử nó trước rồi báo
    tên nó là báo sai. Kiểm BOM tường minh để tên encoding trong artifact đúng
    với thứ thật sự nằm trên đĩa.
    """
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    for encoding in ENCODINGS:
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        if encoding == "utf-8-sig" and not has_bom:
            return text, "utf-8"
        return text, encoding
    raise AssertionError("unreachable: latin-1 decodes any byte string")


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], str]:
    text, encoding = read_text_any(path)
    return list(csv.DictReader(io.StringIO(text))), encoding


def count_mangled(rows: list[dict[str, str]], column: str) -> int:
    """Đếm ô có dấu hiệu mất ký tự khi Excel lưu sang bảng mã hẹp.

    Không sửa được — thông tin đã mất ở lúc ghi. Chỉ báo để người viết lại.
    """
    return sum(1 for row in rows if REPLACEMENT_MARK in (row.get(column) or ""))
