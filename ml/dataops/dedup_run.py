"""Chạy ba tầng phát hiện trùng lặp trên inventory đã có (DATA_PLAN §7).

Không có pre-filter. Đo được là so khớp **đầy đủ** mọi cặp tốn khoảng 15 phút
(50 µs/cặp cỡ trung vị sau khi vector hoá vòng lag), nên một heuristic gate chỉ
thêm rủi ro bỏ sót mà không đổi được bậc thời gian.
"""

from __future__ import annotations

import csv
import itertools
from collections.abc import Iterator, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from tqdm import tqdm

from ml.dataops.duplicates import DuplicateThresholds, PairMatch
from ml.dataops.fingerprint import (
    FingerprintConfig,
    Standardizer,
    best_alignment,
    content_hash,
    fingerprint,
    fit_standardizer,
    load_pcm,
)

SHORT_FILE_FLOOR_S = 1.0


@dataclass(frozen=True)
class FileEntry:
    file_id: str
    path: Path
    dataset: str
    duration_s: float
    sha256: str
    label: str


@dataclass
class Signature:
    file_id: str
    content_sha256: str
    fingerprint: np.ndarray


def read_inventory(csv_path: Path, extracted_root: Path) -> list[FileEntry]:
    entries: list[FileEntry] = []
    with csv_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            relative = row["relative_path"]
            entries.append(
                FileEntry(
                    file_id=row["file_id"],
                    path=extracted_root / relative,
                    dataset=row["dataset"],
                    duration_s=float(row["duration_s"]),
                    sha256=row["sha256"],
                    label=relative.split("/")[1] if "/" in relative else "",
                )
            )
    if not entries:
        raise RuntimeError(f"Empty inventory: {csv_path}")
    return entries


# ---------- chữ ký ----------


def _signature_worker(payload: tuple[str, str]) -> tuple[str, str, np.ndarray]:
    file_id, path = payload
    waveform = load_pcm(Path(path))
    config = FingerprintConfig()
    return file_id, content_hash(waveform), fingerprint(waveform, config)


def compute_signatures(
    entries: Sequence[FileEntry], cache_path: Path, workers: int = 8
) -> dict[str, Signature]:
    """Decode một lần, lấy cả hash T2 lẫn fingerprint T3. Cache theo `file_id`."""
    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        file_ids = [str(value) for value in cached["file_ids"]]
        hashes = [str(value) for value in cached["content_hashes"]]
        if set(file_ids) == {entry.file_id for entry in entries}:
            return {
                file_id: Signature(file_id, digest, cached[f"fp::{index}"])
                for index, (file_id, digest) in enumerate(zip(file_ids, hashes, strict=True))
            }

    payloads = [(entry.file_id, str(entry.path)) for entry in entries]
    signatures: dict[str, Signature] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for file_id, digest, matrix in tqdm(
            pool.map(_signature_worker, payloads, chunksize=8),
            total=len(payloads),
            desc="signatures",
        ):
            signatures[file_id] = Signature(file_id, digest, matrix.astype(np.float32))

    ordered = [signatures[entry.file_id] for entry in entries]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        file_ids=np.array([item.file_id for item in ordered]),
        content_hashes=np.array([item.content_sha256 for item in ordered]),
        **{f"fp::{index}": item.fingerprint for index, item in enumerate(ordered)},
    )
    return signatures


# ---------- ba tầng ----------


def _hash_matches(
    entries: Sequence[FileEntry], digests: dict[str, str], tier: str
) -> list[PairMatch]:
    buckets: dict[str, list[str]] = {}
    for entry in entries:
        buckets.setdefault(digests[entry.file_id], []).append(entry.file_id)
    duration = {entry.file_id: entry.duration_s for entry in entries}
    matches: list[PairMatch] = []
    for members in buckets.values():
        for left, right in itertools.combinations(sorted(members), 2):
            matches.append(
                PairMatch(
                    left_file_id=left,
                    right_file_id=right,
                    tier=tier,  # type: ignore[arg-type]
                    similarity=1.0,
                    overlap_s=min(duration[left], duration[right]),
                    verdict="duplicate",
                )
            )
    return matches


def tier1_matches(entries: Sequence[FileEntry]) -> list[PairMatch]:
    return _hash_matches(entries, {entry.file_id: entry.sha256 for entry in entries}, "T1")


def tier2_matches(
    entries: Sequence[FileEntry], signatures: dict[str, Signature]
) -> list[PairMatch]:
    digests = {entry.file_id: signatures[entry.file_id].content_sha256 for entry in entries}
    return _hash_matches(entries, digests, "T2")


def required_overlap_s(left: FileEntry, right: FileEntry, thresholds: DuplicateThresholds) -> float:
    """Nới yêu cầu chồng lấp cho file ngắn, nhưng không xuống dưới sàn.

    29% clip DataSEC ngắn hơn 3 s (đo được). Giữ nguyên luật 3 s nghĩa là 1,464
    clip **không bao giờ** bị T3 đối chiếu — một lỗ thủng của cổng D3 chứ không
    phải sự thận trọng.
    """
    shorter = min(left.duration_s, right.duration_s)
    return max(min(thresholds.min_overlap_s, shorter), SHORT_FILE_FLOOR_S)


def tier3_pairs(
    left_entries: Sequence[FileEntry],
    right_entries: Sequence[FileEntry] | None,
    signatures: dict[str, Signature],
    thresholds: DuplicateThresholds,
    *,
    config: FingerprintConfig | None = None,
    desc: str = "T3",
) -> list[PairMatch]:
    """So khớp đầy đủ. `right_entries=None` nghĩa là so nội bộ `left_entries`."""
    config = config or FingerprintConfig()
    pairs = (
        itertools.combinations(left_entries, 2)
        if right_entries is None
        else itertools.product(left_entries, right_entries)
    )
    total = (
        len(left_entries) * (len(left_entries) - 1) // 2
        if right_entries is None
        else len(left_entries) * len(right_entries)
    )
    matches: list[PairMatch] = []
    for left, right in tqdm(pairs, total=total, desc=desc, mininterval=2.0):
        minimum = required_overlap_s(left, right, thresholds)
        result = best_alignment(
            signatures[left.file_id].fingerprint,
            signatures[right.file_id].fingerprint,
            config,
            min_overlap_s=minimum,
        )
        if result.overlap_frames == 0:
            continue
        verdict = thresholds.classify(
            result.similarity,
            result.overlap_s,
            required_overlap_s=minimum,
        )
        if verdict == "distinct" and result.similarity < thresholds.evidence_min:
            continue
        matches.append(
            PairMatch(
                left_file_id=left.file_id,
                right_file_id=right.file_id,
                tier="T3",
                similarity=result.similarity,
                overlap_s=result.overlap_s,
                verdict=verdict,
            )
        )
    return matches


def build_standardizer(
    signatures: Mapping[str, Signature], cache_path: Path
) -> Standardizer:
    """Ước lượng thống kê chuẩn hoá trên **toàn bộ** corpus, rồi cache lại.

    Dùng cả hai dataset là đúng ở đây: dedup chạy **trước** khi có split, và
    thống kê này không dùng nhãn nào. Nó phải được cache vì mọi ngưỡng đã hiệu
    chuẩn chỉ có nghĩa với đúng một bộ thống kê.
    """
    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        return Standardizer(mean=cached["mean"], std=cached["std"])
    standardizer = fit_standardizer([item.fingerprint for item in signatures.values()])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache_path, mean=standardizer.mean, std=standardizer.std)
    return standardizer


def standardize_signatures(
    signatures: Mapping[str, Signature], standardizer: Standardizer
) -> dict[str, Signature]:
    return {
        file_id: Signature(
            file_id, item.content_sha256, standardizer.apply(item.fingerprint)
        )
        for file_id, item in signatures.items()
    }


def unreachable_by_tier3(entries: Sequence[FileEntry]) -> list[str]:
    """File ngắn hơn cả sàn chồng lấp — T3 không thể kết luận gì về chúng."""
    return [entry.file_id for entry in entries if entry.duration_s < SHORT_FILE_FLOOR_S]


def similarity_distribution(
    entries: Sequence[FileEntry],
    signatures: dict[str, Signature],
    thresholds: DuplicateThresholds,
    *,
    sample_pairs: int,
    seed: int,
) -> np.ndarray:
    """Phân bố similarity của cặp **ngẫu nhiên khác nhãn** — negative để hiệu chuẩn."""
    config = FingerprintConfig()
    generator = np.random.default_rng(seed)
    scores: list[float] = []
    attempts = 0
    while len(scores) < sample_pairs and attempts < sample_pairs * 50:
        attempts += 1
        left, right = (entries[index] for index in generator.integers(0, len(entries), 2))
        if left.file_id == right.file_id or left.label == right.label:
            continue
        result = best_alignment(
            signatures[left.file_id].fingerprint,
            signatures[right.file_id].fingerprint,
            config,
            min_overlap_s=required_overlap_s(left, right, thresholds),
        )
        if result.overlap_frames:
            scores.append(result.similarity)
    return np.array(scores, dtype=np.float64)


def iter_positive_pairs(matches: Sequence[PairMatch]) -> Iterator[tuple[str, str]]:
    for match in matches:
        yield match.left_file_id, match.right_file_id
