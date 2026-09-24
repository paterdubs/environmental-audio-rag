"""I7 — bằng chứng biến thiên giữa 2 seed, so với Δ RQ1 (C − B).

    .venv/Scripts/python.exe -m scripts.report_seed_variance \
        ml/runs/<run_b_seed0> ml/runs/<run_b_seed1> \
        ml/runs/<run_c_seed0> ml/runs/<run_c_seed1>

Đọc `evaluation.json` đã có sẵn của 2 seed cho **mỗi** nhánh B và C (không tính
lại metric), đo độ biến thiên giữa 2 seed |seed0 − seed1| trên từng metric, rồi
so với |Δ = C − B| (RQ1, seed0, đã báo trong `rq1_delta_<ngày>.md`). Nếu |Δ|
không lớn hơn rõ rệt độ biến thiên seed đã đo được ở cả hai nhánh, **không thể
khẳng định Δ là tín hiệu thật** — chỉ báo cáo đúng như vậy, không tự diễn giải
thành kết luận có lợi.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("event_f1", "psds_1", "psds_2")


def load_metrics(run_dir: Path) -> dict[str, float]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất — không đưa vào so sánh seed")
    evaluation_path = run_dir / "evaluation.json"
    if not evaluation_path.exists():
        raise SystemExit(f"{run_dir} chưa có evaluation.json — chạy scripts.evaluate_run trước")
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    return {
        "event_f1": float(evaluation["event_based_f1"]["f_measure"]),
        "psds_1": float(evaluation["psds"]["psds_1"]),
        "psds_2": float(evaluation["psds"]["psds_2"]),
    }


def seed_variance(seed0: dict[str, float], seed1: dict[str, float]) -> dict[str, float]:
    return {metric: abs(seed0[metric] - seed1[metric]) for metric in METRICS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_b_seed0", type=Path)
    parser.add_argument("run_b_seed1", type=Path)
    parser.add_argument("run_c_seed0", type=Path)
    parser.add_argument("run_c_seed1", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    b_seed0 = load_metrics(args.run_b_seed0)
    b_seed1 = load_metrics(args.run_b_seed1)
    c_seed0 = load_metrics(args.run_c_seed0)
    c_seed1 = load_metrics(args.run_c_seed1)

    variance_b = seed_variance(b_seed0, b_seed1)
    variance_c = seed_variance(c_seed0, c_seed1)
    delta_rq1 = {metric: c_seed0[metric] - b_seed0[metric] for metric in METRICS}
    max_variance = {
        metric: max(variance_b[metric], variance_c[metric]) for metric in METRICS
    }
    distinguishable = {
        metric: abs(delta_rq1[metric]) > max_variance[metric] for metric in METRICS
    }
    # Tỷ lệ |Δ| / biến thiên seed lớn nhất -- 1 test qua/rớt nhị phân không nói
    # được PSDS-2 (margin ~10%) và event-F1 (margin ~700%) khác nhau bao nhiêu.
    margin_ratio = {
        metric: (
            abs(delta_rq1[metric]) / max_variance[metric]
            if max_variance[metric]
            else float("inf")
        )
        for metric in METRICS
    }

    result = {
        "run_b_seed0": str(args.run_b_seed0),
        "run_b_seed1": str(args.run_b_seed1),
        "run_c_seed0": str(args.run_c_seed0),
        "run_c_seed1": str(args.run_c_seed1),
        "b_seed0": b_seed0,
        "b_seed1": b_seed1,
        "c_seed0": c_seed0,
        "c_seed1": c_seed1,
        "seed_variance_b": variance_b,
        "seed_variance_c": variance_c,
        "delta_rq1_c_minus_b_seed0": delta_rq1,
        "delta_exceeds_seed_variance": distinguishable,
        "margin_ratio_delta_over_max_seed_variance": margin_ratio,
    }

    destination = args.output or (
        ROOT / "docs" / "measurements" / "seed_variance_vs_rq1_delta.md"
    )
    labels = {"event_f1": "event-based F1", "psds_1": "PSDS-1", "psds_2": "PSDS-2"}
    lines = [
        "# I7 — biến thiên giữa 2 seed, so với Δ RQ1 (C − B)",
        "",
        "> Sinh bởi `scripts.report_seed_variance`. Không tính lại metric, chỉ đọc "
        "`evaluation.json` đã có của mỗi seed.",
        "",
        "## Giá trị theo seed",
        "",
        "| Metric | B seed0 | B seed1 | C seed0 | C seed1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        lines.append(
            f"| {labels[metric]} | {b_seed0[metric]:.4f} | {b_seed1[metric]:.4f} | "
            f"{c_seed0[metric]:.4f} | {c_seed1[metric]:.4f} |"
        )
    lines += [
        "",
        "## Độ biến thiên seed so với Δ RQ1",
        "",
        "| Metric | Biến thiên seed B | Biến thiên seed C | \\|Δ RQ1\\| (C−B, seed0) | "
        "Tỷ lệ \\|Δ\\|/biến thiên lớn nhất | Vượt biến thiên? |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for metric in METRICS:
        mark = "✅ có" if distinguishable[metric] else "⚠️ KHÔNG"
        lines.append(
            f"| {labels[metric]} | {variance_b[metric]:.4f} | {variance_c[metric]:.4f} | "
            f"{abs(delta_rq1[metric]):.4f} | {margin_ratio[metric]:.2f}× | {mark} |"
        )
    lines += ["", "## Diễn giải"]
    for metric in METRICS:
        ratio = margin_ratio[metric]
        if not distinguishable[metric]:
            lines.append(
                f"- **{labels[metric]}**: Δ RQ1 **không** lớn hơn biến thiên seed — "
                "**không thể khẳng định** đây là tín hiệu thật thay vì nhiễu giữa các lần "
                "chạy. Phải ghi vào Hạn chế của báo cáo cuối, không diễn giải như kết luận."
            )
        elif ratio < 1.5:
            lines.append(
                f"- **{labels[metric]}**: Δ RQ1 vượt biến thiên seed nhưng chỉ **{ratio:.2f}×**"
                " — biên rất mỏng (~"
                f"{(ratio - 1) * 100:.0f}%), không đủ chắc để gọi là tín hiệu rõ ràng với "
                "chỉ 2 seed/nhánh. Báo cáo cả hai khả năng, không chọn diễn giải có lợi hơn."
            )
        else:
            lines.append(
                f"- **{labels[metric]}**: Δ RQ1 vượt biến thiên seed rõ rệt (**{ratio:.2f}×**)"
                " — có thể coi là tín hiệu, dù vẫn chỉ 2 seed/nhánh."
            )
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
