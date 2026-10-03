"""Kiểm tra cấu trúc tệp DOCX báo cáo giữa kỳ theo quy cách mẫu khoa (task L3).

Chỉ đọc tệp DOCX (và PDF nếu có); in kết quả dạng Markdown để chép vào report/kiem_tra_bao_cao.md.

    .venv/Scripts/python.exe -m scripts.check_midterm_docx
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx"
TWIP_PER_CM = 567
EXPECTED_MARGINS = {"top": 1701, "bottom": 1701, "left": 1985, "right": 1134}
# (cỡ chữ half-point, before, after, line) theo hướng dẫn chữ của mẫu; None = không kiểm.
EXPECTED_STYLES = {
    "Heading1": (28, 480, 480, 276),
    "Heading2": (None, 120, 240, 276),
    "Heading3": (None, 120, 240, 276),
    "Heading4": (None, 120, 240, 276),
    "Content": (None, 200, 0, 360),
    "Caption": (None, 120, 240, 276),
    "TOC1": (None, 0, 0, 276),
    "TableofFigures": (None, 0, 0, 276),
}


def _block(styles: str, style_id: str) -> str:
    match = re.search(rf'<w:style [^>]*w:styleId="{style_id}"[^>]*>.*?</w:style>', styles, re.S)
    return match.group(0) if match else ""


def style_props(styles: str, style_id: str) -> dict[str, str | None]:
    """Giá trị hiệu lực: đi theo chuỗi basedOn, vì Word bỏ thuộc tính trùng style cha khi lưu."""
    chain, current = [], style_id
    while current and len(chain) < 10:
        block = _block(styles, current)
        if not block:
            break
        chain.append(block)
        parent = re.search(r'<w:basedOn w:val="([^"]+)"', block)
        current = parent.group(1) if parent else ""
    defaults = re.search(r"<w:docDefaults>.*?</w:docDefaults>", styles, re.S)
    chain.append(defaults.group(0) if defaults else "")

    def attr(tag: str, name: str) -> str | None:
        for block in chain:
            match = re.search(rf"<w:{tag} [^>]*w:{name}=\"(\d+)\"", block)
            if match:
                return match.group(1)
        return "0" if tag == "spacing" and name in ("before", "after") else None

    own = chain[0]
    return {
        "sz": attr("sz", "val"),
        "before": attr("spacing", "before"),
        "after": attr("spacing", "after"),
        "line": attr("spacing", "line"),
        "caps": "yes" if "<w:caps/>" in own else "no",
        "italic": "yes" if "<w:i/>" in own else "no",
    }


def field_instructions(document: str) -> Counter:
    """Ghép instrText của từng field (Word có thể tách một lệnh thành nhiều run)."""
    counts: Counter = Counter()
    for chunk in document.split('w:fldCharType="begin"')[1:]:
        code = "".join(
            re.findall(
                r"<w:instrText[^>]*>([^<]*)</w:instrText>",
                chunk.split('w:fldCharType="separate"')[0],
            )
        )
        words = code.split()
        if words:
            key = " ".join(words[:2]) if words[0] in ("SEQ", "TOC") else words[0]
            counts[key] += 1
    return counts


def check(docx: Path) -> list[tuple[str, str, bool]]:
    with zipfile.ZipFile(docx) as archive:
        document = archive.read("word/document.xml").decode("utf-8")
        styles = archive.read("word/styles.xml").decode("utf-8")
        footers = {
            n: archive.read(n).decode("utf-8")
            for n in archive.namelist()
            if re.match(r"word/footer\d\.xml", n)
        }
    rows: list[tuple[str, str, bool]] = []
    sections = re.findall(
        r"<w:sectPr>.*?</w:sectPr>|<w:sectPr [^>]*>.*?</w:sectPr>", document, re.S
    )
    rows.append(("Số section", str(len(sections)), len(sections) == 5))
    for index, section in enumerate(sections, start=1):
        size = re.search(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"', section)
        margins = dict(
            re.findall(
                r'w:(top|bottom|left|right)="(\d+)"',
                re.search(r"<w:pgMar [^>]*>", section).group(0),
            )
        )
        ok_margin = all(int(margins[k]) == v for k, v in EXPECTED_MARGINS.items())
        numbering = re.search(r"<w:pgNumType[^>]*>", section)
        width_cm = int(size.group(1)) / TWIP_PER_CM
        height_cm = int(size.group(2)) / TWIP_PER_CM
        rows.append(
            (
                f"Section {index}: khổ, lề, đánh số",
                f"{width_cm:.1f}×{height_cm:.1f} cm; "
                f"lề T/D/Tr/P {margins['top']}/{margins['bottom']}/{margins['left']}/"
                f"{margins['right']} twip; {numbering.group(0) if numbering else 'không đánh số'}",
                ok_margin and abs(int(size.group(1)) - 11906) <= 2,
            )
        )
    for style_id, (sz, before, after, line) in EXPECTED_STYLES.items():
        props = style_props(styles, style_id)
        ok = (
            props.get("before") == str(before)
            and props.get("after") == str(after)
            and props.get("line") == str(line)
            and (sz is None or props.get("sz") == str(sz))
        )
        rows.append((f"Style {style_id}", ", ".join(f"{k}={v}" for k, v in props.items()), ok))
    normal = re.search(r'w:styleId="Normal".*?</w:style>', styles, re.S).group(0)
    rows.append(
        (
            "Font Normal",
            "Times New Roman 13"
            if 'w:ascii="Times New Roman"' in normal and '<w:sz w:val="26"/>' in normal
            else "khác",
            'w:ascii="Times New Roman"' in normal,
        )
    )
    instructions = field_instructions(document)
    rows.append(
        (
            "Field trong thân",
            ", ".join(f"{k}: {v}" for k, v in sorted(instructions.items())),
            instructions.get("TOC \\o", 0) == 1 and instructions.get("TOC \\h", 0) == 2,
        )
    )
    page_footers = [n for n, x in footers.items() if "PAGE" in x]
    rows.append(
        ("Footer có số trang", ", ".join(page_footers), page_footers == ["word/footer2.xml"])
    )
    text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", document))
    leftovers = [m for m in ("@@", "⟪", "⟫", "[@") if m in text]
    rows.append(("Marker nguồn còn sót", ", ".join(leftovers) or "không", not leftovers))
    rows.append(("Placeholder [CẦN ĐIỀN", str(text.count("[CẦN ĐIỀN")), True))
    rows.append(("Đánh dấu ⚠️ CẦN XÁC MINH", str(text.count("CẦN XÁC MINH")), True))
    tables = re.findall(r"<w:tbl>.*?</w:tbl>", document, re.S)
    rows.append(
        (
            "Bảng có hàng tiêu đề lặp",
            f"{sum('<w:tblHeader/>' in t for t in tables)}/{len(tables)}",
            True,
        )
    )
    drawings = document.count("<w:drawing>")
    rows.append(("Ảnh trong thân (gồm logo bìa)", str(drawings), True))
    return rows


def pdf_checks(pdf: Path) -> list[tuple[str, str, bool]]:
    if not pdf.is_file():
        return [("PDF xem trước", "không có", False)]
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=False).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, check=False
    ).stdout.decode("utf-8", errors="replace")
    broken = sum(text.count(s) for s in ("Error! Reference", "Lỗi! Không tìm thấy", "Error! No"))
    escaped = sum(text.count(s) for s in ("&lt;", "&gt;", "&amp;"))
    return [
        ("PDF: số trang", pages.group(1) if pages else "?", bool(pages)),
        ("PDF: lỗi tham chiếu field", str(broken), broken == 0),
        ("PDF: thực thể XML lọt ra chữ", str(escaped), escaped == 0),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", type=Path, default=DOCX)
    args = parser.parse_args()
    rows = check(args.docx) + pdf_checks(args.docx.with_suffix(".pdf"))
    print("| Kiểm tra | Kết quả | Đạt |\n|---|---|:---:|")
    for name, value, ok in rows:
        print(f"| {name} | {value.replace('|', '/')} | {'✅' if ok else '❌'} |")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
