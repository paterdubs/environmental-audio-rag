"""Sơ đồ khối dạng shape Word (DrawingML), sửa được trực tiếp trong Word.

Một sơ đồ là danh sách hộp (`Box`) và đường (`Line`, có hoặc không có mũi tên), tọa độ theo cm,
gốc ở góc trên bên trái. `render()` trả về một đoạn `<w:p>` chứa khung vẽ (drawing canvas,
`wpc`) nằm cùng dòng chữ, nên sơ đồ trôi theo văn bản và đi liền với chú thích như một hình.

Ba điều đã kiểm bằng Word 365 khi thử nghiệm (ghi chú nghiên cứu "Tinh gọn báo cáo khóa luận"):
khai báo `xmlns:a` ngay trên `<a:graphic>` (gói mẫu của khoa không khai báo ở gốc); mọi id phải
duy nhất trong toàn văn bản (dùng một bộ đếm chung, bắt đầu từ 900001); đoạn trong hộp phải đặt
`pPr` tường minh, nếu không sẽ thừa hưởng thụt dòng đầu của style thân bài.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from html import escape

EMU_PER_CM = 360_000
MAX_WIDTH_CM = 15.5  # bề rộng vùng chữ của mẫu khoa (5.579.745 EMU)
FONT = "Times New Roman"
INK, MUTED = "1F2328", "57606A"
FILLS = {
    "plain": "F5F6F8",
    "model": "FBEFE8",
    "store": "EAF1FB",
    "offline": "ECF8F1",
    "none": None,
}
URI_CANVAS = "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"

_ids = itertools.count(900_001)


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float
    lines: tuple[str, ...]
    fill: str = "plain"
    title: bool = True  # dòng đầu in đậm
    size: float = 9.5
    border: bool = True
    align: str = "center"
    italic: bool = False


@dataclass(frozen=True)
class Line:
    points: tuple[tuple[float, float], ...]
    arrow: bool = True
    dashed: bool = False
    width_pt: float = 1.0


@dataclass(frozen=True)
class Diagram:
    name: str
    width: float
    height: float
    items: tuple[Box | Line, ...]
    descr: str

    def __post_init__(self) -> None:
        if self.width > MAX_WIDTH_CM + 1e-9:
            raise ValueError(f"sơ đồ {self.name} rộng {self.width} cm > {MAX_WIDTH_CM} cm")
        for item in self.items:
            xs, ys = _extent(item)
            if min(xs) < -1e-9 or max(xs) > self.width + 1e-9:
                raise ValueError(f"sơ đồ {self.name}: phần tử tràn ngang {item}")
            if min(ys) < -1e-9 or max(ys) > self.height + 1e-9:
                raise ValueError(f"sơ đồ {self.name}: phần tử tràn dọc {item}")


def _extent(item: Box | Line) -> tuple[list[float], list[float]]:
    if isinstance(item, Box):
        return [item.x, item.x + item.w], [item.y, item.y + item.h]
    return [p[0] for p in item.points], [p[1] for p in item.points]


def emu(cm: float) -> int:
    return round(cm * EMU_PER_CM)


def _run(text: str, size: float, bold: bool, italic: bool, color: str) -> str:
    flags = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "")
    return (
        f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>{flags}'
        f'<w:color w:val="{color}"/><w:sz w:val="{round(size * 2)}"/>'
        f'<w:szCs w:val="{round(size * 2)}"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
    )


def _paragraph(text: str, box: Box, bold: bool) -> str:
    color = INK if bold or not box.title else MUTED
    return (
        '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:left="0" w:right="0" w:firstLine="0"/>'
        f'<w:jc w:val="{box.align}"/></w:pPr>'
        f"{_run(text, box.size, bold, box.italic, color)}</w:p>"
    )


def _box_xml(box: Box) -> str:
    ident = next(_ids)
    fill = FILLS[box.fill]
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    line_xml = (
        f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{MUTED}"/></a:solidFill></a:ln>'
        if box.border
        else "<a:ln><a:noFill/></a:ln>"
    )
    paragraphs = "".join(
        _paragraph(text, box, box.title and index == 0 and len(box.lines) > 1)
        for index, text in enumerate(box.lines)
    )
    inset = emu(0.08)
    return (
        f'<wps:wsp><wps:cNvPr id="{ident}" name="Hộp {ident}"/><wps:cNvSpPr/>'
        f'<wps:spPr><a:xfrm><a:off x="{emu(box.x)}" y="{emu(box.y)}"/>'
        f'<a:ext cx="{emu(box.w)}" cy="{emu(box.h)}"/></a:xfrm>'
        '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst>'
        f"</a:prstGeom>{fill_xml}{line_xml}</wps:spPr>"
        f"<wps:txbx><w:txbxContent>{paragraphs}</w:txbxContent></wps:txbx>"
        f'<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="{inset}" tIns="{inset}" '
        f'rIns="{inset}" bIns="{inset}" anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr>'
        "</wps:wsp>"
    )


def _segment_xml(start: tuple[float, float], end: tuple[float, float], line: Line,
                 head: bool) -> str:
    ident = next(_ids)
    (x0, y0), (x1, y1) = start, end
    flips = (' flipH="1"' if x1 < x0 else "") + (' flipV="1"' if y1 < y0 else "")
    dash = '<a:prstDash val="dash"/>' if line.dashed else ""
    tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if head else ""
    return (
        f'<wps:wsp><wps:cNvPr id="{ident}" name="Đường {ident}"/><wps:cNvCnPr/>'
        f"<wps:spPr><a:xfrm{flips}><a:off x=\"{emu(min(x0, x1))}\" y=\"{emu(min(y0, y1))}\"/>"
        f'<a:ext cx="{emu(abs(x1 - x0))}" cy="{emu(abs(y1 - y0))}"/></a:xfrm>'
        '<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>'
        f'<a:ln w="{round(line.width_pt * 12700)}"><a:solidFill><a:srgbClr val="{MUTED}"/>'
        f"</a:solidFill>{dash}{tail}</a:ln></wps:spPr><wps:bodyPr/></wps:wsp>"
    )


def _line_xml(line: Line) -> str:
    points = line.points
    if len(points) < 2:
        raise ValueError("đường cần ít nhất hai điểm")
    last = len(points) - 2
    return "".join(
        _segment_xml(points[i], points[i + 1], line, line.arrow and i == last)
        for i in range(len(points) - 1)
    )


def render(diagram: Diagram) -> str:
    """Đoạn `FigurePara` chứa khung vẽ; marker `@@CAP:fig:…@@` ngay sau sẽ thêm keepNext."""
    shapes = "".join(
        _box_xml(item) if isinstance(item, Box) else _line_xml(item) for item in diagram.items
    )
    doc_id = next(_ids)
    cx, cy = emu(diagram.width), emu(diagram.height)
    drawing = (
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{doc_id}" name="Sơ đồ {escape(diagram.name)}" '
        f'descr="{escape(diagram.descr)}"/><wp:cNvGraphicFramePr/>'
        f'<a:graphic xmlns:a="{NS_A}"><a:graphicData uri="{URI_CANVAS}">'
        f"<wpc:wpc><wpc:bg/><wpc:whole/>{shapes}</wpc:wpc>"
        "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
    )
    return f'<w:p><w:pPr><w:pStyle w:val="FigurePara"/></w:pPr>{drawing}</w:p>'


def boxes_in(diagram: Diagram) -> Iterable[Box]:
    return (item for item in diagram.items if isinstance(item, Box))
