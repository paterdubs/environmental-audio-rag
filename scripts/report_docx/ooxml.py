"""Biến đổi XML thân bài do Pandoc sinh thành XML theo style và field của mẫu khoa."""

from __future__ import annotations

import itertools
import math
import re
from collections.abc import Callable
from html import escape, unescape

from scripts.report_docx.markdown import INLINE_REF, LABELS, USED_MARK, Registry

TEXT_WIDTH = 8787  # twip: A4 11906 − lề trái 1985 − lề phải 1134
_BOOKMARK_IDS = itertools.count(9000)
_TOKEN = re.compile(r"<(/?)w:(p|tbl)\b([^>]*?)(/?)>")
_WT = re.compile(r"<[wm]:t(?:\s[^>]*)?>([^<]*)</[wm]:t>")  # chữ thường và chữ trong công thức
_PARAGRAPH_MARKER = re.compile(r"^@@(\w+)(?::(.*))?@@$", re.S)
_EQNO_ONLY = re.compile(r"^⟪eqno:([\w-]+)⟫$")
BODY_STYLES = {"FirstParagraph", "BodyText", "Normal"}


def top_level_elements(body: str) -> list[str]:
    """Tách các phần tử con trực tiếp `<w:p>`/`<w:tbl>` (tính cả lồng trong text box/bảng)."""
    elements, depth, start = [], 0, None
    for match in _TOKEN.finditer(body):
        closing, _, _, selfclosing = match.groups()
        if selfclosing:
            if depth == 0:
                elements.append(match.group(0))
            continue
        if not closing:
            if depth == 0:
                start = match.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                elements.append(body[start : match.end()])
    return elements


def text_of(xml: str) -> str:
    return "".join(_WT.findall(xml)).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def run(text: str, rpr: str = "") -> str:
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text, quote=False)}</w:t></w:r>'


def field(instruction: str, result: str, rpr: str = "") -> str:
    return (
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> {escape(instruction, quote=False)} '
        f'</w:instrText></w:r><w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'{run(result, rpr)}<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def bookmark_name(kind: str, key: str) -> str:
    name = "_Ref" + kind.capitalize() + "_" + re.sub(r"[^A-Za-z0-9]", "_", key)
    return name[:40]


def bookmarked(kind: str, key: str, inner: str) -> str:
    ident = next(_BOOKMARK_IDS)
    return (
        f'<w:bookmarkStart w:id="{ident}" w:name="{bookmark_name(kind, key)}"/>{inner}'
        f'<w:bookmarkEnd w:id="{ident}"/>'
    )


def paragraph(style: str, content: str, extra_ppr: str = "") -> str:
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{extra_ppr}</w:pPr>{content}</w:p>'


def number_fields(kind: str, number: str) -> str:
    """`STYLEREF 1 \\s` + `.` + `SEQ` như mẫu khoa; phụ lục dùng nhãn tĩnh PL.n."""
    if number.startswith("PL."):
        return run(number)
    chapter, index = number.split(".")
    seq = {"tbl": "Bảng", "fig": "Hình", "eq": "PT"}[kind]
    return field("STYLEREF 1 \\s", chapter) + run(".") + field(f"SEQ {seq} \\* ARABIC \\s 1", index)


def caption_paragraph(kind: str, key: str, registry: Registry) -> str:
    number = registry.numbers[(kind, key)]
    label = bookmarked(kind, key, run(f"{LABELS[kind]} ") + number_fields(kind, number))
    keep = "<w:keepNext/>" if kind == "tbl" else ""
    return paragraph("Caption", label + run(" " + registry.captions[(kind, key)]), keep)


def equation_paragraph(math_paragraph: str, key: str, registry: Registry) -> str:
    match = re.search(
        r"<m:oMathPara>.*?(<m:oMath>.*</m:oMath>).*?</m:oMathPara>", math_paragraph, re.S
    )
    if not match:
        raise ValueError(f"Số công thức {key} không đi sau một công thức hiển thị")
    number = bookmarked(
        "eq", key, run("(") + number_fields("eq", registry.numbers[("eq", key)]) + run(")")
    )
    tabs = (
        f'<w:tabs><w:tab w:val="center" w:pos="{TEXT_WIDTH // 2}"/>'
        f'<w:tab w:val="right" w:pos="{TEXT_WIDTH}"/></w:tabs>'
    )
    return paragraph(
        "Equation", "<w:r><w:tab/></w:r>" + match.group(1) + "<w:r><w:tab/></w:r>" + number, tabs
    )


def replace_inline_refs(xml: str, registry: Registry) -> str:
    """Thay ⟪kind:key⟫ trong từng `<w:r>` bằng field REF tới bookmark của chú thích."""

    def fix_run(match: re.Match) -> str:
        rpr = match.group(1) or ""
        text = unescape(match.group(2))  # w:t đã escape; run() sẽ escape lại
        if "⟪" not in text:
            return match.group(0)
        pieces, last = [], 0
        for ref in INLINE_REF.finditer(text):
            pieces.append(run(text[last : ref.start()], rpr) if ref.start() > last else "")
            kind, key = ref.groups()
            pieces.append(
                field(f"REF {bookmark_name(kind, key)} \\h", registry.text(kind, key), rpr)
            )
            last = ref.end()
        pieces.append(run(text[last:], rpr) if last < len(text) else "")
        return "".join(pieces)

    return re.sub(r"<w:r>(<w:rPr>.*?</w:rPr>)?<w:t(?:\s[^>]*)?>([^<]*)</w:t></w:r>", fix_run, xml)


def restyle_paragraph(xml: str) -> str:
    if "<w:numPr>" in xml:  # danh sách gạch đầu dòng của Pandoc → style Bullet của mẫu
        return re.sub(
            r"<w:pPr>.*?</w:pPr>",
            '<w:pPr><w:pStyle w:val="Bullet"/></w:pPr>',
            xml,
            count=1,
            flags=re.S,
        )
    if "<w:drawing>" in xml:
        return re.sub(
            r"<w:pPr>.*?</w:pPr>",
            '<w:pPr><w:pStyle w:val="FigurePara"/></w:pPr>',
            xml,
            count=1,
            flags=re.S,
        )
    style = re.search(r'<w:pStyle w:val="([^"]+)"', xml)
    if style and style.group(1) in BODY_STYLES | {"Compact"}:
        return xml.replace(f'<w:pStyle w:val="{style.group(1)}" />', '<w:pStyle w:val="Content"/>')
    return xml


# ---------------------------------------------------------------- bảng
_NUMERIC = re.compile(r"^[−+\-–]?[\d.,]+%?$|^\[.*\]$|^—$")


def _column_widths(rows: list[list[str]]) -> list[int]:
    """Mỗi cột đủ rộng cho từ dài nhất (tiêu đề được phép xuống dòng hơn), phần còn lại chia
    theo lượng chữ của cột — tránh cột bị ép thành chữ dọc."""
    columns = max(len(row) for row in rows)
    header, body = rows[0], rows[1:] or rows
    minimums, weights = [], []
    for index in range(columns):
        cells = [row[index] for row in body if index < len(row)]
        body_word = max((len(word) for cell in cells for word in cell.split()), default=1)
        head_word = max(
            (len(word) for word in (header[index] if index < len(header) else "").split()),
            default=1,
        )
        minimums.append(max(body_word * 110, head_word * 105) + 330)
        mean = sum(len(cell) for cell in cells) / max(len(cells), 1)
        peak = max((len(cell) for cell in cells), default=1)
        weights.append(math.sqrt(max(mean, 1.0) * max(peak, 1)))
    spare = TEXT_WIDTH - sum(minimums)
    if spare <= 0:
        widths = [int(m * TEXT_WIDTH / sum(minimums)) for m in minimums]
    else:
        widths = [m + int(spare * w / sum(weights)) for m, w in zip(minimums, weights, strict=True)]
    widths[-1] += TEXT_WIDTH - sum(widths)
    return widths


def transform_table(xml: str, percents: list[float] | None = None) -> str:
    rows_xml = re.findall(r"<w:tr>.*?</w:tr>|<w:tr .*?</w:tr>", xml, re.S)
    rows = [
        [text_of(cell) for cell in re.findall(r"<w:tc>.*?</w:tc>", row, re.S)] for row in rows_xml
    ]
    if percents:  # tỷ lệ cột khai báo tường minh bằng @@COLWIDTHS@@
        widths = [int(TEXT_WIDTH * p / sum(percents)) for p in percents]
        widths[-1] += TEXT_WIDTH - sum(widths)
    else:
        widths = _column_widths(rows)
    small = len(widths) >= 7
    border = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    tblpr = (
        '<w:tblPr><w:tblW w:w="{0}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
        + "".join(
            border.format(side) for side in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        + '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar>'
        '<w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar>'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" '
        'w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
    ).format(TEXT_WIDTH)
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"
    out_rows = []
    for row_index, row in enumerate(rows_xml):
        header = row_index == 0
        used = USED_MARK in row
        row = row.replace(USED_MARK, "")
        cells = re.findall(r"<w:tc>.*?</w:tc>", row, re.S)
        new_cells = []
        for col, cell in enumerate(cells):
            text = text_of(cell)
            jc = re.search(r'<w:jc w:val="(\w+)"', cell)
            align = (
                jc.group(1)
                if jc
                else ("right" if _NUMERIC.match(text.strip()) and not header else "left")
            )
            if header:
                align = "center"
            style = "TableTextSmall" if small else "TableText"
            runs = "".join(
                re.findall(r"<w:r>.*?</w:r>|<w:r .*?</w:r>|<m:oMath>.*?</m:oMath>", cell, re.S)
            )
            if header:
                runs = re.sub(r"<w:r>(?!<w:rPr>)", "<w:r><w:rPr><w:b/></w:rPr>", runs)
                runs = runs.replace("<w:rPr><w:rStyle", "<w:rPr><w:b/><w:rStyle")
            fill = "E7E6E6" if header else ("D9D9D9" if used else "")
            shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
            # Bảng ngắn: giữ mọi hàng cùng trang với hàng sau (và với tiêu đề bảng ở trên).
            keep = "<w:keepNext/>" if len(rows_xml) <= 16 else ""
            new_cells.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[col]}" w:type="dxa"/>{shade}'
                f'<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{keep}<w:jc w:val="{align}"/>'
                f"</w:pPr>{runs}</w:p></w:tc>"
            )
        trpr = "<w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if header else "") + "</w:trPr>"
        out_rows.append(f"<w:tr>{trpr}{''.join(new_cells)}</w:tr>")
    return f"<w:tbl>{tblpr}{grid}{''.join(out_rows)}</w:tbl>"


# ---------------------------------------------------------------- lắp thân bài
def transform_body(body: str, registry: Registry, handlers: dict[str, Callable[[str], str]]) -> str:
    """Áp mọi biến đổi lên dãy phần tử thân bài theo thứ tự."""
    out: list[str] = []
    percents: list[float] | None = None
    for element in top_level_elements(body):
        if element.startswith("<w:tbl"):
            out.append(transform_table(replace_inline_refs(element, registry), percents))
            percents = None
            continue
        text = text_of(element).strip()
        eqno = _EQNO_ONLY.match(text)
        if eqno:
            out[-1] = equation_paragraph(out[-1], eqno.group(1), registry)
            continue
        marker = _PARAGRAPH_MARKER.match(text)
        if marker:
            name, argument = marker.group(1), marker.group(2) or ""
            if name == "COLWIDTHS":
                percents = [float(v) for v in argument.split(",")]
                continue
            if name == "CAP":
                kind, rest = argument.split(":", 1)
                key = rest.split("|", 1)[0]
                if kind == "fig" and out:
                    out[-1] = out[-1].replace(
                        '<w:pStyle w:val="FigurePara"/>',
                        '<w:pStyle w:val="FigurePara"/><w:keepNext/>',
                    )
                out.append(caption_paragraph(kind, key, registry))
                continue
            if name not in handlers:
                raise KeyError(f"Marker chưa hỗ trợ: {name}")
            out.append(handlers[name](argument))
            continue
        out.append(replace_inline_refs(restyle_paragraph(element), registry))
    return "".join(out)
