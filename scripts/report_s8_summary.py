"""Tổng hợp S8 W5/W6 f2 từ measurement đã có; không đọc prediction hay DB.

Script nhận rõ baseline cũ và artifact f2 để mọi số trong báo cáo truy ngược được. RQ2 dùng
caption e2e; RQ3 báo gold và parse theo ADR-0036. N-gram/per-class nằm ở artifact riêng.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
CAPTION_METRICS = ("hallucination_rate", "omission_rate", "forbidden_term_rate")
RETRIEVAL_METRICS = ("ndcg@10", "recall@1", "recall@5", "recall@10", "filter_exactness")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caption-old", type=Path, required=True)
    parser.add_argument("--caption-new-all", type=Path, required=True)
    parser.add_argument("--caption-new-annotated", type=Path, required=True)
    parser.add_argument("--retrieval-old", type=Path, required=True)
    parser.add_argument("--retrieval-new-gold", type=Path, required=True)
    parser.add_argument("--retrieval-new-parsed", type=Path, required=True)
    parser.add_argument("--answers-new-gold", type=Path)
    parser.add_argument("--answers-new-parsed", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def caption_extract(payload: dict[str, Any]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for key, summary in payload["summary"].items():
        if not key.endswith("/e2e"):
            continue
        cis = payload["ci"][key]
        extracted[key] = {
            "n": summary["n"],
            **{
                metric: {
                    "estimate": summary[metric],
                    "lower": cis[metric]["lower"],
                    "upper": cis[metric]["upper"],
                }
                for metric in CAPTION_METRICS
            },
        }
    return extracted


def retrieval_extract(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: {
            "n": row["n"],
            **{metric: row[metric] for metric in RETRIEVAL_METRICS},
            "ndcg@10_ci": row["ci_ndcg@10"],
        }
        for key, row in payload["summary"].items()
    }


def answer_extract(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if payload is None:
        return None
    return {
        key: {
            "n": row["n"],
            "unsupported_claim_rate": row["unsupported_claim_rate"],
            "contract_ok": row["contract_ok"],
            "evidence_real": row["evidence_real"],
            "citations_satisfy_filters": row["citations_satisfy_filters"],
        }
        for key, row in payload["summary"].items()
    }


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "caption_old": args.caption_old,
        "caption_new_all": args.caption_new_all,
        "caption_new_annotated": args.caption_new_annotated,
        "retrieval_old": args.retrieval_old,
        "retrieval_new_gold": args.retrieval_new_gold,
        "retrieval_new_parsed": args.retrieval_new_parsed,
    }
    answer_gold = _read(args.answers_new_gold) if args.answers_new_gold else None
    answer_parsed = _read(args.answers_new_parsed) if args.answers_new_parsed else None
    old_retrieval = retrieval_extract(_read(args.retrieval_old))
    new_gold = retrieval_extract(_read(args.retrieval_new_gold))
    deltas = {
        key: {
            metric: new_gold[key][metric] - old_retrieval[key][metric]
            for metric in RETRIEVAL_METRICS
        }
        for key in sorted(set(old_retrieval) & set(new_gold))
    }
    return {
        "scope": "S8 W5/W6 trên f2",
        "sources": {key: str(path) for key, path in paths.items()},
        "git": git_state(ROOT),
        "rq2": {
            "baseline_v1_all": caption_extract(_read(args.caption_old)),
            "f2_all": caption_extract(_read(args.caption_new_all)),
            "f2_annotated": caption_extract(_read(args.caption_new_annotated)),
        },
        "rq3": {
            "baseline_run_b_gold": old_retrieval,
            "f2_gold": new_gold,
            "f2_parsed": retrieval_extract(_read(args.retrieval_new_parsed)),
            "f2_gold_minus_baseline": deltas,
            "answers_f2_gold": answer_extract(answer_gold),
            "answers_f2_parsed": answer_extract(answer_parsed),
        },
    }


def _ci(metric: dict[str, float]) -> str:
    return f"{metric['estimate']:.3f} [{metric['lower']:.3f}, {metric['upper']:.3f}]"


def render(result: dict[str, Any]) -> str:
    lines = [
        "# S8 — W5/W6 trên hệ thống f2",
        "",
        "> Sinh bởi `scripts.report_s8_summary`, chỉ đọc measurement đã khóa. RQ2 LLM là EN; "
        "template VI và bảng per-class/n-gram nằm trong artifact riêng. Baseline RQ2 là ensemble "
        "C v1 (142 recording); baseline RQ3 là corpus run B.",
        "",
        "## RQ2 — caption e2e",
        "",
        "| Tập / nhánh | n | Hallucination [CI 95%] | Omission [CI 95%] | G3 [CI 95%] |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, group in result["rq2"].items():
        for branch, row in group.items():
            lines.append(
                f"| {label} · {branch} | {row['n']} | {_ci(row['hallucination_rate'])} | "
                f"{_ci(row['omission_rate'])} | {_ci(row['forbidden_term_rate'])} |"
            )
    lines += [
        "",
        "## RQ3 — retrieval test",
        "",
        "| Corpus/filter · cấu hình/ngôn ngữ | n | nDCG@10 [CI 95%] | R@1 | R@5 | R@10 | "
        "Filter exactness |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("baseline_run_b_gold", "f2_gold", "f2_parsed"):
        for key, row in result["rq3"][label].items():
            ci = row["ndcg@10_ci"]
            lines.append(
                f"| {label} · {key} | {row['n']} | {row['ndcg@10']:.3f} "
                f"[{ci['lower']:.3f}, {ci['upper']:.3f}] | {row['recall@1']:.3f} | "
                f"{row['recall@5']:.3f} | {row['recall@10']:.3f} | "
                f"{row['filter_exactness']:.3f} |"
            )
    if result["rq3"]["answers_f2_gold"] is not None:
        lines += ["", "## Ràng buộc câu trả lời f2", "",
                  "| Bộ lọc · cấu hình/ngôn ngữ | n | Unsupported-claim | Contract | "
                  "Evidence thật | Trích thỏa lọc |", "|---|---:|---:|---:|---:|---:|"]
        for label in ("answers_f2_gold", "answers_f2_parsed"):
            for key, row in result["rq3"][label].items():
                lines.append(
                    f"| {label} · {key} | {row['n']} | "
                    f"{row['unsupported_claim_rate']:.3f} | {row['contract_ok']}/{row['n']} | "
                    f"{row['evidence_real']}/{row['n']} | "
                    f"{row['citations_satisfy_filters']}/{row['n']} |"
                )
    lines += ["", "## Nguồn", ""]
    lines.extend(f"- `{key}`: `{path}`" for key, path in result["sources"].items())
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    result = build_result(args)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    destination = args.output or ROOT / "docs/measurements" / f"s8_summary_{stamp}.md"
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
