"""DataSEC clips with strong pseudo-labels for SED training (ADR-0041 §10, O-F).

Shared by `scripts.pseudo_label_datasec` (writes the labels) and `scripts.train_sed`
(`--pseudo-labels`, adds the clips to the train split). Clips are cached as 16 kHz PCM under
`data/cache/datasec_o_f_wav16k/` and use the 100 fps label grid of DataSED.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ml.datasets.waveforms import SedWaveformDataset

CACHE_DIRNAME = "datasec_o_f_wav16k"
SAMPLES_PER_FRAME = 160  # 16 kHz at the 100 fps label grid
EVENT_COLUMNS = ["recording_id", "class_id", "onset_s", "offset_s"]


def clip_table(cache: pd.DataFrame) -> pd.DataFrame:
    """Recordings table for `SedWaveformDataset`: one row per clip, label-grid frame count."""
    return pd.DataFrame({
        "recording_id": cache["file_id"].astype(str),
        "feature_relative_path": cache["feature_relative_path"].astype(str),
        "frames": cache["samples"].astype(int) // SAMPLES_PER_FRAME + 1,
    })


def keep_tag_class(events: dict[str, list[dict]], tags: dict[str, str]
                   ) -> tuple[list[dict], list[str]]:
    """(pseudo events of each clip's own class, clips without any such event)."""
    rows, dropped = [], []
    for clip, tag in tags.items():
        own = [e for e in events.get(clip, []) if e["event_label"] == tag]
        if not own:
            dropped.append(clip)
        rows.extend({"recording_id": clip, "class_id": tag, "onset_s": float(e["onset"]),
                     "offset_s": float(e["offset"])} for e in own)
    return rows, dropped


def check_fold(pseudo_manifest: dict, cv_fold: int | None) -> None:
    """A student of fold k may only learn from labels of the teacher of fold k (ADR-0041 §10)."""
    teacher_fold = pseudo_manifest["config"].get("teacher_cv_fold")
    if teacher_fold != cv_fold:
        raise SystemExit(f"nhãn giả từ teacher cv_fold={teacher_fold!r} nhưng student "
                         f"--cv-fold={cv_fold!r} (ADR-0041 §10)")


def load_pseudo_run(run: Path, cv_fold: int | None) -> dict:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("task") != "pseudo_labels" or not manifest.get("complete"):
        raise SystemExit(f"{run} không phải run pseudo_labels hoàn tất")
    check_fold(manifest, cv_fold)
    clips = pd.read_csv(run / "clips.csv")
    events = pd.read_csv(run / "events.csv")
    if not set(events["recording_id"]) <= set(clips["file_id"]):
        raise SystemExit(f"{run}: event thuộc clip đã bị bỏ")
    return {"clips": clips, "events": events[EVENT_COLUMNS],
            "info": {"run": run.name, "teacher": manifest["config"]["teacher"],
                     "teacher_cv_fold": manifest["config"].get("teacher_cv_fold"),
                     "clips": len(clips), "events": len(events)}}


def pseudo_dataset(pseudo: dict, *, cache_root: Path, class_ids: tuple[str, ...],
                   frame_rate: float, window_frames: int, hop_frames: int,
                   random_crop: bool) -> SedWaveformDataset:
    return SedWaveformDataset(clip_table(pseudo["clips"]), pseudo["events"],
                              waveform_root=cache_root, class_ids=class_ids,
                              frame_rate=frame_rate, window_frames=window_frames,
                              hop_frames=hop_frames, random_crop=random_crop)
