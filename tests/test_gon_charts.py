"""Biểu đồ và hình công nghệ của bản tinh gọn: số đúng artifact, kiểu số Việt, logo khớp bảng."""

from __future__ import annotations

import pytest

pytest.importorskip("matplotlib")

from scripts import build_gon_charts as charts  # noqa: E402
from scripts import build_tech_overview as tech  # noqa: E402
from scripts import gon_chart_style as cs  # noqa: E402
from scripts import gon_charts_redraw as redraw  # noqa: E402
from scripts import vendor_tech_icons as vendor  # noqa: E402


def _data(*keys: str) -> dict:
    missing = [charts.SOURCES[k] for k in keys if not charts.SOURCES[k].exists()]
    if missing:
        pytest.skip(f"thiếu artifact: {missing}")
    return {k: charts.load(charts.SOURCES[k]) for k in keys}


def test_vietnamese_number_format_uses_comma_and_true_minus():
    assert cs.vn(0.1158507955829928, 4) == "0,1159"
    assert cs.vn(-0.0029, 4) == "−0,0029"
    assert cs.vn(0.0164, 4, sign=True) == "+0,0164"
    assert cs.vn(-0.00001, 4) == "0,0000"  # không in "−0,0000"


def test_main_differences_flip_v1_minus_v2_into_v2_minus_v1():
    data = _data("final", "v2_vs_v1", "lbr_context")
    rows = charts.main_differences(data["final"], data["v2_vs_v1"], data["lbr_context"])
    v2v1 = next(r for r in rows if r["label"] == "SED v2 − SED v1")
    assert (round(v2v1["estimate"], 4), round(v2v1["lower"], 4), round(v2v1["upper"], 4)) == (
        0.0536, 0.0261, 0.0853)
    assert [r["n"] for r in rows] == [142, 139, 142, 139, 564, 139]
    assert all(r["lower"] <= r["estimate"] <= r["upper"] for r in rows)


def test_oof_candidates_end_with_lbr_and_only_lbr_clears_zero():
    data = _data("oof_o1", "oof_o2", "oof_p1", "oof_p4", "lbr_selection", "lbr_application")
    rows = charts.oof_deltas(data)
    assert [r["group"] for r in rows][-3:] == ["lbr"] * 3
    assert all(r["lower"] > 0 for r in rows if r["group"] == "lbr")
    assert not any(r["lower"] > 0 for r in rows if r["group"] == "other")


def test_failure_and_error_splits_add_up_and_reject_mismatch():
    data = _data("failures", "ceiling_v1")
    rows = charts.failure_split(data["failures"])
    assert {r["total"] for r in rows} == {705}
    assert next(r for r in rows if r["system"] == "B0")["sed_miss"] == 349
    assert charts.error_split(data["ceiling_v1"]) == (112, 417, 357)
    broken = {"system": {"n_reference": 10, "n_collar_match": 1,
                         "n_overlap_but_boundary_miss": 1, "n_deleted": 1}}
    with pytest.raises(ValueError, match="không cộng đủ"):
        charts.error_split(broken)


def test_checker_rates_report_out_of_taxonomy_gap():
    kinds, sources = charts.checker_rates(_data("checker")["checker"])
    oov = next(k for k in kinds if "ngoài hệ lớp" in k[0])
    assert oov[1:3] == (1336, 2144)
    assert sources[0][3] == 0.0 and sources[-1][3] == 1.0  # xếp tăng dần


def test_query_diffs_pair_hybrid_with_vector_per_query():
    rows = [{"query_id": "q1", "language": "en", "n_relevant": 2, "mode": m, "ndcg@10": v}
            for m, v in (("hybrid", 0.2), ("vector_only", 0.5))]
    rows += [{"query_id": "q2", "language": "en", "n_relevant": 0, "mode": "hybrid",
              "ndcg@10": 0.0}]
    assert redraw.query_diffs(rows) == pytest.approx([-0.3])


def test_build_writes_every_chart_and_manifest(tmp_path):
    if not all(p.exists() for p in charts.SOURCES.values()):
        pytest.skip("thiếu artifact")
    manifest = charts.build(tmp_path)
    assert len(manifest["figures"]) == 14
    assert all((tmp_path / name).stat().st_size > 10_000 for name in manifest["figures"])
    assert all(len(s["sha256"]) == 64 for s in manifest["sources"].values())


def test_normalise_path_splits_compact_arc_flags():
    assert tech.normalise_path("M1 2a.5.5 0 00.5-.5h1") == "M 1 2 a .5 .5 0 0 0 .5 -.5 h 1"
    with pytest.raises(ValueError, match="cờ cung"):
        tech.normalise_path("M0 0a1 1 0 2 1 1 1")


def test_tech_figure_follows_the_tech_table_and_every_logo_is_used():
    layers = tech.read_layers()
    names = {n for layer in layers for n in layer.techs}
    assert layers[0].name == "Hạ tầng" and layers[-1].name == "Giao diện"
    assert set(tech.LOGOS) <= names  # tên logo nào cũng phải có trong bảng
    assert {"Python", "PostgreSQL 16 + pgvector", "Playwright"} <= names - set(tech.LOGOS)


def test_light_brand_colours_go_on_a_dark_tile():
    assert tech.needs_dark_tile("61DAFB") and tech.needs_dark_tile("FFD21E")
    assert not tech.needs_dark_tile("EE4C2C") and not tech.needs_dark_tile("2496ED")


def test_vendored_svg_must_be_a_single_path():
    good = ('<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
            '<title>X</title><path d="M0 0h24v24H0z"/></svg>')
    assert vendor.path_data(good) == "M0 0h24v24H0z"
    with pytest.raises(ValueError):
        vendor.path_data(good.replace("<path", "<script>alert(1)</script><path"))
    icons = tech.load_icons()
    assert set(tech.LOGOS.values()) <= set(icons)
