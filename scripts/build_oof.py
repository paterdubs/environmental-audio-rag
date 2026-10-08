"""Giai đoạn O, tầng C (ADR-0041 §2): ghép dự đoán held-out của 5 run fold thành một run OOF.

    .venv/Scripts/python.exe -m scripts.build_oof --label B0 ml/runs/<fold0> ... ml/runs/<fold4>
    .venv/Scripts/python.exe -m scripts.select_postproc_cv ml/runs/sed_oof_B0_<ts> \
        --eval-set annotated

Mỗi member là bất kỳ run nào có `predictions/dev.npz` là **fold held-out** của nó: run fold đơn
(`train_sed --cv-fold k`), run dẫn xuất chồng lấn (`dump_predictions --hop-seconds`) hay ensemble
nhiều seed của cùng fold. Script không tin nhãn: kiểm trực tiếp tập recording của từng member
khớp đúng một fold trong `data/splits/datased_trainval_folds.csv`, các fold rời nhau và hợp lại
đủ mọi recording của file fold. Kết quả là `predictions/dev.npz` trên khoảng 564 recording mà các
script chọn hậu xử lý dùng nguyên như dev (tham chiếu lấy theo recording có trong artifact).
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.predictions import PredictionArtifact, load_predictions, save_predictions
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file

ROOT = Path(__file__).resolve().parents[1]
FOLDS_PATH = ROOT / "data" / "splits" / "datased_trainval_folds.csv"
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def fold_of_members(members: Sequence[PredictionArtifact], folds: pd.DataFrame) -> list[int]:
    """Fold index each member covers exactly; raise on partial, repeated or missing folds."""
    by_fold = {int(k): set(g["recording_id"].astype(str)) for k, g in folds.groupby("fold")}
    found: list[int] = []
    for index, member in enumerate(members):
        recordings = set(member.recording_ids.astype(str))
        matches = [k for k, ids in by_fold.items() if ids == recordings]
        if len(matches) != 1:
            raise ValueError(f"member {index} không phủ đúng một fold "
                             f"({len(recordings)} recording)")
        found.append(matches[0])
    if sorted(found) != sorted(by_fold):
        raise ValueError(f"fold thiếu hoặc lặp: {sorted(found)} so với {sorted(by_fold)}")
    return found


def concatenate(members: Sequence[PredictionArtifact]) -> PredictionArtifact:
    first = members[0]
    for index, other in enumerate(members[1:], start=1):
        for field in ("class_ids", "frame_hop_s", "taxonomy_sha256", "window_weighting"):
            if getattr(first, field) != getattr(other, field):
                raise ValueError(f"member {index} khác member 0 ở {field}")
        if other.logits.shape[1:] != first.logits.shape[1:]:
            raise ValueError(f"member {index} khác độ dài cửa sổ")
    return PredictionArtifact(
        logits=np.concatenate([m.logits for m in members]),
        targets=np.concatenate([m.targets for m in members]),
        recording_ids=np.concatenate([m.recording_ids for m in members]),
        frame_offsets_s=np.concatenate([m.frame_offsets_s for m in members]),
        mask=np.concatenate([m.mask for m in members]), class_ids=first.class_ids, split="dev",
        model_version="sed-oof-v1.0", frame_hop_s=first.frame_hop_s,
        taxonomy_sha256=first.taxonomy_sha256, window_weighting=first.window_weighting,
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("members", nargs=5, type=Path)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    manifests = [json.loads((m / "manifest.json").read_text(encoding="utf-8"))
                 for m in args.members]
    for member, manifest in zip(args.members, manifests, strict=True):
        if not manifest.get("complete") or any(manifest.get(k) != manifests[0].get(k)
                                               for k in SHARED):
            raise SystemExit(f"{member}: chưa hoàn tất hoặc khác dữ liệu với member đầu")
    artifacts = [load_predictions(m / "predictions/dev.npz", expected_class_ids=class_ids)
                 for m in args.members]
    folds = fold_of_members(artifacts, pd.read_csv(FOLDS_PATH))
    out = ROOT / "ml" / "runs" / f"sed_oof_{args.label}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    digest = save_predictions(out / "predictions/dev.npz", concatenate(artifacts),
                              expected_class_ids=class_ids)
    manifest = {
        "run_id": out.name, "task": "sed_oof", "complete": True,
        "command": ["python", "-m", "scripts.build_oof", *sys.argv[1:]],
        "class_ids": list(class_ids), **{key: manifests[0][key] for key in SHARED},
        "config": {"oof_label": args.label, "members": [m.name for m in args.members],
                   "fold_of_member": folds, "cv_folds_sha256": sha256_file(FOLDS_PATH),
                   "members_git_dirty": [bool(m.get("git", {}).get("dirty")) for m in manifests]},
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "git": git_state(ROOT),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps({"dev_predictions_sha256": digest}, indent=2),
                                      encoding="utf-8")
    print(json.dumps({"run_dir": str(out), "dev_predictions_sha256": digest}, indent=1))


if __name__ == "__main__":
    main()
