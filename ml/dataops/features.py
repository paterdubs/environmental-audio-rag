from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from ml.features.logmel import LogMelConfig, extract_logmel, save_feature


@dataclass(frozen=True)
class FeatureRecord:
    file_id: str
    audio_relative_path: str
    feature_relative_path: str
    audio_sha256: str
    feature_sha256: str
    mel_bins: int
    frames: int
    feature_config_sha256: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_one(
    row: dict,
    audio_root: Path,
    feature_root: Path,
    config: LogMelConfig,
) -> FeatureRecord:
    relative = Path(row["relative_path"])
    audio_path = audio_root / relative
    feature_relative = relative.with_suffix(".npy")
    destination = feature_root / feature_relative
    if destination.exists():
        feature = np.load(destination, mmap_mode="r", allow_pickle=False)
        if feature.ndim != 2 or feature.shape[0] != config.n_mels:
            raise RuntimeError(f"Existing feature has wrong shape: {destination}")
    else:
        feature = extract_logmel(audio_path, config)
        save_feature(feature, destination)
    return FeatureRecord(
        file_id=str(row["file_id"]),
        audio_relative_path=relative.as_posix(),
        feature_relative_path=feature_relative.as_posix(),
        audio_sha256=str(row["sha256"]),
        feature_sha256=_sha256(destination),
        mel_bins=int(feature.shape[0]),
        frames=int(feature.shape[1]),
        feature_config_sha256=config.checksum,
    )


def build_features(
    inventory: pd.DataFrame,
    *,
    audio_root: Path,
    feature_root: Path,
    config: LogMelConfig,
    workers: int = 4,
) -> pd.DataFrame:
    required = {"file_id", "relative_path", "sha256"}
    missing = required.difference(inventory.columns)
    if missing:
        raise ValueError(f"Inventory missing columns: {sorted(missing)}")
    rows = inventory.to_dict(orient="records")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(
            tqdm(
                pool.map(
                    lambda row: _extract_one(row, audio_root, feature_root, config), rows
                ),
                total=len(rows),
                desc=f"logmel:{feature_root.name}",
            )
        )
    return pd.DataFrame(asdict(record) for record in records).sort_values("file_id")
