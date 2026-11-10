"""Số chính (R5): mỗi ô truy được về file + khóa; thiếu nguồn thì dừng; khớp artifact thật."""

import json
from pathlib import Path

import pytest

from scripts import report_final_numbers as final
from scripts.report_final_numbers_render import render_markdown

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "ml" / "runs"


def test_sources_resolve_ml_runs_against_runs_root_and_keep_the_key(tmp_path):
    (tmp_path / "runs" / "r").mkdir(parents=True)
    (tmp_path / "runs" / "r" / "e.json").write_text(json.dumps({"a": [{"k": "x", "v": 3}]}),
                                                    encoding="utf-8")
    src = final.Sources(tmp_path / "repo", tmp_path / "runs")
    cell = src.get("ml/runs/r/e.json", ["a", {"k": "x"}, "v"])
    assert cell == {"value": 3, "source": "ml/runs/r/e.json", "key": ["a", {"k": "x"}, "v"]}
    with pytest.raises(SystemExit, match="thiếu nguồn"):
        src.get("docs/measurements/none.json", ["a"])


def _write(root: Path, rel: str, data: dict) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return rel


def test_rq2_and_psds_sections_read_their_reports(tmp_path, monkeypatch):
    ci = {"estimate": 0.1, "lower": 0.0, "upper": 0.2}
    cell = {"ci": {m: ci for m in ("hallucination_rate", "omission_rate", "context_term_rate",
                                   "over_specific_rate", "temporal_order_eligible")},
            "n_truncated": 1}
    llm = _write(tmp_path, "docs/measurements/rq2.json", {
        "systems": {"f2": "a", "B0": "b"}, "e2e": {"constrained": {"f2": cell, "B0": cell}},
        "oracle": {"constrained": cell}, "oracle_check": {"n": 3, "identical": 3, "ok": True}})
    psds = _write(tmp_path, "docs/measurements/psds.json", {"hypotheses": {
        "reproduced": True, "explained": True, "delta_psds_linear": {"psds_1": -0.01},
        "delta_event_f1_micro": 0.05, "hypotheses": {"H1": {"psds_1": {"supported": True}}}}})
    template = {lang: {"summary": {m: 0.0 for m in ("hallucination_rate", "omission_rate",
                                                    "forbidden_term_rate",
                                                    "over_specific_rate")}}
                for lang in ("en", "vi")}
    for stem in final.TEMPLATE.values():
        _write(tmp_path, f"docs/measurements/{stem}.json", {"languages": template})
    src = final.Sources(tmp_path, tmp_path / "runs")
    rq2 = final.rq2(src, llm)
    assert rq2["llm_e2e"]["constrained"]["B0"]["n_truncated"]["value"] == 1
    assert rq2["llm_oracle"]["constrained"]["omission_rate"]["value"] == ci
    assert final.psds_diagnosis(src, psds)["supported"] == {"H1": {"psds_1": True}}


@pytest.mark.skipif(not (RUNS / "sed_ensemble_B0_final_test_20261014T085016Z").exists(),
                    reason="cần ml/runs đã đóng băng (chạy trong repo chính)")
def test_real_sources_reproduce_the_locked_headline_numbers():
    src = final.Sources(ROOT, RUNS)
    sed = final.sed(src)
    rows = sed["rows"]
    assert round(rows["B0"]["micro"]["value"], 4) == 0.1806
    assert round(rows["lbrv2_f1"]["micro"]["value"], 4) == 0.2965
    assert round(rows["lbrv2_f1"]["delta_micro_vs_b0"]["lower"]["value"], 4) == 0.0741
    assert round(rows["B0"]["psds_linear"]["psds_1"]["value"], 4) == 0.3131
    assert round(rows["B0"]["psds_log"]["psds_2"]["value"], 4) == 0.7452
    assert round(rows["lbrv3_recall_first"]["intersection_recall"]["value"], 4) == 0.8203
    assert round(sed["b0_minus_f2"]["estimate"]["value"], 4) == 0.0164
    assert round(final.rq3(src)["lbrv3"]["ndcg10_gold"]["hybrid/en"]["estimate"]["value"],
                 3) == 0.670
    assert round(final.rq1(src)["v1"]["bootstrap_c_minus_b"]["estimate"]["value"], 4) == -0.0071
    out = {"sed": sed, "rq1": final.rq1(src), "rq3": final.rq3(src), "demo": final.demo(src),
           "rq2": {"template": {}, "llm_e2e": {}, "llm_oracle": {}, "oracle_check": None},
           "psds_diagnosis": {"reproduced": False, "explained": False, "supported": {},
                              "source": "x"}, "git": {"revision": "r", "dirty": False}}
    text = render_markdown(out)
    assert "LBR V2, điểm f1 (số chính)" in text and "0.2965" in text
