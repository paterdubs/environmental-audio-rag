"""RQ2 ba tầng: chấm mô tả so với dòng thời gian được đưa vào và so với nhãn gốc (chỉ dev).

Các số RQ2 đã khóa chấm mô tả so với chính dòng thời gian SED mà nó nhận, nên "0 ảo giác" ở nhánh
có ràng buộc là đúng theo cấu tạo. Script này thêm tầng thứ ba: chấm cùng mô tả e2e so với dòng thời
gian của nhãn gốc, để tách lỗi do bộ sinh mô tả khỏi lỗi do SED.

- `oracle`: mô tả sinh từ dòng thời gian nhãn gốc, chấm so với nhãn gốc (chỉ run f2 có mức này).
- `e2e_vs_pred`: mô tả sinh từ dòng thời gian dự đoán, chấm so với chính dòng đó (thước RQ2 cũ).
- `e2e_vs_gt`: cùng mô tả đó, chấm so với nhãn gốc.

Chỉ đọc tệp `captions/*_dev.jsonl` đã sinh (không gọi LLM, không mở test); mô tả mẫu cố định sinh
lại tất định bằng `TemplateCaptioner`. Bộ đánh giá `annotated` (bỏ bản ghi thiếu nhãn gốc).

    .venv/Scripts/python.exe -m scripts.report_caption_vs_gt
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.bootstrap import recording_bootstrap
from ml.evaluation.coverage import unannotated_recordings
from ml.evaluation.grounding import evaluate_grounding
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
RUNS = ROOT / "ml" / "runs"
SYSTEMS = {  # hệ SED → run chứa mô tả dev (ADR-0040, ADR-0044, ADR-0047/0048)
    "f2": "sed_ensemble_s13_f2_20260929T045053Z",
    "B0": "sed_filtered_B0_oof_dev_20261107T181008Z",
    "lbrv2": "sed_lbr_oofevents_sed_lbr_B0_20261109T172809Z_f1_20261110T062901Z",
    "lbrv3": "sed_lbr_oofevents_sed_lbr_B0v3_20261110T042337Z_recall_first_20261110T063606Z",
}
BRANCHES = ("template", "unconstrained", "constrained", "constrained_cover")
TIERS = ("oracle", "e2e_vs_pred", "e2e_vs_gt")
METRICS = ("hallucination_rate", "omission_rate", "event_precision", "event_recall")
SEED = 20260922


def read_rows(path: Path, excluded: frozenset[str]) -> dict[str, dict[str, dict]]:
    """level → recording_id → row, recordings without ground truth dropped."""
    out: dict[str, dict[str, dict]] = {"oracle": {}, "e2e": {}}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["recording_id"] not in excluded:
                out[row["level"]][row["recording_id"]] = row
    return out


def tier_scores(gt: dict[str, dict], oracle: dict[str, dict] | None, e2e: dict[str, dict],
                caption: Callable[[dict], dict],
                lexicon: CaptionLexicon) -> dict[str, dict[str, dict[str, float]]]:
    """tier → recording_id → metrics. `caption(row)` returns the caption to score."""
    scores: dict[str, dict[str, dict[str, float]]] = {t: {} for t in TIERS}
    for rid in sorted(set(gt) & set(e2e)):
        if oracle is not None:
            scores["oracle"][rid] = evaluate_grounding(gt[rid], caption(oracle[rid]),
                                                       lexicon).as_dict()
        text = caption(e2e[rid])
        scores["e2e_vs_pred"][rid] = evaluate_grounding(e2e[rid]["timeline"], text,
                                                        lexicon).as_dict()
        scores["e2e_vs_gt"][rid] = evaluate_grounding(gt[rid], text, lexicon).as_dict()
    return {tier: per_rec for tier, per_rec in scores.items() if per_rec}


def summarise(scores: dict[str, dict[str, dict[str, float]]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for tier, per_rec in scores.items():
        ids = sorted(per_rec)
        cell: dict[str, Any] = {"n": len(ids)}
        for metric in METRICS:
            ci = asdict(recording_bootstrap(
                ids, lambda s, m=metric, p=per_rec: mean(p[r][m] for r in s), seed=SEED))
            cell[metric] = {k: ci[k] for k in ("estimate", "lower", "upper")}
        out[tier] = cell
    return out


def build() -> dict[str, Any]:
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    template = TemplateCaptioner(lexicon)
    excluded = unannotated_recordings()
    # Chỉ run f2 có mức oracle (ADR-0040); dòng thời gian nhãn gốc dùng chung cho mọi hệ.
    reference = read_rows(RUNS / SYSTEMS["f2"] / "captions" / "constrained_dev.jsonl", excluded)
    gt = {rid: row["timeline"] for rid, row in reference["oracle"].items()}
    results, sources = {}, {"ground_truth": f"ml/runs/{SYSTEMS['f2']}/captions/"
                                            "constrained_dev.jsonl (level oracle)"}
    for system, run in SYSTEMS.items():
        files = {b: read_rows(RUNS / run / "captions" / f"{b}_dev.jsonl", excluded)
                 for b in BRANCHES[1:]}
        for branch in files:
            sources[f"{system}/{branch}"] = f"ml/runs/{run}/captions/{branch}_dev.jsonl"
        results[f"{system}/template"] = summarise(tier_scores(
            gt, reference["oracle"] if system == "f2" else None, files["constrained"]["e2e"],
            lambda row: template.caption(row["timeline"]), lexicon))
        for branch, rows in files.items():
            results[f"{system}/{branch}"] = summarise(tier_scores(
                gt, rows["oracle"] or None, rows["e2e"], lambda row: row["caption"], lexicon))
    return {"split": "dev", "eval_set": "annotated", "results": results, "sources": sources,
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    lines = ["# RQ2 ba tầng: mô tả so với dòng thời gian dự đoán và với nhãn gốc (dev, annotated)",
             "", "> Sinh bởi `scripts.report_caption_vs_gt`; chỉ đọc mô tả dev đã sinh. "
             "Ô: trung bình theo bản ghi [CI 95% bootstrap].", ""]
    for metric, title in (("hallucination_rate", "Tỷ lệ ảo giác"),
                          ("omission_rate", "Tỷ lệ bỏ sót")):
        lines += [f"## {title}", "", "| Hệ | Nhánh | n | oracle | e2e so với dự đoán | "
                  "e2e so với nhãn gốc |", "|---|---|---:|---:|---:|---:|"]
        for key, cell in data["results"].items():
            system, branch = key.split("/")
            parts = [f"{cell[t][metric]['estimate']:.3f}" if t in cell else "—"
                     for t in TIERS[:2]]
            gt = cell["e2e_vs_gt"][metric]
            parts.append(f"{gt['estimate']:.3f} [{gt['lower']:.3f}, {gt['upper']:.3f}]")
            lines.append(f"| {system} | {branch} | {cell['e2e_vs_gt']['n']} | "
                         + " | ".join(parts) + " |")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = M / f"caption_vs_gt_dev_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
