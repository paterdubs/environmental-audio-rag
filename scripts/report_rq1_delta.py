"""RQ1 — so sánh ba nhánh SED từ `evaluation.json` đã có (không tính lại metric).

    .venv/Scripts/python.exe -m scripts.report_rq1_delta \
        ml/runs/<run_id_A> ml/runs/<run_id_B> ml/runs/<run_id_C>

In lại đúng số đã ghi trong `evaluation.json`/`manifest.json` của từng run, tính
Δ = C − B (RQ1: đóng góp của DataSEC) và Δ = C − A (tổng lợi ích pretraining,
KHÔNG phải câu trả lời RQ1 — ADR-0002). Sinh `docs/measurements/rq1_delta_<ngày>.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_branch(run_dir: Path, *, expected_weight_source_prefix: str | None = None) -> dict:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất — không đưa vào so sánh RQ1")
    evaluation_path = run_dir / "evaluation.json"
    if not evaluation_path.exists():
        raise SystemExit(f"{run_dir} chưa có evaluation.json — chạy scripts.evaluate_run trước")
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    weight_source = str(manifest["config"].get("weight_source", ""))
    prefix_ok = not expected_weight_source_prefix or weight_source.startswith(
        expected_weight_source_prefix
    )
    if not prefix_ok:
        raise SystemExit(
            f"{run_dir} có weight_source={weight_source!r}, "
            f"cần bắt đầu bằng {expected_weight_source_prefix!r} — sai thứ tự tham số?"
        )
    return {
        "run_id": run_dir.name,
        "weight_source": weight_source,
        "git_dirty": manifest["git"]["dirty"],
        "event_f1": evaluation["event_based_f1"]["f_measure"],
        "event_f1_ci": evaluation["event_based_f1_bootstrap"],
        "psds_1": evaluation["psds"]["psds_1"],
        "psds_2": evaluation["psds"]["psds_2"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_a", type=Path, help="Nhánh A (scratch)")
    parser.add_argument("run_b", type=Path, help="Nhánh B (AudioSet -> DataSED)")
    parser.add_argument("run_c", type=Path, help="Nhánh C (AudioSet -> DataSEC -> DataSED)")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    branch_a = load_branch(args.run_a, expected_weight_source_prefix="scratch")
    branch_b = load_branch(args.run_b, expected_weight_source_prefix="audioset")
    branch_c = load_branch(args.run_c, expected_weight_source_prefix="datasec")

    delta_c_minus_b = {
        "event_f1": branch_c["event_f1"] - branch_b["event_f1"],
        "psds_1": branch_c["psds_1"] - branch_b["psds_1"],
        "psds_2": branch_c["psds_2"] - branch_b["psds_2"],
    }
    delta_c_minus_a = {
        "event_f1": branch_c["event_f1"] - branch_a["event_f1"],
        "psds_1": branch_c["psds_1"] - branch_a["psds_1"],
        "psds_2": branch_c["psds_2"] - branch_a["psds_2"],
    }

    any_dirty = any(b["git_dirty"] for b in (branch_a, branch_b, branch_c))
    result = {
        "branches": {"A": branch_a, "B": branch_b, "C": branch_c},
        "delta_c_minus_b_RQ1": delta_c_minus_b,
        "delta_c_minus_a_total_pretraining_benefit": delta_c_minus_a,
        "any_run_dirty": any_dirty,
        "locked": False,  # 1 seed, chưa qua D2-style seed check -- không tự đặt True
    }

    destination = args.output or (
        ROOT / "docs" / "measurements"
        / f"rq1_delta_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    lines = [
        "# RQ1 — so sánh ba nhánh SED (C − B, C − A)",
        "",
        f"> Sinh bởi `scripts.report_rq1_delta {args.run_a} {args.run_b} {args.run_c}`. "
        "Không tính lại metric, chỉ đọc `evaluation.json` đã có.",
        "",
        "⚠️ **Số thăm dò, chưa khoá chính thức** — 1 seed mỗi nhánh, chưa qua D2-style "
        "seed-reproducibility check. Không trích dẫn như kết luận cuối của RQ1.",
        "",
    ]
    if any_dirty:
        lines.append(
            "⚠️ **Ít nhất một run có `git.dirty=true`** — số dưới đây là thăm dò, "
            "chạy lại trên tree sạch trước khi khoá chính thức."
        )
        lines.append("")

    lines += [
        "## Ba nhánh",
        "",
        "| | Nhánh A (scratch) | Nhánh B (AudioSet) | Nhánh C (AudioSet→DataSEC) |",
        "|---|---:|---:|---:|",
        f"| run_id | `{branch_a['run_id']}` | `{branch_b['run_id']}` | `{branch_c['run_id']}` |",
        f"| event-based F1 | {branch_a['event_f1']:.4f} | {branch_b['event_f1']:.4f} | "
        f"{branch_c['event_f1']:.4f} |",
        f"| PSDS-1 | {branch_a['psds_1']:.4f} | {branch_b['psds_1']:.4f} | "
        f"{branch_c['psds_1']:.4f} |",
        f"| PSDS-2 | {branch_a['psds_2']:.4f} | {branch_b['psds_2']:.4f} | "
        f"{branch_c['psds_2']:.4f} |",
        f"| git.dirty | {branch_a['git_dirty']} | {branch_b['git_dirty']} | "
        f"{branch_c['git_dirty']} |",
        "",
        "## Δ = C − B — **câu trả lời RQ1** (đóng góp riêng của pretraining DataSEC)",
        "",
        "| Metric | Δ |",
        "|---|---:|",
        f"| event-based F1 | {delta_c_minus_b['event_f1']:+.4f} |",
        f"| PSDS-1 | {delta_c_minus_b['psds_1']:+.4f} |",
        f"| PSDS-2 | {delta_c_minus_b['psds_2']:+.4f} |",
        "",
        "## Δ = C − A — tổng lợi ích pretraining (KHÔNG phải RQ1, ADR-0002)",
        "",
        "| Metric | Δ |",
        "|---|---:|",
        f"| event-based F1 | {delta_c_minus_a['event_f1']:+.4f} |",
        f"| PSDS-1 | {delta_c_minus_a['psds_1']:+.4f} |",
        f"| PSDS-2 | {delta_c_minus_a['psds_2']:+.4f} |",
    ]
    destination.write_text("\n".join(lines), encoding="utf-8")
    (destination.with_suffix(".json")).write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
