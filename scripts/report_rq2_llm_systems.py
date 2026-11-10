"""Bảng RQ2 caption LLM theo hệ thống SED (ADR-0048 §1): f2 (S8), B0, LBR V2, LBR V3.

    .venv/Scripts/python.exe -m scripts.report_rq2_llm_systems --split test --eval-set annotated \\
        --frozen-lexicon-sha256 <sha> [--runs-root <ml/runs>] [--system nhãn=<run>]...

Chấm lại từ file caption bằng đúng `score_captions.score_sources` (template chấm trên cùng
timeline), rồi báo theo nhánh × hệ thống ở mức e2e: số chính + CI bootstrap theo recording, hiệu
số cặp so với f2 và so với B0, số caption bị cắt (meta). Mức oracle không phụ thuộc hệ thống SED:
lấy từ caption S8 của f2, kèm kiểm timeline oracle đã lưu trùng ground truth dựng lại. Chỉ mô tả —
không chọn hay đổi gì từ các số này.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ml.captioning.lexicon import CaptionLexicon
from ml.evaluation.caption_stats import CI_METRICS, metric_ci, paired_difference, summarise
from ml.evaluation.coverage import EVAL_SETS, eval_suffix, unannotated_recordings
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate, oracle_timelines
from scripts.report_rq2_llm_systems_render import render_markdown
from scripts.score_captions import LLM_BRANCHES, score_sources

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = ("template", *LLM_BRANCHES)
_F2 = "sed_ensemble_s13_f2_20260929T045053Z"
DEFAULT_SYSTEMS = {  # ADR-0048 §1; đường dẫn tương đối --runs-root
    "test": {"f2": _F2, "B0": "sed_ensemble_B0_final_test_20261014T085016Z",
             "lbrv2": "sed_lbr_B0_20261109T172809Z", "lbrv3": "sed_lbr_B0v3_20261110T042337Z"},
    "dev": {"f2": _F2, "B0": "sed_filtered_B0_oof_dev_20261107T181008Z",
            "lbrv2": "sed_lbr_oofevents_sed_lbr_B0_20261109T172809Z_f1_20261110T062901Z",
            "lbrv3": ("sed_lbr_oofevents_sed_lbr_B0v3_20261110T042337Z_recall_first"
                      "_20261110T063606Z")},
}


def parse_systems(values: list[str]) -> dict[str, Path]:
    systems = {}
    for value in values:
        label, sep, path = value.partition("=")
        if not (sep and label and path):
            raise SystemExit(f"--system cần nhãn=<run>, nhận {value!r}")
        systems[label] = Path(path)
    return systems


def sources_of(run_dir: Path, split: str) -> list[Path]:
    paths = [run_dir / "captions" / f"{b}_{split}.jsonl" for b in LLM_BRANCHES]
    return [p for p in paths if p.exists()]


def load_scored(run_dir: Path, split: str, lexicon: CaptionLexicon, eval_set: str) -> dict:
    sources = sources_of(run_dir, split)
    if not sources:
        raise SystemExit(f"{run_dir.name}: không có caption LLM cho split {split}")
    scored, _ = score_sources(sources, lexicon, eval_set)
    return scored


def truncation(run_dir: Path, split: str) -> dict[str, int]:
    out = {"template": 0}
    for path in sources_of(run_dir, split):
        meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
        out[path.stem.rsplit("_", 1)[0]] = int(meta.get("n_truncated", 0))
    return out


def _cell(scores: dict, n_truncated: int) -> dict[str, Any]:
    return {"summary": summarise(scores), "n_truncated": n_truncated,
            "ci": {m: asdict(metric_ci(scores, m)) for m in CI_METRICS}}


def build_result(systems: dict[str, Path], *, split: str, eval_set: str,
                 lexicon: CaptionLexicon, references: tuple[str, ...] = ("f2", "B0"),
                 oracle_label: str = "f2") -> dict[str, Any]:
    scored = {label: load_scored(run, split, lexicon, eval_set) for label, run in systems.items()}
    cut = {label: truncation(run, split) for label, run in systems.items()}
    e2e: dict[str, dict[str, Any]] = {}
    paired: dict[str, dict[str, Any]] = {}
    for branch in BRANCHES:
        cells = {label: _cell(s[(branch, "e2e")], cut[label].get(branch, 0))
                 for label, s in scored.items() if (branch, "e2e") in s}
        if not cells:
            continue
        e2e[branch] = cells
        paired[branch] = {}
        for ref in references:
            for label in cells:
                if label == ref or ref not in cells:
                    continue
                first, second = scored[label][(branch, "e2e")], scored[ref][(branch, "e2e")]
                if set(first) != set(second):
                    paired[branch][f"{label}−{ref}"] = {"skipped": "khác tập recording"}
                    continue
                paired[branch][f"{label}−{ref}"] = {
                    m: asdict(paired_difference(first, second, m)) for m in CI_METRICS}
    oracle = {}
    if oracle_label in scored:
        oracle = {branch: _cell(scored[oracle_label][(branch, "oracle")],
                                cut[oracle_label].get(branch, 0))
                  for branch in BRANCHES if (branch, "oracle") in scored[oracle_label]}
    return {"e2e": e2e, "paired": paired, "oracle": oracle}


def rebuild_oracle(recording_ids: list[str]) -> dict[str, dict[str, Any]]:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    recordings = pd.read_csv(ROOT / "data/manifests/datased_recordings.csv")
    durations = dict(zip(recordings["recording_id"], recordings["duration_s"], strict=True))
    return oracle_timelines(recording_ids, durations, taxonomy)


def oracle_check(run_dir: Path, split: str, eval_set: str) -> dict[str, Any]:
    """Timeline oracle đã lưu ở S8 phải trùng ground truth dựng lại (ADR-0048 §1)."""
    excluded = unannotated_recordings() if eval_set == "annotated" else frozenset()
    stored: dict[str, Any] = {}
    for path in sources_of(run_dir, split):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["level"] == "oracle" and row["recording_id"] not in excluded:
                stored.setdefault(row["recording_id"], row["timeline"])
    rebuilt = rebuild_oracle(sorted(stored))
    mismatched = sorted(r for r in stored if rebuilt.get(r) != stored[r])
    return {"n": len(stored), "identical": len(stored) - len(mismatched),
            "mismatched": mismatched, "ok": bool(stored) and not mismatched}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--runs-root", type=Path, default=ROOT / "ml/runs")
    parser.add_argument("--system", action="append", default=[])
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    check_test_gate(args.split, lexicon.sha256(), args.frozen_lexicon_sha256)
    systems = (parse_systems(args.system) if args.system else
               {k: args.runs_root / v for k, v in DEFAULT_SYSTEMS[args.split].items()})
    result = build_result(systems, split=args.split, eval_set=args.eval_set, lexicon=lexicon)
    check = oracle_check(systems["f2"], args.split, args.eval_set) if "f2" in systems else None
    if check is not None and not check["ok"]:
        result["oracle"] = {}  # ADR-0048: lệch thì không dùng lại oracle S8
    out = {"split": args.split, "eval_set": args.eval_set, "lexicon_sha256": lexicon.sha256(),
           "systems": {k: v.name for k, v in systems.items()}, "oracle_check": check,
           **result, "git": git, "created_at": datetime.now(UTC).isoformat()}
    stem = (f"rq2_llm_systems_{datetime.now(UTC):%Y%m%d}_{args.split}"
            f"{eval_suffix(args.eval_set)}")
    out_dir = ROOT / "docs" / "measurements"
    (out_dir / f"{stem}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    (out_dir / f"{stem}.md").write_text(render_markdown(out), encoding="utf-8")
    print(render_markdown(out))


if __name__ == "__main__":
    main()
