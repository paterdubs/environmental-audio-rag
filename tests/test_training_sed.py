"""collect_predictions (G2, ADR-0020 §6) — gom logit thô đúng danh tính cửa sổ."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch
from torch.utils.data import DataLoader

from ml.datasets.features import SedFeatureDataset
from ml.evaluation.predictions import load_predictions, save_predictions
from ml.models import SoundEventDetector
from ml.training.sed import collect_predictions

CLASS_IDS = ("bird", "car")
FRAME_RATE = 50.0
FAKE_TAXONOMY_SHA256 = hashlib.sha256(b"fixture").hexdigest()


def _write_feature(path: Path, frames: int, *, mel: int = 8, seed: int) -> None:
    rng = np.random.default_rng(seed)
    np.save(path, rng.normal(size=(mel, frames)).astype(np.float32))


def _build_dataset(tmp_path: Path) -> SedFeatureDataset:
    feature_root = tmp_path / "features"
    feature_root.mkdir()
    recordings = []
    for index, (recording_id, frames) in enumerate([("r1", 60), ("r2", 30)]):
        relative = f"{recording_id}.npy"
        _write_feature(feature_root / relative, frames, seed=index)
        recordings.append(
            {"recording_id": recording_id, "feature_relative_path": relative, "frames": frames}
        )
    events = pd.DataFrame(
        [{"recording_id": "r1", "class_id": "bird", "onset_s": 0.1, "offset_s": 0.3}]
    )
    dataset = SedFeatureDataset(
        pd.DataFrame(recordings),
        events,
        feature_root=feature_root,
        class_ids=CLASS_IDS,
        frame_rate=FRAME_RATE,
        window_frames=20,
        hop_frames=20,
    )
    return dataset


def test_collect_predictions_matches_window_count_and_recording_identity(tmp_path: Path) -> None:
    dataset = _build_dataset(tmp_path)
    loader = DataLoader(dataset, batch_size=4, shuffle=False)
    model = SoundEventDetector(classes=len(CLASS_IDS))

    artifact = collect_predictions(
        model,
        loader,
        device=torch.device("cpu"),
        class_ids=CLASS_IDS,
        split="dev",
        model_version="sed-v1.0",
        taxonomy_sha256=FAKE_TAXONOMY_SHA256,
        frame_rate=FRAME_RATE,
    )

    assert artifact.logits.shape[0] == len(dataset.windows)
    assert list(artifact.recording_ids) == [window.recording_id for window in dataset.windows]
    expected_offsets = [window.start_frame / FRAME_RATE for window in dataset.windows]
    assert artifact.frame_offsets_s.tolist() == pytest.approx(expected_offsets)


def test_collect_predictions_artifact_round_trips_through_save_predictions(
    tmp_path: Path,
) -> None:
    dataset = _build_dataset(tmp_path)
    loader = DataLoader(dataset, batch_size=4, shuffle=False)
    model = SoundEventDetector(classes=len(CLASS_IDS))

    artifact = collect_predictions(
        model,
        loader,
        device=torch.device("cpu"),
        class_ids=CLASS_IDS,
        split="dev",
        model_version="sed-v1.0",
        taxonomy_sha256=FAKE_TAXONOMY_SHA256,
        frame_rate=FRAME_RATE,
    )

    destination = tmp_path / "dev.npz"
    digest = save_predictions(destination, artifact, expected_class_ids=CLASS_IDS)
    reloaded = load_predictions(destination, expected_class_ids=CLASS_IDS)
    assert reloaded.split == "dev"
    assert reloaded.logits.shape == artifact.logits.shape
    assert len(digest) == 64


def test_collect_predictions_rejects_a_shuffled_loader(tmp_path: Path) -> None:
    dataset = _build_dataset(tmp_path)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    model = SoundEventDetector(classes=len(CLASS_IDS))

    with pytest.raises(ValueError, match="tuần tự"):
        collect_predictions(
            model,
            loader,
            device=torch.device("cpu"),
            class_ids=CLASS_IDS,
            split="dev",
            model_version="sed-v1.0",
            taxonomy_sha256=FAKE_TAXONOMY_SHA256,
            frame_rate=FRAME_RATE,
        )


def test_collect_predictions_rejects_drop_last(tmp_path: Path) -> None:
    dataset = _build_dataset(tmp_path)
    loader = DataLoader(dataset, batch_size=4, shuffle=False, drop_last=True)
    model = SoundEventDetector(classes=len(CLASS_IDS))

    with pytest.raises(ValueError, match="drop_last"):
        collect_predictions(
            model,
            loader,
            device=torch.device("cpu"),
            class_ids=CLASS_IDS,
            split="dev",
            model_version="sed-v1.0",
            taxonomy_sha256=FAKE_TAXONOMY_SHA256,
            frame_rate=FRAME_RATE,
        )
