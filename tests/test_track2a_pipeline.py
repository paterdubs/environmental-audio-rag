"""Track 2a data path (ADR-0032 §2): waveform windows on the v2 grid, head, encoded loader."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader

from ml.datasets.features import SedFeatureDataset
from ml.datasets.waveforms import SedWaveformDataset
from ml.models.embedding_sed import EmbeddingSequenceSED
from ml.training.encoded import EncodedLoader
from ml.training.sed import collect_predictions

CLASS_IDS = ("birds", "horn")
FRAME_RATE = 100.0
SAMPLES_PER_FRAME = 160
WINDOW_FRAMES = 100  # 1 s windows keep the fixtures small
EVENTS = pd.DataFrame([
    {"recording_id": "r1", "class_id": "birds", "onset_s": 0.25, "offset_s": 1.40},
    {"recording_id": "r2", "class_id": "horn", "onset_s": 0.10, "offset_s": 0.30},
])


def _recordings(tmp_path: Path) -> pd.DataFrame:
    """r1: 250 frames, audio 91 samples short of the grid (as real caches); r2: < one window."""
    (tmp_path / "wav").mkdir()
    (tmp_path / "mel").mkdir()
    rows = []
    for recording_id, frames, missing in (("r1", 250, 91), ("r2", 60, 0)):
        samples = frames * SAMPLES_PER_FRAME - missing
        np.save(tmp_path / "wav" / f"{recording_id}.npy",
                (np.arange(samples) % 20_000 - 10_000).astype(np.int16))
        np.save(tmp_path / "mel" / f"{recording_id}.npy",
                np.tile(np.arange(frames, dtype=np.float32), (4, 1)))
        rows.append({"recording_id": recording_id, "feature_relative_path": f"{recording_id}.npy",
                     "frames": frames})
    return pd.DataFrame(rows)


def _datasets(tmp_path: Path, *, random_crop: bool = False
              ) -> tuple[SedWaveformDataset, SedFeatureDataset]:
    recordings = _recordings(tmp_path)
    common = {"class_ids": CLASS_IDS, "frame_rate": FRAME_RATE, "window_frames": WINDOW_FRAMES,
              "hop_frames": WINDOW_FRAMES, "random_crop": random_crop}
    waveform = SedWaveformDataset(recordings, EVENTS, waveform_root=tmp_path / "wav", **common)
    feature = SedFeatureDataset(recordings, EVENTS, feature_root=tmp_path / "mel", **common)
    return waveform, feature


def test_windows_targets_and_masks_are_those_of_the_logmel_dataset(tmp_path: Path) -> None:
    waveform, feature = _datasets(tmp_path)
    assert waveform.windows == feature.windows
    for index in range(len(waveform)):
        _, target, valid = waveform[index]
        _, expected_target, expected_valid = feature[index]
        assert torch.equal(target, expected_target) and torch.equal(valid, expected_valid)


def test_input_is_the_matching_waveform_span_zero_padded_past_the_audio(tmp_path: Path) -> None:
    waveform, _ = _datasets(tmp_path)
    audio = np.load(tmp_path / "wav" / "r1.npy")
    for index, window in enumerate(waveform.windows):
        if window.recording_id != "r1":
            continue
        signal = waveform[index][0].numpy()
        assert signal.shape == (WINDOW_FRAMES * SAMPLES_PER_FRAME,)
        start = window.start_frame * SAMPLES_PER_FRAME
        span = audio[start:start + WINDOW_FRAMES * SAMPLES_PER_FRAME]
        np.testing.assert_array_equal(signal[: len(span)], span / 32768.0)
        assert not signal[len(span):].any()
    short = next(i for i, w in enumerate(waveform.windows) if w.recording_id == "r2")
    signal, _, valid = waveform[short]
    assert not signal[60 * SAMPLES_PER_FRAME:].any() and int(valid.sum()) == 60


def test_random_crops_follow_the_same_rng_draws_as_the_logmel_dataset(tmp_path: Path) -> None:
    waveform, feature = _datasets(tmp_path, random_crop=True)
    np.random.seed(7)
    waveform_targets = [waveform[0][1] for _ in range(10)]
    np.random.seed(7)
    feature_targets = [feature[0][1] for _ in range(10)]
    assert all(torch.equal(a, b) for a, b in zip(waveform_targets, feature_targets, strict=True))
    assert len({int(t[:, 0].argmax()) for t in waveform_targets}) > 1  # crops actually move


def test_rejects_non_pcm16_caches_and_fractional_samples_per_frame(tmp_path: Path) -> None:
    waveform, _ = _datasets(tmp_path)
    np.save(tmp_path / "wav" / "r1.npy", np.zeros(40_000, dtype=np.float32))
    with pytest.raises(ValueError, match="int16"):
        waveform[0]
    one_recording = pd.DataFrame(
        [{"recording_id": "r", "feature_relative_path": "r.npy", "frames": 10}])
    with pytest.raises(ValueError, match="whole number of samples"):
        SedWaveformDataset(one_recording, EVENTS.iloc[:0], waveform_root=tmp_path,
                           class_ids=CLASS_IDS, frame_rate=30.0, window_frames=10,
                           hop_frames=10)


def test_head_runs_at_embedding_rate_and_repeats_logits_onto_the_label_grid() -> None:
    head = EmbeddingSequenceSED(21, input_size=12, output_frames=1000, hidden_size=8)
    logits = head.eval()(torch.randn(2, 250, 12))
    assert logits.shape == (2, 1000, 21)
    assert torch.equal(logits[:, 0::4], logits[:, 3::4])  # each 40 ms step covers 4 frames
    with pytest.raises(ValueError):
        head(torch.randn(250, 12))


class _MeanPool(nn.Module):
    """Stand-in frozen encoder: [batch, samples] -> [batch, 5, 3] block means."""

    def __init__(self) -> None:
        super().__init__()
        self.scale = nn.Parameter(torch.ones(1), requires_grad=False)

    def forward(self, waveforms: torch.Tensor) -> torch.Tensor:
        blocks = waveforms.reshape(waveforms.shape[0], 5, -1)
        return torch.stack([blocks.mean(-1), blocks.amax(-1), blocks.amin(-1)], -1) * self.scale


def test_encoded_loader_feeds_collect_predictions_like_a_plain_loader(tmp_path: Path) -> None:
    waveform, _ = _datasets(tmp_path)
    plain = DataLoader(waveform, batch_size=2, shuffle=False)
    loader = EncodedLoader(plain, _MeanPool(), torch.device("cpu"))
    assert len(loader) == len(plain) and loader.dataset is waveform and not loader.drop_last
    features, targets, _ = next(iter(loader))
    assert features.shape == (2, 5, 3) and not features.requires_grad
    assert targets.device.type == "cpu"
    head = EmbeddingSequenceSED(len(CLASS_IDS), input_size=3, output_frames=WINDOW_FRAMES,
                                hidden_size=4)
    artifact = collect_predictions(
        head, loader, device=torch.device("cpu"), class_ids=CLASS_IDS, split="dev",
        model_version="sed-t2a-test", taxonomy_sha256=hashlib.sha256(b"t").hexdigest(),
        frame_rate=FRAME_RATE)
    assert artifact.logits.shape == (len(waveform), WINDOW_FRAMES, len(CLASS_IDS))
    assert list(artifact.recording_ids) == [w.recording_id for w in waveform.windows]
    with pytest.raises(ValueError, match="frozen encoder"):
        EncodedLoader(plain, nn.Linear(2, 2), torch.device("cpu"))
