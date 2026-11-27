"""Đổi cách *hiển thị* bảng sinh tự động cho một bản báo cáo, không đổi giá trị số.

Một bản báo cáo (ví dụ bản tinh gọn `report/gon_src/`) có thể khai báo `display.yaml`:

    names:            # thay chuỗi theo thứ tự, áp lên ô bảng và dòng nguồn
      - ["LBR V2", "LBR chính"]
    names_skip: [06_s13_ranking_test.md]   # bảng giữ nguyên mã gốc
    vi_numbers: true  # 0.2965 -> 0,2965; [a, b] -> [a; b]; -0.1 -> −0,1
    numbers_skip: [f15_tech_stack.md]      # bảng có số phiên bản, không đổi dấu thập phân
    short_sources: true                    # dòng nguồn chỉ giữ tên tệp, bỏ đường dẫn

Mặc định (không có tệp) thì không làm gì, nên bản báo cáo cũ dựng ra y hệt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_DECIMAL = re.compile(r"(?<![\w.])([+\-−]?\d+)\.(\d+)(?![\w.])")
_MINUS = re.compile(r"(?<![\w.\-])-(?=\d)")
_BRACKET = re.compile(r"\[([^\[\]]*)\]")
_PATH = re.compile(r"(?<![\w])(?:[\w.\-]+/)+([\w.\-*{},]+)")


@dataclass(frozen=True)
class Display:
    names: tuple[tuple[str, str], ...] = ()
    names_skip: frozenset[str] = field(default_factory=frozenset)
    vi_numbers: bool = False
    numbers_skip: frozenset[str] = field(default_factory=frozenset)
    short_sources: bool = False

    @property
    def active(self) -> bool:
        return bool(self.names) or self.vi_numbers or self.short_sources


NONE = Display()


def load(path: Path | None) -> Display:
    if path is None or not path.is_file():
        return NONE
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    names = tuple((str(a), str(b)) for a, b in raw.get("names", []))
    return Display(
        names=names,
        names_skip=frozenset(raw.get("names_skip", [])),
        vi_numbers=bool(raw.get("vi_numbers", False)),
        numbers_skip=frozenset(raw.get("numbers_skip", [])),
        short_sources=bool(raw.get("short_sources", False)),
    )


def vi_number_text(text: str) -> str:
    """Đổi số kiểu Anh sang kiểu Việt trong một chuỗi; chỉ đụng vào số đứng riêng."""
    text = _MINUS.sub("−", text)
    text = _DECIMAL.sub(lambda m: f"{m.group(1)},{m.group(2)}", text)
    return _BRACKET.sub(lambda m: "[" + m.group(1).replace(", ", "; ") + "]", text)


def rename(text: str, names: tuple[tuple[str, str], ...]) -> str:
    for old, new in names:
        text = text.replace(old, new)
    return text


def apply_table(lines: list[str], name: str, display: Display) -> list[str]:
    """Áp lên các dòng bảng Markdown (đã lọc); dòng phân cách giữ nguyên."""
    out = []
    for line in lines:
        if set(line.replace("|", "").strip()) <= set("-: "):
            out.append(line)
            continue
        if display.names and name not in display.names_skip:
            line = rename(line, display.names)
        if display.vi_numbers and name not in display.numbers_skip:
            line = vi_number_text(line)
        out.append(line)
    return out


def apply_source(note: str, name: str, display: Display) -> str:
    if display.short_sources:
        note = _PATH.sub(lambda m: m.group(1), note)
    if display.names and name not in display.names_skip:
        note = rename(note, display.names)
    return note
