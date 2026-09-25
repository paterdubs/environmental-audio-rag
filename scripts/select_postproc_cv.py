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
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
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
from ml.provenance import git_state
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
    parser.add_argument("--workers", type=int, default=1,
                        help="số tiến trình; >1 chạy song song, kết quả y hệt")
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


def load_context(run_dir: Path, n_folds: int) -> dict:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(run_dir / "predictions/dev.npz", expected_class_ids=class_ids)
    probabilities = stack_predictions_by_recording(artifact)
    frame_rate = 1.0 / artifact.frame_hop_s
    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    groups = dict(zip(splits["recording_id"].astype(str), splits["leakage_group"], strict=True))
    train_ids = set(splits.loc[splits["split"] == "train", "recording_id"].astype(str))
    train_events = load_events_by_recording(train_ids)
    return {
        "taxonomy": taxonomy, "class_ids": class_ids, "probabilities": probabilities,
        "reference": load_events_by_recording(set(probabilities)), "frame_rate": frame_rate,
        "folds": assign_folds(sorted(probabilities), groups, n_folds),
        "priors_by_p": {
            p: derive_duration_priors(train_events, class_ids=class_ids, frame_rate=frame_rate,
                                      source_split="train", taxonomy=taxonomy,
                                      g_max_percentile=p)
            for p in G_MAX_PERCENTILES
        },
    }


def run_task(ctx: dict, mode: str, p: float, fold: int | None):
    """Fit θ on every fold but `fold` and return the held-out event-F1; with
    `fold=None`, fit on the whole dev set and return the thresholds."""
    fit_ids = [r for r, f in ctx["folds"].items() if f != fold]
    shared = (ctx["class_ids"], ctx["priors_by_p"][p], ctx["frame_rate"])
    thresholds = fit(mode, {r: ctx["probabilities"][r] for r in fit_ids},
                     {r: ctx["reference"][r] for r in fit_ids}, *shared, ctx["taxonomy"])
    if fold is None:
        return thresholds
    held_ids = [r for r, f in ctx["folds"].items() if f == fold]
    return score({r: ctx["probabilities"][r] for r in held_ids},
                 {r: ctx["reference"][r] for r in held_ids}, thresholds, *shared)


_WORKER_CTX: dict | None = None


def _init_worker(run_dir: str, n_folds: int) -> None:
    global _WORKER_CTX
    _WORKER_CTX = load_context(Path(run_dir), n_folds)


def _worker(task: tuple[str, float, int | None]):
    return task, run_task(_WORKER_CTX, *task)


def build_tasks(n_folds: int, *, speculative_refits: bool) -> list[tuple[str, float, int | None]]:
    """Every (mode, percentile, fold) once, longest first: per_class before global,
    whole-dev refits (fold None) before folds, so the slowest fits do not form the tail."""
    folds: list[int | None] = [*([None] if speculative_refits else []), *range(n_folds)]
    return [(m, p, k) for m in MODES for k in folds for p in G_MAX_PERCENTILES]


def run_all(args: argparse.Namespace, ctx: dict) -> dict:
    """Serial (`--workers 1`) or process-parallel; identical results either way.

    In parallel mode the four whole-dev refits run alongside the folds
    (speculatively), so wall time is bounded by the slowest single fit. A failed
    task cancels the queued ones instead of letting the pool run to the end.
    """
    parallel = args.workers > 1
    tasks = build_tasks(args.folds, speculative_refits=parallel)
    outputs: dict = {}
    start = time.monotonic()

    def done(task, value) -> None:
        outputs[task] = value
        print(f"[{len(outputs)}/{len(tasks)}] {task} {time.monotonic() - start:.0f}s", flush=True)

    if not parallel:
        for task in tasks:
            done(task, run_task(ctx, *task))
        return outputs
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker,
                             initargs=(str(args.run_dir), args.folds)) as pool:
        futures = [pool.submit(_worker, task) for task in tasks]
        try:
            for future in as_completed(futures):
                done(*future.result())
        except BaseException:
            for future in futures:
                future.cancel()
            raise
    return outputs


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((args.run_dir / "metrics.json").read_text(encoding="utf-8"))
    git = git_state(ROOT)  # code that produced the selection, recorded before the long run
    ctx = load_context(args.run_dir, args.folds)
    outputs = run_all(args, ctx)

    results = {}
    for mode in MODES:
        for p in G_MAX_PERCENTILES:
            fold_scores = [outputs[(mode, p, k)] for k in range(args.folds)]
            results[f"{mode}|{p:g}"] = {"mean": mean(fold_scores), "sd": stdev(fold_scores),
                                        "folds": fold_scores}
            print(mode, p, round(mean(fold_scores), 4), flush=True)

    best_key = max(results, key=lambda key: results[key]["mean"])
    default_key = f"{DEFAULT[0]}|{DEFAULT[1]:g}"
    if results[best_key]["mean"] <= results[default_key]["mean"]:
        best_key = default_key
    mode, p = best_key.split("|")[0], float(best_key.split("|")[1])
    thresholds = outputs.get((mode, p, None)) or run_task(ctx, mode, p, None)
    postproc = build_postproc_artifact(
        class_ids=ctx["class_ids"], thresholds=thresholds, priors=ctx["priors_by_p"][p],
        taxonomy_sha256=ctx["taxonomy"].checksum, split_sha256=manifest["split_sha256"],
        data_manifest_sha256=manifest["data_manifest_sha256"],
        dev_predictions_sha256=metrics["dev_predictions_sha256"], threshold_mode=mode,
        taxonomy=ctx["taxonomy"],
    )
    write_postproc_json(args.run_dir / "postproc_cv.json", postproc, taxonomy=ctx["taxonomy"])
    report = {"run": args.run_dir.name, "folds": args.folds, "grouping": "leakage_group",
              "selected": {"threshold_mode": mode, "g_max_percentile": p},
              "cv": results, "git": git, "workers": args.workers}
    (args.run_dir / "postproc_cv_selection.json").write_text(json.dumps(report, indent=2),
                                                             encoding="utf-8")
    print(json.dumps(report["selected"]))


if __name__ == "__main__":
    main()
