"""W5 5.8 — chấm grounding (C2) cho caption đã sinh, theo nhánh × mức.

    .venv/Scripts/python.exe -m scripts.score_captions ml/runs/<sed_run> --split dev --audit
    .venv/Scripts/python.exe -m scripts.score_captions ml/runs/<sed_run> --split test \\
        --frozen-lexicon-sha256 <sha>

Đọc mọi `<run>/captions/<nhánh LLM>_<split>.jsonl` có mặt (bất biến, do
`scripts.generate_llm_captions` sinh), chấm bằng lexicon hiện tại, và chấm luôn nhánh
template trên ĐÚNG các timeline đó (cùng input — evaluation_protocol §8.2; timeline lệch
giữa hai nhánh thì dừng). Chấm test đòi lexicon đã đóng băng (ADR-0022 §3).

Mỗi số chính kèm CI bootstrap theo recording (evaluation_protocol Q3); so sánh nhánh là
hiệu số **cặp** (lấy mẫu recording chung). Bảng gắn run, split/taxonomy/prediction hash
và hash file caption (Q5). `--audit` (chỉ dev): từ nằm ngoài mọi mention, theo tần suất.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.caption_stats import CI_METRICS, metric_ci, paired_difference, summarise
from ml.evaluation.grounding import GroundingMetrics, collapse_enumerations, evaluate_grounding
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate

ROOT = Path(__file__).resolve().parents[1]
LLM_BRANCHES = ("unconstrained", "constrained", "constrained_cover")
PAIRS = (("constrained", "unconstrained"), ("constrained_cover", "unconstrained"),
         ("constrained_cover", "constrained"))
STOPWORDS = frozenset(
    "a an the of and or with by in on at to from for as is are be was were it its this that "
    "then while throughout followed before after during between into over under along "
    "recording environmental soundscape sound sounds audio heard audible distinct distant "
    "brief briefly continuous intermittent occasional steady sudden final first second "
    "seconds minute minutes end start beginning later throughout captures features".split()
)
Scored = dict[tuple[str, str], dict[str, GroundingMetrics]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


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


def score_sources(sources: list[Path], lexicon: CaptionLexicon) -> tuple[Scored, Counter[str]]:
    """Score every LLM caption and the template on the identical timelines."""
    scored: Scored = {}
    audit: Counter[str] = Counter()
    reference: dict[tuple[str, str], Any] = {}
    for source in sources:
        branch = source.stem.rsplit("_", 1)[0]
        for line in source.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            key = (row["recording_id"], row["level"])
            if reference.setdefault(key, row["timeline"]) != row["timeline"]:
                raise SystemExit(f"{source.name}: timeline {key} khác nhánh trước — không so được")
            scored.setdefault((branch, row["level"]), {})[row["recording_id"]] = (
                evaluate_grounding(row["timeline"], row["caption"], lexicon))
            if branch == "unconstrained":
                audit.update(uncovered_words(row["caption"]["text"], lexicon))
    template = TemplateCaptioner(lexicon)
    for (rid, level), timeline in sorted(reference.items()):
        scored.setdefault(("template", level), {})[rid] = evaluate_grounding(
            timeline, template.caption(timeline), lexicon)
    return scored, audit


def statistics(scored: Scored) -> dict[str, Any]:
    summary, intervals, paired = {}, {}, {}
    for (branch, level), scores in sorted(scored.items()):
        key = f"{branch}/{level}"
        summary[key] = summarise(scores)
        intervals[key] = {m: asdict(metric_ci(scores, m)) for m in CI_METRICS}
    levels = sorted({level for _, level in scored})
    for first, second in PAIRS:
        for level in levels:
            if (first, level) in scored and (second, level) in scored:
                paired[f"{first}−{second}/{level}"] = {
                    m: asdict(paired_difference(scored[(first, level)], scored[(second, level)], m))
                    for m in CI_METRICS}
    return {"summary": summary, "ci": intervals, "paired": paired}


def provenance(run_dir: Path, split: str, sources: list[Path], lexicon: CaptionLexicon) -> dict:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    if manifest["taxonomy_sha256"] != lexicon.taxonomy.checksum:
        raise SystemExit("run khoá theo taxonomy khác taxonomy đang dùng")
    captions = {}
    for path in sources:
        meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
        captions[path.name] = meta["output_sha256"]
    return {"run": run_dir.name, "split": split, "split_sha256": manifest["split_sha256"],
            "taxonomy_sha256": manifest["taxonomy_sha256"],
            "predictions_sha256": metrics[f"{split}_predictions_sha256"],
            "captions_sha256": captions, "lexicon_version": lexicon.version,
            "lexicon_sha256": lexicon.sha256(), "git": git_state(ROOT)}


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    check_test_gate(args.split, lexicon.sha256(), args.frozen_lexicon_sha256)
    if args.audit and args.split != "dev":
        raise SystemExit("--audit chỉ cho dev: mở rộng lexicon bằng caption test = tuning test")
    sources = [args.run_dir / "captions" / f"{b}_{args.split}.jsonl" for b in LLM_BRANCHES]
    sources = [path for path in sources if path.exists()]
    if not sources:
        raise SystemExit(f"không có caption nào cho split {args.split}")
    scored, audit = score_sources(sources, lexicon)
    result = {**provenance(args.run_dir, args.split, sources, lexicon), **statistics(scored)}
    if args.audit:
        result["uncovered_words"] = audit.most_common(150)
    destination = args.output or (
        ROOT / "docs/measurements" / f"caption_grounding_{args.run_dir.name}_{args.split}.md")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


def _ci(entry: dict[str, float]) -> str:
    return f"{entry['estimate']:.3f} [{entry['lower']:.3f}, {entry['upper']:.3f}]"


def _signed_ci(entry: dict[str, float]) -> str:
    return f"{entry['estimate']:+.3f} [{entry['lower']:+.3f}, {entry['upper']:+.3f}]"


def render(result: dict[str, Any]) -> str:
    lines = [
        f"# Grounding caption — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.score_captions`. Lexicon `{result['lexicon_version']}` "
        f"`{result['lexicon_sha256'][:8]}…` · split `{result['split_sha256'][:8]}…` · "
        f"taxonomy `{result['taxonomy_sha256'][:8]}…` · prediction "
        f"`{result['predictions_sha256'][:8]}…`. Mơ hồ xử theo hướng có lợi cho caption "
        "(ADR-0022 §3) → Δ so với unconstrained là cận dưới.", "",
        "Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** "
        "phải Kendall τ). Cột \"≥2\" chỉ tính caption có ít nhất 2 mention — caption 0–1 "
        "mention mặc định 1.0.", "",
        "| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ "
        "| Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, s in result["summary"].items():
        lines.append(
            f"| {key} | {s['n']} | {s['hallucination_rate']:.4f} | {s['hallucination_micro']:.4f} "
            f"| {s['omission_rate']:.4f} | {s['temporal_order_accuracy']:.4f} "
            f"| {s['temporal_order_eligible']:.4f} ({s['n_temporal_eligible']}) "
            f"| {s['forbidden_term_rate']:.4f} | {s['over_specific_rate']:.4f} "
            f"| {s['context_term_rate']:.4f} | {s['n_mentions']:.2f} |")
    header = " | ".join(CI_METRICS)
    lines += ["", "## CI 95% (bootstrap theo recording, 1000 lần)", "",
              f"| Nhánh / mức | {header} |", "|---|" + "---:|" * len(CI_METRICS)]
    for key, entry in result["ci"].items():
        lines.append(f"| {key} | " + " | ".join(_ci(entry[m]) for m in CI_METRICS) + " |")
    lines += ["", "## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%", "",
              f"| So sánh | {header} |", "|---|" + "---:|" * len(CI_METRICS)]
    for key, entry in result["paired"].items():
        lines.append(f"| {key} | " + " | ".join(_signed_ci(entry[m]) for m in CI_METRICS) + " |")
    if "uncovered_words" in result:
        lines += ["", "## Audit: từ ngoài mọi mention (dev)", "",
                  ", ".join(f"{w} ({n})" for w, n in result["uncovered_words"])]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
