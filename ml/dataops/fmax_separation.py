"""Measured fmax separation study for the D3 acoustic fingerprint."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import librosa
import numpy as np

from ml.dataops.dedup_run import FileEntry, required_overlap_s
from ml.dataops.duplicates import DuplicateThresholds
from ml.dataops.fingerprint import FingerprintConfig, best_alignment, fit_standardizer, load_pcm


@dataclass(frozen=True)
class FmaxStudyConfig:
    """Protocol constants locked before E2 measures the high-frequency classes."""

    sample_per_class: int
    top_classes: int
    cross_class_pairs: int
    seed: int
    fmax_values: tuple[float, float]
    global_negative_max: float
    allowed_excess: float


def mean_spectral_centroids(
    by_class: Mapping[str, Sequence[FileEntry]], *, sample_per_class: int, seed: int
) -> tuple[dict[str, float], dict[str, list[FileEntry]]]:
    """Sample each class deterministically before ranking its mean spectral centroid."""
    generator = np.random.default_rng(seed)
    means: dict[str, float] = {}
    samples: dict[str, list[FileEntry]] = {}
    for class_id, entries in sorted(by_class.items()):
        indices = generator.choice(
            len(entries), size=min(sample_per_class, len(entries)), replace=False
        )
        selected = [entries[int(index)] for index in indices]
        values = [
            float(librosa.feature.spectral_centroid(y=load_pcm(item.path), sr=16_000).mean())
            for item in selected
        ]
        means[class_id] = float(np.mean(values))
        samples[class_id] = selected
    return means, samples


def top_centroid_classes(centroids: Mapping[str, float], count: int) -> list[str]:
    """Return a stable ranking so labels are measured rather than guessed in advance."""
    return [
        class_id
        for class_id, _ in sorted(centroids.items(), key=lambda item: (-item[1], item[0]))[:count]
    ]


def sample_valid_cross_class_pairs(
    by_class: Mapping[str, Sequence[FileEntry]],
    matrices: Mapping[str, np.ndarray],
    *,
    count: int,
    config: FingerprintConfig,
    thresholds: DuplicateThresholds,
    seed: int,
) -> list[tuple[FileEntry, FileEntry]]:
    """Draw a fixed number of distinct-class pairs that can support T3 overlap."""
    classes = tuple(sorted(by_class))
    if len(classes) < 2:
        raise ValueError("Need at least two classes for a cross-class study")
    generator = np.random.default_rng(seed)
    pairs: list[tuple[FileEntry, FileEntry]] = []
    attempts = 0
    while len(pairs) < count and attempts < count * 50:
        attempts += 1
        left_class, right_class = generator.choice(classes, size=2, replace=False)
        left = by_class[str(left_class)][int(generator.integers(len(by_class[str(left_class)])))]
        right = by_class[str(right_class)][int(generator.integers(len(by_class[str(right_class)])))]
        result = best_alignment(
            matrices[left.file_id],
            matrices[right.file_id],
            config,
            min_overlap_s=required_overlap_s(left, right, thresholds),
        )
        if result.overlap_frames:
            pairs.append((left, right))
    if len(pairs) != count:
        raise RuntimeError(f"Only sampled {len(pairs)}/{count} valid cross-class pairs")
    return pairs


def pair_scores(
    pairs: Sequence[tuple[FileEntry, FileEntry]],
    matrices: Mapping[str, np.ndarray],
    *,
    config: FingerprintConfig,
    thresholds: DuplicateThresholds,
) -> np.ndarray:
    """Score a fixed pair list, so fmax is the only changing comparison variable."""
    scores = []
    for left, right in pairs:
        result = best_alignment(
            matrices[left.file_id],
            matrices[right.file_id],
            config,
            min_overlap_s=required_overlap_s(left, right, thresholds),
        )
        if not result.overlap_frames:
            raise RuntimeError("A pair valid at 7 kHz was invalid at the comparison fmax")
        scores.append(result.similarity)
    return np.asarray(scores, dtype=np.float64)


def standardize_selected(matrices: Mapping[str, np.ndarray]) -> tuple[dict[str, np.ndarray], str]:
    """Fit one standardizer per fmax on the same selected clips for a fair comparison."""
    standardizer = fit_standardizer(list(matrices.values()))
    standardized = {
        file_id: standardizer.apply(matrix) for file_id, matrix in matrices.items()
    }
    return standardized, standardizer.checksum


def describe_scores(scores: np.ndarray) -> dict[str, float | int]:
    """Return only distribution values declared in the E2 protocol."""
    return {
        "count": int(scores.size),
        "mean": float(scores.mean()),
        "p99": float(np.percentile(scores, 99)),
        "max": float(scores.max()),
    }


def exceeds_global_negative_guard(
    scores: Mapping[str, float | int], *, global_max: float, allowed_excess: float
) -> bool:
    """Flag a documented limitation when max or p99 exceeds the locked margin."""
    limit = global_max + allowed_excess
    return float(scores["max"]) > limit or float(scores["p99"]) > limit
