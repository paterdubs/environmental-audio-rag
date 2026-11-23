import json

import pytest

from scripts import build_research_figures as brf


def _cell(v):
    return {"value": v, "source": "x", "key": ["k"]}


def test_journey_rows_pair_test_scores_with_the_selection_score_of_each_generation():
    s13_test = {"results": [{"label": lab, "micro": m, "micro_ci_lower": m - 0.03,
                             "micro_ci_upper": m + 0.03, "macro": m - 0.01}
                            for lab, m in (("a", 0.09), ("c", 0.15), ("f2", 0.16))]}
    s13_rank = {"ranking": [{"label": lab, "annotated": {"score": {"mean": s}}}
                            for lab, s in (("a", 0.16), ("c", 0.22), ("f2", 0.24))]}
    sed = {k: {"micro": _cell(m), "macro": _cell(m - 0.05),
               "micro_ci": {"lower": _cell(m - 0.05), "upper": _cell(m + 0.05)}}
           for k, m in (("B0", 0.18), ("lbrv2_f1", 0.30))}
    lbr = {"rows": {"B0": {"micro": 0.234}, "LBR_v2": {"micro": 0.333}}}
    rows = brf.journey_rows(s13_test, s13_rank, {"sed": {"rows": sed}}, lbr)
    assert [r["name"] for r in rows] == ["v1", "v2", "f2", "B0", "B0 + LBR V2"]
    assert [r["select_kind"] for r in rows] == ["dev CV"] * 3 + ["OOF"] * 2
    assert rows[-1]["micro"] == 0.30 and rows[-1]["select"] == 0.333
    assert rows[0]["lower"] == pytest.approx(0.06)


def test_fn_breakdown_labels_every_kind_and_sorts_ascending():
    kinds = {k: i for i, k in enumerate(brf.FN_KINDS)}
    rows = brf.fn_breakdown({"breakdown": {"fn_kinds": kinds}})
    assert len(rows) == len(brf.FN_KINDS)
    assert [v for _, v in rows] == sorted(kinds.values())


def test_per_class_pairs_drop_small_classes_and_sort_by_lbr_score():
    b0 = {"event_based_f1_per_class": {"a": {"f_measure": 0.1}, "b": {"f_measure": 0.2},
                                       "c": {"f_measure": 0.3}}}
    v2 = {"event_based_f1_per_class": {"a": {"f_measure": 0.5}, "b": {"f_measure": 0.4},
                                       "c": {"f_measure": 0.9}}}
    rows = brf.per_class_pairs(b0, v2, {"a": 12, "b": 30, "c": 4}, 10)
    assert rows == [("b", 30, 0.2, 0.4), ("a", 12, 0.1, 0.5)]


def test_fold_histories_reads_only_member_runs(tmp_path, monkeypatch):
    for name in ("sed_polyphonic_1", "sed_polyphonic_2"):
        logs = tmp_path / "ml" / "runs" / name / "logs"
        logs.mkdir(parents=True)
        (logs / "history.json").write_text(json.dumps({"epochs": [{"epoch": 1}]}),
                                           encoding="utf-8")
    monkeypatch.setattr(brf, "ROOT", tmp_path)
    manifest = {"command": ["python", "--members", "ml/runs/sed_polyphonic_1",
                            "ml/runs/sed_polyphonic_2", "--postproc", "ml/runs/sed_oof_x/s.json"]}
    assert brf.fold_histories(manifest) == [[{"epoch": 1}], [{"epoch": 1}]]
