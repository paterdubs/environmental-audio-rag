from __future__ import annotations

from scripts.report_sed_ceilings import MEASUREMENTS, output_path


def test_untagged_name_is_unchanged() -> None:
    assert output_path(None, "20260926") == MEASUREMENTS / "sed_ceilings_20260926.md"


def test_tag_keeps_another_system_from_overwriting_the_same_day() -> None:
    assert output_path("v2", "20260926") == MEASUREMENTS / "sed_ceilings_v2_20260926.md"
