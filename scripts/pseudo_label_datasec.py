"""O-F (ADR-0041 §10): turn DataSEC pool clips into strong pseudo-labels with a SED teacher.

    # tier S: teacher trained on the original train split, its own CV-selected θ post-processing
    .venv/Scripts/python.exe -m scripts.pseudo_label_datasec ml/runs/<teacher> --label s \\
        --postproc ml/runs/<teacher>/postproc_cv_annotated.json
    # tier C, fold k: teacher fold k; θ refit on the OTHER folds of the teacher's OOF run with
    # per-fold priors, so no label of fold k reaches the student of fold k
    .venv/Scripts/python.exe -m scripts.pseudo_label_datasec ml/runs/<fold k> --label c<k> \\
        --oof-run ml/runs/<teacher OOF h5> --oof-fold k

Inference is the B0 one (hop 5 s, triangular floor 0.3). Each clip keeps only the teacher's events
of its folder (tag) class; clips with none are dropped and counted. Writes
`ml/runs/pseudo_datasec_<label>_<ts>/` with `events.csv`, `clips.csv`, `summary.json`, manifest.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import torch

from ml.datasets.datasec_pseudo import CACHE_DIRNAME, clip_table, keep_tag_class
from ml.datasets.waveforms import SedWaveformDataset
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file
from ml.training.sed import collect_predictions
from scripts import select_postproc_cv as theta_cv
from scripts.dump_predictions import load_model
from scripts.evaluate_run import priors_from_postproc
from scripts.train_sed import make_loader

ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = ROOT / "data" / "cache" / CACHE_DIRNAME
CACHE_MANIFEST = ROOT / "data" / "manifests" / "datasec_o_f_wav16k.csv"
HOP_SECONDS, WEIGHTING = 5.0, "triangular:0.3"


def fold_thresholds(oof_run: Path, fold: int, config: str, class_ids: tuple[str, ...]
                    ) -> tuple[dict, dict]:
    """θ fit on every OOF fold but `fold` with that fold's priors (select_postproc_cv)."""
    mode, percentile = config.split("|")
    ctx = theta_cv.load_context(oof_run, 5, "annotated")
    if "fold_priors" not in ctx:
        raise SystemExit(f"{oof_run} không phải run OOF")
    priors = theta_cv.priors_for(ctx, float(percentile), fold)
    fit_ids = [r for r, f in ctx["folds"].items() if f != fold]
    thresholds = theta_cv.fit(mode, {r: ctx["probabilities"][r] for r in fit_ids},
                              {r: ctx["reference"][r] for r in fit_ids}, class_ids, priors,
                              ctx["frame_rate"], ctx["taxonomy"])
    return thresholds, priors


def postprocessing(args: argparse.Namespace, class_ids: tuple[str, ...]) -> tuple[dict, dict, dict]:
    """(thresholds, priors, provenance). Only the θ family is supported (O-D selects θ)."""
    if args.oof_run is not None:
        selection = json.loads((args.oof_run / "postproc_cv_selection_annotated.json")
                               .read_text(encoding="utf-8"))
        selected = selection["selected"]
        if selected.get("threshold_mode") != "global":
            raise SystemExit(f"cấu hình OOF không phải θ global: {selected!r}")
        config = f"global|{float(selected['g_max_percentile']):g}"
        thresholds, priors = fold_thresholds(args.oof_run, args.oof_fold, config, class_ids)
        return thresholds, priors, {"oof_run": args.oof_run.name, "oof_fold": args.oof_fold,
                                    "theta_config": config}
    postproc = json.loads(args.postproc.read_text(encoding="utf-8"))
    if postproc.get("family", "theta") != "theta":
        raise SystemExit("O-F chỉ hỗ trợ hậu xử lý θ")
    thresholds = {c: postproc["per_class"][c]["theta"] for c in class_ids}
    return thresholds, priors_from_postproc(postproc, class_ids), {
        "postproc": str(args.postproc), "postproc_sha256": sha256_file(args.postproc)}


def teacher_probabilities(run: Path, clips: pd.DataFrame, class_ids: tuple[str, ...],
                          device: torch.device) -> dict:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    config = manifest["config"]
    frame_rate = float(config["frame_rate"])
    dataset = SedWaveformDataset(
        clips, pd.DataFrame(columns=["recording_id", "class_id", "onset_s", "offset_s"]),
        waveform_root=CACHE_ROOT, class_ids=class_ids, frame_rate=frame_rate,
        window_frames=int(config["window_frames"]), hop_frames=round(HOP_SECONDS * frame_rate))
    loader = make_loader(dataset, batch_size=int(config["batch_size"]), shuffle=False,
                         device=device)
    model = load_model(run, config, len(class_ids), device)
    artifact = collect_predictions(model, loader, device=device, class_ids=class_ids,
                                   split="dev", model_version=str(config["model_version"]),
                                   taxonomy_sha256=manifest["taxonomy_sha256"],
                                   frame_rate=frame_rate)
    artifact = dataclasses.replace(artifact, window_weighting=WEIGHTING)
    return stack_predictions_by_recording(artifact), frame_rate, manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("teacher", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--postproc", type=Path, default=None)
    parser.add_argument("--oof-run", type=Path, default=None)
    parser.add_argument("--oof-fold", type=int, default=None)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    if (args.postproc is None) == (args.oof_run is None):
        parser.error("cần đúng một trong --postproc (tầng S) hoặc --oof-run (tầng C)")
    if (args.oof_run is None) != (args.oof_fold is None):
        parser.error("--oof-run đi cùng --oof-fold")
    return args


def check_teacher(manifest: dict, args: argparse.Namespace) -> None:
    """Tier C: the teacher must be the fold-k model; tier S: a model of the original split."""
    fold = manifest["config"].get("cv_fold")
    if fold != args.oof_fold:
        raise SystemExit(f"teacher cv_fold={fold!r} khác --oof-fold={args.oof_fold!r} "
                         "(ADR-0041 §10: student fold k chỉ dùng teacher fold k)")
    if not manifest.get("complete") or manifest["git"]["dirty"]:
        raise SystemExit("teacher chưa hoàn tất hoặc train trên tree bẩn")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    cache = pd.read_csv(CACHE_MANIFEST)
    tags = dict(zip(cache["file_id"].astype(str), cache["class_id"].astype(str), strict=True))
    check_teacher(json.loads((args.teacher / "manifest.json").read_text(encoding="utf-8")), args)
    thresholds, priors, post_info = postprocessing(args, class_ids)
    probabilities, frame_rate, manifest = teacher_probabilities(
        args.teacher, clip_table(cache), class_ids, torch.device(args.device))
    events = process_recordings(probabilities, class_ids=class_ids, thresholds=thresholds,
                                priors=priors, frame_rate=frame_rate)
    rows, dropped = keep_tag_class(events, tags)
    write_run(args, rows, dropped, cache, manifest, post_info)


def write_run(args: argparse.Namespace, rows: list[dict], dropped: list[str], cache: pd.DataFrame,
              teacher: dict, post_info: dict) -> None:
    out = ROOT / "ml" / "runs" / f"pseudo_datasec_{args.label}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    out.mkdir(parents=True)
    events = pd.DataFrame(rows, columns=["recording_id", "class_id", "onset_s", "offset_s"])
    events.to_csv(out / "events.csv", index=False, lineterminator="\n")
    kept = cache[~cache["file_id"].isin(dropped)]
    kept.to_csv(out / "clips.csv", index=False, lineterminator="\n")
    duration = events["offset_s"] - events["onset_s"]
    summary = {
        "clips": len(cache), "clips_kept": len(kept), "clips_dropped": len(dropped),
        "events": len(events), "event_seconds": float(duration.sum()),
        "per_class": {c: {"clips": int((cache["class_id"] == c).sum()),
                          "kept": int((kept["class_id"] == c).sum()),
                          "events": int((events["class_id"] == c).sum()),
                          "median_event_s": float(duration[events["class_id"] == c].median())
                          if (events["class_id"] == c).any() else None}
                      for c in sorted(cache["class_id"].unique())},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    manifest = {
        "run_id": out.name, "task": "pseudo_labels", "complete": True,
        "command": ["python", "-m", "scripts.pseudo_label_datasec", *sys.argv[1:]],
        "class_ids": teacher["class_ids"],
        **{k: teacher[k] for k in ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")},
        "config": {"teacher": args.teacher.name,
                   "teacher_cv_fold": teacher["config"].get("cv_fold"),
                   "hop_seconds": HOP_SECONDS, "window_weighting": WEIGHTING,
                   "cache_manifest_sha256": sha256_file(CACHE_MANIFEST), **post_info},
        "environment": {"python": platform.python_version(), "torch": torch.__version__},
        "git": git_state(ROOT),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"run_dir": str(out), **{k: summary[k] for k in
                      ("clips_kept", "clips_dropped", "events")}}, indent=1))


if __name__ == "__main__":
    main()
