from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.datasets.features import SedFeatureDataset
from ml.models import SoundEventDetector
from ml.taxonomy import load_taxonomy
from ml.training.common import (
    create_run_directory,
    git_state,
    runtime_environment,
    seed_everything,
    sha256_file,
    write_json,
)
from ml.training.sed import SedTrainingConfig, estimate_pos_weight, run_epoch, train_sed

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train DataSED polyphonic baseline")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--pretrained-classifier", type=Path)
    parser.add_argument("--evaluate-test", action="store_true")
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    seed_everything(args.seed)
    device = torch.device(args.device)
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    config = SedTrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )

    recordings = pd.read_csv(ROOT / "data" / "manifests" / "datased_recordings.csv")
    features = pd.read_csv(ROOT / "data" / "manifests" / "datased_logmel_v1.csv")
    splits_path = ROOT / "data" / "splits" / "datased_polyphonic.csv"
    splits = pd.read_csv(splits_path)
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    joined = (
        recordings.drop(columns=["frames"]).merge(
            features[["file_id", "feature_relative_path", "frames"]],
            on="file_id",
            validate="one_to_one",
        )
        .merge(splits[["recording_id", "split"]], on="recording_id", validate="one_to_one")
    )
    feature_root = ROOT / "data" / "features" / "datased" / "logmel_v1"
    loaders: dict[str, DataLoader] = {}
    for split in ("train", "validation", "test"):
        subset = joined[joined["split"] == split]
        dataset = SedFeatureDataset(
            subset,
            events,
            feature_root=feature_root,
            class_ids=class_ids,
            window_frames=config.window_frames,
            hop_frames=config.hop_frames,
        )
        loaders[split] = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=split == "train",
            num_workers=0,
            pin_memory=device.type == "cuda",
        )

    train_ids = set(joined.loc[joined["split"] == "train", "recording_id"])
    train_events = events[events["recording_id"].isin(train_ids)]
    pos_weight = estimate_pos_weight(
        class_ids,
        train_events[["class_id", "onset_s", "offset_s"]].itertuples(index=False, name=None),
        float(joined.loc[joined["split"] == "train", "duration_s"].sum()),
    )
    model = SoundEventDetector(classes=len(class_ids))
    if args.pretrained_classifier:
        checkpoint = torch.load(args.pretrained_classifier, map_location="cpu", weights_only=True)
        model.load_classifier_encoder(checkpoint)

    run = create_run_directory(ROOT, "sed_polyphonic")
    manifest = {
        "command": sys.argv,
        "config": asdict(config),
        "class_ids": class_ids,
        "taxonomy_sha256": taxonomy.checksum,
        "split_sha256": sha256_file(splits_path),
        "pretrained_classifier": (
            str(args.pretrained_classifier) if args.pretrained_classifier else None
        ),
        "git": git_state(ROOT),
        "environment": runtime_environment(),
        "dataset_windows": {name: len(loader.dataset) for name, loader in loaders.items()},
        "pos_weight": pos_weight.tolist(),
        "complete": False,
    }
    write_json(run / "manifest.json", manifest)
    history, best_path = train_sed(
        model,
        loaders,
        device=device,
        pos_weight=pos_weight,
        config=config,
        checkpoint_directory=run / "checkpoints",
    )
    write_json(run / "logs" / "history.json", {"epochs": history})
    metrics = {"best_validation": max(item["validation"]["macro_f1"] for item in history)}
    if args.evaluate_test:
        checkpoint = torch.load(best_path, map_location=device, weights_only=True)
        model.load_state_dict(checkpoint["model_state"])
        with torch.inference_mode():
            metrics["test"] = run_epoch(
                model,
                loaders["test"],
                device=device,
                pos_weight=pos_weight.to(device),
                optimizer=None,
                scaler=None,
                threshold=config.threshold,
            )
    write_json(run / "metrics.json", metrics)
    manifest["complete"] = True
    manifest["best_checkpoint"] = str(best_path.relative_to(run))
    write_json(run / "manifest.json", manifest)
    print(json.dumps({"run": str(run), "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
