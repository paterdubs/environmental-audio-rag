"""W4 4.6 — cặp lớp bị nhầm thật (substitution) từ dự đoán SED, để cập nhật taxonomy.md §8.

    .venv/Scripts/python.exe -m scripts.report_confusable_pairs ml/runs/<run> [...]

Mặc định corpus **dev** (không cần mở test để mô tả lỗi; `--split test` chỉ để đối chiếu).
Mỗi run: timeline e2e từ dự đoán + `postproc.json` đóng băng (cùng đường đi W5/W6), so với
annotation polyphonic; đếm substitution a→b theo `ml.evaluation.confusion` (event `a` bị bỏ
lỡ, bị chồng bởi dự đoán sai `b`). Gộp nhiều run: tổng, trung bình mỗi run và số run có cặp đó
— cặp chỉ xuất hiện ở một run là nhiễu seed, không phải `confusable_with`. Đối chiếu với các cặp
giả thuyết âm học đang có trong bảng §8.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.confusion import substitutions, unordered
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording
from scripts.generate_llm_captions import e2e_timelines

ROOT = Path(__file__).resolve().parents[1]
SPLIT_FILE = {"dev": "dev", "test": "test"}
TOP = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--split", choices=tuple(SPLIT_FILE), default="dev")
    parser.add_argument("--tag", default="clean")
    return parser.parse_args()


def hypothesis_pairs(class_ids: tuple[str, ...]) -> set[tuple[str, str]]:
    """Pairs in the acoustic table of taxonomy.md §8 (names may be truncated with '…')."""
    text = (ROOT / "docs/taxonomy.md").read_text(encoding="utf-8")
    section = text.split("## 8.", 1)[1].split("\n## ", 1)[0]
    pairs = set()
    for a, b in re.findall(r"^\| `([^`]+)` ↔ `([^`]+)` \|", section, flags=re.M):
        resolved = [next(c for c in class_ids if c.startswith(n.rstrip("…"))) for n in (a, b)]
        pairs.add(tuple(sorted(resolved)))
    return pairs


def run_counts(run: Path, split: str, taxonomy) -> tuple[Counter, Counter, int]:
    timelines = e2e_timelines(run, SPLIT_FILE[split], taxonomy)
    estimate = {rid: [{"event_label": e["class_id"], "onset": e["onset_s"],
                       "offset": e["offset_s"]} for e in t["events"]]
                for rid, t in timelines.items()}
    reference = load_events_by_recording(set(estimate))
    counts, seconds = substitutions(reference, estimate)
    return counts, seconds, sum(len(v) for v in reference.values())


def aggregate(per_run: list[Counter], seconds: list[Counter], hypotheses) -> list[dict]:
    folded = [unordered(c) for c in per_run]
    folded_s = [unordered(s) for s in seconds]
    directed = per_run
    rows = []
    for pair in set().union(*folded):
        a, b = pair
        rows.append({
            "pair": list(pair), "total": sum(f[pair] for f in folded),
            "mean_per_run": sum(f[pair] for f in folded) / len(folded),
            "runs_present": sum(f[pair] > 0 for f in folded),
            "a_to_b": sum(d[(a, b)] for d in directed), "b_to_a": sum(d[(b, a)] for d in directed),
            "overlap_s": sum(f[pair] for f in folded_s), "in_table": pair in hypotheses})
    return sorted(rows, key=lambda r: (-r["total"], r["pair"]))


def render(result: dict) -> str:
    n = len(result["runs"])
    lines = [
        f"# Cặp lớp bị nhầm thật (substitution) — corpus `{result['split']}`, {n} run", "",
        "> Sinh bởi `scripts.report_confusable_pairs`. Substitution a→b: event tham chiếu `a` "
        "bị bỏ lỡ và bị chồng bởi một dự đoán sai `b` (không có `b` thật chồng lên) — đa âm "
        "không bị tính là nhầm. Đếm theo cặp event, gộp hai chiều. \"Run có\" = số run có ít "
        "nhất một lượt; cặp chỉ ở 1 run là nhiễu seed.", "",
        f"Tổng substitution: {result['total_substitutions']} lượt trên "
        f"{result['reference_events']} event tham chiếu (cộng qua các run).", "",
        "| # | Cặp | Tổng | TB/run | Run có | a→b | b→a | Chồng lấp (s) | Trong bảng §8 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for i, r in enumerate(result["pairs"][:TOP], 1):
        a, b = r["pair"]
        lines.append(f"| {i} | `{a}` ↔ `{b}` | {r['total']} | {r['mean_per_run']:.1f} "
                     f"| {r['runs_present']}/{n} | {r['a_to_b']} | {r['b_to_a']} "
                     f"| {r['overlap_s']:.0f} | {'✓' if r['in_table'] else ''} |")
    observed = {tuple(r["pair"]): r for r in result["pairs"]}
    lines += ["", "## Cặp giả thuyết âm học trong bảng §8", "",
              "| Cặp | Tổng | Run có | Hạng |", "|---|---:|---:|---:|"]
    rank = {tuple(r["pair"]): i for i, r in enumerate(result["pairs"], 1)}
    for pair in sorted(result["hypotheses"]):
        r = observed.get(tuple(pair))
        lines.append(f"| `{pair[0]}` ↔ `{pair[1]}` | {r['total'] if r else 0} "
                     f"| {r['runs_present'] if r else 0}/{n} | {rank.get(tuple(pair), '—')} |")
    lines += ["", "Runs: " + ", ".join(f"`{r}`" for r in result["runs"])]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    hypotheses = hypothesis_pairs(taxonomy.class_ids)
    measured = [run_counts(run, args.split, taxonomy) for run in args.runs]
    pairs = aggregate([m[0] for m in measured], [m[1] for m in measured], hypotheses)
    result = {"split": args.split, "runs": [r.name for r in args.runs], "git": git,
              "reference_events": sum(m[2] for m in measured),
              "total_substitutions": sum(sum(m[0].values()) for m in measured),
              "hypotheses": sorted(list(p) for p in hypotheses), "pairs": pairs}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"confusable_pairs_{args.tag}_{args.split}_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
