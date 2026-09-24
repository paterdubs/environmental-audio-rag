"""Ablation A5 — độ nhạy của duration prior theo percentile (ADR-0003 §3, nợ
kỹ thuật #8: "Percentile 5/50 cho duration prior chưa có cơ sở thực nghiệm").

    .venv/Scripts/python.exe -m scripts.report_duration_prior_ablation ml/runs/<run_id>

`d_min_c` (percentile 5 thời lượng event) và `g_max_c` (percentile 50 khoảng
cách giữa hai event cùng lớp) được ADR-0003 chọn không có cơ sở thực nghiệm.
Script này suy lại duration prior từ **train** với các percentile khác nhau —
dùng thẳng `derive_duration_priors` (không viết lại logic phần trăm vị) — giữ
nguyên θ per-class đã đóng băng trong `postproc.json`, rồi đo event-based F1
trên **test** cho từng lựa chọn.

**Phạm vi có chủ ý thu hẹp**: không quét lại θ cho mỗi tổ hợp percentile (sẽ
là một ablation tốn kém hơn nhiều — 399 lần đánh giá mỗi tổ hợp). Đây là câu
hỏi "giữ nguyên ngưỡng đã học, đổi cách suy duration prior có đổi F1 không",
không phải "percentile tối ưu đồng thời với θ là gì". Nếu F1 gần như không đổi
giữa các percentile, đó là bằng chứng percentile 5/50 không nhạy cảm — không
phải một khiếm khuyết cần vá.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import (
    derive_duration_priors,
    process_recordings,
    stack_predictions_by_recording,
)
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]

D_MIN_PERCENTILE_GRID = (1.0, 5.0, 10.0, 25.0)
G_MAX_PERCENTILE_GRID = (25.0, 50.0, 75.0)
BASELINE_D_MIN_PERCENTILE = 5.0
BASELINE_G_MAX_PERCENTILE = 50.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_train_events(class_ids: tuple[str, ...]) -> dict[str, list[dict[str, object]]]:
    splits = pd.read_csv(ROOT / "data" / "splits" / "datased_polyphonic.csv")
    train_ids = set(splits.loc[splits["split"] == "train", "recording_id"].astype(str))
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    subset = events[events["recording_id"].isin(train_ids)]
    grouped: dict[str, list[dict[str, object]]] = {rid: [] for rid in train_ids}
    for row in subset.itertuples(index=False):
        if row.class_id not in class_ids:
            continue
        grouped[str(row.recording_id)].append(
            {"class_id": row.class_id, "onset_s": row.onset_s, "offset_s": row.offset_s}
        )
    return grouped


def evaluate_test_f1(
    *,
    probabilities: dict[str, object],
    class_ids: tuple[str, ...],
    thresholds: dict[str, float],
    priors: dict[str, object],
    frame_rate: float,
    reference: dict[str, list[dict[str, object]]],
) -> float:
    estimate = process_recordings(
        probabilities, class_ids=class_ids, thresholds=thresholds, priors=priors,
        frame_rate=frame_rate,
    )
    result = event_based_f1(reference, estimate, event_label_list=list(class_ids))
    return float(result["f_measure"]["f_measure"])


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
    train_events = load_train_events(class_ids)

    rows: list[dict[str, object]] = []
    seen: set[tuple[float, float]] = set()
    for d_min_pct in D_MIN_PERCENTILE_GRID:
        key = (d_min_pct, BASELINE_G_MAX_PERCENTILE)
        if key in seen:
            continue
        seen.add(key)
        priors = derive_duration_priors(
            train_events, class_ids=class_ids, frame_rate=frame_rate, source_split="train",
            d_min_percentile=d_min_pct, g_max_percentile=BASELINE_G_MAX_PERCENTILE,
        )
        f1 = evaluate_test_f1(
            probabilities=probabilities, class_ids=class_ids, thresholds=thresholds,
            priors=priors, frame_rate=frame_rate, reference=reference,
        )
        rows.append(
            {
                "sweep": "d_min_percentile",
                "d_min_percentile": d_min_pct,
                "g_max_percentile": BASELINE_G_MAX_PERCENTILE,
                "is_baseline": d_min_pct == BASELINE_D_MIN_PERCENTILE,
                "event_f1": f1,
            }
        )

    for g_max_pct in G_MAX_PERCENTILE_GRID:
        key = (BASELINE_D_MIN_PERCENTILE, g_max_pct)
        if key in seen:
            continue
        seen.add(key)
        priors = derive_duration_priors(
            train_events, class_ids=class_ids, frame_rate=frame_rate, source_split="train",
            d_min_percentile=BASELINE_D_MIN_PERCENTILE, g_max_percentile=g_max_pct,
        )
        f1 = evaluate_test_f1(
            probabilities=probabilities, class_ids=class_ids, thresholds=thresholds,
            priors=priors, frame_rate=frame_rate, reference=reference,
        )
        rows.append(
            {
                "sweep": "g_max_percentile",
                "d_min_percentile": BASELINE_D_MIN_PERCENTILE,
                "g_max_percentile": g_max_pct,
                "is_baseline": g_max_pct == BASELINE_G_MAX_PERCENTILE,
                "event_f1": f1,
            }
        )

    f1_values = [row["event_f1"] for row in rows]
    spread = max(f1_values) - min(f1_values)
    baseline_f1 = next(row["event_f1"] for row in rows if row["is_baseline"])

    output_data = {
        "run": str(args.run_dir),
        "baseline_event_f1": baseline_f1,
        "spread_max_minus_min": spread,
        "rows": rows,
    }

    destination = args.output or (
        ROOT / "docs" / "measurements" / f"{args.run_dir.name}_duration_prior_ablation_A5.md"
    )
    lines = [
        f"# Ablation A5 — percentile duration prior — `{args.run_dir.name}`",
        "",
        f"> Sinh bởi `scripts.report_duration_prior_ablation {args.run_dir}`. θ per-class "
        "giữ nguyên từ `postproc.json` đã đóng băng; chỉ percentile suy `d_min_s`/`g_max_s` "
        "đổi. Không sửa artifact chính thức.",
        "",
        f"Baseline (percentile 5/50, ADR-0003): event-based F1 test = **{baseline_f1:.4f}**",
        "",
        "## Quét percentile `d_min_s` (giữ `g_max_s` ở percentile 50)",
        "",
        "| Percentile d_min | Event F1 | Δ so baseline |",
        "|---:|---:|---:|",
    ]
    for row in rows:
        if row["sweep"] != "d_min_percentile":
            continue
        marker = " (baseline)" if row["is_baseline"] else ""
        lines.append(
            f"| {row['d_min_percentile']:g}{marker} | {row['event_f1']:.4f} | "
            f"{row['event_f1'] - baseline_f1:+.4f} |"
        )
    lines += [
        "",
        "## Quét percentile `g_max_s` (giữ `d_min_s` ở percentile 5)",
        "",
        "| Percentile g_max | Event F1 | Δ so baseline |",
        "|---:|---:|---:|",
    ]
    for row in rows:
        if row["sweep"] != "g_max_percentile":
            continue
        marker = " (baseline)" if row["is_baseline"] else ""
        lines.append(
            f"| {row['g_max_percentile']:g}{marker} | {row['event_f1']:.4f} | "
            f"{row['event_f1'] - baseline_f1:+.4f} |"
        )
    lines += ["", "## Diễn giải", ""]
    if spread < 0.005:
        lines.append(
            f"Khoảng biến thiên F1 giữa mọi percentile đã quét chỉ **{spread:.4f}** — "
            "percentile 5/50 KHÔNG nhạy cảm trong dải đã thử. Chọn 5/50 hay lân cận "
            "không thay đổi kết luận, không cần hiệu chuẩn thêm cho nợ kỹ thuật #8."
        )
    else:
        lines.append(
            f"Khoảng biến thiên F1 giữa các percentile là **{spread:.4f}** — đủ lớn để "
            "percentile ảnh hưởng tới kết quả. Xem bảng trên để biết percentile nào tốt "
            "hơn baseline; **không** tự đổi percentile chính thức chỉ từ một ablation "
            "post-hoc — cần một vòng chọn trên dev nếu muốn thay đổi ADR-0003."
        )
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
