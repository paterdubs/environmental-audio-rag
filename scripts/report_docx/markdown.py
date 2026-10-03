"""Tiền xử lý nguồn Markdown của báo cáo trước khi đưa qua Pandoc.

Quy ước marker (một đoạn riêng, trừ tham chiếu nội dòng):

- ``@@CAP:tbl:key|Tiêu đề@@`` trước bảng, ``@@CAP:fig:key|Chú thích@@`` sau hình.
- ``@@NOTE:văn bản@@`` — dòng nguồn dưới bảng/hình.
- ``@@INCLUDE:đường/dẫn.md@@`` — chèn bảng sinh tự động (chỉ phần bảng + dòng nguồn).
  Tuỳ chọn sau dấu ``|`` (chỉ đổi cách trình bày, không đổi số): ``keep=regex`` giữ các hàng
  khớp điều kiện ``cột:regex`` (nối nhiều điều kiện bằng ``&``; muốn dùng dấu ``|`` trong
  regex thì đặt thêm một dấu gạch chéo ngược phía trước); ``cols=1,3,4`` giữ các cột (đánh số
  từ 1 theo bảng gốc); ``best=4+,5-`` in đậm giá trị lớn nhất (``+``) hoặc nhỏ nhất (``-``)
  của cột; ``group=2`` tính "tốt nhất" riêng cho từng nhóm hàng cùng giá trị ở cột 2;
  ``used=cột:regex`` tô nền xám nhạt các hàng khớp.
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
INCLUDE = re.compile(r"^@@INCLUDE:([^@|]+)((?:\|(?:\\.|[^@|\\])+)*)@@\s*$")
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


USED_MARK = "⟦used⟧"
_NUMBER = re.compile(r"^[+\-−]?\d+(?:[.,]\d+)?$")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _to_number(cell: str) -> float | None:
    text = cell.replace("**", "").strip()
    return float(text.replace(",", ".").replace("−", "-")) if _NUMBER.match(text) else None


def _options(raw: str) -> dict[str, str]:
    parts = re.split(r"(?<!\\)\|", raw)
    return dict(part.replace("\\|", "|").split("=", 1) for part in parts if "=" in part)


def _matcher(spec: str):
    """Điều kiện `cột:regex` (nối bằng `&`) trên các ô của một hàng (cột đánh số từ 1)."""
    rules = []
    for item in spec.split("&"):
        col, _, pattern = item.partition(":")
        rules.append((int(col) - 1, re.compile(pattern)))
    return lambda row: all(col < len(row) and rx.search(row[col]) for col, rx in rules)


def _bold_best(rows: list[list[str]], spec: str, group: int | None) -> None:
    """In đậm (tại chỗ) giá trị tốt nhất của từng cột trong `spec`, tính riêng từng nhóm."""
    for item in filter(None, (part.strip() for part in spec.split(","))):
        col, direction = int(item[:-1]) - 1, item[-1]
        buckets: dict[str, list[list[str]]] = {}
        for row in rows:
            buckets.setdefault(row[group - 1] if group else "", []).append(row)
        for bucket in buckets.values():
            values = [(_to_number(row[col]), row) for row in bucket]
            numbers = [v for v, _ in values if v is not None]
            if not numbers:
                continue
            target = max(numbers) if direction == "+" else min(numbers)
            for value, row in values:
                if value == target:
                    row[col] = f"**{row[col]}**"


def expand_include(path: Path, options: str = "") -> list[str]:
    """Chỉ lấy bảng và dòng `**Nguồn:**` của một bảng do script sinh ra; áp tuỳ chọn trình bày."""
    lines = path.read_text(encoding="utf-8").splitlines()
    table = [line for line in lines if line.startswith("|")]
    if len(table) < 3:
        raise ValueError(f"{path} không chứa bảng Markdown")
    opts = _options(options)
    if opts:
        table = _restyle_table(table, opts)
    source = next((line for line in lines if line.startswith("**Nguồn:**")), None)
    out = ["", *table, ""]
    if source:
        note = source.replace("**Nguồn:**", "Nguồn:").replace("`", "")
        note += " Bảng sinh tự động bởi script, không sửa tay."
        legend = []
        if "best" in opts:
            legend.append("In đậm: giá trị tốt nhất trong cột (không hàm ý khác biệt có ý nghĩa)")
        if "used" in opts:
            legend.append("nền xám: cấu hình đang dùng")
        if legend:
            note += " " + "; ".join(legend) + "."
        out += [f"@@NOTE:{note}@@", ""]
    return out


def _restyle_table(table: list[str], opts: dict[str, str]) -> list[str]:
    header, divider, body = table[0], table[1], [_cells(line) for line in table[2:]]
    if "keep" in opts:
        body = list(filter(_matcher(opts["keep"]), body))
        if not body:
            raise ValueError(f"keep={opts['keep']} không khớp hàng nào")
    is_used = _matcher(opts["used"]) if "used" in opts else (lambda row: False)
    flags = [bool(is_used(row)) for row in body]
    if "best" in opts:
        _bold_best(body, opts["best"], int(opts["group"]) if "group" in opts else None)
    head, align = _cells(header), _cells(divider)
    keep_cols = [int(c) - 1 for c in opts["cols"].split(",")] if "cols" in opts else None
    pick = (lambda cells: [cells[i] for i in keep_cols]) if keep_cols else (lambda cells: cells)
    rows = [pick(row) for row in body]
    for row, flag in zip(rows, flags, strict=True):
        if flag:
            row[0] = USED_MARK + row[0]
    render = lambda cells: "| " + " | ".join(cells) + " |"  # noqa: E731
    return [render(pick(head)), render(pick(align)), *(render(row) for row in rows)]


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
            out.extend(expand_include(root / include.group(1).strip(), include.group(2)))
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
