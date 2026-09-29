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
from ml.datasets.waveforms import PCM16_SCALE
from ml.evaluation.ensemble import average_predictions
from ml.evaluation.predictions import PredictionArtifact
from ml.models.sed_factory import frame_mn_model, sed_model
from ml.postprocessing import (
    priors_from_postproc,
    process_recordings,
    stack_predictions_by_recording,
)
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.postprocessing.sebb import SebbParams, sebb_candidates, select_boxes
from ml.taxonomy import Taxonomy

BATCH_SIZE = 8
SERVED_ID = "served"


@dataclass(frozen=True)
class MemberConfig:
    frame_rate: float
    window_frames: int
    hop_frames: int
    feature_set: str
    input_kind: str = "logmel"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def member_config(manifest: dict[str, Any]) -> MemberConfig:
    config = manifest["config"]
    encoder = config.get("encoder_type")
    if encoder not in {"panns", "frame_mn"}:
        raise ValueError(f"served encoder is unsupported: {encoder!r}")
    return MemberConfig(float(config["frame_rate"]), int(config["window_frames"]),
                        int(config["hop_frames"]), str(config["feature_set"]),
                        "waveform_16k" if encoder == "frame_mn" else "logmel")


def load_member(run_dir: Path, class_count: int, device: torch.device) -> torch.nn.Module:
    """Checkpoint carries the input normalisation buffers, so no normalisation file is read.
    The architecture comes from the member's manifest (v1 when the keys are absent)."""
    config = _read_json(run_dir / "manifest.json")["config"]
    model = (frame_mn_model(config, class_count) if config.get("encoder_type") == "frame_mn"
             else sed_model(config, class_count))
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
        self.postproc_family = str(self.postproc.get("family", "theta"))
        if getattr(self, "postproc_family", "theta") == "csebb":
            selected = self.postproc.get("selected", {})
            self.sebb_params = SebbParams(
                step_filter_s=float(selected["step_filter_s"]),
                merge_abs=(None if selected.get("merge_abs") is None
                           else float(selected["merge_abs"])),
                merge_rel=(None if selected.get("merge_rel") is None
                           else float(selected["merge_rel"])),
            )
            self.sebb_threshold = float(selected["threshold"])
        else:
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

    def _member_logits(self, model: torch.nn.Module, windows: np.ndarray) -> np.ndarray:
        chunks = []
        with torch.inference_mode():
            for start in range(0, len(windows), BATCH_SIZE):
                batch = torch.from_numpy(windows[start:start + BATCH_SIZE])
                if self.config.input_kind == "logmel":
                    batch = batch.unsqueeze(1)
                batch = batch.to(self.device)
                with torch.amp.autocast(device_type=self.device.type,
                                        enabled=self.device.type == "cuda"):
                    logits = model(batch)
                chunks.append(logits.float().cpu().numpy())
        return np.concatenate(chunks, axis=0)

    def artifacts(
        self, signal: np.ndarray, *, total_frames: int | None = None
    ) -> list[PredictionArtifact]:
        """One window-indexed artifact per member, shaped like `collect_predictions` output."""
        total = signal.shape[1] if self.config.input_kind == "logmel" else total_frames
        if total is None:
            raise ValueError("waveform serving requires the label-grid frame count")
        width = self.config.window_frames
        starts = window_starts(total, width, self.config.hop_frames)
        shape = ((len(starts), signal.shape[0], width) if self.config.input_kind == "logmel"
                 else (len(starts), width * 160))
        windows = np.zeros(shape, dtype=np.float32)
        mask = np.zeros((len(starts), width), dtype=bool)
        for index, start in enumerate(starts):
            available = min(width, total - start)
            if self.config.input_kind == "logmel":
                windows[index, :, :available] = signal[:, start:start + available]
            else:
                sample_start, sample_stop = start * 160, (start + available) * 160
                available_samples = min(sample_stop, signal.shape[0]) - sample_start
                if available_samples > 0:
                    windows[index, :available_samples] = signal[
                        sample_start:sample_start + available_samples] / PCM16_SCALE
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

    def probabilities(self, signal: np.ndarray, *, total_frames: int | None = None) -> np.ndarray:
        """[frames, classes] probabilities of the ensemble for one log-mel [mel, frames]."""
        members = self.artifacts(signal, total_frames=total_frames)
        merged = average_predictions(members) if len(members) > 1 else members[0]
        return stack_predictions_by_recording(merged)[SERVED_ID]

    def events(self, probabilities: np.ndarray) -> list[dict[str, Any]]:
        if getattr(self, "postproc_family", "theta") == "csebb":
            candidates = sebb_candidates({SERVED_ID: probabilities}, class_ids=self.class_ids,
                                         frame_rate=self.config.frame_rate,
                                         params=self.sebb_params)
            return select_boxes(candidates, self.sebb_threshold).get(SERVED_ID, [])
        thresholds = {c: float(self.postproc["per_class"][c]["theta"]) for c in self.class_ids}
        return process_recordings(
            {SERVED_ID: probabilities}, class_ids=self.class_ids, thresholds=thresholds,
            priors=priors_from_postproc(self.postproc, self.class_ids),
            frame_rate=self.config.frame_rate,
        ).get(SERVED_ID, [])
