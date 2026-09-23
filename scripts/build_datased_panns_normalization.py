"""Build train-only DataSED log-mel statistics for the PANNs branch B encoder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from ml.dataops.textio import read_csv_rows

ROOT = Path(__file__).resolve().parents[1]
FEATURE_SET = "logmel_panns_v1"
DEFAULT_OUTPUT = ROOT / "data" / "manifests" / "datased_logmel_panns_v1_train_normalization.npz"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build train-only DataSED PANNs input-normalization statistics."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def train_feature_paths(root: Path) -> tuple[list[Path], str]:
    """Resolve frozen DataSED train records to feature paths through the recording manifest."""
    recordings, _ = read_csv_rows(root / "data" / "manifests" / "datased_recordings.csv")
    features, _ = read_csv_rows(root / "data" / "manifests" / f"datased_{FEATURE_SET}.csv")
    splits, _ = read_csv_rows(root / "data" / "splits" / "datased_polyphonic.csv")
    file_id_by_recording = {row["recording_id"]: row["file_id"] for row in recordings}
    train_recordings = {row["recording_id"] for row in splits if row["split"] == "train"}
    unknown = train_recordings.difference(file_id_by_recording)
    if unknown:
        raise ValueError(f"Train recording missing from DataSED manifest: {sorted(unknown)[0]}")
    paths_by_file_id = {row["file_id"]: row["feature_relative_path"] for row in features}
    config_hashes = {row["feature_config_sha256"] for row in features}
    if len(config_hashes) != 1:
        raise ValueError(f"Expected one feature config hash, found {len(config_hashes)}")

    train_file_ids = {file_id_by_recording[recording] for recording in train_recordings}
    intersection = train_file_ids.intersection(paths_by_file_id)
    # DataSED split uses recording_id while features use full file_id; a zero join would pass
    # silently but calculate no statistics, so prove the cross-namespace join is non-empty.
    if not intersection:
        raise ValueError("Train split and feature manifest have an empty file_id intersection")
    if intersection != train_file_ids:
        missing = sorted(train_file_ids.difference(intersection))
        raise ValueError(f"Train recordings missing PANNs features: {missing[0]}")
    feature_root = root / "data" / "features" / "datased" / FEATURE_SET
    paths = [feature_root / paths_by_file_id[file_id] for file_id in sorted(intersection)]
    return paths, config_hashes.pop()


def stream_statistics(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, int]:
    """Calculate population per-mel mean/std without concatenating the full feature cache."""
    total = np.zeros(64, dtype=np.float64)
    squared_total = np.zeros(64, dtype=np.float64)
    frames = 0
    for path in paths:
        values = np.load(path, mmap_mode="r", allow_pickle=False)
        if values.ndim != 2 or values.shape[0] != 64 or not np.isfinite(values).all():
            raise ValueError(f"Expected finite [64, frames] feature: {path}")
        # Feature extraction locks the orientation as [mel, time]; reducing axis 1 preserves
        # a distinct statistic for each mel band instead of mixing bands into time indices.
        total += values.sum(axis=1, dtype=np.float64)
        squared_total += np.square(values, dtype=np.float64).sum(axis=1, dtype=np.float64)
        frames += int(values.shape[1])
    if frames < 1:
        raise ValueError("Cannot calculate normalization from zero frames")
    mean = total / frames
    variance = np.maximum(squared_total / frames - np.square(mean), 0.0)
    std = np.sqrt(variance)
    if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std <= 0).any():
        raise ValueError(
            "Normalization statistics must be finite with positive standard deviations"
        )
    return mean.astype(np.float32), std.astype(np.float32), frames


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    paths, config_hash = train_feature_paths(ROOT)
    mean, std, frames = stream_statistics(paths)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output, mean=mean, std=std, frames=np.int64(frames))
    print(
        json.dumps(
            {
                "output": str(output),
                "train_clips": len(paths),
                "frames": frames,
                "mean_range": [float(mean.min()), float(mean.max())],
                "std_range": [float(std.min()), float(std.max())],
                "feature_config_sha256": config_hash,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
