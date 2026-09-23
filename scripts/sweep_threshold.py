"""W3.5-3.7 — suy duration prior từ train, quét θ trên dev, đóng băng `postproc.json`.

    .venv/Scripts/python.exe -m scripts.sweep_threshold ml/runs/<sed_run_id>

Nạp `predictions/dev.npz` đã có sẵn (G2) — **không train lại, không chạy inference
lại**. Chạy cả hai chế độ threshold (global, per-class — ablation A2,
evaluation_protocol.md §2.4) và đóng băng chế độ **per-class** làm `postproc.json`
chính thức (kỳ vọng tốt hơn theo §2.4; nếu dev→test tụt mạnh hơn global thì đó là
dấu hiệu overfit dev, ghi vào Hạn chế — không tự đổi lại đây).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import (
    build_postproc_artifact,
    derive_duration_priors,
    stack_predictions_by_recording,
    sweep_global_threshold,
    sweep_per_class_thresholds,
    write_postproc_json,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))


def load_events_by_recording(recording_ids: set[str]) -> dict[str, list[dict[str, object]]]:
    """Đọc y hệt nguồn `scripts/train_sed.py` dùng để tạo target — không suy lại
    từ frame-level target đã lượng tử hoá, tránh mất độ chính xác onset/offset."""
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    subset = events[events["recording_id"].isin(recording_ids)]
    grouped: dict[str, list[dict[str, object]]] = {rid: [] for rid in recording_ids}
    for row in subset.itertuples(index=False):
        grouped[str(row.recording_id)].append(
            {"event_label": row.class_id, "onset": row.onset_s, "offset": row.offset_s}
        )
    return grouped


def _finite_or_zero(score: float) -> float:
    """`event_based_f1` trả NaN khi một lớp có 0 event tham chiếu **và** 0 dự
    đoán ở một ngưỡng ứng viên (ví dụ θ quá cao). `sweep_per_class_thresholds`
    coi NaN là lỗi (đúng đắn — NaN từ chính logic của nó thường là bug), nhưng
    NaN ở đây là kết quả hợp lệ của một θ tệ. Quy về 0.0: "không tách được lớp
    này ở ngưỡng này" phải thua các ngưỡng làm được, không được làm sweep vỡ."""
    return 0.0 if not math.isfinite(score) else score


def build_score_functions(
    dev_reference: dict[str, list[dict[str, object]]], class_ids: tuple[str, ...]
):
    def global_score(events: dict[str, list[dict[str, object]]]) -> float:
        result = event_based_f1(dev_reference, events, event_label_list=list(class_ids))
        return _finite_or_zero(result["f_measure"]["f_measure"])

    def class_score(events: dict[str, list[dict[str, object]]], class_id: str) -> float:
        reference = {
            recording_id: [e for e in items if e["event_label"] == class_id]
            for recording_id, items in dev_reference.items()
        }
        estimate = {
            recording_id: [e for e in items if e["event_label"] == class_id]
            for recording_id, items in events.items()
        }
        result = event_based_f1(reference, estimate, event_label_list=[class_id])
        return _finite_or_zero(result["f_measure"]["f_measure"])

    return global_score, class_score


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    manifest = load_manifest(args.run_dir)
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất — không quét threshold trên run dở dang")

    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids

    dev_path = args.run_dir / "predictions" / "dev.npz"
    dev_artifact = load_predictions(dev_path, expected_class_ids=class_ids)
    dev_probabilities = stack_predictions_by_recording(dev_artifact)
    dev_reference = load_events_by_recording(set(dev_probabilities))

    splits = pd.read_csv(ROOT / "data" / "splits" / "datased_polyphonic.csv")
    train_ids = set(splits.loc[splits["split"] == "train", "recording_id"].astype(str))
    train_events = load_events_by_recording(train_ids)
    priors = derive_duration_priors(
        train_events, class_ids=class_ids, frame_rate=1.0 / dev_artifact.frame_hop_s,
        source_split="train", taxonomy=taxonomy,
    )

    frame_rate = 1.0 / dev_artifact.frame_hop_s
    global_score, class_score = build_score_functions(dev_reference, class_ids)

    global_theta, global_curve = sweep_global_threshold(
        dev_probabilities, class_ids=class_ids, priors=priors, frame_rate=frame_rate,
        score_fn=global_score, split="dev", taxonomy=taxonomy,
    )
    per_class_thetas, per_class_curves = sweep_per_class_thresholds(
        dev_probabilities, class_ids=class_ids, priors=priors, frame_rate=frame_rate,
        score_fn=class_score, split="dev", taxonomy=taxonomy,
    )

    ablation = {
        "global": {"theta": global_theta, "dev_f1": global_curve[global_theta]},
        "per_class": {
            "thetas": per_class_thetas,
            "dev_f1_at_theta": {
                class_id: per_class_curves[class_id][theta]
                for class_id, theta in per_class_thetas.items()
            },
        },
    }

    metrics = json.loads((args.run_dir / "metrics.json").read_text(encoding="utf-8"))
    postproc = build_postproc_artifact(
        class_ids=class_ids,
        thresholds=per_class_thetas,
        priors=priors,
        taxonomy_sha256=taxonomy.checksum,
        split_sha256=manifest["split_sha256"],
        data_manifest_sha256=manifest["data_manifest_sha256"],
        dev_predictions_sha256=metrics["dev_predictions_sha256"],
        threshold_mode="per_class",
        taxonomy=taxonomy,
    )

    output = args.output or (args.run_dir / "postproc.json")
    write_postproc_json(output, postproc, taxonomy=taxonomy)
    ablation_path = args.run_dir / "threshold_ablation.json"
    ablation_path.write_text(json.dumps(ablation, indent=2), encoding="utf-8")
    print(json.dumps({"postproc": str(output), "ablation": str(ablation_path)}, indent=2))


if __name__ == "__main__":
    main()
