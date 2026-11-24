"""ADR-0050: mô tả gộp theo lớp có rào đón so với mô tả mẫu cố định, trên dòng thời gian dev.

θ_hedge = phân vị 33,3% điểm sự kiện trong dòng thời gian dev của hệ phục vụ (LBR V3
`recall_first`), tính một lần ở đây. Với bốn hệ SED (134 bản ghi có nhãn): ảo giác/bỏ sót so với
dự đoán và với nhãn gốc, thứ tự thời gian, độ dài; và rào đón có mang thông tin không (độ chính xác
theo lớp của mệnh đề có/không rào đón, hiệu và CI bootstrap theo bản ghi). Không gọi LLM, không mở
test.

    .venv/Scripts/python.exe -m scripts.report_grouped_captions
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from ml.captioning.grouped import GroupedTemplateCaptioner
from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.coverage import unannotated_recordings
from ml.evaluation.grounding import evaluate_grounding
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_caption_vs_gt import RUNS, SYSTEMS, read_rows

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
SERVED = "lbrv3"
PERCENTILE = 100.0 / 3.0
SEED = 20260922
N_RESAMPLE = 10_000
METRICS = ("hallucination_rate", "omission_rate", "temporal_order_accuracy")


def hedge_threshold(timelines: list[dict]) -> float:
    scores = [e["score"] for t in timelines for e in t["events"]]
    return float(np.percentile(scores, PERCENTILE))


def hedge_outcomes(captioner: GroupedTemplateCaptioner, timeline: dict,
                   gt_classes: set[str]) -> list[tuple[bool, bool]]:
    """(hedged, class present in ground truth) per clause."""
    return [(c["hedged"], c["class_id"] in gt_classes) for c in captioner.clauses(timeline)]


def precision_gap(per_rec: list[list[tuple[bool, bool]]], seed: int = SEED,
                  n: int = N_RESAMPLE) -> dict[str, Any]:
    """Pooled precision of unhedged minus hedged clauses, bootstrap over recordings."""
    def stat(sample: list[list[tuple[bool, bool]]]) -> float | None:
        flat = [x for rec in sample for x in rec]
        plain = [ok for h, ok in flat if not h]
        hedged = [ok for h, ok in flat if h]
        if not plain or not hedged:
            return None
        return sum(plain) / len(plain) - sum(hedged) / len(hedged)

    flat = [x for rec in per_rec for x in rec]
    counts = {"hedged": sum(h for h, _ in flat), "hedged_correct": sum(h and ok for h, ok in flat),
              "plain": sum(not h for h, _ in flat),
              "plain_correct": sum((not h) and ok for h, ok in flat)}
    estimate = stat(per_rec)
    rng = np.random.default_rng(seed)
    draws = [stat([per_rec[i] for i in rng.integers(0, len(per_rec), len(per_rec))])
             for _ in range(n)]
    valid = np.array([d for d in draws if d is not None])
    lower, upper = (np.quantile(valid, [0.025, 0.975]) if valid.size else (np.nan, np.nan))
    return {**counts, "estimate": estimate, "lower": float(lower), "upper": float(upper),
            "n_valid_draws": int(valid.size)}


def evaluate(captioner: TemplateCaptioner, timelines: dict[str, dict], gt: dict[str, dict],
             lexicon: CaptionLexicon) -> dict[str, Any]:
    pred, truth, chars = [], [], []
    for rid, timeline in timelines.items():
        caption = captioner.caption(timeline)
        pred.append(evaluate_grounding(timeline, caption, lexicon).as_dict())
        truth.append(evaluate_grounding(gt[rid], caption, lexicon).as_dict())
        chars.append(len(caption["text"]))
    return {"vs_pred": {m: mean(r[m] for r in pred) for m in METRICS},
            "vs_gt": {m: mean(r[m] for r in truth) for m in METRICS[:2]},
            "chars_mean": mean(chars), "chars_max": max(chars), "n": len(chars)}


def build() -> dict[str, Any]:
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    excluded = unannotated_recordings()
    reference = read_rows(RUNS / SYSTEMS["f2"] / "captions" / "constrained_dev.jsonl", excluded)
    gt = {rid: row["timeline"] for rid, row in reference["oracle"].items()}
    timelines = {system: {rid: row["timeline"] for rid, row in read_rows(
        RUNS / run / "captions" / "constrained_dev.jsonl", excluded)["e2e"].items() if rid in gt}
        for system, run in SYSTEMS.items()}
    theta = hedge_threshold(list(timelines[SERVED].values()))
    template = TemplateCaptioner(lexicon)
    grouped = GroupedTemplateCaptioner(lexicon, hedge_threshold=theta)
    results = {}
    for system, tls in timelines.items():
        outcomes = [hedge_outcomes(grouped, tl, {e["class_id"] for e in gt[rid]["events"]})
                    for rid, tl in sorted(tls.items())]
        results[system] = {"template": evaluate(template, tls, gt, lexicon),
                           "grouped": evaluate(grouped, tls, gt, lexicon),
                           "hedging": precision_gap([o for o in outcomes if o])}
    return {"split": "dev", "eval_set": "annotated", "adr": "ADR-0050", "served": SERVED,
            "hedge_percentile": PERCENTILE, "hedge_threshold": theta, "results": results,
            "sources": {s: f"ml/runs/{r}/captions/constrained_dev.jsonl"
                        for s, r in SYSTEMS.items()},
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    lines = [f"# Mô tả gộp theo lớp có rào đón (dev, ADR-0050), θ_hedge = "
             f"{data['hedge_threshold']:.4f}", "",
             "> Sinh bởi `scripts.report_grouped_captions`.", "",
             "| Hệ | Bộ sinh | Ảo giác / bỏ sót (dự đoán) | Thứ tự | Ảo giác / bỏ sót (nhãn gốc) "
             "| Ký tự TB | Ký tự max |", "|---|---|---:|---:|---:|---:|---:|"]
    for system, r in data["results"].items():
        for name in ("template", "grouped"):
            x = r[name]
            lines.append(
                f"| {system} | {name} | {x['vs_pred']['hallucination_rate']:.3f} / "
                f"{x['vs_pred']['omission_rate']:.3f} | "
                f"{x['vs_pred']['temporal_order_accuracy']:.3f} | "
                f"{x['vs_gt']['hallucination_rate']:.3f} / {x['vs_gt']['omission_rate']:.3f} | "
                f"{x['chars_mean']:.0f} | {x['chars_max']} |")
    lines += ["", "| Hệ | Mệnh đề rào đón (đúng/tổng) | Không rào đón (đúng/tổng) | "
              "Hiệu độ chính xác [CI 95%] |", "|---|---:|---:|---:|"]
    for system, r in data["results"].items():
        h = r["hedging"]
        est = "—" if h["estimate"] is None else (
            f"{h['estimate']:+.3f} [{h['lower']:+.3f}, {h['upper']:+.3f}]")
        lines.append(f"| {system} | {h['hedged_correct']}/{h['hedged']} | "
                     f"{h['plain_correct']}/{h['plain']} | {est} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = M / f"grouped_captions_dev_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
