"""Tiền xử lý nguồn Markdown của báo cáo trước khi đưa qua Pandoc.

Quy ước marker (một đoạn riêng, trừ tham chiếu nội dòng):

- ``@@CAP:tbl:key|Tiêu đề@@`` trước bảng, ``@@CAP:fig:key|Chú thích@@`` sau hình.
- ``@@NOTE:văn bản@@`` — dòng nguồn dưới bảng/hình.
- ``@@INCLUDE:đường/dẫn.md@@`` — chèn bảng sinh tự động (chỉ phần bảng + dòng nguồn).
- ``⟪eqno:key⟫`` — đoạn ngay sau công thức hiển thị, mang số công thức.
- ``⟪tbl:key⟫``, ``⟪fig:key⟫``, ``⟪eq:key⟫`` — tham chiếu nội dòng (thành field REF).
- ``[@khóa]`` / ``[@a; @b]`` — trích dẫn, thành ``[n]`` theo danh mục đã sắp xếp.
- ``@@APPENDIX@@`` — từ đây chú thích dùng nhãn tĩnh ``PL.n`` (phụ lục không có số chương).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CITATION = re.compile(r"\[(@[^\]\s;]+(?:\s*;\s*@[^\]\s;]+)*)\]")
CAPTION = re.compile(r"^@@CAP:(tbl|fig):([\w-]+)\|(.+)@@\s*$")
INCLUDE = re.compile(r"^@@INCLUDE:([^@|]+)@@\s*$")
EQNO = re.compile(r"⟪eqno:([\w-]+)⟫")
INLINE_REF = re.compile(r"⟪(tbl|fig|eq):([\w-]+)⟫")
LABELS = {"tbl": "Bảng", "fig": "Hình"}


@dataclass
class Registry:
    """Số đã gán cho bảng/hình/công thức, dùng làm kết quả có sẵn của field."""

    numbers: dict[tuple[str, str], str] = field(default_factory=dict)
    captions: dict[tuple[str, str], str] = field(default_factory=dict)

    def add(self, kind: str, key: str, number: str, caption: str = "") -> None:
        if (kind, key) in self.numbers:
            raise ValueError(f"Khóa {kind}:{key} khai báo hai lần")
        self.numbers[(kind, key)] = number
        self.captions[(kind, key)] = caption

    def text(self, kind: str, key: str) -> str:
        number = self.numbers[(kind, key)]
        return f"({number})" if kind == "eq" else f"{LABELS[kind]} {number}"


def replace_citations(text: str, numbers: dict[str, int]) -> str:
    def repl(match: re.Match) -> str:
        keys = [part.strip().lstrip("@") for part in match.group(1).split(";")]
        missing = [key for key in keys if key not in numbers]
        if missing:
            raise KeyError(f"Trích dẫn không có trong bibliography: {missing}")
        return "[" + ", ".join(str(n) for n in sorted({numbers[k] for k in keys})) + "]"

    return CITATION.sub(repl, text)


def expand_include(path: Path) -> list[str]:
    """Chỉ lấy bảng và dòng `**Nguồn:**` của một bảng do script sinh ra."""
    lines = path.read_text(encoding="utf-8").splitlines()
    table = [line for line in lines if line.startswith("|")]
    if len(table) < 3:
        raise ValueError(f"{path} không chứa bảng Markdown")
    source = next((line for line in lines if line.startswith("**Nguồn:**")), None)
    out = ["", *table, ""]
    if source:
        note = source.replace("**Nguồn:**", "Nguồn:").replace("`", "")
        out += [f"@@NOTE:{note} Bảng sinh tự động bởi script, không sửa tay.@@", ""]
    return out


def number_document(lines: list[str], root: Path) -> tuple[list[str], Registry]:
    """Mở rộng INCLUDE, đánh số chú thích/công thức theo chương; trả về dòng mới và registry."""
    registry = Registry()
    chapter = 0
    counters = {"tbl": 0, "fig": 0, "eq": 0}
    appendix = False
    appendix_counter = {"tbl": 0, "fig": 0}
    out: list[str] = []
    for line in lines:
        include = INCLUDE.match(line)
        if include:
            out.extend(expand_include(root / include.group(1).strip()))
            continue
        if line.strip() == "@@APPENDIX@@":
            appendix = True
            out.append(line)
            continue
        if line.startswith("# ") and not appendix:
            chapter += 1
            counters = {"tbl": 0, "fig": 0, "eq": 0}
        caption = CAPTION.match(line)
        if caption:
            kind, key, text = caption.groups()
            if appendix:
                appendix_counter[kind] += 1
                registry.add(kind, key, f"PL.{appendix_counter[kind]}", text)
            else:
                counters[kind] += 1
                registry.add(kind, key, f"{chapter}.{counters[kind]}", text)
        for key in EQNO.findall(line):
            counters["eq"] += 1
            registry.add("eq", key, f"{chapter}.{counters['eq']}")
        out.append(line)
    return out, registry


def check_references(lines: list[str], registry: Registry) -> None:
    missing = sorted(
        {
            f"{kind}:{key}"
            for line in lines
            for kind, key in INLINE_REF.findall(line)
            if (kind, key) not in registry.numbers
        }
    )
    if missing:
        raise KeyError(f"Tham chiếu tới khóa chưa khai báo: {missing}")


def prepare(files: list[Path], root: Path, cite_numbers: dict[str, int]) -> tuple[str, Registry]:
    lines: list[str] = []
    for path in files:
        lines.extend(path.read_text(encoding="utf-8").splitlines())
        lines.append("")
    lines, registry = number_document(lines, root)
    check_references(lines, registry)
    text = replace_citations("\n".join(lines), cite_numbers)
    return text, registry
