"""Kiểu bảng và sơ đồ theo mức quan trọng của bản tinh gọn, và bộ kiểm chữ viết tắt.

Mặc định (không có `display.yaml`) phải giữ đúng kiểu cũ để bản chính dựng ra không đổi.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_report_acronyms as acr
from scripts.report_docx import diagram as dg
from scripts.report_docx import display as disp
from scripts.report_docx.ooxml import transform_table
from scripts.report_docx.package import NEW_STYLES, new_styles

_TABLE = (
    "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>H</w:t></w:r></w:p></w:tc></w:tr>"
    "<w:tr><w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
)


def test_default_table_style_matches_previous_builds():
    style = disp.TableStyle()
    assert (style.text_pt, style.small_pt, style.note_pt, style.header_fill) == (
        11.0, 10.0, 11.0, "E7E6E6")
    assert NEW_STYLES == new_styles()
    assert '<w:sz w:val="22"/>' in NEW_STYLES and '<w:sz w:val="20"/>' in NEW_STYLES
    assert 'w:fill="E7E6E6"' in transform_table(_TABLE)


def test_display_yaml_sets_13pt_and_white_header(tmp_path: Path):
    path = tmp_path / "display.yaml"
    path.write_text("table:\n  text_pt: 13\n  small_pt: 13\n  note_pt: 13\n"
                    "  header_fill: \"\"\ndiagram_levels: true\n", encoding="utf-8")
    shown = disp.load(path)
    assert shown.table.header_fill == "" and shown.diagram_levels
    styles = new_styles(shown.table)
    assert '<w:sz w:val="26"/>' in styles and '<w:sz w:val="22"/>' not in styles
    out = transform_table(_TABLE, header_fill=shown.table.header_fill)
    assert "<w:shd" not in out  # ô tiêu đề trắng, không tô nền
    assert "<w:b/>" in out  # tiêu đề vẫn in đậm


def test_display_yaml_rejects_unknown_table_key(tmp_path: Path):
    path = tmp_path / "display.yaml"
    path.write_text("table:\n  font: 13\n", encoding="utf-8")
    with pytest.raises(KeyError, match="font"):
        disp.load(path)


def _levels_diagram() -> dg.Diagram:
    return dg.Diagram("t", 10.0, 2.0, (
        dg.Box(0, 0, 2, 1, ("Bối cảnh", "dòng phụ"), level=1),
        dg.Box(2.5, 0, 2, 1, ("Bước", "dòng phụ"), fill="model", level=2),
        dg.Box(5, 0, 2, 1, ("Quan trọng", "dòng phụ"), fill="store", level=3),
        dg.Box(7.5, 0, 2, 1, ("Đóng góp", "dòng phụ"), fill="offline", level=4),
        dg.Line(((2, 0.5), (2.5, 0.5))),
    ), "mô tả")


def test_levels_off_keeps_old_palette():
    xml = dg.render(_levels_diagram())
    for color in ("F5F6F8", "FBEFE8", "EAF1FB", "ECF8F1"):
        assert f'val="{color}"' in xml
    assert dg.WHITE not in xml


def test_levels_on_darkens_by_level_and_uses_white_text_on_top_level():
    xml = dg.render(_levels_diagram(), levels=True)
    for fill in ("F0F0F0", "FDAE6B", "4292C6", "006D2C"):
        assert f'<a:srgbClr val="{fill}"/>' in xml
    assert f'<w:color w:val="{dg.WHITE}"/>' in xml
    assert '<a:ln w="19050">' in xml  # viền 1,5 pt ở mức 4
    assert '<a:ln w="15875">' in xml  # mũi tên chính 1,25 pt
    # Mức 2 trở lên không dùng chữ xám (không đủ tương phản trên nền đậm).
    level2 = xml.split("Bước")[1].split("Quan trọng")[0]
    assert dg.MUTED not in level2.split("</wps:txbx>")[0]


def test_legend_adds_four_level_boxes_below_diagram():
    pytest.importorskip("yaml")
    from scripts import report_diagrams

    try:
        plain = report_diagrams.build("lbr")
        with_legend = report_diagrams.build("lbr", legend=True)
    except FileNotFoundError as exc:
        pytest.skip(f"thiếu artifact: {exc}")
    texts = {box.lines[0] for box in dg.boxes_in(with_legend)}
    assert set(report_diagrams.LEGEND_LEVELS) <= texts
    assert with_legend.height > plain.height


def _write_source(tmp_path: Path, body: str, abbreviations: str) -> Path:
    (tmp_path / "00_phan_dau.md").write_text(
        "@@TITLE:ABSTRACT@@\n\nText.\n\n@@PAGEBREAK@@\n\n@@TITLE:TÓM TẮT@@\n\nChữ.\n\n"
        "@@PAGEBREAK@@\n\n@@HEADING1N:DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT@@\n\n"
        "| Từ viết tắt | Từ đầy đủ | Nghĩa |\n|---|---|---|\n" + abbreviations
        + "\n@@PAGEBREAK@@\n", encoding="utf-8")
    (tmp_path / "01_gioi_thieu.md").write_text(body, encoding="utf-8")
    return tmp_path


def test_acronym_checker_accepts_expansion_at_first_use(tmp_path: Path):
    source = _write_source(
        tmp_path, "Phát hiện sự kiện âm thanh (Sound Event Detection – SED) rồi SED.\n",
        "| SED | Sound Event Detection | Phát hiện sự kiện âm thanh |\n")
    assert acr.check(source) == []


def test_acronym_checker_reports_late_definition_unused_and_missing(tmp_path: Path):
    source = _write_source(
        tmp_path, "Dùng SED trước. Sau đó PSDS và PSDS-2 mới xuất hiện.\n",
        "| SED | Sound Event Detection | Phát hiện |\n| LLM | Large Language Model | Mô hình |\n")
    problems = acr.check(source)
    assert any("lần đầu chưa viết đầy đủ: SED" in p for p in problems)
    assert any("không dùng: LLM" in p for p in problems)
    assert any("thiếu trong danh mục: PSDS" in p for p in problems)
