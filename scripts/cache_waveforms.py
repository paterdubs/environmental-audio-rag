"""Cache DataSED recordings as 16 kHz PCM for frozen waveform encoders (Track 2a, ADR-0032 §2).

    .venv/Scripts/python.exe -m scripts.cache_waveforms [--workers 4]

Same loader as the log-mel features (`librosa.load(sr=16000, mono=True)`, librosa's default
soxr_hq resampler), stored as 16-bit PCM like the source WAVs, one `.npy` per recording under
`data/cache/datased_wav16k/`. Relative paths are those of `logmel_panns_v1`, so a recording's
feature path is also its waveform path. Every split is cached: this is input preprocessing like
the log-mel features that already exist for test, not a model output (ADR-0032 §2 keeps test
*embeddings* until after the final selection). Writes `data/manifests/datased_wav16k.csv`.

`--source datasec_o_f` caches the O-F pool instead (ADR-0041 §10: `datasec_o_f_pool.csv`, train
split of DataSEC v4 only) to `data/cache/datasec_o_f_wav16k/`, after checking every WAV against
the SHA-256 recorded in the pool; writes `data/manifests/datasec_o_f_wav16k.csv`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 16_000
CACHE_NAME = "datased_wav16k"
AUDIO_ROOT = ROOT / "data" / "raw" / "datased" / "extracted"
CACHE_ROOT = ROOT / "data" / "cache" / CACHE_NAME
MANIFEST = ROOT / "data" / "manifests" / f"{CACHE_NAME}.csv"
DATASEC_AUDIO_ROOT = ROOT / "data" / "raw" / "datasec" / "extracted"
O_F_POOL = ROOT / "data" / "manifests" / "datasec_o_f_pool.csv"
O_F_CACHE_NAME = "datasec_o_f_wav16k"


def to_pcm16(waveform: np.ndarray) -> np.ndarray:
    """Float waveform in [-1, 1] -> int16, rounding and clipping resampler overshoot."""
    return np.clip(np.round(waveform * 32768.0), -32768, 32767).astype(np.int16)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cache_one(audio_relative_path: str, relative_path: str, *, audio_root: Path = AUDIO_ROOT,
              cache_root: Path = CACHE_ROOT, expected_sha256: str | None = None
              ) -> dict[str, object]:
    destination = cache_root / relative_path
    if not destination.exists():
        source = audio_root / audio_relative_path
        if expected_sha256 is not None and _sha256(source) != expected_sha256:
            raise ValueError(f"{source}: SHA-256 differs from the pool manifest")
        waveform, _ = librosa.load(source, sr=SAMPLE_RATE, mono=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".npy.tmp")
        with temporary.open("wb") as handle:
            np.save(handle, to_pcm16(waveform), allow_pickle=False)
        temporary.replace(destination)
    samples = np.load(destination, mmap_mode="r", allow_pickle=False).shape[0]
    return {"feature_relative_path": relative_path, "samples": int(samples),
            "sha256": _sha256(destination)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--source", choices=("datased", "datasec_o_f"), default="datased")
    args = parser.parse_args()
    if args.source == "datasec_o_f":
        cache_o_f_pool(args.workers)
        return
    features = pd.read_csv(ROOT / "data" / "manifests" / "datased_logmel_panns_v1.csv")
    rows = list(zip(features["audio_relative_path"], features["feature_relative_path"],
                    strict=True))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(tqdm(pool.map(lambda row: cache_one(*row), rows), total=len(rows),
                            desc=CACHE_NAME))
    table = features[["file_id", "audio_relative_path", "feature_relative_path"]].merge(
        pd.DataFrame(records), on="feature_relative_path", validate="one_to_one")
    table["sample_rate"] = SAMPLE_RATE
    table.sort_values("file_id").to_csv(MANIFEST, index=False, lineterminator="\n")
    MANIFEST.with_suffix(".json").write_text(json.dumps({
        "sample_rate": SAMPLE_RATE, "dtype": "int16", "loader": "librosa.load(mono=True)",
        "librosa": librosa.__version__, "res_type": "soxr_hq (librosa default)",
    }, indent=2), encoding="utf-8")
    print(f"wrote {len(table)} rows to {MANIFEST}; "
          f"{table['samples'].sum() / SAMPLE_RATE / 3600:.2f} h cached")


def o_f_relative_path(audio_relative_path: str) -> str:
    return str(Path(audio_relative_path).with_suffix(".npy").as_posix())


def cache_o_f_pool(workers: int) -> None:
    """ADR-0041 §10: the DataSEC O-F pool as 16 kHz PCM, hash-checked against the pool."""
    pool = pd.read_csv(O_F_POOL)
    cache_root = ROOT / "data" / "cache" / O_F_CACHE_NAME
    rows = list(zip(pool["relative_path"], pool["sha256"], strict=True))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        records = list(tqdm(executor.map(
            lambda row: cache_one(row[0], o_f_relative_path(row[0]), audio_root=DATASEC_AUDIO_ROOT,
                                  cache_root=cache_root, expected_sha256=row[1]), rows),
            total=len(rows), desc=O_F_CACHE_NAME))
    table = pool[["file_id", "class_id", "relative_path"]].rename(
        columns={"relative_path": "audio_relative_path"}).assign(
        feature_relative_path=[o_f_relative_path(p) for p in pool["relative_path"]]).merge(
        pd.DataFrame(records), on="feature_relative_path", validate="one_to_one")
    table["sample_rate"] = SAMPLE_RATE
    manifest = ROOT / "data" / "manifests" / f"{O_F_CACHE_NAME}.csv"
    table.sort_values("file_id").to_csv(manifest, index=False, lineterminator="\n")
    print(f"wrote {len(table)} rows to {manifest}; "
          f"{table['samples'].sum() / SAMPLE_RATE / 3600:.2f} h cached")


if __name__ == "__main__":
    main()
