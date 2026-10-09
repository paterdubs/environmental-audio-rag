"""BEATs fine-tuned end to end on DataSED (ADR-0041 O-D).

Same input path as the frozen Track 2a embedder (`ml/models/beats_frozen.py`: Kaldi fbank,
BEATs, pooling to 250 steps of 40 ms), but every BEATs weight trains, dropout/layerdrop follow
train/eval mode, and a fresh 21-class linear head sits on the 768-d steps. The head output is
repeated (nearest) onto the 10 ms label grid like `FrameMnSED`, so prediction artifacts and every
downstream step are unchanged. `encoder` / `head` attributes let `build_optimizer` give the
pretrained encoder its own (smaller) learning rate.

T0 gate (08/10, RTX 3070 Laptop 8 GB, fp16 autocast, AdamW): batch 8 peaks at 5.5 GB and
0.33 s/step; batch 16 spills to shared memory (4.1 s/step), so the recipe uses batch 8.
"""

from __future__ import annotations

from pathlib import Path

from torch import Tensor, nn

from ml.models.beats_frozen import (
    BEATS_STRONG_1_SHA256,
    EMBED_DIM,
    BeatsLoadReport,
    FrozenBeatsEncoder,
)


class TrainableBeatsEncoder(FrozenBeatsEncoder):
    """`FrozenBeatsEncoder` with gradients and normal train/eval behaviour."""

    def __init__(self) -> None:
        super().__init__()
        self.beats.requires_grad_(True)

    def train(self, mode: bool = True) -> TrainableBeatsEncoder:
        return nn.Module.train(self, mode)


class BeatsFinetuneSED(nn.Module):
    """`[batch, samples]` 16 kHz waveforms -> logits `[batch, output_frames, classes]`."""

    def __init__(self, classes: int, *, output_frames: int = 1000) -> None:
        super().__init__()
        if output_frames <= 0:
            raise ValueError("output_frames must be positive")
        self.output_frames = output_frames
        self.encoder = TrainableBeatsEncoder()
        self.head = nn.Linear(EMBED_DIM, classes)

    def forward(self, waveforms: Tensor) -> Tensor:
        logits = self.head(self.encoder(waveforms))
        return nn.functional.interpolate(logits.transpose(1, 2), size=self.output_frames,
                                         mode="nearest").transpose(1, 2)

    def load_pretrained(self, path: Path, expected_sha256: str | None = BEATS_STRONG_1_SHA256
                        ) -> BeatsLoadReport:
        return self.encoder.load_pretrained(path, expected_sha256=expected_sha256)
