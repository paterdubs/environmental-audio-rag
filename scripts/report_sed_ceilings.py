"""Chẩn đoán trần event-F1 của SED trên dev — đo trước khi chọn hướng cải thiện.

    .venv/Scripts/python.exe -m scripts.report_sed_ceilings [--run ml/runs/<run>]

Ba câu hỏi, đều trả lời trên **dev hoặc chỉ ground truth** (không chạm test):

1. **Trần do độ phân giải thời gian.** Một model *hoàn hảo* nhưng chỉ ra quyết định theo
   khối k frame (CNN14 trong repo: 1000 frame → 15 khối ≈ 0.64 s) đạt event-F1 bao nhiêu?
   Mô phỏng: khối bật khi ground truth phủ ≥ 50% khối (làm tròn về biên gần nhất — cận trên).
2. **Trần do người gán nhãn.** Các cặp recording giống từng byte được chú giải hai lần độc
   lập (`report_annotation_consistency`): event-F1 của chú giải này so với chú giải kia.
3. **Phân rã lỗi của hệ thống hiện tại** (dev, in-sample vì hậu xử lý chọn trên dev):
   bao nhiêu event khớp collar, bao nhiêu chồng đúng lớp nhưng lệch biên, bao nhiêu bị bỏ
   sót; kèm event-F1 chỉ onset / chỉ offset và segment-based F1 1 s để thấy lỗi nằm ở đâu.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.errors import classify_event_errors
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1, event_counts_per_recording
from ml.postprocessing import process_recordings
from ml.postprocessing.calibration import priors_from_postproc, stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_annotation_consistency import identical_pairs

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "docs" / "measurements"
FRAME_RATE = 100.0
BLOCKS = (1, 4, 8, 16, 32, 64, 128)  # frame @ 100 fps: 10 ms … 1.28 s
DEFAULT_RUN = ROOT / "ml/runs/sed_ensemble_C_clean_20260925T045631Z"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--postproc", default="postproc_cv.json")
    return parser.parse_args()


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    recordings = pd.read_csv(ROOT / "data/manifests/datased_recordings.csv")
    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    events = pd.read_csv(ROOT / "data/annotations/datased_polyphonic_events.csv")
    return recordings.merge(splits[["recording_id", "split"]], on="recording_id"), events


def reference_events(events: pd.DataFrame, recording_ids: list[str]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {rid: [] for rid in recording_ids}
    for row in events[events["recording_id"].isin(recording_ids)].itertuples(index=False):
        grouped[str(row.recording_id)].append(
            {"event_label": row.class_id, "onset": float(row.onset_s),
             "offset": float(row.offset_s)})
    return grouped


def ground_truth_frames(ref: list[dict], duration_s: float, class_ids: tuple[str, ...]
                        ) -> np.ndarray:
    """Cùng quy tắc làm tròn với `SedFeatureDataset` (floor onset, ceil offset)."""
    frames = math.ceil(duration_s * FRAME_RATE)
    index = {class_id: i for i, class_id in enumerate(class_ids)}
    target = np.zeros((frames, len(class_ids)), dtype=np.float32)
    for event in ref:
        onset = math.floor(event["onset"] * FRAME_RATE)
        offset = max(onset + 1, math.ceil(event["offset"] * FRAME_RATE))
        target[onset:offset, index[event["event_label"]]] = 1.0
    return target


def block_decisions(target: np.ndarray, block: int) -> np.ndarray:
    """Model hoàn hảo ở độ phân giải `block` frame: khối bật khi GT phủ ≥ 50% khối."""
    frames = target.shape[0]
    padded = np.zeros((math.ceil(frames / block) * block, target.shape[1]), dtype=np.float32)
    padded[:frames] = target
    coverage = padded.reshape(-1, block, target.shape[1]).mean(axis=1)
    return np.repeat(coverage >= 0.5, block, axis=0)[:frames]


def frames_to_events(active: np.ndarray, class_ids: tuple[str, ...]) -> list[dict]:
    rows = []
    for index, class_id in enumerate(class_ids):
        padded = np.pad(active[:, index].astype(np.int8), (1, 1))
        changes = np.diff(padded)
        for start, stop in zip(np.flatnonzero(changes == 1), np.flatnonzero(changes == -1),
                               strict=True):
            rows.append({"event_label": class_id, "onset": start / FRAME_RATE,
                         "offset": stop / FRAME_RATE})
    return rows


def f1(reference: dict, estimate: dict, class_ids: tuple[str, ...], **kwargs) -> float:
    return float(event_based_f1(reference, estimate, event_label_list=list(class_ids),
                                **kwargs)["f_measure"]["f_measure"])


def resolution_ceiling(reference: dict, durations: dict, class_ids: tuple[str, ...]) -> list:
    rows = []
    for block in BLOCKS:
        estimate = {rid: frames_to_events(block_decisions(
            ground_truth_frames(ref, durations[rid], class_ids), block), class_ids)
            for rid, ref in reference.items()}
        rows.append({"block_frames": block, "block_s": block / FRAME_RATE,
                     "event_f1": f1(reference, estimate, class_ids),
                     "event_f1_collar_1s": f1(reference, estimate, class_ids, t_collar=1.0)})
    return rows


def human_agreement(recordings: pd.DataFrame, events: pd.DataFrame,
                    class_ids: tuple[str, ...]) -> dict:
    """Event-F1 giữa hai lần chú giải cùng một audio, trung bình hai chiều (ref↔est)."""
    pairs = identical_pairs(recordings)
    result = {"pairs": [list(pair) for pair in pairs]}
    for collar in (0.2, 1.0):
        scores = []
        for left, right in ((0, 1), (1, 0)):
            reference = {f"pair{i}": reference_events(events, [pair[left]])[pair[left]]
                         for i, pair in enumerate(pairs)}
            estimate = {f"pair{i}": reference_events(events, [pair[right]])[pair[right]]
                        for i, pair in enumerate(pairs)}
            scores.append(f1(reference, estimate, class_ids, t_collar=collar))
        result[f"event_f1_collar_{collar:g}s"] = sum(scores) / 2
    return result


def segment_f1(reference: dict, estimate: dict, class_ids: tuple[str, ...]) -> float:
    import sed_eval

    metric = sed_eval.sound_event.SegmentBasedMetrics(list(class_ids), time_resolution=1.0)
    for rid in sorted(set(reference) | set(estimate)):
        ref = [{**e, "filename": rid} for e in reference.get(rid, [])]
        est = [{**e, "filename": rid, "event_label": e.get("event_label", e.get("class_id"))}
               for e in estimate.get(rid, [])]
        metric.evaluate(reference_event_list=ref, estimated_event_list=est)
    return float(metric.results()["overall"]["f_measure"]["f_measure"])


def system_decomposition(run: Path, postproc_name: str, reference: dict,
                         class_ids: tuple[str, ...]) -> dict:
    postproc = json.loads((run / postproc_name).read_text(encoding="utf-8"))
    artifact = load_predictions(run / "predictions/dev.npz", expected_class_ids=class_ids)
    probabilities = stack_predictions_by_recording(artifact)
    thresholds = {c: postproc["per_class"][c]["theta"] for c in class_ids}
    estimate = process_recordings(
        probabilities, class_ids=class_ids, thresholds=thresholds,
        priors=priors_from_postproc(postproc, class_ids),
        frame_rate=1.0 / artifact.frame_hop_s)
    counts = event_counts_per_recording(reference, estimate, event_label_list=list(class_ids))
    n_ref, n_sys, n_tp = (sum(values) for values in zip(*counts.values(), strict=True))
    _, summary = classify_event_errors(reference, estimate)
    deletions = sum(errors["deletion"] for errors in summary.values())
    return {
        "run": run.name, "postproc": postproc_name, "n_reference": n_ref,
        "n_estimate": n_sys, "n_collar_match": n_tp,
        "n_overlap_but_boundary_miss": n_ref - deletions - n_tp, "n_deleted": deletions,
        "event_f1": f1(reference, estimate, class_ids),
        "event_f1_onset_only": f1(reference, estimate, class_ids, evaluate_offset=False),
        "event_f1_offset_only": f1(reference, estimate, class_ids, evaluate_onset=False),
        "segment_f1_1s": segment_f1(reference, estimate, class_ids),
    }


def render(result: dict) -> str:
    system = result["system"]
    human = result["human_agreement"]
    lines = [
        "# Trần event-F1 của SED — chẩn đoán trên dev", "",
        "> Sinh bởi `scripts.report_sed_ceilings`. Chỉ dev + ground truth; không chạm test. "
        "Event-F1 = `sed_eval`, collar onset 0.2 s, offset max(0.2 s, 20% độ dài) như protocol.",
        "", "## 1. Trần do độ phân giải (model hoàn hảo, quyết định theo khối)", "",
        "| Khối | Độ dài | Event-F1 (collar 0.2 s) | Event-F1 (collar 1 s) |",
        "|---:|---:|---:|---:|"]
    lines += [f"| {r['block_frames']} | {r['block_s']:.2f} s | {r['event_f1']:.4f} "
              f"| {r['event_f1_collar_1s']:.4f} |" for r in result["resolution_ceiling"]]
    lines += ["", "CNN14 trong repo ra quyết định theo khối ≈ 0.64 s (1000 frame → 15 khối; "
              "ADR-0014). Mô phỏng làm tròn biên về khối gần nhất nên là **cận trên**.", "",
              "## 2. Trần do người gán nhãn (cặp recording giống từng byte)", "",
              f"{len(human['pairs'])} cặp, trung bình hai chiều: event-F1 collar 0.2 s "
              f"**{human['event_f1_collar_0.2s']:.4f}**, collar 1 s "
              f"{human['event_f1_collar_1s']:.4f}. Cỡ mẫu nhỏ — tín hiệu, không phải nghiên "
              "cứu agreement.", "",
              f"## 3. Phân rã lỗi hệ thống hiện tại (`{system['run']}`, dev, in-sample)", "",
              "| Hạng mục | Số event |", "|---|---:|",
              f"| Event tham chiếu | {system['n_reference']} |",
              f"| Khớp collar (TP) | {system['n_collar_match']} |",
              f"| Chồng đúng lớp nhưng lệch biên | {system['n_overlap_but_boundary_miss']} |",
              f"| Bỏ sót (không dự đoán nào chồng đúng lớp) | {system['n_deleted']} |",
              f"| Event dự đoán | {system['n_estimate']} |", "",
              "| Metric | Giá trị |", "|---|---:|",
              f"| Event-F1 (onset + offset) | {system['event_f1']:.4f} |",
              f"| Event-F1 chỉ onset | {system['event_f1_onset_only']:.4f} |",
              f"| Event-F1 chỉ offset | {system['event_f1_offset_only']:.4f} |",
              f"| Segment-based F1 (1 s) | {system['segment_f1_1s']:.4f} |"]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    recordings, events = load_tables()
    dev = recordings[recordings["split"] == "validation"]
    reference = reference_events(events, dev["recording_id"].tolist())
    durations = dict(zip(dev["recording_id"], dev["duration_s"], strict=True))
    result = {
        "git": git_state(ROOT),
        "resolution_ceiling": resolution_ceiling(reference, durations, class_ids),
        "human_agreement": human_agreement(recordings, events, class_ids),
        "system": system_decomposition(args.run, args.postproc, reference, class_ids),
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = MEASUREMENTS / f"sed_ceilings_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
