from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ml.dataops.features import build_features
from ml.features.logmel import load_logmel_config

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract versioned log-mel features")
    parser.add_argument("dataset", choices=("datasec", "datased"))
    parser.add_argument(
        "--feature-set",
        default="logmel_v1",
        choices=("logmel_v1", "logmel_panns_v1"),
        help="Named frontend from ml/configs/features.yaml (default: logmel_v1)",
    )
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inventory_path = ROOT / "data" / "manifests" / f"{args.dataset}_inventory.csv"
    audio_root = ROOT / "data" / "raw" / args.dataset / "extracted"
    feature_root = ROOT / "data" / "features" / args.dataset / args.feature_set
    output_path = ROOT / "data" / "manifests" / f"{args.dataset}_{args.feature_set}.csv"
    config = load_logmel_config(args.feature_set)
    features = build_features(
        pd.read_csv(inventory_path),
        audio_root=audio_root,
        feature_root=feature_root,
        config=config,
        workers=args.workers,
    )
    features.to_csv(output_path, index=False, lineterminator="\n")
    config_path = output_path.with_suffix(".json")
    config_path.write_text(
        json.dumps({**asdict(config), "sha256": config.checksum}, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(features)} feature rows to {output_path}")


if __name__ == "__main__":
    main()
