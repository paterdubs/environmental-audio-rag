"""Dựng báo cáo khóa luận giữa kỳ (DOCX) từ `report/src/` theo mẫu khoa.

Chỉ đọc nguồn Markdown, bảng/hình đã sinh từ artifact và bibliography; không chạy suy luận hay
đánh giá nào.

    .venv/Scripts/python.exe -m scripts.build_midterm_report
    powershell -File scripts/update_docx_fields.ps1
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

from scripts.report_docx import bib as biblio
from scripts.report_docx.markdown import prepare
from scripts.report_docx.ooxml import transform_body
from scripts.report_docx.package import FrontInfo, assemble, marker_handlers

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report" / "src"
TEMPLATE = ROOT / "report" / "Mau bao cao KLTN_DS.docx"
BIBLIOGRAPHY = ROOT / "docs" / "thesis" / "bibliography.bib"
OUTPUT = ROOT / "report" / "Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx"
BUILD = ROOT / "report" / "build"


def find_pandoc() -> str:
    found = shutil.which("pandoc")
    if found:
        return found
    for candidate in (
        Path("C:/Program Files/Pandoc/pandoc.exe"),
        Path.home() / "AppData/Local/Pandoc/pandoc.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    raise SystemExit("Không tìm thấy Pandoc")


def body_inner(docx: Path) -> str:
    with zipfile.ZipFile(docx) as archive:
        xml = archive.read("word/document.xml").decode("utf-8")
    inner = xml[xml.index("<w:body>") + len("<w:body>") : xml.rindex("</w:body>")]
    return inner[: inner.rindex("<w:sectPr")] if "<w:sectPr" in inner else inner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = biblio.load(BIBLIOGRAPHY)
    numbers = biblio.numbering(entries)
    files = sorted(SOURCE.glob("[0-9][0-9]_*.md"))
    text, registry = prepare(files, ROOT, numbers)
    cited = {key for key in numbers if f"[{numbers[key]}" in text or f", {numbers[key]}" in text}
    unused = sorted(set(numbers) - cited)
    BUILD.mkdir(parents=True, exist_ok=True)
    merged = BUILD / "report_body.md"
    merged.write_text(text, encoding="utf-8", newline="\n")
    body_docx = BUILD / "report_body.docx"
    subprocess.run(
        [
            find_pandoc(),
            str(merged),
            "--from=markdown+tex_math_dollars-citations",
            "--to=docx",
            f"--resource-path={ROOT}",
            f"--output={body_docx}",
        ],
        check=True,
    )
    body = transform_body(body_inner(body_docx), registry, marker_handlers(entries))
    info = FrontInfo(**yaml.safe_load((SOURCE / "front_info.yaml").read_text(encoding="utf-8")))
    assemble(TEMPLATE, body_docx, body, info, args.output)
    print(
        f"Đã ghi {args.output.relative_to(ROOT)}: {len(files)} tệp nguồn, "
        f"{len(registry.numbers)} đối tượng đánh số, {len(entries)} tài liệu tham khảo."
    )
    if unused:
        print(
            f"Cảnh báo: tài liệu trong danh mục nhưng không được trích: {unused}", file=sys.stderr
        )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
