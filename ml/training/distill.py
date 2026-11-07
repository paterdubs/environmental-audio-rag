"""ADR-0043 P2: soft targets for knowledge distillation from frozen teacher predictions.

Each teacher is a `sed_rewindow_*` run holding `predictions/train.npz` of one model trained on the
same data as the student will be (same `cv_fold`, so the student's held-out fold is never seen by
any teacher). Probabilities are stacked per recording with the artifact's own window weighting
and averaged over teachers on the common frame grid.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ml.evaluation.predictions import load_predictions
from ml.postprocessing.calibration import stack_predictions_by_recording
from ml.training.common import sha256_file

SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def _manifest(run: Path) -> dict:
    return json.loads((run / "manifest.json").read_text(encoding="utf-8"))


def teacher_fold(run: Path, runs_dir: Path) -> int | None:
    """`cv_fold` of the training run behind a rewindow teacher (None = trained on `train`)."""
    config = _manifest(run)["config"]
    return _manifest(runs_dir / config["source_run"])["config"].get("cv_fold")


def average_teachers(probabilities: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    """Mean over teachers per recording, truncated to the shortest teacher's frame count."""
    common = set(probabilities[0]).intersection(*probabilities[1:])
    averaged = {}
    for recording in sorted(common):
        frames = min(p[recording].shape[0] for p in probabilities)
        averaged[recording] = np.mean([p[recording][:frames] for p in probabilities], axis=0)
    return averaged


def load_teacher(teachers: list[Path], *, cv_fold: int | None, class_ids: tuple[str, ...],
                 student_manifest: dict, runs_dir: Path) -> tuple[dict[str, np.ndarray], dict]:
    """Averaged teacher probabilities and provenance; refuses any fold or data mismatch."""
    stacked, provenance = [], []
    for run in teachers:
        manifest = _manifest(run)
        if not manifest.get("complete"):
            raise SystemExit(f"{run}: teacher chưa hoàn tất")
        if any(manifest.get(k) != student_manifest.get(k) for k in SHARED):
            raise SystemExit(f"{run}: teacher khác dữ liệu/split với student")
        fold = teacher_fold(run, runs_dir)
        if fold != cv_fold:
            raise SystemExit(f"{run}: teacher cv_fold={fold}, student cv_fold={cv_fold} — "
                             "teacher phải chưa từng thấy fold giữ lại của student")
        path = run / "predictions" / "train.npz"
        artifact = load_predictions(path, expected_class_ids=class_ids)
        if artifact.split != "train":
            raise SystemExit(f"{path}: split={artifact.split!r}, cần 'train'")
        stacked.append(stack_predictions_by_recording(artifact))
        provenance.append({"run": run.name, "train_predictions_sha256": sha256_file(path),
                           "source_run": manifest["config"]["source_run"]})
    return average_teachers(stacked), {"teachers": provenance}
