from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.datasets.features import ClassificationFeatureDataset
from ml.models import AudioClassifier
from ml.taxonomy import load_taxonomy
from ml.training.classification import (
    ClassificationTrainingConfig,
    inverse_frequency_weights,
    run_epoch,
    train_classifier,
)
from ml.training.common import (
    create_run_directory,
    git_state,
    runtime_environment,
    seed_everything,
    sha256_file,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train DataSEC 22-class baseline")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=20260922)
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
    class_ids = taxonomy.class_ids
    config = ClassificationTrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )

    clips = pd.read_csv(ROOT / "data" / "manifests" / "datasec_clips.csv")
    features = pd.read_csv(ROOT / "data" / "manifests" / "datasec_logmel_v1.csv")
    split_path = ROOT / "data" / "splits" / "datasec.csv"
    splits = pd.read_csv(split_path)
    joined = (
        clips.merge(
            features[["file_id", "feature_relative_path"]],
            on="file_id",
            validate="one_to_one",
        )
        .merge(splits[["clip_id", "split"]], on="clip_id", validate="one_to_one")
    )
    feature_root = ROOT / "data" / "features" / "datasec" / "logmel_v1"
    loaders: dict[str, DataLoader] = {}
    for split in ("train", "validation", "test"):
        subset = joined[joined["split"] == split]
        dataset = ClassificationFeatureDataset(
            subset,
            feature_root=feature_root,
            class_ids=class_ids,
            frames=config.frames,
            random_crop=split == "train",
        )
        loaders[split] = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=split == "train",
            num_workers=0,
            pin_memory=device.type == "cuda",
        )

    class_index = {class_id: index for index, class_id in enumerate(class_ids)}
    train_labels = [
        class_index[class_id]
        for class_id in joined.loc[joined["split"] == "train", "class_id"]
    ]
    class_weight = inverse_frequency_weights(train_labels, len(class_ids))
    model = AudioClassifier(classes=len(class_ids))
    run = create_run_directory(ROOT, "classifier_datasec")
    manifest = {
        "command": sys.argv,
        "config": asdict(config),
        "class_ids": class_ids,
        "taxonomy_sha256": taxonomy.checksum,
        "split_sha256": sha256_file(split_path),
        "git": git_state(ROOT),
        "environment": runtime_environment(),
        "dataset_items": {name: len(loader.dataset) for name, loader in loaders.items()},
        "class_weight": class_weight.tolist(),
        "complete": False,
    }
    write_json(run / "manifest.json", manifest)
    history, best_path = train_classifier(
        model,
        loaders,
        device=device,
        class_weight=class_weight,
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
                class_weight=class_weight.to(device),
                optimizer=None,
                scaler=None,
            )
    write_json(run / "metrics.json", metrics)
    manifest["complete"] = True
    manifest["best_checkpoint"] = str(best_path.relative_to(run))
    write_json(run / "manifest.json", manifest)
    print(json.dumps({"run": str(run), "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
