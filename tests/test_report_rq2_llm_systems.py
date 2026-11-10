"""Bảng RQ2 LLM theo hệ thống (ADR-0048 §1): chấm lại, CI, hiệu số cặp, oracle dùng lại."""

import json
from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.taxonomy import load_taxonomy
from scripts import report_rq2_llm_systems as report

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
LEXICON = CaptionLexicon.from_taxonomy(TAXONOMY)
RIDS = ("S-0001", "S-0002", "S-0003")


def _timeline(rid: str, classes: list[str]) -> dict:
    events = [{"class_id": c, "onset_s": 1.0 + i, "offset_s": 2.0 + i, "score": 0.9}
              for i, c in enumerate(classes)]
    return canonicalize_timeline(f"datased:{rid}", 30.0, events, TAXONOMY, model_version="m")


def _write(run: Path, branch: str, split: str, rows: list[dict], truncated: int = 0) -> None:
    (run / "captions").mkdir(parents=True, exist_ok=True)
    path = run / "captions" / f"{branch}_{split}.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    path.with_suffix(".meta.json").write_text(json.dumps({"n_truncated": truncated}),
                                              encoding="utf-8")


def _rows(level: str, *, drop_mention: bool = False) -> list[dict]:
    template = TemplateCaptioner(LEXICON)
    rows = []
    for rid in RIDS:
        timeline = _timeline(rid, ["birds", "music"])
        caption = template.caption(_timeline(rid, ["birds"]) if drop_mention else timeline)
        rows.append({"recording_id": rid, "level": level, "timeline": timeline,
                     "caption": caption})
    return rows


@pytest.fixture()
def runs(tmp_path: Path) -> dict[str, Path]:
    f2, b0 = tmp_path / "f2", tmp_path / "b0"
    _write(f2, "constrained", "test", _rows("e2e") + _rows("oracle"))
    _write(b0, "constrained", "test", _rows("e2e", drop_mention=True), truncated=2)
    return {"f2": f2, "B0": b0}


def test_system_scores_contain_template_and_llm_branches_on_the_same_timelines(runs):
    scored = report.load_scored(runs["B0"], "test", LEXICON, "annotated")
    assert set(scored) == {("constrained", "e2e"), ("template", "e2e")}
    assert set(scored[("constrained", "e2e")]) == set(RIDS)


def test_result_reports_ci_paired_differences_truncation_and_oracle_from_reference(runs):
    result = report.build_result(runs, split="test", eval_set="annotated", lexicon=LEXICON,
                                 references=("f2", "B0"), oracle_label="f2")
    row = result["e2e"]["constrained"]
    assert row["f2"]["summary"]["omission_rate"] == pytest.approx(0.0)
    assert row["B0"]["summary"]["omission_rate"] == pytest.approx(0.5)  # sót music
    assert row["B0"]["n_truncated"] == 2 and row["f2"]["n_truncated"] == 0
    diff = result["paired"]["constrained"]["B0−f2"]["omission_rate"]
    assert diff["estimate"] == pytest.approx(0.5)
    assert "B0−B0" not in result["paired"]["constrained"]
    assert set(result["oracle"]["constrained"]) == {"summary", "ci", "n_truncated"}


def test_oracle_check_compares_stored_oracle_timelines_with_ground_truth(tmp_path, monkeypatch):
    rows = _rows("oracle")
    run = tmp_path / "f2"
    _write(run, "constrained", "test", rows)
    rebuilt = {r["recording_id"]: r["timeline"] for r in rows}
    monkeypatch.setattr(report, "rebuild_oracle", lambda rids: {r: rebuilt[r] for r in rids})
    assert report.oracle_check(run, "test", "annotated") == {
        "n": 3, "identical": 3, "mismatched": [], "ok": True}
    rebuilt["S-0002"] = _timeline("S-0002", ["voices"])
    check = report.oracle_check(run, "test", "annotated")
    assert check["ok"] is False and check["mismatched"] == ["S-0002"]


def test_default_systems_follow_adr_0048():
    assert list(report.DEFAULT_SYSTEMS["test"]) == ["f2", "B0", "lbrv2", "lbrv3"]
    assert report.DEFAULT_SYSTEMS["dev"]["lbrv3"].startswith("sed_lbr_oofevents_sed_lbr_B0v3")
    assert report.parse_systems(["x=ml/runs/a"]) == {"x": Path("ml/runs/a")}
    with pytest.raises(SystemExit):
        report.parse_systems(["x"])
