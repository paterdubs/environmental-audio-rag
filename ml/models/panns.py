"""PANNs CNN14-compatible audio encoder.

The implementation intentionally does not download checkpoints. A checkpoint
can be supplied explicitly with :meth:`load_local_checkpoint`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


def safe_batch_size(window_seconds: float, *, max_vram_gb: float = 8.0) -> int:
    """Return a conservative CNN14 batch upper bound for the available VRAM."""

    if window_seconds <= 0 or max_vram_gb <= 0:
        raise ValueError("window_seconds and max_vram_gb must be positive")
    if max_vram_gb < 8:
        return 1
    if window_seconds <= 5:
        return 4
    if window_seconds <= 10:
        return 2
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

    def __init__(self, *, channels: tuple[int, ...] = (64, 128, 256, 512, 1024, 2048)) -> None:
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
        encoded = inputs
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
