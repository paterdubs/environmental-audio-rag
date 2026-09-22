from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import Tensor
from torch.utils.data import Dataset


def _fit_frames(feature: np.ndarray, frames: int, *, random_crop: bool) -> np.ndarray:
    if feature.ndim != 2:
        raise ValueError(f"Expected [mel, time], got {feature.shape}")
    available = feature.shape[1]
    if available >= frames:
        start = (
            np.random.randint(0, available - frames + 1)
            if random_crop
            else (available - frames) // 2
        )
        return np.asarray(feature[:, start : start + frames], dtype=np.float32)
    output = np.zeros((feature.shape[0], frames), dtype=np.float32)
    output[:, :available] = feature
    return output


class ClassificationFeatureDataset(Dataset):
    def __init__(
        self,
        rows: pd.DataFrame,
        *,
        feature_root: Path,
        class_ids: tuple[str, ...],
        frames: int = 250,
        random_crop: bool = False,
    ) -> None:
        required = {"feature_relative_path", "class_id"}
        missing = required.difference(rows.columns)
        if missing:
            raise ValueError(f"Classification manifest missing: {sorted(missing)}")
        self.rows = rows.reset_index(drop=True)
        self.feature_root = feature_root
        self.class_index = {class_id: index for index, class_id in enumerate(class_ids)}
        unknown = set(self.rows["class_id"]).difference(self.class_index)
        if unknown:
            raise ValueError(f"Unknown class IDs: {sorted(unknown)}")
        self.frames = frames
        self.random_crop = random_crop

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor]:
        row = self.rows.iloc[index]
        feature = np.load(
            self.feature_root / row["feature_relative_path"], mmap_mode="r", allow_pickle=False
        )
        fitted = _fit_frames(feature, self.frames, random_crop=self.random_crop)
        label = self.class_index[str(row["class_id"])]
        return torch.from_numpy(fitted).unsqueeze(0), torch.tensor(label, dtype=torch.long)


@dataclass(frozen=True)
class SedWindow:
    recording_id: str
    feature_relative_path: str
    start_frame: int
    available_frames: int


class SedFeatureDataset(Dataset):
    def __init__(
        self,
        recordings: pd.DataFrame,
        events: pd.DataFrame,
        *,
        feature_root: Path,
        class_ids: tuple[str, ...],
        frame_rate: float = 50.0,
        window_frames: int = 500,
        hop_frames: int = 250,
    ) -> None:
        recording_required = {"recording_id", "feature_relative_path", "frames"}
        event_required = {"recording_id", "class_id", "onset_s", "offset_s"}
        if missing := recording_required.difference(recordings.columns):
            raise ValueError(f"Recording manifest missing: {sorted(missing)}")
        if missing := event_required.difference(events.columns):
            raise ValueError(f"Event manifest missing: {sorted(missing)}")
        self.feature_root = feature_root
        self.class_index = {class_id: index for index, class_id in enumerate(class_ids)}
        self.frame_rate = frame_rate
        self.window_frames = window_frames
        self.events = {
            str(recording_id): group.reset_index(drop=True)
            for recording_id, group in events.groupby("recording_id", sort=False)
        }
        unknown = set(events["class_id"]).difference(self.class_index)
        if unknown:
            raise ValueError(f"Unknown SED class IDs: {sorted(unknown)}")

        self.windows: list[SedWindow] = []
        for row in recordings.itertuples(index=False):
            total = int(row.frames)
            starts = list(range(0, max(total - window_frames + 1, 1), hop_frames))
            last = max(total - window_frames, 0)
            if not starts or starts[-1] != last:
                starts.append(last)
            self.windows.extend(
                SedWindow(
                    recording_id=str(row.recording_id),
                    feature_relative_path=str(row.feature_relative_path),
                    start_frame=start,
                    available_frames=min(window_frames, total - start),
                )
                for start in starts
            )

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor, Tensor]:
        window = self.windows[index]
        feature = np.load(
            self.feature_root / window.feature_relative_path, mmap_mode="r", allow_pickle=False
        )
        fitted = np.zeros((feature.shape[0], self.window_frames), dtype=np.float32)
        stop = window.start_frame + window.available_frames
        fitted[:, : window.available_frames] = feature[:, window.start_frame : stop]
        target = np.zeros((self.window_frames, len(self.class_index)), dtype=np.float32)
        for event in self.events.get(window.recording_id, pd.DataFrame()).itertuples(index=False):
            onset = math.floor(float(event.onset_s) * self.frame_rate) - window.start_frame
            offset = math.ceil(float(event.offset_s) * self.frame_rate) - window.start_frame
            onset = max(0, min(onset, self.window_frames))
            offset = max(onset + 1, min(offset, self.window_frames))
            if onset < self.window_frames:
                target[onset:offset, self.class_index[str(event.class_id)]] = 1.0
        valid = np.zeros(self.window_frames, dtype=np.float32)
        valid[: window.available_frames] = 1.0
        return (
            torch.from_numpy(fitted).unsqueeze(0),
            torch.from_numpy(target),
            torch.from_numpy(valid),
        )
