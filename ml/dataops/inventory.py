from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import soundfile as sf
from tqdm import tqdm


@dataclass(frozen=True)
class AudioRecord:
    dataset: str
    file_id: str
    relative_path: str
    bytes: int
    sha256: str
    sample_rate: int
    channels: int
    frames: int
    duration_s: float
    format: str
    subtype: str


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_audio(dataset: str, root: Path, path: Path) -> AudioRecord:
    info = sf.info(path)
    relative = path.relative_to(root).as_posix()
    return AudioRecord(
        dataset=dataset,
        file_id=f"{dataset}:{relative}",
        relative_path=relative,
        bytes=path.stat().st_size,
        sha256=sha256_file(path),
        sample_rate=int(info.samplerate),
        channels=int(info.channels),
        frames=int(info.frames),
        duration_s=float(info.duration),
        format=info.format,
        subtype=info.subtype,
    )


def build_inventory(dataset: str, root: Path, workers: int = 4) -> list[AudioRecord]:
    audio = sorted(path for path in root.rglob("*") if path.suffix.lower() == ".wav")
    if not audio:
        raise RuntimeError(f"No WAV files under {root}")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(
            tqdm(
                pool.map(lambda path: inspect_audio(dataset, root, path), audio),
                total=len(audio),
                desc=f"inventory:{dataset}",
            )
        )
    return records


def write_inventory(records: Iterable[AudioRecord], path: Path) -> None:
    rows = [asdict(record) for record in records]
    if not rows:
        raise ValueError("Cannot write an empty inventory")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def inventory_summary(records: list[AudioRecord]) -> dict:
    by_rate: dict[int, int] = defaultdict(int)
    by_channels: dict[int, int] = defaultdict(int)
    by_hash: dict[str, list[str]] = defaultdict(list)
    for record in records:
        by_rate[record.sample_rate] += 1
        by_channels[record.channels] += 1
        by_hash[record.sha256].append(record.file_id)
    duplicate_groups = [members for members in by_hash.values() if len(members) > 1]
    return {
        "dataset": records[0].dataset,
        "files": len(records),
        "hours": sum(record.duration_s for record in records) / 3600,
        "bytes": sum(record.bytes for record in records),
        "sample_rates": dict(sorted(by_rate.items())),
        "channels": dict(sorted(by_channels.items())),
        "exact_duplicate_groups": duplicate_groups,
    }


def write_summary(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

