"""Số chính của luận văn — một nguồn duy nhất cho SYSTEM §8.4, báo cáo cuối và slide (R5).

    .venv/Scripts/python.exe -m scripts.report_final_numbers --rq2-llm <rq2_llm_systems_*.json> \\
        --psds-diagnosis <psds_diagnosis_*.json> [--runs-root <ml/runs>]

Chỉ đọc JSON đã sinh (evaluation trong `ml/runs/`, measurement trong `docs/measurements/`); không
tính lại metric, không mở prediction. Mỗi ô ghi lại file nguồn và khóa để `check_doc_claims` trỏ
được. Thiếu một nguồn thì dừng, không để ô trống ngầm.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state
from scripts.check_doc_claims import select
from scripts.report_final_numbers_render import render_markdown

ROOT = Path(__file__).resolve().parents[1]
M = "docs/measurements"
B0_TEST = "ml/runs/sed_ensemble_B0_final_test_20261014T085016Z"
EVAL_LBR = f"{B0_TEST}/evaluation_phase_lbr_annotated.json"
EVAL_B0 = f"{B0_TEST}/evaluation_phase_o_annotated.json"
EVAL_F2 = "ml/runs/sed_ensemble_s13_f2_20260929T045053Z/evaluation_cv_annotated.json"
GRID_LBR = f"{M}/lbr_psds_grid_20261110_annotated.json"
GRID_B0 = f"{M}/lbr_psds_grid_20261110_annotated_b0.json"
V2RUN = {"lbr_run": "sed_lbr_B0_20261109T172809Z"}
V3RUN = {"lbr_run": "sed_lbr_B0v3_20261110T042337Z"}
LOG = "log 1e-5..0.99 (mới)"
RQ3 = {"f2": ("retrieval_benchmark_test_20261002", "retrieval_benchmark_test_parsed_20261002",
              "retrieval_answers_test_20261002"),
       "B0": ("retrieval_benchmark_test_s8lite_b0_gold_20261108",
              "retrieval_benchmark_test_s8lite_b0_parsed_20261108",
              "retrieval_answers_test_s8lite_b0_gold_20261108"),
       "lbrv2": ("retrieval_benchmark_test_lbrv2_gold_20261110",
                 "retrieval_benchmark_test_lbrv2_parsed_20261110",
                 "retrieval_answers_test_lbrv2_gold_20261110"),
       "lbrv3": ("retrieval_benchmark_test_lbrv3_gold_20261110",
                 "retrieval_benchmark_test_lbrv3_parsed_20261110",
                 "retrieval_answers_test_lbrv3_gold_20261110")}
TEMPLATE = {"B0": "caption_template_B0_test_annotated_20261107",
            "lbrv2": "caption_template_lbrv2_test_annotated_20261110",
            "lbrv3": "caption_template_lbrv3_test_annotated_20261110"}


class Sources:
    """Đọc JSON một lần; mỗi giá trị trả kèm (file, khóa) để truy được."""

    def __init__(self, root: Path, runs_root: Path) -> None:
        self.root, self.runs_root, self.cache = root, runs_root, {}

    def path(self, source: str) -> Path:
        parts = Path(source).parts
        return (self.runs_root.joinpath(*parts[2:]) if parts[:2] == ("ml", "runs")
                else self.root / source)

    def get(self, source: str, key: list[Any]) -> dict[str, Any]:
        if source not in self.cache:
            path = self.path(source)
            if not path.exists():
                raise SystemExit(f"thiếu nguồn {source}")
            self.cache[source] = json.loads(path.read_text(encoding="utf-8"))
        return {"value": select(self.cache[source], key), "source": source, "key": key}


def _sed_row(src: Sources, base: list[Any], *, ci: tuple[str, list[Any]] | None,
             delta: list[Any] | None) -> dict[str, Any]:
    row = {name: src.get(EVAL_LBR, base + key) for name, key in {
        "macro": ["macro_f1"], "micro": ["micro_f1"], "nsys": ["nsys"], "nref": ["nref"],
        "intersection_recall": ["intersection", "micro", "recall"],
        "intersection_precision": ["intersection", "micro", "precision"],
        "segment_f1_1s": ["segment_f1_1s", "micro"]}.items()}
    if ci is not None:
        row["micro_ci"] = {b: src.get(ci[0], ci[1] + [b]) for b in ("lower", "upper")}
    if delta is not None:
        row["delta_micro_vs_b0"] = {k: src.get(EVAL_LBR, delta + [k])
                                    for k in ("estimate", "lower", "upper")}
    return row


def sed(src: Sources) -> dict[str, Any]:
    f2 = {"macro": src.get(EVAL_F2, ["event_based_f1_macro", "f_measure"]),
          "micro": src.get(EVAL_F2, ["event_based_f1", "f_measure"]),
          "micro_ci": {b: src.get(EVAL_F2, ["event_based_f1_bootstrap", b])
                       for b in ("lower", "upper")},
          "nsys": src.get(EVAL_F2, ["n_events_estimate"]),
          "nref": src.get(EVAL_F2, ["n_events_reference"]),
          "psds_linear": {s: src.get(EVAL_F2, ["psds", s]) for s in ("psds_1", "psds_2")}}
    rows = {
        "f2": f2,
        "B0": _sed_row(src, ["lbr", "baseline", "all"], delta=None,
                       ci=(EVAL_B0, ["event_based_f1_bootstrap"])),
        "lbrv2_f1": _sed_row(src, ["lbr", "points", "f1", "all"],
                             ci=(EVAL_LBR, ["event_based_f1_bootstrap"]),
                             delta=["lbr", "delta_micro_vs_baseline"]),
        "lbrv3_f1": _sed_row(src, ["lbr_extra", V3RUN, "points", "f1", "all"], ci=None,
                             delta=["lbr_extra", V3RUN, "delta_micro_vs_baseline"]),
        "lbrv3_recall_first": _sed_row(src, ["lbr_extra", V3RUN, "points", "recall_first", "all"],
                                       ci=None, delta=None),
    }
    rows["B0"]["psds_linear"] = {s: src.get(EVAL_B0, ["psds", s]) for s in ("psds_1", "psds_2")}
    rows["B0"]["psds_log"] = {s: src.get(GRID_B0, ["results", {"system": "B0 (cSEBB)"}, "curves",
                                                   LOG, "psds", s]) for s in ("psds_1", "psds_2")}
    for label, run in (("lbrv2_f1", V2RUN), ("lbrv3_f1", V3RUN), ("lbrv3_recall_first", V3RUN)):
        rows[label]["psds_old_grid"] = {s: src.get(GRID_LBR, ["results", run, "curves",
                                                              "T_GRID (cũ)", "psds", s])
                                        for s in ("psds_1", "psds_2")}
        rows[label]["psds_log"] = {s: src.get(GRID_LBR, ["results", run, "curves", LOG, "psds", s])
                                   for s in ("psds_1", "psds_2")}
    b0_f2 = f"{M}/rq1_multirun_bootstrap_phase_o_b0_vs_f2_20261014.json"
    vn = ["lbr_extra", V3RUN, "points", "recall_first", "vn", "intersection", "micro"]
    return {"rows": rows,
            "b0_minus_f2": {k: src.get(b0_f2, ["differences", "B0-f2", k])
                            for k in ("estimate", "lower", "upper")},
            "lbrv3_recall_first_vn": {k: src.get(EVAL_LBR, vn + [k])
                                      for k in ("recall", "precision")},
            "n_recordings": src.get(EVAL_LBR, ["n_recordings"])}


def rq1(src: Sources) -> dict[str, Any]:
    out = {}
    for name, multiseed, boot in (
            ("v1", f"{M}/rq1_multiseed_clean_20260924.json",
             f"{M}/rq1_multirun_bootstrap_clean_20260925.json"),
            ("v2", f"{M}/rq1_v2_multiseed_20260929.json",
             f"{M}/rq1_multirun_bootstrap_rq1_v2_annotated_20260929.json")):
        out[name] = {
            "branches": {b: {k: src.get(multiseed, ["branches", b, "event_f1", k])
                             for k in ("mean", "sd", "n")} for b in ("B", "C")},
            "welch_p": {m: src.get(multiseed, ["welch", m, "p"])
                        for m in ("event_f1", "psds_1", "psds_2")},
            "bootstrap_c_minus_b": {k: src.get(boot, ["differences", "C-B", k])
                                    for k in ("estimate", "lower", "upper")}}
    return out


def rq2(src: Sources, llm: str) -> dict[str, Any]:
    template = {label: {lang: {m: src.get(f"{M}/{stem}.json",
                                          ["languages", lang, "summary", m])
                               for m in ("hallucination_rate", "omission_rate",
                                         "forbidden_term_rate", "over_specific_rate")}
                        for lang in ("en", "vi")} for label, stem in TEMPLATE.items()}
    data = json.loads(src.path(llm).read_text(encoding="utf-8"))
    metrics = ("hallucination_rate", "omission_rate", "context_term_rate", "over_specific_rate",
               "temporal_order_eligible")
    systems = list(data["systems"])
    e2e = {branch: {label: {m: src.get(llm, ["e2e", branch, label, "ci", m]) for m in metrics}
                    | {"n_truncated": src.get(llm, ["e2e", branch, label, "n_truncated"])}
                    for label in systems if label in data["e2e"][branch]}
           for branch in data["e2e"]}
    oracle = {branch: {m: src.get(llm, ["oracle", branch, "ci", m]) for m in metrics}
              for branch in data.get("oracle", {})}
    return {"template": template, "llm_e2e": e2e, "llm_oracle": oracle,
            "oracle_check": data.get("oracle_check"), "llm_source": llm}


def rq3(src: Sources) -> dict[str, Any]:
    out = {}
    for label, (gold, parsed, answers) in RQ3.items():
        g, p, a = (f"{M}/{gold}.json", f"{M}/{parsed}.json", f"{M}/{answers}.json")
        out[label] = {
            "ndcg10_gold": {cfg: {k: src.get(g, ["summary", cfg, "ci_ndcg@10", k])
                                  for k in ("estimate", "lower", "upper")}
                            for cfg in ("structured_only/en", "vector_only/en", "hybrid/en",
                                        "hybrid/vi")},
            "ndcg10_parsed_hybrid_en": src.get(p, ["summary", "hybrid/en", "ndcg@10"]),
            "answers_hybrid_en": {k: src.get(a, ["summary", "hybrid/en", k])
                                  for k in ("n", "unsupported_claim_rate", "contract_ok",
                                            "answered", "cited_relevant_share")}}
    return out


def demo(src: Sources) -> dict[str, Any]:
    parity = f"{M}/inference_parity_sed_lbr_b0v3_20261110t042337z_recall_first_cuda_20261110.json"
    e2e = f"{M}/demo_lbrv3_e2e_20261110.json"
    return {"parity": {k: src.get(parity, ["summary", k]) for k in (
                "n_events", "n_shared_events", "n_within_frame", "n_within_collar",
                "prob_max_abs")},
            "e2e": {k: src.get(e2e, [k]) for k in ("upload_elapsed_s", "rag_elapsed_s",
                                                   "events")}}


def psds_diagnosis(src: Sources, path: str) -> dict[str, Any]:
    h = src.get(path, ["hypotheses"])["value"]
    return {"source": path, "reproduced": h["reproduced"], "explained": h["explained"],
            "delta_psds_linear": h["delta_psds_linear"],
            "delta_event_f1_micro": h["delta_event_f1_micro"],
            "supported": {name: {s: item["supported"] for s, item in by.items()}
                          for name, by in h["hypotheses"].items()}}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rq2-llm", required=True, help="docs/measurements/rq2_llm_systems_*")
    parser.add_argument("--psds-diagnosis", required=True,
                        help="docs/measurements/psds_diagnosis_*")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "ml/runs")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    src = Sources(ROOT, args.runs_root)
    out = {"sed": sed(src), "rq1": rq1(src), "rq2": rq2(src, args.rq2_llm), "rq3": rq3(src),
           "psds_diagnosis": psds_diagnosis(src, args.psds_diagnosis), "demo": demo(src),
           "sources": sorted(src.cache), "git": git, "created_at": datetime.now(UTC).isoformat()}
    stem = f"final_numbers_{datetime.now(UTC):%Y%m%d}"
    (ROOT / M / f"{stem}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    (ROOT / M / f"{stem}.md").write_text(render_markdown(out), encoding="utf-8")
    print(render_markdown(out))


if __name__ == "__main__":
    main()
