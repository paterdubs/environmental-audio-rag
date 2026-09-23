"""PANNs CNN14-compatible audio encoder.

The implementation intentionally does not download checkpoints. A checkpoint
can be supplied explicitly with :meth:`load_local_checkpoint`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import Tensor, nn


@dataclass(frozen=True)
class PannsConfig:
    """Feature and training defaults that fit the project's 8 GB GPU."""

    sample_rate: int = 32_000
    mel_bins: int = 64
    window_seconds: float = 5.0
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    amp: bool = True
    max_vram_gb: float = 8.0

    def __post_init__(self) -> None:
        if self.sample_rate <= 0 or self.mel_bins <= 0:
            raise ValueError("sample_rate and mel_bins must be positive")
        if self.window_seconds <= 0 or self.batch_size <= 0:
            raise ValueError("window_seconds and batch_size must be positive")
        if self.gradient_accumulation_steps <= 0 or self.max_vram_gb <= 0:
            raise ValueError("accumulation steps and max_vram_gb must be positive")


@dataclass(frozen=True)
class PretrainedLoadReport:
    """Evidence for the convolutional-block portion loaded from AudioSet."""

    checkpoint_tensors: int
    checkpoint_parameters: int
    transplanted_tensors: int
    transplanted_parameters: int

    @property
    def parameter_fraction(self) -> float:
        return self.transplanted_parameters / self.checkpoint_parameters


def load_feature_normalization(path: str | Path) -> tuple[Tensor, Tensor]:
    """Load train-only per-mel z-score statistics saved by the F1 measurement."""
    with np.load(Path(path), allow_pickle=False) as values:
        mean = np.asarray(values["mean"], dtype=np.float32)
        std = np.asarray(values["std"], dtype=np.float32)
    if mean.shape != (64,) or std.shape != (64,) or not np.isfinite(std).all():
        raise ValueError("normalization statistics must contain 64 finite mean/std values")
    if not np.isfinite(mean).all() or (std <= 0).any():
        raise ValueError("normalization statistics must have finite means and positive std")
    return torch.from_numpy(mean), torch.from_numpy(std)


_PANN_KEY = re.compile(r"^conv_block([1-6])\.(conv[12]|bn[12])\.(.+)$")
_LAYER_FOR_PANN = {"conv1": 0, "bn1": 1, "conv2": 3, "bn2": 4}


def remap_audioset_state_dict(state: dict[str, Tensor]) -> dict[str, Tensor]:
    """Map official CNN14 convolutional-block keys to this encoder's blocks only."""
    remapped: dict[str, Tensor] = {}
    for key, value in state.items():
        match = _PANN_KEY.fullmatch(key)
        if match is None:
            continue
        block, layer, suffix = match.groups()
        target = f"{int(block) - 1}.layers.{_LAYER_FOR_PANN[layer]}.{suffix}"
        remapped[target] = value
    return remapped


def safe_batch_size(window_seconds: float, *, max_vram_gb: float = 8.0) -> int:
    """Return a conservative CNN14 batch upper bound for the available VRAM."""

    if window_seconds <= 0 or max_vram_gb <= 0:
        raise ValueError("window_seconds and max_vram_gb must be positive")
    if max_vram_gb < 8:
        return 1
    if window_seconds <= 5:
        return 32
    if window_seconds <= 10:
        return 24
    return 1


class _PannsConvBlock(nn.Module):
    def __init__(self, input_channels: int, output_channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(input_channels, output_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(output_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(output_channels, output_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(output_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.layers(inputs)


class PannsCNN14Encoder(nn.Module):
    """CNN14 feature extractor with PANNs' six-block channel layout.

    Inputs are log-mel tensors shaped ``[batch, 1, mel_bins, frames]``. The
    output is ``[batch, 2048, reduced_frames]``; frequency is pooled away and
    time is reduced by the six 2x2 pooling operations.
    """

    output_channels = 2048

    def __init__(
        self,
        *,
        channels: tuple[int, ...] = (64, 128, 256, 512, 1024, 2048),
        normalization_path: str | Path | None = None,
    ) -> None:
        super().__init__()
        if len(channels) != 6 or any(channel <= 0 for channel in channels):
            raise ValueError("CNN14 requires six positive channel sizes")
        blocks: list[nn.Module] = []
        input_channels = 1
        for output_channels in channels:
            blocks.append(_PannsConvBlock(input_channels, output_channels))
            input_channels = output_channels
        self.blocks = nn.ModuleList(blocks)
        self.output_channels = channels[-1]
        self.register_buffer("input_mean", torch.zeros(1, 1, 64, 1))
        self.register_buffer("input_std", torch.ones(1, 1, 64, 1))
        if normalization_path is not None:
            self.set_input_normalization(*load_feature_normalization(normalization_path))

    def set_input_normalization(self, mean: Tensor, std: Tensor) -> None:
        """Install immutable train-corpus per-mel statistics before CNN14 blocks."""
        if mean.shape != (64,) or std.shape != (64,) or torch.any(std <= 0):
            raise ValueError("normalization mean/std must each have 64 values and positive std")
        self.input_mean.copy_(mean.to(dtype=self.input_mean.dtype).reshape(1, 1, 64, 1))
        self.input_std.copy_(std.to(dtype=self.input_std.dtype).reshape(1, 1, 64, 1))

    @property
    def time_reduction(self) -> int:
        """Tỉ lệ CNN14 nén trục thời gian — 2 lần mỗi khối, sáu khối = /64."""
        return 2 ** len(self.blocks)

    def forward(self, inputs: Tensor) -> Tensor:
        if inputs.ndim != 4 or inputs.shape[1] != 1:
            raise ValueError("expected log-mel input shaped [batch, 1, mel_bins, frames]")
        frames = inputs.shape[-1]
        if frames < self.time_reduction:
            raise ValueError(
                f"CNN14 nén trục thời gian /{self.time_reduction} qua sáu lần pool 2x2; "
                f"input chỉ có {frames} frame sẽ về 0 giữa chừng. Cần ≥ {self.time_reduction} "
                "frame — cửa sổ SED thật (500 frame @ 50 fps = 10 s) thoả điều kiện này."
            )
        if inputs.shape[2] != self.input_mean.shape[2]:
            raise ValueError("CNN14 normalization expects 64 mel bands")
        encoded = (inputs - self.input_mean) / self.input_std
        for block in self.blocks:
            encoded = block(encoded)
            encoded = nn.functional.avg_pool2d(encoded, kernel_size=(2, 2))
        return encoded.mean(dim=2)

    def load_local_checkpoint(self, path: str | Path, *, strict: bool = True) -> None:
        """Load a caller-provided checkpoint; never fetch weights implicitly."""

        checkpoint = torch.load(Path(path), map_location="cpu", weights_only=True)
        state = checkpoint.get("model_state", checkpoint)
        if not isinstance(state, dict):
            raise ValueError("checkpoint must contain a state-dict or model_state")
        self.load_state_dict(state, strict=strict)

    def load_audioset_pretrained(self, path: str | Path) -> PretrainedLoadReport:
        """Strictly load only remapped official CNN14 convolutional-block tensors."""
        # The official 2020 PANNs pickle contains NumPy reconstruction metadata,
        # which PyTorch 2.6 rejects under weights_only. This loader is only for
        # the verified official checkpoint; load_local_checkpoint remains safe.
        checkpoint = torch.load(Path(path), map_location="cpu", weights_only=False)
        state = checkpoint.get("model", checkpoint)
        if not isinstance(state, dict) or not all(
            isinstance(key, str) and isinstance(value, Tensor) for key, value in state.items()
        ):
            raise ValueError("checkpoint must contain a tensor state-dict or model state-dict")
        remapped = remap_audioset_state_dict(state)
        # Strict here makes a missing or shape-mismatched transferred tensor fail loudly.
        self.blocks.load_state_dict(remapped, strict=True)
        return PretrainedLoadReport(
            checkpoint_tensors=len(state),
            checkpoint_parameters=sum(value.numel() for value in state.values()),
            transplanted_tensors=len(remapped),
            transplanted_parameters=sum(value.numel() for value in remapped.values()),
        )


class PannsAudioClassifier(nn.Module):
    """Clip classifier using CNN14 embeddings."""

    def __init__(
        self, classes: int, encoder: PannsCNN14Encoder | None = None, dropout: float = 0.2
    ) -> None:
        super().__init__()
        self.encoder = encoder or PannsCNN14Encoder()
        self.head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(self.encoder.output_channels, classes)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.head(self.encoder(inputs).mean(dim=-1))
