"""S8-lite (ADR-0044): grounding caption template EN + VI trên timeline e2e của một hệ SED.

    .venv/Scripts/python.exe -m scripts.score_template_e2e --label B0 \\
        --predictions-run ml/runs/<run có predictions/<split>.npz> \\
        --postproc ml/runs/<run>/sebb_cv_selection_annotated.json --split dev --eval-set annotated

Template tất định nên không cần LLM: timeline dựng bằng đúng `e2e_timelines` mà RQ2 dùng, caption
EN chấm bằng lexicon EN đã đóng băng, caption VI bằng lexicon VI (ADR-0025). Mức `oracle` không
phụ thuộc SED nên không chấm lại ở đây. Ra `docs/measurements/caption_template_<label>_<split>…`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.caption_stats import CI_METRICS, metric_ci, summarise
from ml.evaluation.coverage import EVAL_SETS, eval_suffix, unannotated_recordings
from ml.evaluation.grounding import evaluate_grounding
from ml.postprocessing.lbr_apply import OPERATING_POINTS
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file
from scripts.generate_llm_captions import check_test_gate, e2e_timelines

ROOT = Path(__file__).resolve().parents[1]
HEADLINE = ("hallucination_rate", "omission_rate", "forbidden_term_rate", "over_specific_rate")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True)
    parser.add_argument("--predictions-run", type=Path, required=True)
    parser.add_argument("--postproc", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--lbr-point", choices=OPERATING_POINTS, default=None,
                        help="bắt buộc khi --postproc là manifest LBR (ADR-0047)")
    return parser.parse_args()


def score(timelines: dict, lexicon: CaptionLexicon, language: str) -> dict:
    captioner = TemplateCaptioner(lexicon)
    scores = {rid: evaluate_grounding(t, captioner.caption(t, language=language), lexicon)
              for rid, t in timelines.items()}
    return {"summary": summarise(scores),
            "ci": {m: asdict(metric_ci(scores, m)) for m in CI_METRICS}}


def markdown(result: dict) -> str:
    lines = [f"# Caption template trên e2e — {result['label']} · {result['split']} "
             f"({result['eval_set']})", "",
             f"Sinh bởi `scripts.score_template_e2e`; prediction `{result['predictions_run']}` "
             f"(sha `{result['predictions_sha256'][:12]}…`), hậu xử lý `{result['postproc']}`.", "",
             "| Ngôn ngữ | n | " + " | ".join(HEADLINE) + " |",
             "|---|---:|" + "---:|" * len(HEADLINE)]
    for language, block in result["languages"].items():
        cells = [f"{block['summary'][m]:.4f}" for m in HEADLINE]
        lines.append(f"| {language} | {block['summary']['n']} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    english = CaptionLexicon.from_taxonomy(taxonomy)
    check_test_gate(args.split, english.sha256(), args.frozen_lexicon_sha256)
    vietnamese = CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG)
    timelines = e2e_timelines(args.predictions_run, args.split, taxonomy, args.postproc,
                              args.predictions_run, lbr_point=args.lbr_point)
    excluded = unannotated_recordings() if args.eval_set == "annotated" else frozenset()
    timelines = {rid: t for rid, t in timelines.items() if rid not in excluded}
    result = {
        "label": args.label, "split": args.split, "eval_set": args.eval_set,
        "predictions_run": args.predictions_run.name,
        "predictions_sha256": sha256_file(
            args.predictions_run / "predictions" / f"{args.split}.npz"),
        "postproc": str(args.postproc), "postproc_sha256": sha256_file(args.postproc),
        "lbr_point": args.lbr_point,
        "lexicon_sha256": {"en": english.sha256(), "vi": vietnamese.sha256()},
        "languages": {"en": score(timelines, english, "en"),
                      "vi": score(timelines, vietnamese, "vi")},
        "generated_at": datetime.now(UTC).isoformat(), "git": git_state(ROOT),
    }
    stem = f"caption_template_{args.label}_{args.split}{eval_suffix(args.eval_set)}"
    out = ROOT / "docs" / "measurements" / f"{stem}_{datetime.now(UTC):%Y%m%d}"
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
    print(markdown(result))


if __name__ == "__main__":
    main()
