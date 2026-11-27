"""Kiểm thử tầng hiển thị bảng của bản báo cáo tinh gọn (scripts/report_docx/display.py)."""

from __future__ import annotations

from pathlib import Path

from scripts.report_docx import display as disp
from scripts.report_docx.markdown import expand_include

_TABLE = """| Hệ thống | Micro [CI 95%] | Δ |
|---|---:|---:|
| LBR V2, điểm f1 | 0.2965 [0.2293, 0.3603] | -0.0071 |
| B0 | 0.1806 [0.1261, 0.2384] | +0.1159 [+0.0741, +0.1593] |

**Nguồn:** `docs/measurements/final_numbers_20261110.json`, `ml/runs/x/manifest.json`.
"""


def test_vi_numbers_convert_decimal_minus_and_ci_separator():
    text = "| 0.2965 [0.2293, 0.3603] | -0.0071 | 1,000 |"
    assert disp.vi_number_text(text) == "| 0,2965 [0,2293; 0,3603] | −0,0071 | 1,000 |"


def test_vi_numbers_leave_versions_and_names_untouched():
    for text in ("Qwen3.5-9B", "python 3.12.1", "pg16", "f13.md", "S-0233", "2×256"):
        assert disp.vi_number_text(text) == text


def test_no_display_file_keeps_old_output(tmp_path: Path):
    path = tmp_path / "t.md"
    path.write_text(_TABLE, encoding="utf-8")
    assert disp.load(tmp_path / "missing.yaml") is disp.NONE
    old = expand_include(path)
    assert "| LBR V2, điểm f1 | 0.2965 [0.2293, 0.3603] | -0.0071 |" in old
    assert any("Bảng sinh tự động bởi script" in line for line in old)


def test_display_renames_converts_and_shortens_sources(tmp_path: Path):
    path = tmp_path / "t.md"
    path.write_text(_TABLE, encoding="utf-8")
    config = tmp_path / "display.yaml"
    config.write_text(
        "names:\n  - ['LBR V2, điểm f1', 'LBR chính']\n  - ['B0', 'Hệ cơ sở']\n"
        "vi_numbers: true\nshort_sources: true\n",
        encoding="utf-8",
    )
    lines = expand_include(path, "", disp.load(config))
    assert "| LBR chính | 0,2965 [0,2293; 0,3603] | −0,0071 |" in lines
    assert "| Hệ cơ sở | 0,1806 [0,1261; 0,2384] | +0,1159 [+0,0741; +0,1593] |" in lines
    note = next(line for line in lines if line.startswith("@@NOTE:"))
    assert "final_numbers_20261110.json" in note and "docs/measurements" not in note
    assert "manifest.json" in note and "ml/runs" not in note


def test_skip_lists_protect_selected_tables(tmp_path: Path):
    path = tmp_path / "f15_tech_stack.md"
    table = "| Tên | Phiên bản |\n|---|---|\n| fastapi | >=0.115,<0.116 |\n"
    path.write_text(table, encoding="utf-8")
    display = disp.Display(names=(("fastapi", "X"),), vi_numbers=True,
                           names_skip=frozenset({path.name}),
                           numbers_skip=frozenset({path.name}))
    assert "| fastapi | >=0.115,<0.116 |" in expand_include(path, "", display)
