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
from ml.dataops.fingerprint import FingerprintConfig, best_alignment

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
INTERIM = ROOT / "data" / "interim" / "dedup"
STANDARDIZER_CACHE = INTERIM / "standardizer.npz"
PAIR_CACHE = INTERIM / "pair_matches.csv"
DATASETS = ("datasec", "datased")


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["signatures", "calibrate", "detect", "regroup", "cohesion"]
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--sample-pairs", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--duplicate-min", type=float, default=0.95)
    parser.add_argument("--review-min", type=float, default=0.85)
    parser.add_argument("--cohesion-min", type=float, default=COHESION_MIN_SIMILARITY)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.action == "signatures":
        command_signatures(args.workers)
    elif args.action == "calibrate":
        command_calibrate(args.sample_pairs, args.seed)
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
