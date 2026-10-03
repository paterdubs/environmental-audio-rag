"""Kiểm thử bộ dựng báo cáo DOCX (scripts/report_docx): danh mục, trích dẫn, đánh số, bảng."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.report_docx import bib
from scripts.report_docx.markdown import (
    Registry,
    check_references,
    number_document,
    replace_citations,
)
from scripts.report_docx.ooxml import (
    TEXT_WIDTH,
    _column_widths,
    replace_inline_refs,
    top_level_elements,
    transform_table,
)

BIB = """
@article{zeta2020,
  author   = {Zeta, Anna and Beta, Bob},
  title    = {Late Paper},
  journal  = {Journal},
  year     = {2020},
  volume   = {3},
  number   = {2},
  pages    = {10--20},
  language = {en}
}

@misc{alpha2021,
  author   = {Alpha, Carl},
  title    = {Preprint},
  year     = {2021},
  eprint   = {2101.00001},
  version  = {2},
  language = {en}
}

@article{viet2019,
  author   = {Nguyễn, Văn An},
  title    = {Bài tiếng Việt},
  journal  = {Tạp chí},
  year     = {2019},
  language = {vi}
}
"""


def test_bibliography_groups_vietnamese_first_then_sorts_by_family_name():
    entries = bib.parse_bib(BIB)
    groups = bib.ordered(entries)
    assert [language for language, _ in groups] == ["vi", "en"]
    assert [entry.key for entry in groups[1][1]] == ["alpha2021", "zeta2020"]
    assert bib.numbering(entries) == {"viet2019": 1, "alpha2021": 2, "zeta2020": 3}


def test_format_entry_follows_template_order_for_articles_and_preprints():
    entries = {entry.key: entry for entry in bib.parse_bib(BIB)}
    article = "".join(text for text, _ in bib.format_entry(entries["zeta2020"]))
    assert article == "Anna Zeta, Bob Beta (2020), “Late Paper”, Journal, Vol. 3 (2), pp. 10–20."
    preprint = "".join(text for text, _ in bib.format_entry(entries["alpha2021"]))
    assert "arXiv:2101.00001v2" in preprint


def test_duplicate_bib_keys_are_rejected():
    with pytest.raises(ValueError, match="trùng"):
        bib.parse_bib(BIB + BIB)


def test_citations_become_sorted_numbers_and_unknown_keys_fail():
    numbers = {"a": 3, "b": 1}
    assert replace_citations("x [@a; @b] y [@b]", numbers) == "x [1, 3] y [1]"
    with pytest.raises(KeyError):
        replace_citations("[@missing]", numbers)


def test_captions_and_equations_are_numbered_per_chapter_and_appendix_is_static(tmp_path: Path):
    lines = [
        "# One",
        "@@CAP:tbl:a|A@@",
        "⟪eqno:e1⟫",
        "# Two",
        "@@CAP:tbl:b|B@@",
        "@@CAP:fig:c|C@@",
        "⟪eqno:e2⟫",
        "@@APPENDIX@@",
        "@@CAP:tbl:d|D@@",
    ]
    _, registry = number_document(lines, tmp_path)
    assert registry.numbers[("tbl", "a")] == "1.1"
    assert registry.numbers[("tbl", "b")] == "2.1"
    assert registry.numbers[("fig", "c")] == "2.1"
    assert registry.numbers[("eq", "e2")] == "2.1"
    assert registry.numbers[("tbl", "d")] == "PL.1"
    assert registry.text("eq", "e1") == "(1.1)"


def test_reference_to_undeclared_key_fails():
    with pytest.raises(KeyError, match="tbl:nope"):
        check_references(["xem ⟪tbl:nope⟫"], Registry())


def test_inline_reference_becomes_ref_field_without_double_escaping():
    registry = Registry()
    registry.add("tbl", "rq", "1.2", "RQ")
    xml = '<w:r><w:t xml:space="preserve">p &lt; 0,05 (⟪tbl:rq⟫)</w:t></w:r>'
    out = replace_inline_refs(xml, registry)
    assert "REF _RefTbl_rq \\h" in out
    assert "Bảng 1.2" in out
    assert "&amp;lt;" not in out and "&lt;" in out


def test_column_widths_fill_text_width_and_respect_longest_word():
    rows = [["Mã", "Mục tiêu"], ["O1", "một câu khá dài mô tả mục tiêu của đề tài"]]
    widths = _column_widths(rows)
    assert sum(widths) == TEXT_WIDTH
    assert widths[0] >= 2 * 105 + 330


def test_table_header_repeats_and_short_tables_stay_together():
    table = (
        "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>H</w:t></w:r></w:p></w:tc></w:tr>"
        "<w:tr><w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
    )
    out = transform_table(table)
    assert out.count("<w:tblHeader/>") == 1
    assert out.count("<w:cantSplit/>") == 2
    assert out.count("<w:keepNext/>") == 2


def test_top_level_split_keeps_nested_paragraphs_inside_tables():
    body = (
        "<w:p><w:r><w:t>a</w:t></w:r></w:p>"
        "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>b</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
    )
    elements = top_level_elements(body)
    assert len(elements) == 2 and elements[1].startswith("<w:tbl>")
