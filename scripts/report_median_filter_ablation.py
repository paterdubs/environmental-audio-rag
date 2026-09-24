"""Ablation A3 — median filter cải thiện event-F1, hay chỉ làm mất event ngắn
(ADR-0003, mục "Evidence cần kiểm lại": "Median filter có cải thiện event-F1
không, hay chỉ làm mất event ngắn như `glass_breaking`?").

    .venv/Scripts/python.exe -m scripts.report_median_filter_ablation ml/runs/<sed_run_id>

So sánh event-based F1 trên **test** giữa hai cấu hình hậu xử lý, giữ nguyên θ
và mọi tham số khác đã đóng băng trong `postproc.json`:

1. **Có lọc** (chính thức) — `median_w` suy từ train, đúng ADR-0003 §3.
2. **Không lọc** — `median_w=1` cho mọi lớp (no-op, xem `_median_filter`
   trong `ml/postprocessing/events.py`), mọi tham số khác giữ nguyên.

Báo cáo tổng hợp **và từng lớp**, sắp theo `d_min_s` tăng dần (lớp ngắn nhất
trước) để trả lời đúng câu hỏi ADR-0003 đặt ra: lớp ngắn/xung có bị mất event vì
lọc median không. **Không sửa `postproc.json` đã đóng băng.**
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording
from scripts.report_threshold_ablation import priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def class_f1(result: dict, class_id: str) -> float | None:
    entry = result["per_class"].get(class_id, {}).get("f_measure", {}).get("f_measure")
    if entry is None or not math.isfinite(entry):
        return None
    return float(entry)


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất — không báo cáo ablation trên run dở dang")

    postproc = json.loads((args.run_dir / "postproc.json").read_text(encoding="utf-8"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    class_ids = taxonomy.polyphonic_class_ids

    artifact = load_predictions(
        args.run_dir / "predictions" / "test.npz", expected_class_ids=class_ids
    )
    if artifact.split != "test":
        raise SystemExit(f"predictions split={artifact.split!r}, cần 'test'")

    probabilities = stack_predictions_by_recording(artifact)
    reference = load_events_by_recording(set(probabilities))
    frame_rate = 1.0 / artifact.frame_hop_s
    thresholds = {
        class_id: float(postproc["per_class"][class_id]["theta"]) for class_id in class_ids
    }

    priors_filtered = priors_from_postproc(postproc, class_ids)
    priors_unfiltered = {
        class_id: replace(prior, median_w=1) for class_id, prior in priors_filtered.items()
    }

    results = {}
    for mode, priors in (("filtered", priors_filtered), ("unfiltered", priors_unfiltered)):
        estimate = process_recordings(
            probabilities, class_ids=class_ids, thresholds=thresholds, priors=priors,
            frame_rate=frame_rate,
        )
        results[mode] = event_based_f1(reference, estimate, event_label_list=list(class_ids))

    overall = {mode: results[mode]["f_measure"]["f_measure"] for mode in ("filtered", "unfiltered")}
    per_class = {
        class_id: {mode: class_f1(results[mode], class_id) for mode in ("filtered", "unfiltered")}
        for class_id in class_ids
    }
    ordered_classes = sorted(class_ids, key=lambda cid: priors_filtered[cid].d_min_s)

    output_data = {
        "run": str(args.run_dir),
        "overall": overall,
        "overall_delta_filtered_minus_unfiltered": overall["filtered"] - overall["unfiltered"],
        "per_class": per_class,
        "per_class_d_min_s": {cid: priors_filtered[cid].d_min_s for cid in class_ids},
        "ordered_by_d_min_s": ordered_classes,
    }

    destination = args.output or (
        ROOT / "docs" / "measurements" / f"{args.run_dir.name}_median_filter_ablation_A3.md"
    )
    lines = [
        f"# Ablation A3 — median filter — `{args.run_dir.name}`",
        "",
        f"> Sinh bởi `scripts.report_median_filter_ablation {args.run_dir}`. θ và "
        "duration prior khác giữ nguyên từ `postproc.json` đã đóng băng; chỉ "
        "`median_w` đổi (1 = không lọc). Không sửa artifact chính thức.",
        "",
        "⚠️ Nếu run này là nhánh A (scratch, dò đường): hầu hết lớp có F1 gần 0 vì "
        "model gần như chưa học được — kết luận từ ablation này **chưa đại diện**, "
        "chạy lại trên nhánh B/C (đã pretrain) trước khi kết luận trong báo cáo cuối.",
        "",
        "## Tổng hợp (test, đa lớp đồng thời)",
        "",
        "| Cấu hình | Event F1 |",
        "|---|---:|",
        f"| Có lọc (chính thức) | {overall['filtered']:.4f} |",
        f"| Không lọc (median_w=1) | {overall['unfiltered']:.4f} |",
        f"| Δ (có lọc − không lọc) | "
        f"{output_data['overall_delta_filtered_minus_unfiltered']:+.4f} |",
        "",
        "## Từng lớp, sắp theo d_min_s tăng dần (lớp ngắn/xung trước)",
        "",
        "| class_id | d_min_s (train) | F1 có lọc | F1 không lọc | Δ |",
        "|---|---:|---:|---:|---:|",
    ]
    def fmt(value: float | None) -> str:
        return f"{value:.4f}" if value is not None else "N/A"

    for class_id in ordered_classes:
        f_filtered = per_class[class_id]["filtered"]
        f_unfiltered = per_class[class_id]["unfiltered"]
        delta = (
            f_filtered - f_unfiltered
            if f_filtered is not None and f_unfiltered is not None
            else None
        )
        lines.append(
            f"| {class_id} | {priors_filtered[class_id].d_min_s:.3f} | {fmt(f_filtered)} | "
            f"{fmt(f_unfiltered)} | {fmt(delta)} |"
        )
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
