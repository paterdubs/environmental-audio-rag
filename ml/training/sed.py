from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, f1_score
from torch import Tensor, nn
from torch.utils.data import DataLoader, SequentialSampler

from ml.evaluation.predictions import PredictionArtifact
from ml.models import SoundEventDetector
from ml.training.augment import augment_batch

SELECT_METRICS = ("macro_f1", "macro_average_precision")


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
    # SED v2 (ADR-0030). Defaults reproduce the v1 recipe of every RQ1 run exactly.
    encoder_learning_rate: float | None = None  # None: one learning rate for everything
    warmup_epochs: int = 0
    cosine_decay: bool = False
    select_metric: str = "macro_f1"
    mixup_p: float = 0.0
    filter_augment_p: float = 0.0

    def __post_init__(self) -> None:
        if self.select_metric not in SELECT_METRICS:
            raise ValueError(f"select_metric must be one of {SELECT_METRICS}")
        if not (0 <= self.mixup_p <= 1 and 0 <= self.filter_augment_p <= 1):
            raise ValueError("augmentation probabilities must be in [0, 1]")
        if self.warmup_epochs < 0 or self.warmup_epochs > self.epochs:
            raise ValueError("warmup_epochs must be in [0, epochs]")


def build_optimizer(model: SoundEventDetector, config: SedTrainingConfig
                    ) -> torch.optim.Optimizer:
    """v1: one AdamW over every parameter. v2: the pretrained encoder learns more slowly."""
    if config.encoder_learning_rate is None:
        return torch.optim.AdamW(model.parameters(), lr=config.learning_rate,
                                 weight_decay=config.weight_decay)
    encoder = list(model.encoder.parameters())
    encoder_ids = {id(parameter) for parameter in encoder}
    head = [parameter for parameter in model.parameters() if id(parameter) not in encoder_ids]
    return torch.optim.AdamW(
        [{"params": encoder, "lr": config.encoder_learning_rate},
         {"params": head, "lr": config.learning_rate}],
        weight_decay=config.weight_decay)


def build_scheduler(optimizer: torch.optim.Optimizer, config: SedTrainingConfig,
                    steps_per_epoch: int) -> torch.optim.lr_scheduler.LambdaLR | None:
    """Per-step linear warmup, then cosine decay to 0 (or constant); None for v1."""
    if config.warmup_epochs == 0 and not config.cosine_decay:
        return None
    warmup = config.warmup_epochs * steps_per_epoch
    total = config.epochs * steps_per_epoch

    def factor(step: int) -> float:
        if step < warmup:
            return (step + 1) / warmup
        if not config.cosine_decay:
            return 1.0
        return 0.5 * (1.0 + math.cos(math.pi * (step - warmup) / max(1, total - warmup)))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, factor)


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
    scheduler: torch.optim.lr_scheduler.LambdaLR | None = None,
    augmentation: tuple[float, float] = (0.0, 0.0),
) -> dict:
    """One pass; `augmentation` = (mixup_p, filter_augment_p), applied only when training."""
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
            if any(augmentation):
                features, targets, valid = augment_batch(
                    features, targets, valid, mixup_p=augmentation[0],
                    filter_augment_p=augmentation[1])
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
            if scheduler is not None:
                scheduler.step()
        losses.append(float(loss.detach()))
        keep = valid.bool().cpu().numpy()
        # Mixup makes training targets soft; frame metrics need binary labels.
        batch_targets = (targets.detach() >= 0.5).float().cpu().numpy()
        batch_probabilities = logits.detach().sigmoid().cpu().numpy()
        all_targets.append(batch_targets[keep])
        all_probabilities.append(batch_probabilities[keep])
    metrics = frame_metrics(
        np.concatenate(all_targets), np.concatenate(all_probabilities), threshold
    )
    metrics["loss"] = float(np.mean(losses))
    return metrics


def collect_predictions(
    model: SoundEventDetector,
    loader: DataLoader,
    *,
    device: torch.device,
    class_ids: tuple[str, ...],
    split: str,
    model_version: str,
    taxonomy_sha256: str,
    frame_rate: float,
) -> PredictionArtifact:
    """Gom logit thô của một split thành `PredictionArtifact` (ADR-0020 §6).

    Danh tính cửa sổ (`recording_id`, `start_frame`) **không** đi qua batch —
    `SedFeatureDataset.__getitem__` chỉ trả `(features, target, valid)`. Ở đây
    lấy lại từ `dataset.windows` theo đúng thứ tự index, nên **chỉ đúng khi
    loader duyệt tuần tự**; guard bên dưới từ chối mọi loader khác thay vì ghép
    logit sai recording một cách im lặng.

    Dùng autocast y hệt `run_epoch` để frame metric tính lại từ NPZ khớp đúng số
    đã báo cáo — lệch nghĩa là artifact không đến từ cùng checkpoint/state.
    """
    dataset = loader.dataset
    windows = getattr(dataset, "windows", None)
    if windows is None:
        raise TypeError("collect_predictions cần một SedFeatureDataset (thiếu .windows)")
    if not isinstance(loader.sampler, SequentialSampler):
        raise ValueError(
            "loader phải duyệt tuần tự (shuffle=False, không sampler) — "
            f"nhận {type(loader.sampler).__name__}; thứ tự khác làm logit lệch recording"
        )
    if loader.drop_last:
        raise ValueError("drop_last=True sẽ bỏ mất cửa sổ cuối — không dùng để dump prediction")
    if frame_rate <= 0:
        raise ValueError("frame_rate phải dương")

    model.to(device)
    model.eval()
    logit_chunks: list[np.ndarray] = []
    target_chunks: list[np.ndarray] = []
    mask_chunks: list[np.ndarray] = []
    with torch.inference_mode():
        for features, targets, valid in loader:
            features = features.to(device, non_blocking=True)
            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
                logits = model(features)
            logit_chunks.append(logits.float().cpu().numpy())
            target_chunks.append(targets.numpy())
            mask_chunks.append(valid.numpy())

    logits_array = np.concatenate(logit_chunks, axis=0)
    if logits_array.shape[0] != len(windows):
        raise ValueError(
            f"đếm được {logits_array.shape[0]} cửa sổ nhưng dataset có {len(windows)} — "
            "thứ tự/độ dài không khớp, không ghép được danh tính recording"
        )
    return PredictionArtifact(
        logits=logits_array,
        targets=np.concatenate(target_chunks, axis=0).astype(np.uint8),
        recording_ids=np.asarray([window.recording_id for window in windows], dtype=np.str_),
        frame_offsets_s=np.asarray(
            [window.start_frame / frame_rate for window in windows], dtype=np.float64
        ),
        mask=np.concatenate(mask_chunks, axis=0).astype(bool),
        class_ids=tuple(class_ids),
        split=split,
        model_version=model_version,
        frame_hop_s=1.0 / frame_rate,
        taxonomy_sha256=taxonomy_sha256,
    )


def train_sed(
    model: SoundEventDetector,
    loaders: dict[str, DataLoader],
    *,
    device: torch.device,
    pos_weight: Tensor,
    config: SedTrainingConfig,
    checkpoint_directory: Path,
) -> tuple[list[dict], Path]:
    optimizer = build_optimizer(model, config)
    scheduler = build_scheduler(optimizer, config, len(loaders["train"]))
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
            scheduler=scheduler,
            augmentation=(config.mixup_p, config.filter_augment_p),
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
        if validation_metrics[config.select_metric] > best_score:
            best_score = validation_metrics[config.select_metric]
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
