"""Kiểm thử sơ đồ khối dạng shape Word của bản tinh gọn (report_docx/diagram, report_diagrams)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from scripts.report_docx import diagram as dg

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"'
)


def _parse(xml: str) -> ET.Element:
    return ET.fromstring(f"<root {NS}>{xml}</root>")


def _small() -> dg.Diagram:
    return dg.Diagram(
        "t", 10.0, 3.0,
        (dg.Box(0, 0, 4, 2, ("Tiêu đề", "dòng có dấu: ắ ơ ư đ <&>")),
         dg.Box(6, 0, 4, 2, ("Hộp hai",)),
         dg.Line(((4, 1), (6, 1))),
         dg.Line(((9, 2), (9, 2.8), (1, 2.8)), dashed=True)),
        "mô tả thay thế",
    )


def test_render_is_wellformed_inline_canvas_with_escaped_text():
    xml = dg.render(_small())
    root = _parse(xml)
    assert root.find(".//{*}inline") is not None
    assert 'uri="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"' in xml
    assert '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">' in xml
    assert "ắ ơ ư đ &lt;&amp;&gt;" in xml
    assert '<w:pStyle w:val="FigurePara"/>' in xml
    assert all(ord(ch) >= 32 for ch in xml)


def test_ids_are_unique_across_renders_and_boxes_reset_indent():
    xml = dg.render(_small()) + dg.render(_small())
    ids = re.findall(r'(?:cNvPr|docPr) id="(\d+)"', xml)
    assert len(ids) == len(set(ids)) and min(map(int, ids)) >= 900_001
    assert xml.count('<w:ind w:left="0" w:right="0" w:firstLine="0"/>') == 6


def test_flipped_segments_and_arrowhead_only_on_last_segment():
    xml = dg.render(_small())
    assert 'flipH="1"' in xml  # đoạn đi từ phải sang trái
    assert xml.count('<a:tailEnd type="triangle"') == 2
    assert xml.count('<a:prstDash val="dash"/>') == 2


def test_diagram_rejects_overflow():
    with pytest.raises(ValueError, match="rộng"):
        dg.Diagram("x", 16.0, 1.0, (), "")
    with pytest.raises(ValueError, match="tràn"):
        dg.Diagram("x", 5.0, 1.0, (dg.Box(4, 0, 2, 1, ("a",)),), "")


@pytest.mark.parametrize(
    "name", ["pipeline", "dataflow", "lbr", "architecture", "uploadflow", "queryflow", "erd"]
)
def test_every_report_diagram_builds_and_renders(name):
    pytest.importorskip("yaml")
    from scripts import report_diagrams

    try:
        diagram = report_diagrams.build(name)
    except FileNotFoundError as exc:  # artifact nằm ngoài git (ml/runs, data/)
        pytest.skip(f"thiếu artifact: {exc}")
    _parse(dg.render(diagram))
    assert diagram.width <= dg.MAX_WIDTH_CM


def test_dataflow_reads_upload_limits_from_code():
    from scripts import report_diagrams
    from services.common.audio import ALLOWED_SUFFIXES, MAX_DURATION_S

    try:
        diagram = report_diagrams.build("dataflow")
    except FileNotFoundError as exc:
        pytest.skip(f"thiếu artifact: {exc}")
    text = " ".join(line for box in dg.boxes_in(diagram) for line in box.lines)
    for suffix in ALLOWED_SUFFIXES:
        assert suffix[1:].upper() in text
    assert f"{MAX_DURATION_S:g} s" in text


def test_erd_draws_every_table_of_the_migration():
    from scripts import report_diagrams
    from scripts.build_system_figures import MIGRATION, parse_schema

    tables = {t.name for t in parse_schema(MIGRATION.read_text(encoding="utf-8"))}
    titles = {box.lines[0] for box in dg.boxes_in(report_diagrams.build("erd"))}
    assert tables <= titles
