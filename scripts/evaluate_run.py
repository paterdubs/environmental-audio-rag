"""W4.1-4.4 — event-based F1, PSDS-1/2, bootstrap CI theo recording, phân tích lỗi.

    .venv/Scripts/python.exe -m scripts.evaluate_run ml/runs/<sed_run_id>

Nạp `predictions/test.npz` (G2) + `postproc.json` đã đóng băng (H2/sweep_threshold)
— chạy **một lần**, không quay lại sửa θ. Sinh
`docs/measurements/<run_id>_eval.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from ml.evaluation.bootstrap import recording_bootstrap
from ml.evaluation.errors import classify_event_errors
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1, psds_score
from ml.postprocessing import DurationPrior, process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID, validate_postproc_artifact
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]

PSDS_SCENARIOS = {
    # evaluation_protocol.md §3.3 -- đóng băng, không phải suy đoán.
    "psds_1": {"dtc_threshold": 0.7, "gtc_threshold": 0.7, "alpha_ct": 0.0, "alpha_st": 1.0,
               "max_efpr": 100.0},
    "psds_2": {"dtc_threshold": 0.1, "gtc_threshold": 0.1, "cttc_threshold": 0.3,
               "alpha_ct": 0.5, "alpha_st": 1.0, "max_efpr": 100.0},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--postproc", type=Path, default=None)
    return parser.parse_args()


def load_events_by_recording(recording_ids: set[str]) -> dict[str, list[dict[str, object]]]:
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    subset = events[events["recording_id"].isin(recording_ids)]
    grouped: dict[str, list[dict[str, object]]] = {rid: [] for rid in recording_ids}
    for row in subset.itertuples(index=False):
        grouped[str(row.recording_id)].append(
            {"event_label": row.class_id, "onset": row.onset_s, "offset": row.offset_s}
        )
    return grouped


def priors_from_postproc(postproc: dict, class_ids: tuple[str, ...]) -> dict[str, DurationPrior]:
    return {
        class_id: DurationPrior(
            median_w=postproc["per_class"][class_id]["median_w"],
            d_min_s=postproc["per_class"][class_id]["d_min_s"],
            g_max_s=postproc["per_class"][class_id]["g_max_s"],
            n_events=postproc["per_class"][class_id]["n_train_events"],
        )
        for class_id in class_ids
    }


def to_detection_frame(events_by_recording: dict[str, list[dict[str, object]]]) -> pd.DataFrame:
    """`process_recordings` output -> psds_eval's flat filename/onset/offset/
    event_label(+confidence) table."""
    rows = [
        {
            "filename": recording_id,
            "event_label": event["class_id"],
            "onset": event["onset_s"],
            "offset": event["offset_s"],
            "confidence": event["score"],
        }
        for recording_id, events in events_by_recording.items()
        for event in events
    ]
    return pd.DataFrame(rows, columns=["filename", "event_label", "onset", "offset", "confidence"])


def psds_operating_points(
    probabilities: dict[str, object],
    *,
    class_ids: tuple[str, ...],
    priors: dict[str, DurationPrior],
    frame_rate: float,
) -> list[tuple[pd.DataFrame]]:
    """PSDS đo **hiệu năng trên toàn dải operating point**
    (evaluation_protocol.md §3.1) — một θ đã đóng băng (dùng cho event-based
    F1) chỉ là một điểm, không phải dải. Quét cùng lưới ngưỡng dùng ở W3.6
    (`DEFAULT_THRESHOLD_GRID`), áp **đồng nhất mọi lớp** ở mỗi điểm lưới, giữ
    nguyên duration prior đã đóng băng từ train — chỉ ngưỡng thay đổi giữa các
    điểm, đúng tinh thần PSD-ROC quét theo confidence.
    """
    points: list[tuple[pd.DataFrame]] = []
    for theta in DEFAULT_THRESHOLD_GRID:
        events = process_recordings(
            probabilities,
            class_ids=class_ids,
            thresholds=dict.fromkeys(class_ids, theta),
            priors=priors,
            frame_rate=frame_rate,
        )
        frame = to_detection_frame(events).drop(columns=["confidence"])
        if len(frame):
            points.append((frame,))
    return points


def to_reference_frame(events_by_recording: dict[str, list[dict[str, object]]]) -> pd.DataFrame:
    rows = [
        {
            "filename": recording_id,
            "event_label": event["event_label"],
            "onset": event["onset"],
            "offset": event["offset"],
        }
        for recording_id, events in events_by_recording.items()
        for event in events
    ]
    return pd.DataFrame(rows, columns=["filename", "event_label", "onset", "offset"])


def bootstrap_event_f1(
    reference: dict[str, list[dict[str, object]]],
    estimate: dict[str, list[dict[str, object]]],
    class_ids: tuple[str, ...],
) -> dict[str, float]:
    """Bootstrap theo **recording** (không theo event/frame — CLAUDE.md §5).

    `recording_bootstrap` lấy mẫu có hoàn lại trên recording_id; một recording
    được chọn 2 lần trong cùng một mẫu phải đóng góp gấp đôi vào tổng — nếu gộp
    lại theo dict thì trùng khoá sẽ mất bản sao. Gắn hậu tố occurrence để mỗi
    lần xuất hiện là một "file" độc lập trong mắt `sed_eval`, đúng ngữ nghĩa
    "recording này nặng gấp đôi trong mẫu này".
    """
    recording_ids = sorted(reference)

    def statistic(sample: list[str]) -> float:
        ref_sample: dict[str, list[dict[str, object]]] = {}
        est_sample: dict[str, list[dict[str, object]]] = {}
        for occurrence, recording_id in enumerate(sample):
            key = f"{recording_id}#{occurrence}"
            ref_sample[key] = reference.get(recording_id, [])
            est_sample[key] = estimate.get(recording_id, [])
        result = event_based_f1(ref_sample, est_sample, event_label_list=list(class_ids))
        return result["f_measure"]["f_measure"]

    ci = recording_bootstrap(recording_ids, statistic)
    return {"estimate": ci.estimate, "lower": ci.lower, "upper": ci.upper,
            "confidence": ci.confidence, "n_recordings": ci.n_recordings}


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất — không đánh giá run dở dang")

    postproc_path = args.postproc or (args.run_dir / "postproc.json")
    postproc = json.loads(postproc_path.read_text(encoding="utf-8"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    validate_postproc_artifact(postproc, taxonomy=taxonomy)  # từ chối postproc chưa frozen/sai
    class_ids = taxonomy.polyphonic_class_ids
    if postproc["taxonomy_sha256"] != taxonomy.checksum:
        raise SystemExit("postproc.json khoá theo taxonomy khác taxonomy đang dùng")

    test_artifact = load_predictions(
        args.run_dir / "predictions" / "test.npz", expected_class_ids=class_ids
    )
    if test_artifact.split != "test":
        raise SystemExit(f"prediction artifact split={test_artifact.split!r}, cần 'test'")

    probabilities = stack_predictions_by_recording(test_artifact)
    reference = load_events_by_recording(set(probabilities))
    priors = priors_from_postproc(postproc, class_ids)
    thresholds = {class_id: postproc["per_class"][class_id]["theta"] for class_id in class_ids}
    frame_rate = 1.0 / test_artifact.frame_hop_s

    estimate = process_recordings(
        probabilities, class_ids=class_ids, thresholds=thresholds, priors=priors,
        frame_rate=frame_rate,
    )

    event_f1 = event_based_f1(reference, estimate, event_label_list=list(class_ids))
    ci = bootstrap_event_f1(reference, estimate, class_ids)

    metadata = pd.DataFrame(
        {"filename": list(probabilities), "duration": [
            probabilities[rid].shape[0] / frame_rate for rid in probabilities
        ]}
    )
    ground_truth = to_reference_frame(reference)
    operating_points = psds_operating_points(
        probabilities, class_ids=class_ids, priors=priors, frame_rate=frame_rate
    )
    psds_values = {
        name: (
            psds_score(
                ground_truth=ground_truth, metadata=metadata,
                operating_points=operating_points, scenario=scenario,
            )
            if operating_points
            else 0.0
        )
        for name, scenario in PSDS_SCENARIOS.items()
    }

    errors, error_summary = classify_event_errors(reference, estimate)
    error_totals: dict[str, int] = {}
    for counts in error_summary.values():
        for kind, count in counts.items():
            error_totals[kind] = error_totals.get(kind, 0) + count

    result = {
        "run": str(args.run_dir),
        "postproc": str(postproc_path),
        "event_based_f1": event_f1["f_measure"],
        "event_based_f1_per_class": {
            class_id: event_f1["per_class"].get(class_id, {}).get("f_measure", {})
            for class_id in class_ids
        },
        "event_based_f1_bootstrap": ci,
        "psds": psds_values,
        "error_totals": error_totals,
        "n_events_reference": sum(len(v) for v in reference.values()),
        "n_events_estimate": sum(len(v) for v in estimate.values()),
        "n_error_instances": len(errors),
    }
    output_path = args.run_dir / "evaluation.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    report_path = ROOT / "docs" / "measurements" / f"{args.run_dir.name}_eval.md"
    report_path.write_text(_render_report(result), encoding="utf-8")
    print(json.dumps({"evaluation": str(output_path), "report": str(report_path)}, indent=2))


def _render_report(result: dict) -> str:
    f1 = result["event_based_f1"]
    ci = result["event_based_f1_bootstrap"]
    lines = [
        f"# Đánh giá SED — `{Path(result['run']).name}`",
        "",
        f"> Sinh bởi `scripts.evaluate_run {result['run']}`. Test chạy **một lần**, "
        "postproc đã đóng băng trước khi mở test.",
        "",
        "## Event-based F1 (test)",
        "",
        "| Metric | Giá trị |",
        "|---|---:|",
        f"| F1 | {f1.get('f_measure', float('nan')):.4f} |",
        f"| Precision | {f1.get('precision', float('nan')):.4f} |",
        f"| Recall | {f1.get('recall', float('nan')):.4f} |",
        f"| Bootstrap 95% CI (theo recording, n={ci['n_recordings']}) | "
        f"[{ci['lower']:.4f}, {ci['upper']:.4f}] |",
        "",
        "## PSDS",
        "",
        "| Scenario | Giá trị |",
        "|---|---:|",
    ]
    for name, value in result["psds"].items():
        lines.append(f"| {name} | {value:.4f} |")
    lines += [
        "",
        "## Phân tích lỗi (mô tả, không thay thế event-based F1)",
        "",
        "| Loại | Số lượt |",
        "|---|---:|",
    ]
    for kind, count in sorted(result["error_totals"].items()):
        lines.append(f"| {kind} | {count} |")
    lines += [
        "",
        f"Số event tham chiếu: {result['n_events_reference']} · "
        f"dự đoán: {result['n_events_estimate']}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
