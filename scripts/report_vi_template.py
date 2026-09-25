"""W5 — kiểm caption template tiếng Việt trên timeline thật (ADR-0025).

    .venv/Scripts/python.exe -m scripts.report_vi_template ml/runs/<sed_run> --split test

Dùng đúng các timeline (oracle + e2e) mà RQ2 đã chấm, sinh caption template tiếng Việt,
chấm grounding bằng lexicon tiếng Việt. Template tất định nên kỳ vọng hallucination,
omission, từ cấm G3 và gọi tên quá mức đều 0 — script kiểm điều đó trên dữ liệu thật
(fixture chỉ vài event) và in vài câu mẫu để người dùng duyệt văn phong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.grounding import evaluate_grounding
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("hallucination_rate", "omission_rate", "temporal_order_accuracy",
           "forbidden_term_rate", "over_specific_rate", "evidence_coverage", "n_mentions")
N_EXAMPLES = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_timelines(run_dir: Path, split: str) -> dict[tuple[str, str], dict[str, Any]]:
    source = run_dir / "captions" / f"unconstrained_{split}.jsonl"
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    return {(row["recording_id"], row["level"]): row["timeline"] for row in rows}


def evaluate(timelines: dict, lexicon: CaptionLexicon) -> dict[str, Any]:
    captioner = TemplateCaptioner(lexicon)
    scored: dict[str, list] = {}
    examples: dict[str, list[str]] = {}
    for (_, level), timeline in sorted(timelines.items()):
        caption = captioner.caption(timeline, language="vi")
        scored.setdefault(level, []).append(evaluate_grounding(timeline, caption, lexicon))
        if len(examples.setdefault(level, [])) < N_EXAMPLES and 2 <= len(timeline["events"]) <= 4:
            examples[level].append(caption["text"])
    summary = {level: {"n": len(rows), **{m: mean(getattr(r, m) for r in rows) for m in METRICS}}
               for level, rows in scored.items()}
    return {"summary": summary, "examples": examples}


def render(result: dict[str, Any]) -> str:
    lines = [
        f"# Caption template tiếng Việt — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.report_vi_template`. Lexicon `{result['lexicon_version']}` "
        f"sha256 `{result['lexicon_sha256'][:16]}…`; cùng timeline RQ2 đã chấm (ADR-0025).", "",
        "| Mức | n | Halluc. ↓ | Omission ↓ | Temporal ↑ | Forbidden ↓ | Over-specific ↓ "
        "| Evidence ↑ | Mentions |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for level, s in sorted(result["summary"].items()):
        lines.append(
            f"| {level} | {s['n']} | {s['hallucination_rate']:.4f} | {s['omission_rate']:.4f} "
            f"| {s['temporal_order_accuracy']:.4f} | {s['forbidden_term_rate']:.4f} "
            f"| {s['over_specific_rate']:.4f} | {s['evidence_coverage']:.4f} "
            f"| {s['n_mentions']:.2f} |")
    lines += ["", "## Câu mẫu (timeline 2–4 event, để duyệt văn phong)", ""]
    for level, texts in sorted(result["examples"].items()):
        lines += [f"- **{level}:** {text}" for text in texts]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"),
                                           config=VI_LEXICON_CONFIG)
    result = {"run": args.run_dir.name, "split": args.split, "lexicon_version": lexicon.version,
              "lexicon_sha256": lexicon.sha256(),
              **evaluate(load_timelines(args.run_dir, args.split), lexicon)}
    destination = args.output or (
        ROOT / "docs/measurements" / f"caption_vi_template_{args.run_dir.name}_{args.split}.md")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
