"""W5 — BLEU-4 và CIDEr của caption LLM, **chỉ để tham khảo** (evaluation_protocol §8.3).

    .venv/Scripts/python.exe -m scripts.report_caption_ngram ml/runs/<sed_run> --split test

Tham chiếu là caption template sinh tất định từ **cùng** timeline (không phải caption
người viết), nên n-gram không đo chất lượng ngôn ngữ, không phát hiện hallucination, và
thiên vị nhánh constrained (grammar dùng cụm từ gần template). Không dùng để kết luận.

Scorer lấy từ thư viện chuẩn `pycocoevalcap` (Bleu, Cider). Tách từ PTB của thư viện cần
Java — máy không có — nên dùng tách từ tất định đơn giản (chữ thường, giữ số thập phân
và từ nối gạch); ghi rõ trong measurement.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from pycocoevalcap.bleu.bleu import Bleu
from pycocoevalcap.cider.cider import Cider

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.taxonomy import load_taxonomy
from scripts.score_captions import LLM_BRANCHES

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"[a-z0-9]+(?:[.'-][a-z0-9]+)*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def tokenize(text: str) -> str:
    return " ".join(TOKEN.findall(text.lower()))


def ngram_scores(references: dict[str, str], hypotheses: dict[str, str]) -> dict[str, float]:
    """Corpus BLEU-1..4 and CIDEr, one reference per item (pycocoevalcap scorers)."""
    refs = {key: [tokenize(text)] for key, text in references.items()}
    hyps = {key: [tokenize(hypotheses[key])] for key in references}
    bleu, _ = Bleu(4).compute_score(refs, hyps, verbose=0)
    cider, _ = Cider().compute_score(refs, hyps)
    return {"bleu_1": bleu[0], "bleu_4": bleu[3], "cider": float(cider), "n": len(refs)}


def load_pairs(run_dir: Path, split: str) -> dict[str, dict[str, Any]]:
    """{branch/level: {"refs": {...}, "hyps": {...}}} with template references."""
    template = TemplateCaptioner(
        CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")))
    pairs: dict[str, dict[str, Any]] = {}
    for branch in LLM_BRANCHES:
        source = run_dir / "captions" / f"{branch}_{split}.jsonl"
        if not source.exists():
            continue
        for line in source.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            key = f"{row['recording_id']}|{row['level']}"
            group = pairs.setdefault(f"{branch}/{row['level']}", {"refs": {}, "hyps": {}})
            group["refs"][key] = template.caption(row["timeline"])["text"]
            group["hyps"][key] = row["caption"]["text"]
    if not pairs:
        raise SystemExit(f"không có caption nào cho split {split}")
    return pairs


def render(result: dict[str, Any]) -> str:
    lines = [
        f"# N-gram caption (chỉ tham khảo) — `{result['run']}` ({result['split']})", "",
        "> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** "
        "(evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, "
        "không phải caption người viết; nhánh constrained dùng cụm từ gần template theo "
        "cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer "
        "`pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).", "",
        "| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, s in result["scores"].items():
        lines.append(f"| {key} | {s['n']} | {s['bleu_1']:.4f} | {s['bleu_4']:.4f} "
                     f"| {s['cider']:.4f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pairs = load_pairs(args.run_dir, args.split)
    scores = {key: ngram_scores(g["refs"], g["hyps"]) for key, g in sorted(pairs.items())}
    result = {"run": args.run_dir.name, "split": args.split, "reference": "template",
              "tokenizer": TOKEN.pattern, "scores": scores}
    destination = args.output or (
        ROOT / "docs/measurements" / f"caption_ngram_{args.run_dir.name}_{args.split}.md"
    )
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
