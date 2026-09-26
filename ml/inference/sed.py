"""Served SED system: the frozen ensemble of ADR-0024, run exactly like the measured one.

Every numeric step reuses the function that produced the reported numbers: windows from
`window_starts`, logits under the same autocast as `collect_predictions`, members averaged by
`average_predictions`, windows stitched by `stack_predictions_by_recording`, events from
`process_recordings` with the frozen `postproc`. Only the input differs: one feature matrix
instead of a dataset split.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ml.datasets.features import window_starts
from ml.evaluation.ensemble import average_predictions
from ml.evaluation.predictions import PredictionArtifact
from ml.models.audio import SoundEventDetector
from ml.models.sed_factory import sed_model
from ml.postprocessing import (
    priors_from_postproc,
    process_recordings,
    stack_predictions_by_recording,
)
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import Taxonomy

BATCH_SIZE = 8
SERVED_ID = "served"


@dataclass(frozen=True)
class MemberConfig:
    frame_rate: float
    window_frames: int
    hop_frames: int
    feature_set: str


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def member_config(manifest: dict[str, Any]) -> MemberConfig:
    config = manifest["config"]
    if config.get("encoder_type") != "panns":
        raise ValueError("served members must be PANNs runs (ADR-0029 §1)")
    return MemberConfig(float(config["frame_rate"]), int(config["window_frames"]),
                        int(config["hop_frames"]), str(config["feature_set"]))


def load_member(run_dir: Path, class_count: int, device: torch.device) -> SoundEventDetector:
    """Checkpoint carries the input normalisation buffers, so no normalisation file is read.
    The architecture comes from the member's manifest (v1 when the keys are absent)."""
    model = sed_model(_read_json(run_dir / "manifest.json")["config"], class_count)
    checkpoint = torch.load(run_dir / "checkpoints" / "best.pt", map_location="cpu",
                            weights_only=True)
    model.load_state_dict(checkpoint["model_state"])
    return model.to(device).eval()


class ServedSed:
    """Ensemble members + frozen postproc, loaded once."""

    def __init__(self, ensemble_dir: Path, postproc_name: str, taxonomy: Taxonomy,
                 device: torch.device) -> None:
        manifest = _read_json(ensemble_dir / "manifest.json")
        self.model_version = str(manifest["run_id"])
        self.class_ids = taxonomy.polyphonic_class_ids
        self.taxonomy_sha256 = taxonomy.checksum
        self.postproc = _read_json(ensemble_dir / postproc_name)
        validate_postproc_artifact(self.postproc, taxonomy=taxonomy)
        runs_root = ensemble_dir.parent
        member_dirs = [runs_root / name for name in manifest["config"]["members"]]
        configs = {member_config(_read_json(d / "manifest.json")) for d in member_dirs}
        if len(configs) != 1:
            raise ValueError("ensemble members disagree on windowing/features")
        self.config = configs.pop()
        self.device = device
        self.members = [load_member(d, len(self.class_ids), device) for d in member_dirs]
        self.member_ids = [d.name for d in member_dirs]

    def _member_logits(self, model: SoundEventDetector, windows: np.ndarray) -> np.ndarray:
        chunks = []
        with torch.inference_mode():
            for start in range(0, len(windows), BATCH_SIZE):
                batch = torch.from_numpy(windows[start:start + BATCH_SIZE]).unsqueeze(1)
                batch = batch.to(self.device)
                with torch.amp.autocast(device_type=self.device.type,
                                        enabled=self.device.type == "cuda"):
                    logits = model(batch)
                chunks.append(logits.float().cpu().numpy())
        return np.concatenate(chunks, axis=0)

    def artifacts(self, feature: np.ndarray) -> list[PredictionArtifact]:
        """One window-indexed artifact per member, shaped like `collect_predictions` output."""
        total = feature.shape[1]
        width = self.config.window_frames
        starts = window_starts(total, width, self.config.hop_frames)
        windows = np.zeros((len(starts), feature.shape[0], width), dtype=np.float32)
        mask = np.zeros((len(starts), width), dtype=bool)
        for index, start in enumerate(starts):
            available = min(width, total - start)
            windows[index, :, :available] = feature[:, start:start + available]
            mask[index, :available] = True
        shared = {"targets": np.zeros((len(starts), width, len(self.class_ids)), np.uint8),
                  "recording_ids": np.asarray([SERVED_ID] * len(starts), dtype=np.str_),
                  "frame_offsets_s": np.asarray(starts, np.float64) / self.config.frame_rate,
                  "mask": mask, "class_ids": self.class_ids, "split": "serve",
                  "frame_hop_s": 1.0 / self.config.frame_rate,
                  "taxonomy_sha256": self.taxonomy_sha256}
        return [PredictionArtifact(logits=self._member_logits(model, windows),
                                   model_version=member, **shared)
                for model, member in zip(self.members, self.member_ids, strict=True)]

    def probabilities(self, feature: np.ndarray) -> np.ndarray:
        """[frames, classes] probabilities of the ensemble for one log-mel [mel, frames]."""
        members = self.artifacts(feature)
        merged = average_predictions(members) if len(members) > 1 else members[0]
        return stack_predictions_by_recording(merged)[SERVED_ID]

    def events(self, probabilities: np.ndarray) -> list[dict[str, Any]]:
        thresholds = {c: float(self.postproc["per_class"][c]["theta"]) for c in self.class_ids}
        return process_recordings(
            {SERVED_ID: probabilities}, class_ids=self.class_ids, thresholds=thresholds,
            priors=priors_from_postproc(self.postproc, self.class_ids),
            frame_rate=self.config.frame_rate,
        ).get(SERVED_ID, [])
