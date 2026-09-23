"""Cổng D3: phát hiện trùng lặp T1/T2/T3, nội bộ và xuyên dataset.

    .venv/Scripts/python.exe -m scripts.find_duplicates signatures
    .venv/Scripts/python.exe -m scripts.find_duplicates calibrate
    .venv/Scripts/python.exe -m scripts.find_duplicates detect

`signatures` decode và cache; `calibrate` hiệu chuẩn ngưỡng T3 (nợ kỹ thuật #7);
`detect` chạy ba tầng và ghi `duplicate_groups.csv` + `exclusions.csv`.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml

from ml.dataops.datasec_labels import labels_by_file_id
from ml.dataops.dedup_run import (
    FileEntry,
    Signature,
    build_standardizer,
    compute_signatures,
    read_inventory,
    required_overlap_s,
    similarity_distribution,
    standardize_signatures,
    tier1_matches,
    tier2_matches,
    tier3_pairs,
    unreachable_by_tier3,
)
from ml.dataops.duplicates import (
    COHESION_MIN_SIMILARITY,
    DuplicateGroup,
    DuplicateThresholds,
    Exclusion,
    PairMatch,
    assess_alarm,
    build_groups,
    collect_review_pairs,
    human_review_queue,
    split_cohesion_pairs,
    within_dataset_exclusions,
)
from ml.dataops.fingerprint import FingerprintConfig, best_alignment, fingerprint, load_pcm
from ml.dataops.fmax_separation import (
    FmaxStudyConfig,
    describe_scores,
    exceeds_global_negative_guard,
    mean_spectral_centroids,
    pair_scores,
    sample_valid_cross_class_pairs,
    standardize_selected,
    top_centroid_classes,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
INTERIM = ROOT / "data" / "interim" / "dedup"
STANDARDIZER_CACHE = INTERIM / "standardizer.npz"
PAIR_CACHE = INTERIM / "pair_matches.csv"
DATASETS = ("datasec", "datased")
SHORT_CALIBRATION_CONFIG = ROOT / "ml" / "configs" / "short_duplicate_calibration.yaml"
SHORT_CALIBRATION_ARTIFACT = INTERIM / "short_threshold_calibration.json"
SHORT_CALIBRATION_REPORT = (
    ROOT / "docs" / "measurements" / "short_duplicate_calibration_20260923.md"
)
FMAX_STUDY_CONFIG = ROOT / "ml" / "configs" / "fmax_separation.yaml"
FMAX_STUDY_ARTIFACT = INTERIM / "fmax_high_frequency_separation_20260923.json"
FMAX_STUDY_REPORT = ROOT / "docs" / "measurements" / "fmax_high_frequency_separation_20260923.md"


def load_entries(dataset: str) -> list[FileEntry]:
    return read_inventory(
        MANIFESTS / f"{dataset}_inventory.csv",
        ROOT / "data" / "raw" / dataset / "extracted",
    )


def load_raw_signatures(entries: dict[str, list[FileEntry]]) -> dict[str, Signature]:
    return {
        file_id: signature
        for dataset, items in entries.items()
        for file_id, signature in compute_signatures(
            items, INTERIM / f"{dataset}_signatures.npz"
        ).items()
    }


def load_standardized(
    entries: dict[str, list[FileEntry]],
) -> tuple[dict[str, Signature], dict[str, Signature], str]:
    """Chữ ký chuẩn hoá bằng **đúng một** bộ thống kê cho cả hai dataset.

    Ngưỡng đã hiệu chuẩn chỉ có nghĩa với bộ thống kê đã dùng lúc hiệu chuẩn,
    nên checksum của nó phải đi vào mọi artifact. Trả về `(raw, standardized, sha)`.
    """
    raw = load_raw_signatures(entries)
    standardizer = build_standardizer(raw, STANDARDIZER_CACHE)
    return raw, standardize_signatures(raw, standardizer), standardizer.checksum


# ---------- lệnh ----------


def command_signatures(workers: int) -> None:
    for dataset in DATASETS:
        entries = load_entries(dataset)
        signatures = compute_signatures(entries, INTERIM / f"{dataset}_signatures.npz", workers)
        print(f"{dataset}: {len(signatures)} signatures")


def command_calibrate(sample_pairs: int, seed: int) -> None:
    """Hiệu chuẩn ngưỡng T3 bằng positive thật và negative thật (DATA_PLAN §7.3)."""
    thresholds = DuplicateThresholds()
    config = FingerprintConfig()
    entries = {dataset: load_entries(dataset) for dataset in DATASETS}
    _, signatures, standardizer_sha = load_standardized(entries)

    positives: list[float] = []
    negatives: list[float] = []
    for dataset in DATASETS:
        items = entries[dataset]
        by_id = {entry.file_id: entry for entry in items}
        for match in tier1_matches(items):
            left, right = by_id[match.left_file_id], by_id[match.right_file_id]
            positives.append(
                best_alignment(
                    signatures[left.file_id].fingerprint,
                    signatures[right.file_id].fingerprint,
                    config,
                    min_overlap_s=required_overlap_s(left, right, thresholds),
                ).similarity
            )
        negatives.extend(
            similarity_distribution(
                items, signatures, thresholds, sample_pairs=sample_pairs, seed=seed
            ).tolist()
        )

    positive = np.array(positives)
    negative = np.array(negatives)
    report = {
        "fingerprint_sha256": config.checksum,
        "standardizer_sha256": standardizer_sha,
        "seed": seed,
        "positives": _describe(positive, "T1 byte-identical pairs"),
        "negatives": _describe(negative, "random cross-label pairs"),
        "separation": {
            "positive_min": float(positive.min()) if positive.size else None,
            "negative_max": float(negative.max()) if negative.size else None,
            "negative_p999": float(np.percentile(negative, 99.9)) if negative.size else None,
            "separated": bool(
                positive.size and negative.size and positive.min() > negative.max()
            ),
        },
        "default_thresholds": asdict(thresholds),
        "negative_above_review_min": int((negative >= thresholds.review_min).sum()),
        "negative_above_duplicate_min": int((negative >= thresholds.duplicate_min).sum()),
    }
    _write_json(INTERIM / "threshold_calibration.json", report)
    print(json.dumps(report["separation"], indent=2))
    print(
        f"negatives >= {thresholds.review_min}: {report['negative_above_review_min']}"
        f" / {negative.size}"
        f" | >= {thresholds.duplicate_min}: {report['negative_above_duplicate_min']}"
    )


def load_short_calibration_config(path: Path) -> dict:
    """Read the fully locked E1 protocol instead of inferring its pair choices."""
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {
        "durations_s",
        "sample_pairs",
        "seed",
        "short_duplicate_min",
        "positive_cross_dataset_pairs",
    }
    if not isinstance(config, dict) or required.difference(config):
        raise ValueError(f"Invalid short calibration config: {path}")
    return config


def require_short_calibration_caches() -> None:
    """Refuse to decode audio: E1 must assess the exact cached standardized signatures."""
    required = [STANDARDIZER_CACHE, *(INTERIM / f"{name}_signatures.npz" for name in DATASETS)]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing cached signatures for E1: {missing}")


def cropped_similarity(
    left: np.ndarray, right: np.ndarray, duration_s: float, config: FingerprintConfig
) -> float | None:
    """Compare matching leading windows; None means a pair cannot evidence this duration."""
    frames = config.frames_for_seconds(duration_s)
    match = best_alignment(left[:frames], right[:frames], config, min_overlap_s=duration_s)
    return None if match.overlap_frames == 0 else float(match.similarity)


def short_negative_distribution(
    entries: list[FileEntry],
    signatures: dict[str, Signature],
    *,
    duration_s: float,
    config: FingerprintConfig,
    sample_pairs: int,
    seed: int,
) -> np.ndarray:
    """Sample exactly the requested valid cross-label negatives from cached matrices."""
    generator = np.random.default_rng(seed)
    scores: list[float] = []
    attempts = 0
    while len(scores) < sample_pairs and attempts < sample_pairs * 50:
        attempts += 1
        left, right = (entries[index] for index in generator.integers(0, len(entries), 2))
        if left.file_id == right.file_id or left.label == right.label:
            continue
        similarity = cropped_similarity(
            signatures[left.file_id].fingerprint,
            signatures[right.file_id].fingerprint,
            duration_s,
            config,
        )
        if similarity is not None:
            scores.append(similarity)
    if len(scores) != sample_pairs:
        raise RuntimeError(
            f"Only sampled {len(scores)}/{sample_pairs} valid negatives at {duration_s}s"
        )
    return np.asarray(scores, dtype=np.float64)


def confirmed_short_positive_pairs(
    entries: dict[str, list[FileEntry]], protocol: dict
) -> tuple[list[tuple[str, str]], int]:
    """Collect all T1 positives plus the two known cross-dataset duplicate pairs."""
    known_ids = {entry.file_id for items in entries.values() for entry in items}
    tier1 = [
        (match.left_file_id, match.right_file_id)
        for items in entries.values()
        for match in tier1_matches(items)
    ]
    cross = [
        (str(item["left"]), str(item["right"]))
        for item in protocol["positive_cross_dataset_pairs"]
    ]
    missing = {file_id for pair in cross for file_id in pair}.difference(known_ids)
    if missing:
        raise ValueError(f"Configured cross-dataset positives do not exist: {sorted(missing)}")
    return tier1 + cross, len(tier1)


def short_calibration_report(report: dict) -> str:
    """Render the E1 evidence from the JSON artifact, never transcribed measurements."""
    lines = [
        "# Short-duplicate threshold calibration",
        "",
        "> Generated by `scripts.find_duplicates calibrate-short` from cached standardized "
        "fingerprints; no audio was decoded.",
        "",
        f"- Fingerprint config SHA-256: `{report['fingerprint_sha256']}`",
        f"- Standardizer SHA-256: `{report['standardizer_sha256']}`",
        f"- Positives: {report['positive_pairs']['total']} "
        f"({report['positive_pairs']['tier1']} T1 + "
        f"{report['positive_pairs']['cross_dataset']} known cross-dataset)",
        f"- Negatives: {report['sample_pairs']} cached DataSEC cross-label pairs per duration; "
        f"seed {report['seed']}",
        "",
        "| Duration (s) | Frames | Positive min | Negative max | `0.99` separated? |",
        "|---:|---:|---:|---:|---|",
    ]
    for duration, result in report["durations"].items():
        lines.append(
            f"| {float(duration):.1f} | {result['frames']} | {result['positive_min']:.6f} | "
            f"{result['negative_max']:.6f} | "
            f"{'yes' if result['separated_at_threshold'] else 'no'} |"
        )
    decision = "kept" if report["keep_short_duplicate_min"] else "not changed automatically"
    lines += [
        "",
        f"**Decision:** `short_duplicate_min = {report['short_duplicate_min']:.2f}` is {decision}. "
        "A failed duration requires an ADR; this command never changes the gate threshold.",
    ]
    return "\n".join(lines) + "\n"


def command_calibrate_short(config_path: Path = SHORT_CALIBRATION_CONFIG) -> None:
    """Run E1 sensitivity/false-positive evidence without changing D3 verdicts."""
    protocol = load_short_calibration_config(config_path)
    require_short_calibration_caches()
    entries = {dataset: load_entries(dataset) for dataset in DATASETS}
    _, signatures, standardizer_sha = load_standardized(entries)
    prior = json.loads((INTERIM / "threshold_calibration.json").read_text(encoding="utf-8"))
    if prior["standardizer_sha256"] != standardizer_sha:
        raise RuntimeError("Cached standardizer differs from the threshold-calibration artifact")
    fingerprint_config = FingerprintConfig()
    positives, tier1_count = confirmed_short_positive_pairs(entries, protocol)
    durations: dict[str, dict] = {}
    threshold = float(protocol["short_duplicate_min"])
    for duration in (float(value) for value in protocol["durations_s"]):
        positive_scores = [
            cropped_similarity(
                signatures[left].fingerprint,
                signatures[right].fingerprint,
                duration,
                fingerprint_config,
            )
            for left, right in positives
        ]
        if any(score is None for score in positive_scores):
            raise RuntimeError(f"A confirmed positive cannot support {duration}s")
        negative_scores = short_negative_distribution(
            entries["datasec"],
            signatures,
            duration_s=duration,
            config=fingerprint_config,
            sample_pairs=int(protocol["sample_pairs"]),
            seed=int(protocol["seed"]),
        )
        positive_min = float(min(score for score in positive_scores if score is not None))
        negative_max = float(negative_scores.max())
        durations[f"{duration:.1f}"] = {
            "frames": fingerprint_config.frames_for_seconds(duration),
            "positive_count": len(positive_scores),
            "positive_min": positive_min,
            "negative_count": int(negative_scores.size),
            "negative_max": negative_max,
            "separated_at_threshold": negative_max < threshold <= positive_min,
        }
    report = {
        "fingerprint_sha256": fingerprint_config.checksum,
        "standardizer_sha256": standardizer_sha,
        "seed": int(protocol["seed"]),
        "sample_pairs": int(protocol["sample_pairs"]),
        "short_duplicate_min": threshold,
        "positive_pairs": {
            "tier1": tier1_count,
            "cross_dataset": len(positives) - tier1_count,
            "total": len(positives),
        },
        "durations": durations,
        "keep_short_duplicate_min": all(
            item["separated_at_threshold"] for item in durations.values()
        ),
    }
    _write_json(SHORT_CALIBRATION_ARTIFACT, report)
    SHORT_CALIBRATION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    SHORT_CALIBRATION_REPORT.write_text(short_calibration_report(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def load_fmax_study_config(path: Path) -> FmaxStudyConfig:
    """Load every E2 sampling and decision constant from its locked YAML config."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {
        "sample_per_class",
        "top_classes",
        "cross_class_pairs",
        "seed",
        "fmax_values",
        "global_negative_max",
        "allowed_excess",
    }
    if not isinstance(payload, dict) or required.difference(payload):
        raise ValueError(f"Invalid fmax study config: {path}")
    values = tuple(float(value) for value in payload["fmax_values"])
    if len(values) != 2:
        raise ValueError("E2 requires exactly two fmax values")
    return FmaxStudyConfig(
        sample_per_class=int(payload["sample_per_class"]),
        top_classes=int(payload["top_classes"]),
        cross_class_pairs=int(payload["cross_class_pairs"]),
        seed=int(payload["seed"]),
        fmax_values=(values[0], values[1]),
        global_negative_max=float(payload["global_negative_max"]),
        allowed_excess=float(payload["allowed_excess"]),
    )


def fmax_study_report(report: dict) -> str:
    """Render the E2 evidence including its pre-registered global-negative guard."""
    lines = [
        "# fmax high-frequency separation study",
        "",
        "> Generated by `scripts.find_duplicates study-fmax`. High-frequency classes were "
        "selected by measured spectral centroid, not by a pre-chosen label name.",
        "",
        "## Spectral-centroid selection",
        "",
        "| Coarse class | Mean centroid (Hz) | Sampled clips |",
        "|---|---:|---:|",
    ]
    lines.extend(
        f"| `{item['class_id']}` | {item['centroid_hz']:.2f} | {item['samples']} |"
        for item in report["top_classes"]
    )
    lines += [
        "",
        "## Cross-class T3 similarity (2,000 fixed pairs)",
        "",
        "| fmax / standardization | Mean | p99 | Max |",
        "|---|---:|---:|---:|",
    ]
    for name, values in report["similarities"].items():
        lines.append(
            f"| {name} | {values['mean']:.6f} | {values['p99']:.6f} | {values['max']:.6f} |"
        )
    limit = report["global_negative_max"] + report["allowed_excess"]
    conclusion = "exceeds" if report["fmax7000_exceeds_guard"] else "does not exceed"
    lines += [
        "",
        "## Guard for the deployed fmax=7000 fingerprint",
        "",
        f"The cached-global fmax=7000 p99/max {conclusion} the locked limit "
        f"**{limit:.6f}** (= global negative max {report['global_negative_max']:.6f} + 0.01).",
        "If it exceeds, this is a documented limitation; the command does not change `fmax`.",
    ]
    return "\n".join(lines) + "\n"


def command_study_fmax(config_path: Path = FMAX_STUDY_CONFIG) -> None:
    """Measure whether removing 7–8 kHz weakens T3 separation for selected classes."""
    study = load_fmax_study_config(config_path)
    entries = {dataset: load_entries(dataset) for dataset in DATASETS}
    raw, standardized, standardizer_sha = load_standardized(entries)
    config_7000 = FingerprintConfig(fmax=study.fmax_values[0])
    config_8000 = FingerprintConfig(fmax=study.fmax_values[1])
    prior = json.loads((INTERIM / "threshold_calibration.json").read_text(encoding="utf-8"))
    if prior["fingerprint_sha256"] != config_7000.checksum:
        raise RuntimeError("The cached raw signatures are not the configured fmax=7000 fingerprint")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    labels = labels_by_file_id(MANIFESTS / "datasec_inventory.csv", taxonomy)
    by_class = {class_id: [] for class_id in taxonomy.class_ids}
    for entry in entries["datasec"]:
        if entry.file_id not in labels:
            raise RuntimeError(f"DataSEC inventory label missing: {entry.file_id}")
        by_class[labels[entry.file_id][0]].append(entry)
    centroids, samples = mean_spectral_centroids(
        by_class, sample_per_class=study.sample_per_class, seed=study.seed
    )
    top_classes = top_centroid_classes(centroids, study.top_classes)
    selected = {class_id: samples[class_id] for class_id in top_classes}
    selected_entries = [entry for values in selected.values() for entry in values]
    raw_7000 = {entry.file_id: raw[entry.file_id].fingerprint for entry in selected_entries}
    thresholds = DuplicateThresholds()
    pairs = sample_valid_cross_class_pairs(
        selected,
        raw_7000,
        count=study.cross_class_pairs,
        config=config_7000,
        thresholds=thresholds,
        seed=study.seed,
    )
    cached_global = {
        entry.file_id: standardized[entry.file_id].fingerprint for entry in selected_entries
    }
    cached_global_scores = pair_scores(
        pairs, cached_global, config=config_7000, thresholds=thresholds
    )
    selected_7000, selected_7000_sha = standardize_selected(raw_7000)
    selected_7000_scores = pair_scores(
        pairs, selected_7000, config=config_7000, thresholds=thresholds
    )
    raw_8000 = {
        entry.file_id: fingerprint(load_pcm(entry.path), config_8000) for entry in selected_entries
    }
    selected_8000, selected_8000_sha = standardize_selected(raw_8000)
    selected_8000_scores = pair_scores(
        pairs, selected_8000, config=config_8000, thresholds=thresholds
    )
    cached_summary = describe_scores(cached_global_scores)
    report = {
        "seed": study.seed,
        "sample_per_class": study.sample_per_class,
        "pair_count": len(pairs),
        "fingerprint_sha256": {"fmax7000": config_7000.checksum, "fmax8000": config_8000.checksum},
        "cached_standardizer_sha256": standardizer_sha,
        "selected_standardizer_sha256": {
            "fmax7000": selected_7000_sha,
            "fmax8000": selected_8000_sha,
        },
        "top_classes": [
            {
                "class_id": class_id,
                "centroid_hz": centroids[class_id],
                "samples": len(samples[class_id]),
            }
            for class_id in top_classes
        ],
        "similarities": {
            "fmax7000 cached-global z-score": cached_summary,
            "fmax7000 selected-sample z-score": describe_scores(selected_7000_scores),
            "fmax8000 selected-sample z-score": describe_scores(selected_8000_scores),
        },
        "global_negative_max": study.global_negative_max,
        "allowed_excess": study.allowed_excess,
        "fmax7000_exceeds_guard": exceeds_global_negative_guard(
            cached_summary,
            global_max=study.global_negative_max,
            allowed_excess=study.allowed_excess,
        ),
    }
    _write_json(FMAX_STUDY_ARTIFACT, report)
    FMAX_STUDY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    FMAX_STUDY_REPORT.write_text(fmax_study_report(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _describe(values: np.ndarray, label: str) -> dict:
    if values.size == 0:
        return {"label": label, "count": 0}
    return {
        "label": label,
        "count": int(values.size),
        "min": float(values.min()),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "p99": float(np.percentile(values, 99)),
        "max": float(values.max()),
    }


def write_pair_cache(path: Path, matches: list[PairMatch]) -> None:
    """Lưu mọi cặp đã khớp. So khớp T3 tốn khoảng 45 phút; cách gom nhóm thì có
    thể phải sửa nhiều lần. Tách hai việc ra để lần sau `regroup` chạy trong giây."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            ["left_file_id", "right_file_id", "tier", "similarity", "overlap_s", "verdict"]
        )
        for match in matches:
            writer.writerow(
                [
                    match.left_file_id,
                    match.right_file_id,
                    match.tier,
                    f"{match.similarity:.6f}",
                    f"{match.overlap_s:.3f}",
                    match.verdict,
                ]
            )


def read_pair_cache(path: Path) -> list[PairMatch]:
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Chạy `detect` trước khi `regroup`.")
    with path.open(encoding="utf-8") as handle:
        return [
            PairMatch(
                left_file_id=row["left_file_id"],
                right_file_id=row["right_file_id"],
                tier=row["tier"],  # type: ignore[arg-type]
                similarity=float(row["similarity"]),
                overlap_s=float(row["overlap_s"]),
                verdict=row["verdict"],  # type: ignore[arg-type]
            )
            for row in csv.DictReader(handle)
        ]


def reclassify(
    matches: list[PairMatch],
    entries: dict[str, list[FileEntry]],
    thresholds: DuplicateThresholds,
) -> list[PairMatch]:
    """Tính lại verdict từ số đo thô theo ngưỡng **hiện hành**.

    Cache giữ `similarity` và `overlap_s` — là số đo. `verdict` là diễn giải, và
    diễn giải phải đi theo ngưỡng đang dùng, không phải ngưỡng lúc chạy `detect`.
    Tin vào verdict đã lưu nghĩa là đổi ngưỡng xong vẫn ra kết quả cũ.
    """
    by_id = {entry.file_id: entry for items in entries.values() for entry in items}
    rebuilt: list[PairMatch] = []
    for match in matches:
        left, right = by_id[match.left_file_id], by_id[match.right_file_id]
        verdict = thresholds.classify(
            match.similarity,
            match.overlap_s,
            required_overlap_s=required_overlap_s(left, right, thresholds),
        )
        if match.tier in {"T1", "T2"}:
            verdict = "duplicate"
        rebuilt.append(
            PairMatch(
                left_file_id=match.left_file_id,
                right_file_id=match.right_file_id,
                tier=match.tier,
                similarity=match.similarity,
                overlap_s=match.overlap_s,
                verdict=verdict,
            )
        )
    return rebuilt


def command_regroup(thresholds: DuplicateThresholds) -> None:
    """Gom nhóm lại từ cache, không chạy lại so khớp."""
    entries = {dataset: load_entries(dataset) for dataset in DATASETS}
    audit = json.loads((MANIFESTS / "duplicate_audit.json").read_text(encoding="utf-8"))
    _finalise(
        reclassify(read_pair_cache(PAIR_CACHE), entries, thresholds),
        entries,
        thresholds,
        standardizer_sha=audit["standardizer_sha256"],
    )


def command_detect(thresholds: DuplicateThresholds) -> None:
    entries = {dataset: load_entries(dataset) for dataset in DATASETS}
    raw, signatures, standardizer_sha = load_standardized(entries)

    matches: list[PairMatch] = []
    for dataset, items in entries.items():
        matches.extend(tier1_matches(items))
        matches.extend(tier2_matches(items, raw))
        matches.extend(tier3_pairs(items, None, signatures, thresholds, desc=f"T3:{dataset}"))
    matches.extend(
        tier3_pairs(
            entries["datasec"], entries["datased"], signatures, thresholds, desc="T3:cross"
        )
    )

    write_pair_cache(PAIR_CACHE, matches)
    _finalise(matches, entries, thresholds, standardizer_sha=standardizer_sha)


def _finalise(
    matches: list[PairMatch],
    entries: dict[str, list[FileEntry]],
    thresholds: DuplicateThresholds,
    *,
    standardizer_sha: str,
) -> None:
    groups = build_groups(matches)
    review_pairs = collect_review_pairs(matches)
    queue = human_review_queue(matches)
    cohesion = split_cohesion_pairs(matches)
    exclusions = within_dataset_exclusions(groups)
    alarm = assess_alarm(
        exclusions,
        total_pretraining_files=len(entries["datasec"]),
        pending_review_groups=len(queue),
    )

    _write_groups(MANIFESTS / "duplicate_groups.csv", groups)
    _write_exclusions(MANIFESTS / "exclusions.csv", exclusions)
    write_pair_cache(MANIFESTS / "review_pairs.csv", review_pairs)
    write_pair_cache(MANIFESTS / "review_queue_cross_dataset.csv", queue)
    _write_cohesion(MANIFESTS / "split_cohesion_pairs.csv", cohesion)
    _write_json(
        MANIFESTS / "duplicate_audit.json",
        {
            "thresholds": asdict(thresholds),
            "fingerprint_sha256": FingerprintConfig().checksum,
            "standardizer_sha256": standardizer_sha,
            "files": {dataset: len(items) for dataset, items in entries.items()},
            "pairs_by_tier": _count_by_tier(matches),
            "groups": len(groups),
            "cross_dataset_groups": sum(1 for group in groups if group.cross_dataset),
            "review_pairs": len(review_pairs),
            "review_queue_cross_dataset": len(queue),
            "split_cohesion_pairs": len(cohesion),
            "unreachable_by_tier3": {
                dataset: unreachable_by_tier3(items) for dataset, items in entries.items()
            },
            "alarm": asdict(alarm),
            "cross_dataset_exclusions_pending_split": True,
        },
    )
    print(
        json.dumps(
            {
                "groups": len(groups),
                "cross_dataset_groups": sum(1 for group in groups if group.cross_dataset),
                "review_pairs": len(review_pairs),
                "review_queue_cross_dataset": len(queue),
                "split_cohesion_pairs": len(cohesion),
                "alarm": alarm.band,
            },
            indent=2,
        )
    )


def _count_by_tier(matches: list[PairMatch]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in matches:
        counts[match.tier] = counts.get(match.tier, 0) + 1
    return counts


def _write_groups(path: Path, groups: list[DuplicateGroup]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "group_id",
                "file_id",
                "datasets",
                "tiers",
                "min_similarity",
                "cross_dataset",
                "needs_review",
            ]
        )
        for group in groups:
            for member in group.members:
                writer.writerow(
                    [
                        group.group_id,
                        member,
                        "|".join(group.datasets),
                        "|".join(group.tiers),
                        f"{group.min_similarity:.6f}",
                        str(group.cross_dataset).lower(),
                        str(group.needs_review).lower(),
                    ]
                )


def _write_cohesion(path: Path, pairs: list[tuple[str, str]]) -> None:
    """Ràng buộc "cùng split" cho create_splits. Không phải loại trừ."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["left_file_id", "right_file_id"])
        writer.writerows(pairs)


def _write_exclusions(path: Path, exclusions: list[Exclusion]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file_id", "group_id", "reason_code", "decided_by"])
        for item in exclusions:
            writer.writerow([item.file_id, item.group_id, item.reason_code, item.decided_by])


def command_cohesion(min_similarity: float) -> None:
    """Ghi lại **chỉ** `split_cohesion_pairs.csv` từ `review_pairs.csv`.

    Cố ý không dùng `regroup`: `_finalise` ghi đè `exclusions.csv` bằng luật nội
    bộ, tức xoá sạch 11 quyết định của người và đặt lại
    `cross_dataset_exclusions_pending_split`. Ngưỡng cohesion không liên quan gì
    tới những thứ đó, nên nó không được phép chạm vào.
    """
    matches = read_pair_cache(MANIFESTS / "review_pairs.csv")
    cohesion = split_cohesion_pairs(matches, min_similarity=min_similarity)
    before = split_cohesion_pairs(matches, min_similarity=0.0)
    _write_cohesion(MANIFESTS / "split_cohesion_pairs.csv", cohesion)
    print(
        json.dumps(
            {
                "cohesion_min_similarity": min_similarity,
                "pairs_before": len(before),
                "pairs_kept": len(cohesion),
                "pairs_dropped": len(before) - len(cohesion),
            },
            indent=2,
        )
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "signatures",
            "calibrate",
            "calibrate-short",
            "study-fmax",
            "detect",
            "regroup",
            "cohesion",
        ],
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--sample-pairs", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--duplicate-min", type=float, default=0.95)
    parser.add_argument("--review-min", type=float, default=0.85)
    parser.add_argument("--cohesion-min", type=float, default=COHESION_MIN_SIMILARITY)
    args = parser.parse_args()
    if args.action == "signatures":
        command_signatures(args.workers)
    elif args.action == "calibrate":
        command_calibrate(args.sample_pairs, args.seed)
    elif args.action == "calibrate-short":
        command_calibrate_short()
    elif args.action == "study-fmax":
        command_study_fmax()
    elif args.action == "cohesion":
        command_cohesion(args.cohesion_min)
    elif args.action == "regroup":
        command_regroup(
            DuplicateThresholds(duplicate_min=args.duplicate_min, review_min=args.review_min)
        )
    else:
        command_detect(
            DuplicateThresholds(duplicate_min=args.duplicate_min, review_min=args.review_min)
        )


if __name__ == "__main__":
    main()
