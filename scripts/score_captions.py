"""W5 5.8 — chấm grounding (C2) cho caption đã sinh, theo nhánh × mức.

    .venv/Scripts/python.exe -m scripts.score_captions ml/runs/<sed_run> --split dev --audit
    .venv/Scripts/python.exe -m scripts.score_captions ml/runs/<sed_run> --split test \\
        --frozen-lexicon-sha256 <sha>

Đọc `<run>/captions/unconstrained_<split>.jsonl` (bất biến, do
`scripts.generate_llm_captions` sinh), chấm lại bằng lexicon hiện tại, và chấm
luôn nhánh template trên ĐÚNG các timeline đó (cùng input — evaluation_protocol
§8.2). Chấm test đòi lexicon đã đóng băng (ADR-0022 §3).

`--audit` (chỉ cho dev): liệt kê từ nằm ngoài mọi mention, theo tần suất — vật
liệu để người rà xem lexicon còn sót cách diễn đạt nguồn âm nào.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.grounding import GroundingMetrics, collapse_enumerations, evaluate_grounding
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("hallucination_rate", "omission_rate", "temporal_order_accuracy",
           "forbidden_term_rate", "over_specific_rate", "context_term_rate",
           "evidence_coverage", "n_mentions")
STOPWORDS = frozenset(
    "a an the of and or with by in on at to from for as is are be was were it its this that "
    "then while throughout followed before after during between into over under along "
    "recording environmental soundscape sound sounds audio heard audible distinct distant "
    "brief briefly continuous intermittent occasional steady sudden final first second "
    "seconds minute minutes end start beginning later throughout captures features".split()
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def summarise(rows: list[GroundingMetrics]) -> dict[str, float]:
    return {name: mean(getattr(row, name) for row in rows) for name in METRICS}


def uncovered_words(text: str, lexicon: CaptionLexicon) -> list[str]:
    spans = [(m.start, m.end) for m in collapse_enumerations(text, lexicon.mentions(text))]
    counted = set(lexicon.context_terms(text)) | set(lexicon.forbidden_terms(text))
    words = []
    for match in re.finditer(r"[a-z][a-z-]+", text.lower()):
        word = match.group()
        if any(s <= match.start() < e for s, e in spans) or word in STOPWORDS | counted:
            continue
        words.append(word)
    return words


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    check_test_gate(args.split, lexicon.sha256(), args.frozen_lexicon_sha256)
    if args.audit and args.split != "dev":
        raise SystemExit("--audit chỉ cho dev: mở rộng lexicon bằng caption test = tuning test")

    source = args.run_dir / "captions" / f"unconstrained_{args.split}.jsonl"
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    template = TemplateCaptioner(lexicon)
    scores: dict[tuple[str, str], list[GroundingMetrics]] = {}
    audit: Counter[str] = Counter()
    for row in rows:
        timeline, level = row["timeline"], row["level"]
        scores.setdefault(("unconstrained", level), []).append(
            evaluate_grounding(timeline, row["caption"], lexicon)
        )
        scores.setdefault(("template", level), []).append(
            evaluate_grounding(timeline, template.caption(timeline), lexicon)
        )
        audit.update(uncovered_words(row["caption"]["text"], lexicon))

    table = {f"{branch}/{level}": {"n": len(v), **summarise(v)}
             for (branch, level), v in sorted(scores.items())}
    result: dict[str, Any] = {
        "run": args.run_dir.name, "split": args.split, "source": str(source),
        "lexicon_version": lexicon.version, "lexicon_sha256": lexicon.sha256(),
        "summary": table,
    }
    if args.audit:
        result["uncovered_words"] = audit.most_common(150)
    destination = args.output or (
        ROOT / "docs/measurements" / f"caption_grounding_{args.run_dir.name}_{args.split}.md"
    )
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


def render(result: dict[str, Any]) -> str:
    lines = [
        f"# Grounding caption — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.score_captions`. Lexicon `{result['lexicon_version']}` "
        f"sha256 `{result['lexicon_sha256'][:16]}…`. Mơ hồ xử theo hướng có lợi cho "
        "caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.", "",
        "| Nhánh / mức | n | Halluc. ↓ | Omission ↓ | Temporal ↑ | Forbidden ↓ "
        "| Over-specific ↓ | Context ↓ | Mentions |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, s in result["summary"].items():
        lines.append(
            f"| {key} | {s['n']} | {s['hallucination_rate']:.4f} | {s['omission_rate']:.4f} "
            f"| {s['temporal_order_accuracy']:.4f} | {s['forbidden_term_rate']:.4f} "
            f"| {s['over_specific_rate']:.4f} | {s['context_term_rate']:.4f} "
            f"| {s['n_mentions']:.2f} |"
        )
    if "uncovered_words" in result:
        lines += ["", "## Audit: từ ngoài mọi mention (dev)", "",
                  ", ".join(f"{w} ({n})" for w, n in result["uncovered_words"])]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
