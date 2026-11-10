"""Slide bảo vệ: đủ số slide, mọi slide chính có ghi chú, không lọt ký hiệu Markdown."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pptx")

from pptx import Presentation  # noqa: E402

from scripts import build_final_slides as slides  # noqa: E402

NEEDS = [
    slides.ROOT / "report" / "final_tables" / "f01_sed.md",
    slides.ROOT / "report" / "final_figures" / "f02_architecture.png",
    slides.ROOT / "docs" / "demo_screenshots" / "04-rag-evidence.png",
]


@pytest.mark.skipif(not all(p.exists() for p in NEEDS), reason="cần bảng/hình sinh sẵn")
def test_final_deck_counts_notes_and_clean_text(tmp_path: Path):
    deck = slides.build(tmp_path / "deck.pptx")

    assert (deck.count, deck.appendix) == (slides.MAIN_TOTAL, 3)
    pres = Presentation(str(tmp_path / "deck.pptx"))
    assert len(pres.slides) == slides.MAIN_TOTAL + 3
    for index, slide in enumerate(pres.slides, start=1):
        texts = [s.text_frame.text for s in slide.shapes if s.has_text_frame]
        for s in slide.shapes:
            if s.has_table:
                texts += [c.text for r in s.table.rows for c in r.cells]
        joined = " ".join(texts)
        assert "**" not in joined and "`" not in joined and "⟪" not in joined
        assert "Tương tác Người" not in joined
        assert slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip(), index
