from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score, f1_score
from torch import Tensor, nn
from torch.utils.data import DataLoader

from ml.models import AudioClassifier, HierarchicalAudioClassifier
from ml.models.hierarchical import (
    IGNORE_SUBCLASS,
    HierarchicalLossWeights,
    hierarchical_loss,
    parent_consistency_rate,
)


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


def hierarchical_metrics(
    coarse_targets: np.ndarray,
    coarse_predictions: np.ndarray,
    subclass_targets: np.ndarray,
    subclass_predictions: np.ndarray,
    *,
    supported_subclass_ids: set[int],
    family_mask: Tensor,
) -> dict:
    """Metric của ADR-0006 §3: hai số subclass macro-F1, không thay thế nhau.

    `supported_subclass_ids` phải cố định từ **một** lần đo (thường là số đếm
    trên test) và truyền vào giống hệt cho mọi epoch — nếu tính lại theo từng
    tập con (train/validation/test) thì "n>=10" mỗi lần trỏ tới một tập subclass
    khác nhau, và hai con số qua các epoch không còn so sánh được với nhau.
    """
    coarse_macro_f1 = float(
        f1_score(coarse_targets, coarse_predictions, average="macro", zero_division=0)
    )
    valid = subclass_targets != IGNORE_SUBCLASS
    if valid.any():
        subclass_macro_f1_all = float(
            f1_score(
                subclass_targets[valid],
                subclass_predictions[valid],
                average="macro",
                zero_division=0,
            )
        )
    else:
        subclass_macro_f1_all = float("nan")

    supported = valid & np.isin(subclass_targets, list(supported_subclass_ids))
    if supported.any() and supported_subclass_ids:
        subclass_macro_f1_supported = float(
            f1_score(
                subclass_targets[supported],
                subclass_predictions[supported],
                average="macro",
                zero_division=0,
                labels=sorted(supported_subclass_ids),
            )
        )
    else:
        subclass_macro_f1_supported = float("nan")

    if valid.any():
        rate = parent_consistency_rate(
            torch.from_numpy(coarse_predictions[valid]),
            torch.from_numpy(subclass_predictions[valid]),
            family_mask,
        )
    else:
        rate = float("nan")

    return {
        "coarse_macro_f1": coarse_macro_f1,
        "subclass_macro_f1_all": subclass_macro_f1_all,
        "subclass_macro_f1_supported": subclass_macro_f1_supported,
        "parent_consistency_rate": rate,
        "items": int(len(coarse_targets)),
        "items_with_subclass": int(valid.sum()),
    }


def run_hierarchical_epoch(
    model: HierarchicalAudioClassifier,
    loader: DataLoader,
    *,
    device: torch.device,
    coarse_weight: Tensor,
    family_mask: Tensor,
    supported_subclass_ids: set[int],
    optimizer: torch.optim.Optimizer | None,
    scaler: torch.amp.GradScaler | None,
    loss_weights: HierarchicalLossWeights | None = None,
) -> dict:
    """Một epoch cho `HierarchicalAudioClassifier`. Batch có 3 phần tử.

    `DataSECFeatureDataset.__getitem__` trả `(x, coarse, subclass)` —
    khác `ClassificationFeatureDataset` trả `(x, label)` mà `run_epoch` (ở
    trên) tiêu thụ. Không dùng chung một hàm cho hai loại batch khác nhau.
    """
    training = optimizer is not None
    model.train(training)
    family_mask = family_mask.to(device)
    losses: list[float] = []
    coarse_targets: list[np.ndarray] = []
    coarse_predictions: list[np.ndarray] = []
    subclass_targets: list[np.ndarray] = []
    subclass_predictions: list[np.ndarray] = []
    for features, coarse, subclass in loader:
        features = features.to(device, non_blocking=True)
        coarse = coarse.to(device, non_blocking=True)
        subclass = subclass.to(device, non_blocking=True)
        if training:
            optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
            coarse_logits, subclass_logits = model(features)
            loss_terms = hierarchical_loss(
                coarse_logits, subclass_logits, coarse, subclass, family_mask,
                weights=loss_weights, coarse_weight=coarse_weight,
            )
            loss = loss_terms["total"]  # duy nhất mang gradient — xem docstring hierarchical_loss
        if training:
            if scaler is None:
                loss.backward()
                optimizer.step()
            else:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        losses.append(float(loss.detach()))
        coarse_targets.append(coarse.detach().cpu().numpy())
        coarse_predictions.append(coarse_logits.detach().argmax(dim=1).cpu().numpy())
        subclass_targets.append(subclass.detach().cpu().numpy())
        subclass_predictions.append(subclass_logits.detach().argmax(dim=1).cpu().numpy())

    metrics = hierarchical_metrics(
        np.concatenate(coarse_targets),
        np.concatenate(coarse_predictions),
        np.concatenate(subclass_targets),
        np.concatenate(subclass_predictions),
        supported_subclass_ids=supported_subclass_ids,
        family_mask=family_mask.cpu(),
    )
    metrics["loss"] = float(np.mean(losses))
    return metrics


def train_hierarchical_classifier(
    model: HierarchicalAudioClassifier,
    loaders: dict[str, DataLoader],
    *,
    device: torch.device,
    coarse_weight: Tensor,
    family_mask: Tensor,
    supported_subclass_ids: set[int],
    config: ClassificationTrainingConfig,
    checkpoint_directory: Path,
    loss_weights: HierarchicalLossWeights | None = None,
) -> tuple[list[dict], Path]:
    """Giống `train_classifier` nhưng chọn best checkpoint theo
    `validation coarse_macro_f1` — coarse là mục tiêu chính, subclass là chỉ
    báo (ADR-0006 §1, ADR-0019 §5)."""
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    model.to(device)
    coarse_weight = coarse_weight.to(device)
    history: list[dict] = []
    best_score = -1.0
    best_path = checkpoint_directory / "best.pt"
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    for epoch in range(1, config.epochs + 1):
        train_metrics = run_hierarchical_epoch(
            model,
            loaders["train"],
            device=device,
            coarse_weight=coarse_weight,
            family_mask=family_mask,
            supported_subclass_ids=supported_subclass_ids,
            optimizer=optimizer,
            scaler=scaler,
            loss_weights=loss_weights,
        )
        with torch.inference_mode():
            validation_metrics = run_hierarchical_epoch(
                model,
                loaders["validation"],
                device=device,
                coarse_weight=coarse_weight,
                family_mask=family_mask,
                supported_subclass_ids=supported_subclass_ids,
                optimizer=None,
                scaler=None,
                loss_weights=loss_weights,
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
        if validation_metrics["coarse_macro_f1"] > best_score:
            best_score = validation_metrics["coarse_macro_f1"]
            torch.save(state, best_path)
    return history, best_path


def inverse_frequency_weights(labels: list[int], classes: int) -> Tensor:
    counts = np.bincount(labels, minlength=classes).astype(np.float64)
    if (counts == 0).any():
        raise ValueError("Every class must be represented in training")
    weights = len(labels) / (classes * counts)
    return torch.tensor(weights, dtype=torch.float32)
