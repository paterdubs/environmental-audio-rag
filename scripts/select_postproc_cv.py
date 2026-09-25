"""Tối ưu SED bước 2+3 — chọn cấu hình hậu xử lý bằng k-fold CV trên DEV.

    .venv/Scripts/python.exe -m scripts.select_postproc_cv ml/runs/<run>
    .venv/Scripts/python.exe -m scripts.evaluate_run ml/runs/<run> \\
        --postproc ml/runs/<run>/postproc_cv.json --tag cv

A2 cho thấy θ per-class overfit dev; A5 gợi ý percentile `g_max` 25 tốt hơn 50 —
nhưng cả hai quan sát đến từ test nên không được dùng để chọn. Script này chọn lại
**chỉ bằng dev**: chia dev thành k fold theo `leakage_group` (bản ghi gần trùng không
tách fold), với mỗi cấu hình (kiểu θ × percentile g_max) fit θ trên k−1 fold, đo
event-F1 trên fold còn lại, lấy trung bình. Cấu hình thắng được fit lại trên toàn bộ
dev → `postproc_cv.json`. Hoà thì chọn cấu hình mặc định (per_class, 50) để không
đổi khi không có bằng chứng.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import mean, stdev

import pandas as pd

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import (
    build_postproc_artifact,
    derive_duration_priors,
    process_recordings,
    stack_predictions_by_recording,
    sweep_global_threshold,
    sweep_per_class_thresholds,
    write_postproc_json,
)
from ml.taxonomy import load_taxonomy
from scripts.sweep_threshold import build_score_functions, load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]
MODES = ("per_class", "global")
G_MAX_PERCENTILES = (50.0, 25.0)
DEFAULT = ("per_class", 50.0)
SEED = "20260922"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--folds", type=int, default=5)
    return parser.parse_args()


def assign_folds(recording_ids: list[str], groups: dict[str, str], k: int) -> dict[str, int]:
    """Deterministic group k-fold: groups ordered by a seeded hash, dealt round-robin."""
    ordered = sorted({groups[r] for r in recording_ids},
                     key=lambda g: hashlib.sha256(f"{SEED}:{g}".encode()).hexdigest())
    fold_of_group = {group: index % k for index, group in enumerate(ordered)}
    return {r: fold_of_group[groups[r]] for r in recording_ids}


def fit(mode, predictions, reference, class_ids, priors, frame_rate, taxonomy) -> dict:
    global_score, class_score = build_score_functions(reference, class_ids)
    common = {"class_ids": class_ids, "priors": priors, "frame_rate": frame_rate,
              "split": "dev", "taxonomy": taxonomy}
    if mode == "global":
        theta, _ = sweep_global_threshold(predictions, score_fn=global_score, **common)
        return dict.fromkeys(class_ids, theta)
    thetas, _ = sweep_per_class_thresholds(predictions, score_fn=class_score, **common)
    return thetas


def score(predictions, reference, thresholds, class_ids, priors, frame_rate) -> float:
    events = process_recordings(predictions, class_ids=class_ids, thresholds=thresholds,
                                priors=priors, frame_rate=frame_rate)
    result = event_based_f1(reference, events, event_label_list=list(class_ids))
    value = result["f_measure"]["f_measure"]
    return float(value) if value == value else 0.0


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((args.run_dir / "metrics.json").read_text(encoding="utf-8"))
    artifact = load_predictions(args.run_dir / "predictions/dev.npz", expected_class_ids=class_ids)
    probabilities = stack_predictions_by_recording(artifact)
    reference = load_events_by_recording(set(probabilities))
    frame_rate = 1.0 / artifact.frame_hop_s

    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    groups = dict(zip(splits["recording_id"].astype(str), splits["leakage_group"], strict=True))
    folds = assign_folds(sorted(probabilities), groups, args.folds)
    train_ids = set(splits.loc[splits["split"] == "train", "recording_id"].astype(str))
    train_events = load_events_by_recording(train_ids)
    priors_by_p = {
        p: derive_duration_priors(train_events, class_ids=class_ids, frame_rate=frame_rate,
                                  source_split="train", taxonomy=taxonomy, g_max_percentile=p)
        for p in G_MAX_PERCENTILES
    }

    results = {}
    for mode in MODES:
        for p in G_MAX_PERCENTILES:
            fold_scores = []
            for k in range(args.folds):
                fit_ids = [r for r, f in folds.items() if f != k]
                held_ids = [r for r, f in folds.items() if f == k]
                thresholds = fit(mode, {r: probabilities[r] for r in fit_ids},
                                 {r: reference[r] for r in fit_ids},
                                 class_ids, priors_by_p[p], frame_rate, taxonomy)
                fold_scores.append(score({r: probabilities[r] for r in held_ids},
                                         {r: reference[r] for r in held_ids},
                                         thresholds, class_ids, priors_by_p[p], frame_rate))
            results[f"{mode}|{p:g}"] = {"mean": mean(fold_scores), "sd": stdev(fold_scores),
                                        "folds": fold_scores}
            print(mode, p, round(mean(fold_scores), 4), flush=True)

    best_key = max(results, key=lambda key: results[key]["mean"])
    default_key = f"{DEFAULT[0]}|{DEFAULT[1]:g}"
    if results[best_key]["mean"] <= results[default_key]["mean"]:
        best_key = default_key
    mode, p = best_key.split("|")[0], float(best_key.split("|")[1])
    thresholds = fit(mode, probabilities, reference, class_ids, priors_by_p[p], frame_rate,
                     taxonomy)
    postproc = build_postproc_artifact(
        class_ids=class_ids, thresholds=thresholds, priors=priors_by_p[p],
        taxonomy_sha256=taxonomy.checksum, split_sha256=manifest["split_sha256"],
        data_manifest_sha256=manifest["data_manifest_sha256"],
        dev_predictions_sha256=metrics["dev_predictions_sha256"], threshold_mode=mode,
        taxonomy=taxonomy,
    )
    write_postproc_json(args.run_dir / "postproc_cv.json", postproc, taxonomy=taxonomy)
    report = {"run": args.run_dir.name, "folds": args.folds, "grouping": "leakage_group",
              "selected": {"threshold_mode": mode, "g_max_percentile": p},
              "cv": results}
    (args.run_dir / "postproc_cv_selection.json").write_text(json.dumps(report, indent=2),
                                                             encoding="utf-8")
    print(json.dumps(report["selected"]))


if __name__ == "__main__":
    main()
