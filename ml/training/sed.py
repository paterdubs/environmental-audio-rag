from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, f1_score
from torch import Tensor, nn
from torch.utils.data import DataLoader

from ml.models import SoundEventDetector


@dataclass(frozen=True)
class SedTrainingConfig:
    epochs: int = 8
    batch_size: int = 8
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    threshold: float = 0.5
    window_frames: int = 500
    hop_frames: int = 500
    seed: int = 20260922


def masked_bce(logits: Tensor, targets: Tensor, valid: Tensor, pos_weight: Tensor) -> Tensor:
    loss = nn.functional.binary_cross_entropy_with_logits(
        logits, targets, pos_weight=pos_weight, reduction="none"
    )
    mask = valid.unsqueeze(-1)
    return (loss * mask).sum() / (mask.sum() * targets.shape[-1]).clamp_min(1.0)


def frame_metrics(targets: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict:
    predictions = probabilities >= threshold
    active = targets.sum(axis=0) > 0
    per_class = f1_score(targets, predictions, average=None, zero_division=0)
    average_precision = average_precision_score(targets, probabilities, average=None)
    return {
        "macro_f1": float(per_class[active].mean()),
        "macro_average_precision": float(np.nanmean(average_precision[active])),
        "per_class_f1": per_class.tolist(),
        "active_classes": int(active.sum()),
        "frames": int(len(targets)),
    }


def run_epoch(
    model: SoundEventDetector,
    loader: DataLoader,
    *,
    device: torch.device,
    pos_weight: Tensor,
    optimizer: torch.optim.Optimizer | None,
    scaler: torch.amp.GradScaler | None,
    threshold: float,
) -> dict:
    training = optimizer is not None
    model.train(training)
    losses: list[float] = []
    all_targets: list[np.ndarray] = []
    all_probabilities: list[np.ndarray] = []
    for features, targets, valid in loader:
        features = features.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)
        valid = valid.to(device, non_blocking=True)
        if training:
            optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(features)
            loss = masked_bce(logits, targets, valid, pos_weight)
        if training:
            if scaler is None:
                loss.backward()
                optimizer.step()
            else:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        losses.append(float(loss.detach()))
        keep = valid.bool().cpu().numpy()
        batch_targets = targets.detach().cpu().numpy()
        batch_probabilities = logits.detach().sigmoid().cpu().numpy()
        all_targets.append(batch_targets[keep])
        all_probabilities.append(batch_probabilities[keep])
    metrics = frame_metrics(
        np.concatenate(all_targets), np.concatenate(all_probabilities), threshold
    )
    metrics["loss"] = float(np.mean(losses))
    return metrics


def train_sed(
    model: SoundEventDetector,
    loaders: dict[str, DataLoader],
    *,
    device: torch.device,
    pos_weight: Tensor,
    config: SedTrainingConfig,
    checkpoint_directory: Path,
) -> tuple[list[dict], Path]:
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    model.to(device)
    pos_weight = pos_weight.to(device)
    history: list[dict] = []
    best_score = -1.0
    best_path = checkpoint_directory / "best.pt"
    for epoch in range(1, config.epochs + 1):
        train_metrics = run_epoch(
            model,
            loaders["train"],
            device=device,
            pos_weight=pos_weight,
            optimizer=optimizer,
            scaler=scaler,
            threshold=config.threshold,
        )
        with torch.inference_mode():
            validation_metrics = run_epoch(
                model,
                loaders["validation"],
                device=device,
                pos_weight=pos_weight,
                optimizer=None,
                scaler=None,
                threshold=config.threshold,
            )
        record = {
            "epoch": epoch,
            "train": train_metrics,
            "validation": validation_metrics,
        }
        history.append(record)
        print(record, flush=True)
        state = {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "config": asdict(config),
            "validation": validation_metrics,
        }
        torch.save(state, checkpoint_directory / "last.pt")
        if validation_metrics["macro_f1"] > best_score:
            best_score = validation_metrics["macro_f1"]
            torch.save(state, best_path)
    return history, best_path


def estimate_pos_weight(
    class_ids: tuple[str, ...],
    events: Iterable[tuple[str, float, float]],
    total_duration_s: float,
    maximum: float = 50.0,
) -> Tensor:
    positive = {class_id: 0.0 for class_id in class_ids}
    for class_id, onset_s, offset_s in events:
        positive[class_id] += max(0.0, offset_s - onset_s)
    values = [
        min(maximum, max(1.0, (total_duration_s - positive[class_id]) / positive[class_id]))
        if positive[class_id] > 0
        else 1.0
        for class_id in class_ids
    ]
    return torch.tensor(values, dtype=torch.float32)
