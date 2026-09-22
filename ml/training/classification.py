from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score, f1_score
from torch import Tensor, nn
from torch.utils.data import DataLoader

from ml.models import AudioClassifier


@dataclass(frozen=True)
class ClassificationTrainingConfig:
    epochs: int = 12
    batch_size: int = 32
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    frames: int = 250
    seed: int = 20260922


def classification_metrics(targets: np.ndarray, predictions: np.ndarray) -> dict:
    return {
        "macro_f1": float(f1_score(targets, predictions, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(targets, predictions)),
        "per_class_f1": f1_score(
            targets, predictions, average=None, zero_division=0
        ).tolist(),
        "items": int(len(targets)),
    }


def run_epoch(
    model: AudioClassifier,
    loader: DataLoader,
    *,
    device: torch.device,
    class_weight: Tensor,
    optimizer: torch.optim.Optimizer | None,
    scaler: torch.amp.GradScaler | None,
) -> dict:
    training = optimizer is not None
    model.train(training)
    losses: list[float] = []
    targets: list[np.ndarray] = []
    predictions: list[np.ndarray] = []
    for features, labels in loader:
        features = features.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        if training:
            optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(features)
            loss = nn.functional.cross_entropy(logits, labels, weight=class_weight)
        if training:
            if scaler is None:
                loss.backward()
                optimizer.step()
            else:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        losses.append(float(loss.detach()))
        targets.append(labels.detach().cpu().numpy())
        predictions.append(logits.detach().argmax(dim=1).cpu().numpy())
    metrics = classification_metrics(np.concatenate(targets), np.concatenate(predictions))
    metrics["loss"] = float(np.mean(losses))
    return metrics


def train_classifier(
    model: AudioClassifier,
    loaders: dict[str, DataLoader],
    *,
    device: torch.device,
    class_weight: Tensor,
    config: ClassificationTrainingConfig,
    checkpoint_directory: Path,
) -> tuple[list[dict], Path]:
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    model.to(device)
    class_weight = class_weight.to(device)
    history: list[dict] = []
    best_score = -1.0
    best_path = checkpoint_directory / "best.pt"
    for epoch in range(1, config.epochs + 1):
        train_metrics = run_epoch(
            model,
            loaders["train"],
            device=device,
            class_weight=class_weight,
            optimizer=optimizer,
            scaler=scaler,
        )
        with torch.inference_mode():
            validation_metrics = run_epoch(
                model,
                loaders["validation"],
                device=device,
                class_weight=class_weight,
                optimizer=None,
                scaler=None,
            )
        record = {"epoch": epoch, "train": train_metrics, "validation": validation_metrics}
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


def inverse_frequency_weights(labels: list[int], classes: int) -> Tensor:
    counts = np.bincount(labels, minlength=classes).astype(np.float64)
    if (counts == 0).any():
        raise ValueError("Every class must be represented in training")
    weights = len(labels) / (classes * counts)
    return torch.tensor(weights, dtype=torch.float32)
