"""Giai đoạn O, tầng C (ADR-0041 §2): chia train ∪ dev annotated thành 5 fold cho OOF.

    .venv/Scripts/python.exe -m scripts.make_cv_folds          # ghi datased_trainval_folds.*
    .venv/Scripts/python.exe -m scripts.make_cv_folds --check  # chỉ kiểm file đã có

Vì sao: dev chỉ 134 recording có GT nên thứ hạng CV dev không ổn định (S40). Dùng lại toàn bộ
phần không phải test (khoảng 564 recording) cho dự đoán out-of-fold cho phép chọn hệ thống trên
gấp 4 lần dữ liệu mà **không** chạm test. Split đóng băng không đổi; file fold chỉ là cách dùng lại
`train`/`validation`.

Luật chia (ghi trước, tất định):
- Đơn vị là `leakage_group` (bản trùng, cụm D3 luôn cùng fold, không bao giờ train một bản rồi
  chấm bản kia).
- Recording thiếu GT polyphonic (ADR-0034) không vào fold nào.
- Phân tầng tham lam: xét nhóm theo lớp hiếm nhất của nó trước (tie: hash seed), gán vào fold làm
  nhỏ nhất tổng bình phương (đếm/đích) theo số recording có mặt mỗi lớp và số recording.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260922
N_FOLDS = 5
OUT = ROOT / "data" / "splits" / "datased_trainval_folds.csv"


def presence_matrix(events: pd.DataFrame, recording_ids: list[str],
                    class_ids: tuple[str, ...]) -> np.ndarray:
    """[recording, class] = 1 when the recording has at least one event of the class."""
    index = {r: i for i, r in enumerate(recording_ids)}
    matrix = np.zeros((len(recording_ids), len(class_ids)), dtype=np.int64)
    column = {c: j for j, c in enumerate(class_ids)}
    for row in events[events["recording_id"].isin(index)].itertuples(index=False):
        matrix[index[str(row.recording_id)], column[str(row.class_id)]] = 1
    return matrix


def assign_group_folds(groups: list[str], counts: np.ndarray, k: int) -> list[int]:
    """`counts[g]` = [recordings, presence per class] of group g. Returns fold per group."""
    target = counts.sum(axis=0) / k
    target[target == 0] = 1.0
    rarity = np.where(counts[:, 1:] > 0, 1.0 / np.maximum(counts.sum(axis=0)[1:], 1), 0.0)
    order = sorted(range(len(groups)), key=lambda g: (-rarity[g].max(), hashlib.sha256(
        f"{SEED}:{groups[g]}".encode()).hexdigest()))
    totals = np.zeros((k, counts.shape[1]), dtype=np.float64)
    folds = [0] * len(groups)
    for g in order:
        cost = (((totals + counts[g]) / target) ** 2).sum(axis=1)
        best = int(np.argmin(cost))
        folds[g] = best
        totals[best] += counts[g]
    return folds


def build_folds(k: int = N_FOLDS) -> pd.DataFrame:
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    splits = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    events = pd.read_csv(ROOT / "data/annotations/datased_polyphonic_events.csv")
    pool = splits[splits["split"].isin(["train", "validation"])
                  & splits["recording_id"].isin(events["recording_id"])].reset_index(drop=True)
    recording_ids = pool["recording_id"].astype(str).tolist()
    presence = presence_matrix(events, recording_ids, class_ids)
    groups = sorted(pool["leakage_group"].unique())
    group_index = {g: i for i, g in enumerate(groups)}
    counts = np.zeros((len(groups), 1 + len(class_ids)), dtype=np.int64)
    for row_index, group in enumerate(pool["leakage_group"]):
        counts[group_index[group], 0] += 1
        counts[group_index[group], 1:] += presence[row_index]
    fold_of_group = dict(zip(groups, assign_group_folds(groups, counts, k), strict=True))
    return pool.assign(fold=pool["leakage_group"].map(fold_of_group)).rename(
        columns={"split": "original_split"})[
        ["recording_id", "leakage_group", "original_split", "fold"]]


def balance(folds: pd.DataFrame) -> dict:
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    events = pd.read_csv(ROOT / "data/annotations/datased_polyphonic_events.csv")
    merged = events.merge(folds[["recording_id", "fold"]], on="recording_id")
    per_class = merged.groupby(["class_id", "fold"])["recording_id"].nunique().unstack(fill_value=0)
    return {
        "recordings_per_fold": folds.groupby("fold").size().tolist(),
        "events_per_fold": merged.groupby("fold").size().tolist(),
        "min_recordings_with_class_in_any_fold": int(per_class.reindex(class_ids).min().min()),
        "per_class_recordings": {c: per_class.loc[c].tolist() for c in class_ids},
        "dev_recordings_per_fold": folds[folds["original_split"] == "validation"]
        .groupby("fold").size().tolist(),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    folds = build_folds()
    if args.check:
        same = pd.read_csv(OUT).equals(folds)
        print(json.dumps({"identical": same}))
        raise SystemExit(0 if same else 1)
    if folds.groupby("leakage_group")["fold"].nunique().max() != 1:
        raise SystemExit("một leakage_group nằm ở nhiều fold")
    folds.to_csv(OUT, index=False, lineterminator="\n")
    meta = {"n_folds": N_FOLDS, "seed": SEED, "csv_sha256": sha256_file(OUT),
            "split_sha256": sha256_file(ROOT / "data/splits/datased_polyphonic.csv"),
            "events_sha256": sha256_file(ROOT / "data/annotations/datased_polyphonic_events.csv"),
            "git": git_state(ROOT), "balance": balance(folds)}
    OUT.with_suffix(".json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    print(json.dumps({k: meta["balance"][k] for k in ("recordings_per_fold", "events_per_fold",
                      "min_recordings_with_class_in_any_fold", "dev_recordings_per_fold")}))


if __name__ == "__main__":
    main()
