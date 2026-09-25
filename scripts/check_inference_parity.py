"""Nghiệm thu 7.1 (ADR-0029 §2): hệ thống phục vụ có tái tạo đúng hệ thống đã đo không.

    .venv/Scripts/python.exe -m scripts.check_inference_parity [--limit N] [--device cuda]

Ba tầng, trên recording **test** DataSED (chỉ so với output đã đóng băng — không đánh giá
lại, không chọn gì):
1. Đặc trưng: WAV → `served_feature` so với file `.npy` đã trích (phải trùng từng phần tử).
2. Xác suất: `ServedSed.probabilities` trên đặc trưng đã lưu so với `predictions/test.npz` của
   ensemble (sai lệch do fp16/cuDNN được đo, không giả định bằng 0).
3. Event: `ServedSed.events` so với event từ xác suất đã đóng băng + cùng postproc.
4. Tái tạo đúng batch: batch test đầu tiên của từng checkpoint, dựng như lúc dump dự đoán
   (`SedFeatureDataset`, batch 24) — logit phải trùng từng bit. Tầng này tách lỗi pipeline
   khỏi nhiễu fp16 do phục vụ từng recording riêng (thành phần batch khác).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.datasets.features import SedFeatureDataset
from ml.evaluation.predictions import load_predictions
from ml.inference.pipeline import served_feature
from ml.inference.sed import ServedSed
from ml.postprocessing import stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
ENSEMBLE = ROOT / "ml/runs/sed_ensemble_C_clean_20260925T045631Z"
POSTPROC = "postproc_cv.json"
TRAIN_BATCH = 24  # batch of the loaders that dumped predictions/test.npz (ADR-0020, C2)
AUDIO_ROOT = ROOT / "data/raw/datased/extracted"
FEATURE_ROOT = ROOT / "data/features/datased/logmel_panns_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def feature_paths() -> dict[str, tuple[Path, Path]]:
    with (ROOT / "data/manifests/datased_logmel_panns_v1.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {Path(r["audio_relative_path"]).stem: (AUDIO_ROOT / r["audio_relative_path"],
                                                  FEATURE_ROOT / r["feature_relative_path"])
            for r in rows}


def batch_reproduction(sed: ServedSed, taxonomy) -> dict[str, float]:
    """Max |Δlogit| per member on the first test batch, rebuilt exactly as when dumped."""
    manifests = ROOT / "data/manifests"
    recordings = pd.read_csv(manifests / "datased_recordings.csv").drop(columns=["frames"])
    features = pd.read_csv(manifests / "datased_logmel_panns_v1.csv")
    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    joined = recordings.merge(features[["file_id", "feature_relative_path", "frames"]],
                              on="file_id").merge(splits[["recording_id", "split"]],
                                                  on="recording_id")
    dataset = SedFeatureDataset(
        joined[joined["split"] == "test"],
        pd.read_csv(ROOT / "data/annotations/datased_polyphonic_events.csv"),
        feature_root=FEATURE_ROOT, class_ids=taxonomy.polyphonic_class_ids,
        frame_rate=sed.config.frame_rate, window_frames=sed.config.window_frames,
        hop_frames=sed.config.hop_frames)
    batch, _, _ = next(iter(DataLoader(dataset, batch_size=TRAIN_BATCH, shuffle=False)))
    out = {}
    for model, member in zip(sed.members, sed.member_ids, strict=True):
        frozen = load_predictions(ROOT / "ml/runs" / member / "predictions/test.npz",
                                  expected_class_ids=taxonomy.polyphonic_class_ids)
        with torch.inference_mode(), torch.amp.autocast(
                device_type=sed.device.type, enabled=sed.device.type == "cuda"):
            logits = model(batch.to(sed.device)).float().cpu().numpy()
        out[member] = float(np.abs(logits - frozen.logits[:TRAIN_BATCH]).max())
    return out


def event_key(events: list[dict]) -> list[tuple]:
    return sorted((e["event_label"], round(float(e["onset"]), 6), round(float(e["offset"]), 6))
                  for e in events)


def check(sed: ServedSed, frozen: dict[str, np.ndarray], rid: str, paths) -> dict:
    audio, stored_path = paths
    stored = np.load(stored_path, allow_pickle=False).astype(np.float32)
    from_wav = served_feature(audio, sed.config.feature_set)
    served = sed.probabilities(stored)
    served_events, frozen_events = event_key(sed.events(served)), event_key(sed.events(frozen[rid]))
    shared = len(set(served_events) & set(frozen_events))
    return {"recording_id": rid, "feature_equal": bool(np.array_equal(from_wav, stored)),
            "feature_max_abs": float(np.abs(from_wav - stored).max())
            if from_wav.shape == stored.shape else None,
            "frames_equal": served.shape == frozen[rid].shape,
            "prob_max_abs": float(np.abs(served - frozen[rid]).max())
            if served.shape == frozen[rid].shape else None,
            "events_equal": served_events == frozen_events, "n_events": len(frozen_events),
            "n_served_events": len(served_events), "n_shared_events": shared}


def render(result: dict) -> str:
    rows, s = result["rows"], result["summary"]
    return "\n".join([
        f"# Parity hệ thống phục vụ — `{result['ensemble']}` + `{result['postproc']}`", "",
        "> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng "
        "trên test; không đánh giá lại, không chọn gì.", "",
        f"| Tầng | Kết quả (n = {len(rows)} recording test, thiết bị `{result['device']}`) |",
        "|---|---|",
        f"| Đặc trưng WAV → log-mel trùng file `.npy` | {s['feature_equal']}/{len(rows)} "
        f"(lệch lớn nhất {s['feature_max_abs']:.3g}) |",
        f"| Số frame khớp | {s['frames_equal']}/{len(rows)} |",
        f"| Xác suất, lệch tuyệt đối lớn nhất | {s['prob_max_abs']:.3g} "
        f"(trung vị theo recording {s['prob_median_abs']:.3g}) |",
        f"| Recording có event trùng khít | {s['events_equal']}/{len(rows)} |",
        f"| Event trùng khít (class + onset + offset) | {s['n_shared_events']} / "
        f"{s['n_events']} đóng băng, {s['n_served_events']} phục vụ |",
        "| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | "
        + ", ".join(f"`{m[-7:]}` {v:.3g}" for m, v in result["batch_reproduction"].items())
        + " |",
        "", "Recording lệch event: " + (", ".join(s["event_mismatches"]) or "không có"),
    ]) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    sed = ServedSed(ENSEMBLE, POSTPROC, taxonomy, torch.device(args.device))
    artifact = load_predictions(ENSEMBLE / "predictions/test.npz",
                                expected_class_ids=taxonomy.polyphonic_class_ids)
    frozen = stack_predictions_by_recording(artifact)
    paths = feature_paths()
    rows = [check(sed, frozen, rid, paths[rid]) for rid in sorted(frozen)[: args.limit]]
    maxima = [r["prob_max_abs"] for r in rows if r["prob_max_abs"] is not None]
    summary = {"feature_equal": sum(r["feature_equal"] for r in rows),
               "feature_max_abs": max((r["feature_max_abs"] or 0.0) for r in rows),
               "frames_equal": sum(r["frames_equal"] for r in rows),
               "prob_max_abs": max(maxima), "prob_median_abs": float(np.median(maxima)),
               "events_equal": sum(r["events_equal"] for r in rows),
               "n_events": sum(r["n_events"] for r in rows),
               "n_served_events": sum(r["n_served_events"] for r in rows),
               "n_shared_events": sum(r["n_shared_events"] for r in rows),
               "event_mismatches": [r["recording_id"] for r in rows if not r["events_equal"]]}
    result = {"ensemble": ENSEMBLE.name, "postproc": POSTPROC, "device": args.device,
              "git": git, "summary": summary, "rows": rows,
              "batch_reproduction": batch_reproduction(sed, taxonomy)}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"inference_parity_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
