"""Hậu xử lý cSEBB — chọn (τ, luật gộp, λ) bằng k-fold CV trên DEV, như ADR-0024 §2.

    .venv/Scripts/python.exe -m scripts.select_sebb_cv ml/runs/<run> [--workers 8]

Lưới ghi trước (ADR-0030 §3): τ ∈ {0.32, 0.48, 0.64, 0.96, 1.28} s (ba giá trị đầu là lưới
của Ebbers và cộng sự 2024; hai giá trị sau cho model có khối thời gian 0.64 s), luật gộp ∈
{abs 0.15/0.2/0.3, rel 1.5/2/3}, ngưỡng hộp λ ∈ lưới ngưỡng dự án. **Dùng chung mọi lớp**
(A2: 21 tham số theo lớp overfit dev 142 recording). Mỗi cấu hình (τ, luật gộp): λ fit trên
k−1 fold (event-F1 lớn nhất), chấm event-F1 trên fold còn lại; điểm = CV mean. Cấu hình
thắng fit lại λ trên toàn dev → `postproc_sebb.json`.

Event-F1 micro = 2·ΣTP / (ΣNref + ΣNsys), nên (Nref, Nsys, TP) theo recording tính **một
lần** cho mỗi (cấu hình, λ) rồi cộng theo fold — không chạy lại sed_eval cho mỗi fold.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean, stdev

import numpy as np
import pandas as pd

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_counts_per_recording
from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID, stack_predictions_by_recording
from ml.postprocessing.sebb import SebbParams, sebb_candidates, select_boxes
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.select_postproc_cv import assign_folds
from scripts.sweep_threshold import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]
STEP_FILTERS_S = (0.32, 0.48, 0.64, 0.96, 1.28)
MERGES = (("abs", 0.15), ("abs", 0.2), ("abs", 0.3), ("rel", 1.5), ("rel", 2.0), ("rel", 3.0))
LAMBDAS = tuple(DEFAULT_THRESHOLD_GRID)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--render-only", action="store_true",
                        help="chỉ sinh lại báo cáo từ sebb_cv_selection.json đã có")
    return parser.parse_args()


def render(selection: dict, baseline: dict | None) -> str:
    rows = sorted(selection["cv"].items(), key=lambda item: -item[1]["mean"])
    lines = [
        f"# cSEBB — chọn bằng CV {selection['folds']} fold trên dev (`{selection['run']}`)", "",
        "> Sinh bởi `scripts.select_sebb_cv`. Chỉ dev; không chạm test. Tham số dùng chung "
        "mọi lớp; λ fit trên k−1 fold, chấm event-F1 trên fold còn lại (ADR-0024 §2).", "",
        "| Cấu hình | CV event-F1 (mean ± sd) | λ theo fold |", "|---|---:|---|"]
    lines += [f"| `{label}` | {r['mean']:.4f} ± {r['sd']:.4f} | "
              f"{', '.join(f'{v:g}' for v in r['lambda_by_fold'])} |" for label, r in rows]
    if baseline is not None:
        lines += ["", f"So sánh: hậu xử lý ADR-0024 đã chọn cho cùng run "
                  f"(`{baseline['config']}`): CV {baseline['mean']:.4f} ± {baseline['sd']:.4f}."]
    return "\n".join(lines) + "\n"


def adr0024_baseline(run_dir: Path) -> dict | None:
    path = run_dir / "postproc_cv_selection.json"
    if not path.exists():
        return None
    selection = json.loads(path.read_text(encoding="utf-8"))
    chosen = selection["selected"]
    key = f"{chosen['threshold_mode']}|{chosen['g_max_percentile']:g}"
    return {"config": key, **selection["cv"][key]}


def write_report(run_dir: Path, selection: dict) -> Path:
    stamp = selection["git"].get("timestamp_utc", "")[:10].replace("-", "") or \
        time.strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"sebb_cv_{run_dir.name}_{stamp}.md"
    out.write_text(render(selection, adr0024_baseline(run_dir)), encoding="utf-8")
    return out


def grid() -> list[SebbParams]:
    return [SebbParams(step_filter_s=tau, **{f"merge_{kind}": value})
            for tau in STEP_FILTERS_S for kind, value in MERGES]


def load_context(run_dir: Path, n_folds: int) -> dict:
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    artifact = load_predictions(run_dir / "predictions/dev.npz", expected_class_ids=class_ids)
    probabilities = stack_predictions_by_recording(artifact)
    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    groups = dict(zip(splits["recording_id"].astype(str), splits["leakage_group"], strict=True))
    recordings = sorted(probabilities)
    return {"class_ids": class_ids, "probabilities": probabilities, "recordings": recordings,
            "frame_rate": 1.0 / artifact.frame_hop_s,
            "reference": load_events_by_recording(set(recordings)),
            "folds": assign_folds(recordings, groups, n_folds),
            "dev_predictions_sha256": artifact_sha(run_dir)}


def artifact_sha(run_dir: Path) -> str | None:
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    return metrics.get("dev_predictions_sha256")


def count_table(ctx: dict, params: SebbParams) -> np.ndarray:
    """[λ, recording, (Nref, Nsys, TP)] for one (τ, merge) configuration."""
    candidates = sebb_candidates(ctx["probabilities"], class_ids=ctx["class_ids"],
                                 frame_rate=ctx["frame_rate"], params=params)
    table = np.zeros((len(LAMBDAS), len(ctx["recordings"]), 3), dtype=np.int64)
    for i, threshold in enumerate(LAMBDAS):
        counts = event_counts_per_recording(ctx["reference"], select_boxes(candidates, threshold),
                                            event_label_list=list(ctx["class_ids"]))
        table[i] = [counts[r] for r in ctx["recordings"]]
    return table


def micro_f1(counts: np.ndarray) -> np.ndarray:
    """Event-F1 per λ from summed counts ([λ, 3] → [λ]); empty denominators score 0."""
    denominator = counts[:, 0] + counts[:, 1]
    return np.where(denominator > 0, 2 * counts[:, 2] / np.maximum(denominator, 1), 0.0)


def cross_validate(ctx: dict, table: np.ndarray, n_folds: int) -> dict:
    fold_of = np.array([ctx["folds"][r] for r in ctx["recordings"]])
    scores, picked = [], []
    for fold in range(n_folds):
        fit = micro_f1(table[:, fold_of != fold].sum(axis=1))
        best = int(np.argmax(fit))  # ties → lowest λ index, deterministic
        picked.append(LAMBDAS[best])
        scores.append(float(micro_f1(table[:, fold_of == fold].sum(axis=1))[best]))
    full = micro_f1(table.sum(axis=1))
    best_full = int(np.argmax(full))
    return {"mean": mean(scores), "sd": stdev(scores), "folds": scores, "lambda_by_fold": picked,
            "lambda_full_dev": LAMBDAS[best_full], "f1_full_dev_in_sample": float(full[best_full])}


_CTX: dict | None = None


def _init(run_dir: str, n_folds: int) -> None:
    global _CTX
    _CTX = load_context(Path(run_dir), n_folds)


def _task(params: SebbParams, n_folds: int) -> tuple[str, dict]:
    return params.label, {"params": params.__dict__,
                          **cross_validate(_CTX, count_table(_CTX, params), n_folds)}


def run_grid(args: argparse.Namespace) -> dict:
    start, results = time.monotonic(), {}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init,
                             initargs=(str(args.run_dir), args.folds)) as pool:
        futures = [pool.submit(_task, params, args.folds) for params in grid()]
        for future in as_completed(futures):
            label, value = future.result()
            results[label] = value
            print(f"[{len(results)}/{len(futures)}] {label} CV {value['mean']:.4f} "
                  f"± {value['sd']:.4f} ({time.monotonic() - start:.0f}s)", flush=True)
    return results


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.render_only:
        selection = json.loads((args.run_dir / "sebb_cv_selection.json").read_text(
            encoding="utf-8"))
        print(write_report(args.run_dir, selection))
        return
    git = git_state(ROOT)
    results = run_grid(args)
    best = max(sorted(results), key=lambda label: results[label]["mean"])
    selection = {"run": args.run_dir.name, "folds": args.folds, "grouping": "leakage_group",
                 "family": "csebb", "shared_across_classes": True,
                 "selected": {"config": best, **results[best]["params"],
                              "threshold": results[best]["lambda_full_dev"]},
                 "cv": results, "git": git}
    (args.run_dir / "sebb_cv_selection.json").write_text(
        json.dumps(selection, indent=1), encoding="utf-8")
    print(json.dumps(selection["selected"], indent=1))
    print(write_report(args.run_dir, selection))


if __name__ == "__main__":
    main()
