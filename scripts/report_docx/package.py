"""Lắp ráp gói DOCX từ package mẫu khoa (styles, numbering, header/footer, bìa, section)."""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from scripts.report_docx import bib as biblio
from scripts.report_docx.ooxml import TEXT_WIDTH, field, paragraph, run, text_of, top_level_elements

NS_EXTRA = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
}
# rId của header/footer trong package mẫu (đọc từ word/_rels/document.xml.rels).
FOOTER_FRONT, HEADER_BODY, FOOTER_BODY, FOOTER_REFS, FOOTER_APPX = (
    "rId9",
    "rId10",
    "rId11",
    "rId13",
    "rId14",
)


@dataclass(frozen=True)
class FrontInfo:
    """Thông tin trang bìa, header, footer — placeholder khi chưa có thông tin thật."""

    title_vi: str
    title_en: str
    student_1: str
    student_2: str
    student_1_en: str
    student_2_en: str
    supervisor: str
    supervisor_en: str
    city_date: str
    city_date_en: str
    header: str
    footer: str


# ---------------------------------------------------------------- styles
def _set_ppr(style_block: str, ppr_inner: str) -> str:
    if "<w:pPr>" in style_block:
        return re.sub(
            r"<w:pPr>.*?</w:pPr>", f"<w:pPr>{ppr_inner}</w:pPr>", style_block, count=1, flags=re.S
        )
    return style_block.replace("</w:style>", f"<w:pPr>{ppr_inner}</w:pPr></w:style>")


def _style_block(styles: str, style_id: str) -> str:
    match = re.search(rf'<w:style [^>]*w:styleId="{style_id}"[^>]*>.*?</w:style>', styles, re.S)
    if not match:
        raise KeyError(f"Mẫu khoa thiếu style {style_id}")
    return match.group(0)


def _spacing(before: int, after: int, line: int) -> str:
    return f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'


def _style(
    style_id: str,
    name: str,
    based_on: str,
    ppr: str = "",
    rpr: str = "",
    kind: str = "paragraph",
    extra: str = "<w:qFormat/>",
) -> str:
    ppr_xml = f"<w:pPr>{ppr}</w:pPr>" if ppr else ""
    rpr_xml = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return (
        f'<w:style w:type="{kind}" w:customStyle="1" w:styleId="{style_id}">'
        f'<w:name w:val="{name}"/><w:basedOn w:val="{based_on}"/>{extra}'
        f"{ppr_xml}{rpr_xml}</w:style>"
    )


_NO_INDENT = '<w:ind w:firstLine="0"/>'
_SIZE = '<w:sz w:val="{0}"/><w:szCs w:val="{0}"/>'
_TNR = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
_DOT_TAB = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TEXT_WIDTH}"/></w:tabs>'
NEW_STYLES = "".join(
    [
        _style(
            "TableText",
            "Table Text",
            "Normal",
            f'<w:keepLines/>{_spacing(20, 20, 240)}{_NO_INDENT}<w:jc w:val="left"/>',
            _SIZE.format(22),
        ),
        _style("TableTextSmall", "Table Text Small", "TableText", rpr=_SIZE.format(20)),
        _style(
            "TableNote",
            "Table Note",
            "Normal",
            f'{_spacing(60, 120, 240)}{_NO_INDENT}<w:jc w:val="left"/>',
            "<w:i/><w:iCs/>" + _SIZE.format(22),
        ),
        _style(
            "FigurePara",
            "Figure Paragraph",
            "Normal",
            f'<w:keepNext/>{_spacing(120, 0, 240)}{_NO_INDENT}<w:jc w:val="center"/>',
        ),
        _style(
            "Equation",
            "Equation",
            "Content",
            f'{_spacing(120, 120, 276)}{_NO_INDENT}<w:jc w:val="left"/>',
        ),
        _style(
            "Bibliography",
            "Bibliography",
            "Normal",
            f'{_spacing(0, 120, 276)}<w:ind w:left="567" w:hanging="567"/><w:jc w:val="both"/>',
        ),
        _style(
            "Heading2N",
            "Heading 2N",
            "Heading2",
            '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>'
            '<w:ind w:left="0" w:firstLine="0"/><w:outlineLvl w:val="1"/>',
            extra='<w:next w:val="Content"/><w:qFormat/>',
        ),
        _style(
            "DotLine",
            "Dot Line",
            "Normal",
            f"{_DOT_TAB}{_spacing(0, 0, 360)}{_NO_INDENT}",
            extra="",
        ),
        _style(
            "VerbatimChar",
            "Verbatim Char",
            "DefaultParagraphFont",
            rpr=_TNR,
            kind="character",
            extra="",
        ),
    ]
)


def patch_styles(styles: str) -> str:
    """Chuẩn hóa style theo hướng dẫn bằng chữ của mẫu (report/quy_cach_bao_cao.md §3)."""
    no_indent = '<w:ind w:left="0" w:firstLine="0"/>'
    patches = {
        "Heading1": (
            '<w:keepNext/><w:keepLines/><w:pageBreakBefore/><w:numPr><w:numId w:val="32"/>'
            f'</w:numPr>{_spacing(480, 480, 276)}<w:ind w:left="0" w:firstLine="0"/>'
            '<w:jc w:val="left"/><w:outlineLvl w:val="0"/>'
        ),
        "Heading2": (
            '<w:keepNext/><w:keepLines/><w:numPr><w:ilvl w:val="1"/><w:numId w:val="32"/>'
            f'</w:numPr>{_spacing(120, 240, 276)}{no_indent}<w:jc w:val="left"/>'
            '<w:outlineLvl w:val="1"/>'
        ),
        "Heading3": (
            '<w:keepNext/><w:keepLines/><w:numPr><w:ilvl w:val="2"/><w:numId w:val="32"/>'
            f'</w:numPr>{_spacing(120, 240, 276)}{no_indent}<w:jc w:val="left"/>'
            '<w:outlineLvl w:val="2"/>'
        ),
        "Heading4": (
            '<w:keepNext/><w:keepLines/><w:numPr><w:ilvl w:val="3"/><w:numId w:val="32"/>'
            f'</w:numPr>{_spacing(120, 240, 276)}{no_indent}<w:jc w:val="left"/>'
            '<w:outlineLvl w:val="3"/>'
        ),
        "Caption": f'{_spacing(120, 240, 276)}<w:ind w:firstLine="0"/><w:jc w:val="center"/>',
        "Content": f'{_spacing(200, 0, 360)}<w:ind w:firstLine="0"/><w:jc w:val="both"/>',
        "Bullet": (
            '<w:numPr><w:numId w:val="30"/></w:numPr>'
            f'{_spacing(0, 0, 360)}<w:ind w:left="284" w:hanging="284"/><w:jc w:val="left"/>'
        ),
        "TableofFigures": f'{_spacing(0, 0, 276)}<w:ind w:firstLine="0"/>',
    }
    for style_id, ppr in patches.items():
        block = _style_block(styles, style_id)
        new = _set_ppr(block, ppr)
        if style_id == "Heading1":
            new = new.replace("<w:b/>", "<w:b/><w:caps/>", 1)
        if style_id == "Caption":
            new = new.replace("<w:i/>", "").replace("<w:iCs/>", "")
        styles = styles.replace(block, new)
    toc_tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TEXT_WIDTH}"/></w:tabs>'
    for style_id, left in (("TOC1", 0), ("TOC2", 260), ("TOC3", 520)):
        block = _style_block(styles, style_id)
        ppr = f'{toc_tab}{_spacing(0, 0, 276)}<w:ind w:left="{left}" w:firstLine="0"/>'
        styles = styles.replace(block, _set_ppr(block, ppr))
    if 'w:styleId="VerbatimChar"' in styles:
        raise ValueError("Mẫu đã có VerbatimChar; cần xem lại trước khi ghi đè")
    return styles.replace("</w:styles>", NEW_STYLES + "</w:styles>")


# ---------------------------------------------------------------- bìa
def set_text(element: str, text: str, size: int | None = None) -> str:
    """Giữ pPr và rPr của run chữ đầu tiên, thay toàn bộ nội dung chữ."""
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", element, re.S)
    first = re.search(r"<w:r(?: [^>]*)?>(<w:rPr>.*?</w:rPr>)?<w:t", element, re.S)
    rpr = first.group(1) or "" if first else ""
    if size is not None:
        rpr = re.sub(r'<w:sz w:val="\d+"/>', f'<w:sz w:val="{size}"/>', rpr)
        rpr = re.sub(r'<w:szCs w:val="\d+"/>', f'<w:szCs w:val="{size}"/>', rpr)
    lines = text.split("\n")
    content = "".join(
        (run(line, rpr) if i == 0 else f"<w:r>{rpr}<w:br/></w:r>" + run(line, rpr))
        for i, line in enumerate(lines)
    )
    return f"<w:p>{ppr.group(0) if ppr else ''}{content}</w:p>"


def cover_elements(template_body: str, info: FrontInfo) -> list[str]:
    elements = top_level_elements(template_body)
    end_cover2 = next(
        i
        for i, e in enumerate(elements)
        if "GUIDANCE AND SAMPLE OF THE GRADUATION REPORT IN 2020" in text_of(e)
    )
    replacements = {
        "HỌ VÀ TÊN SINH VIÊN 1": (info.student_1, None),
        "HỌ VÀ TÊN SINH VIÊN 2": (info.student_2, None),
        "HƯỚNG DẪN VÀ MẪU BÁO CÁO KHÓA LUẬN TỐT NGHIỆP NĂM 2026": (
            "BÁO CÁO GIỮA KỲ KHÓA LUẬN TỐT NGHIỆP\n\n" + info.title_vi.upper(),
            None,
        ),
        "Giảng viên hướng dẫn: TS. Họ và Tên GVHD": (info.supervisor, None),
        "THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026": (info.city_date, None),
        "FULLNAME OF THE FIRST STUDENT": (info.student_1_en, None),
        "FULLNAME OF THE SECOND STUDENT": (info.student_2_en, None),
        "GUIDANCE AND SAMPLE OF THE GRADUATION REPORT IN 2026": (
            "MID-TERM GRADUATION THESIS REPORT\n\n" + info.title_en,
            None,
        ),
        "Supervisor: Dr. Full name of supervisor": (info.supervisor_en, None),
        "HO CHI MINH CITY – DECEMBER 2026": (info.city_date_en, None),
    }
    titles = {
        "HƯỚNG DẪN VÀ MẪU BÁO CÁO KHÓA LUẬN TỐT NGHIỆP NĂM 2026",
        "GUIDANCE AND SAMPLE OF THE GRADUATION REPORT IN 2026",
    }
    out, used, skip_empty = [], set(), 0
    for element in elements[:end_cover2]:
        text = " ".join(text_of(element).split())
        if (
            skip_empty
            and not text
            and "<w:drawing" not in element
            and "<w:sectPr" not in element
            and 'w:type="page"' not in element
        ):
            skip_empty -= 1  # tiêu đề dài hơn mẫu: bỏ bớt dòng trống để bìa vẫn vừa một trang
            continue
        if text in replacements and "<w:drawing" not in element:
            new_text, size = replacements[text]
            element = set_text(element, new_text, size)
            used.add(text)
            skip_empty = (4 if text.startswith("GUIDANCE") else 2) if text in titles else 0
        out.append(element)
    missing = set(replacements) - used
    if missing:
        raise ValueError(f"Không tìm thấy đoạn bìa để thay: {sorted(missing)}")
    return out


# ---------------------------------------------------------------- header/footer
def set_header_footer_text(xml: str, text: str) -> str:
    start = xml.index("</mc:AlternateContent></w:r>") + len("</mc:AlternateContent></w:r>")
    end = xml.find("<w:r><w:ptab", start)
    if end < 0:
        end = xml.rindex("</w:p>")
    return xml[:start] + run(text) + xml[end:]


# ---------------------------------------------------------------- section / marker
def sect_pr(kind: str) -> str:
    refs = {
        "front": f'<w:footerReference w:type="default" r:id="{FOOTER_FRONT}"/>',
        "body": (
            f'<w:headerReference w:type="default" r:id="{HEADER_BODY}"/>'
            f'<w:footerReference w:type="default" r:id="{FOOTER_BODY}"/>'
        ),
        "refs": f'<w:footerReference w:type="default" r:id="{FOOTER_REFS}"/>',
        "appendix": f'<w:footerReference w:type="default" r:id="{FOOTER_APPX}"/>',
    }[kind]
    numbering = {
        "front": '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>',
        "body": '<w:pgNumType w:start="1"/>',
        "refs": '<w:pgNumType w:fmt="lowerLetter" w:start="1"/>',
        "appendix": '<w:pgNumType w:fmt="lowerLetter"/>',
    }[kind]
    return (
        f'<w:sectPr>{refs}<w:pgSz w:w="11906" w:h="16838" w:code="9"/>'
        '<w:pgMar w:top="1701" w:right="1134" w:bottom="1701" w:left="1985" w:header="990" '
        f'w:footer="810" w:gutter="0"/>{numbering}<w:cols w:space="720"/>'
        '<w:docGrid w:linePitch="360"/></w:sectPr>'
    )


def toc_paragraph(instruction: str, placeholder: str) -> str:
    return paragraph("TOC1", field(instruction, placeholder))


def review_page() -> str:
    lines = "".join(paragraph("DotLine", "<w:r><w:tab/></w:r>") for _ in range(16))
    date = paragraph(
        "Normal",
        run("TP. Hồ Chí Minh, ngày …. tháng …. năm ……", "<w:rPr><w:i/></w:rPr>"),
        '<w:spacing w:before="240"/><w:ind w:firstLine="0"/><w:jc w:val="right"/>',
    )
    sign = paragraph(
        "Normal",
        run("CHỮ KÝ CỦA GIẢNG VIÊN", "<w:rPr><w:b/></w:rPr>"),
        '<w:ind w:left="4536" w:firstLine="0"/><w:jc w:val="center"/>',
    )
    return lines + date + sign


def bibliography_paragraphs(entries: list[biblio.Entry]) -> str:
    numbers = biblio.numbering(entries)
    out = []
    for language, members in biblio.ordered(entries):
        out.append(
            paragraph(
                "Content",
                run(biblio.LANGUAGE_TITLES[language], "<w:rPr><w:b/></w:rPr>"),
                "<w:keepNext/>",
            )
        )
        for entry in members:
            runs = run(f"[{numbers[entry.key]}]. ")
            for text, italic in biblio.format_entry(entry):
                runs += run(text, "<w:rPr><w:i/><w:iCs/></w:rPr>" if italic else "")
            out.append(paragraph("Bibliography", runs))
    return "".join(out)


def marker_handlers(entries: list[biblio.Entry]) -> dict:
    page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    return {
        "PAGEBREAK": lambda _: page_break,
        "SECTION": lambda kind: f"<w:p><w:pPr>{sect_pr(kind.strip())}</w:pPr></w:p>",
        "TOC": lambda _: toc_paragraph(
            'TOC \\o "1-3" \\h \\z \\u', "[Mục lục — cập nhật field trong Word]"
        ),
        "TOF": lambda label: toc_paragraph(
            f'TOC \\h \\z \\c "{label.strip()}"',
            f"[Danh mục {label.strip().lower()} — cập nhật field]",
        ),
        "TITLE": lambda text: paragraph("CoverB", run(text.strip())),
        "HEADING1N": lambda text: paragraph("Heading1N", run(text.strip())),
        "HEADING2N": lambda text: paragraph("Heading2N", run(text.strip())),
        "NOTE": lambda text: paragraph("TableNote", run(text.strip())),
        "BIB": lambda _: bibliography_paragraphs(entries),
        "REVIEWPAGE": lambda _: review_page(),
        "APPENDIX": lambda _: "",
    }


# ---------------------------------------------------------------- gói
def assemble(template: Path, body_docx: Path, body_xml: str, info: FrontInfo, output: Path) -> None:
    with zipfile.ZipFile(template) as tz, zipfile.ZipFile(body_docx) as bz:
        files = {name: tz.read(name) for name in tz.namelist()}
        document = files["word/document.xml"].decode("utf-8")
        root_end = document.index("<w:body>")
        root = document[:root_end]
        for prefix, uri in NS_EXTRA.items():
            if f"xmlns:{prefix}=" not in root:
                root = root.replace("<w:document ", f'<w:document xmlns:{prefix}="{uri}" ', 1)
        template_body = document[root_end + len("<w:body>") : document.rindex("</w:body>")]
        covers = "".join(cover_elements(template_body, info))
        rels = files["word/_rels/document.xml.rels"].decode("utf-8")
        body_rels = bz.read("word/_rels/document.xml.rels").decode("utf-8")
        images = []
        for rel in re.findall(r"<Relationship [^>]*>", body_rels):
            rid, target = re.search(r'Id="([^"]+)"', rel), re.search(r'Target="(media/[^"]+)"', rel)
            if rid and target:
                images.append((rid.group(1), target.group(1)))
        for rid, target in images:
            new_id = f"rIdFig{rid[3:]}"
            new_target = f"media/report_{Path(target).name}"
            files[f"word/{new_target}"] = bz.read(f"word/{target}")
            body_xml = body_xml.replace(f'r:embed="{rid}"', f'r:embed="{new_id}"')
            rels = rels.replace(
                "</Relationships>",
                f'<Relationship Id="{new_id}" Type="http://schemas.openxmlformats.org/'
                f'officeDocument/2006/relationships/image" Target="{new_target}"/>'
                "</Relationships>",
            )
    files["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    files["word/styles.xml"] = patch_styles(files["word/styles.xml"].decode("utf-8")).encode(
        "utf-8"
    )
    files["word/header1.xml"] = set_header_footer_text(
        files["word/header1.xml"].decode("utf-8"), info.header
    ).encode("utf-8")
    for name in ("word/footer2.xml", "word/footer3.xml"):
        files[name] = set_header_footer_text(files[name].decode("utf-8"), info.footer).encode(
            "utf-8"
        )
    types = files["[Content_Types].xml"].decode("utf-8")
    if 'Extension="png"' not in types:
        types = types.replace(
            "<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1
        )
    files["[Content_Types].xml"] = types.encode("utf-8")
    final = sect_pr("appendix")
    files["word/document.xml"] = (
        root + "<w:body>" + covers + body_xml + final + "</w:body></w:document>"
    ).encode("utf-8")
    core = files["docProps/core.xml"].decode("utf-8")
    core = re.sub(r"<dc:title>.*?</dc:title>|<dc:title/>", "", core)
    core = core.replace(
        "</cp:coreProperties>", f"<dc:title>{info.title_vi}</dc:title></cp:coreProperties>"
    )
    files["docProps/core.xml"] = core.encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as out:
        for name in ["[Content_Types].xml"] + [n for n in files if n != "[Content_Types].xml"]:
            out.writestr(name, files[name])
