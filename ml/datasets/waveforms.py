"""Waveform windows on the SED label grid, for frozen waveform encoders (Track 2a, ADR-0032 §2).

`SedWaveformDataset` is `SedFeatureDataset` with a different input: windows, random crops, targets
and masks come from the log-mel frame grid (`logmel_panns_v1`, 100 fps) exactly as for SED v2, so
the two systems see the same labelled spans and their prediction files can be ensembled. Each
item's input is the matching span of the recording's 16 kHz waveform cache
(`scripts.cache_waveforms`), zero-padded past the end of the audio.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import Tensor

from ml.datasets.features import SedFeatureDataset, SedWindow

PCM16_SCALE = 32768.0


class SedWaveformDataset(SedFeatureDataset):
    """Items are `(waveform [window_samples], target [frames, classes], valid [frames])`.

    `recordings.feature_relative_path` points into `waveform_root` (int16 `.npy`, one per
    recording); `recordings.frames` is the label-grid frame count that defines the windows.
    """

    def __init__(self, recordings: pd.DataFrame, events: pd.DataFrame, *, waveform_root: Path,
                 class_ids: tuple[str, ...], frame_rate: float = 100.0,
                 window_frames: int = 1000, hop_frames: int = 1000, random_crop: bool = False,
                 sample_rate: int = 16_000) -> None:
        super().__init__(recordings, events, feature_root=waveform_root, class_ids=class_ids,
                         frame_rate=frame_rate, window_frames=window_frames,
                         hop_frames=hop_frames, random_crop=random_crop)
        samples_per_frame = sample_rate / frame_rate
        if samples_per_frame != int(samples_per_frame):
            raise ValueError(f"{sample_rate} Hz is not a whole number of samples per frame "
                             f"at {frame_rate} fps")
        self.samples_per_frame = int(samples_per_frame)
        self.window_samples = window_frames * self.samples_per_frame

    def _load_input(self, window: SedWindow) -> Tensor:
        audio = np.load(self.feature_root / window.feature_relative_path, mmap_mode="r",
                        allow_pickle=False)
        if audio.ndim != 1 or audio.dtype != np.int16:
            raise ValueError(f"{window.feature_relative_path}: expected 1-D int16 PCM, got "
                             f"{audio.dtype} {audio.shape}")
        start = window.start_frame * self.samples_per_frame
        # The frame grid can run up to one hop past the audio (centred STFT frame count).
        stop = min(start + window.available_frames * self.samples_per_frame, audio.shape[0])
        waveform = np.zeros(self.window_samples, dtype=np.float32)
        if stop > start:
            waveform[: stop - start] = audio[start:stop] / PCM16_SCALE
        return torch.from_numpy(waveform)
