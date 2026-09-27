"""Frame-MobileNet fine-tuned end to end on DataSED (Track 2b, ADR-0032 §3).

`frame_mn10_strong_1.pt` (PretrainedSED release v0.0.1) is a MobileNetV3 trained on AudioSet
Strong at 40 ms. This module rebuilds PretrainedSED's `FrameMNWrapper` + `PredictionsWrapper`
(read at commit 1aa47e48, see `ml/models/external/frame_mn/NOTICE.md`), replaces the 447-class
strong head with one for the 21 DataSED classes, and adds no sequence model (as the paper's
students). Everything trains, unlike Track 2a.

    waveform [batch, 160000] (16 kHz, 10 s)
      -> pre-emphasis, STFT (n_fft 512, Hann 400, hop 160, centred), Kaldi mel 128 (0-7000 Hz),
         log, (x + 4.5) / 5                                    -> [batch, 1, 128, 1000]
      -> Frame-MobileNet: stride 2 in time only in the stem and block 1, frequency collapsed to 1
                                                               -> [batch, 250, 960] (40 ms steps)
      -> linear per step                                       -> [batch, 250, classes]
      -> each step repeated (nearest) onto the 10 ms label grid -> [batch, 1000, classes]

The frontend always runs in its eval form and in float32: PretrainedSED's training-time
fmin/fmax jitter is a data augmentation, and ADR-0032 §3 keeps only mixup from the v2 recipe.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn

from ml.models.external.frame_mn import AugmentMelSTFT, get_model

SEQUENCE_LENGTH = 250  # PretrainedSED `seq_len`: 40 ms steps per 10 s window
EMBED_DIM = 960  # frame_mn10: 6 x 160 channels after the last 1x1 convolution
WIDTH_MULT = 1.0  # `NAME_TO_WIDTH("frame_mn10")`
# PretrainedSED release v0.0.1, `frame_mn10_strong_1.pt` (15,537,114 bytes), hashed 27/09/2026.
FRAME_MN10_STRONG_1_SHA256 = "4a0fe320d5369987b772394c51881fb20a602967e6842f72f3e5c8181065ece7"
CHECKPOINT_PREFIX = "model.frame_mn."  # PredictionsWrapper.model(FrameMNWrapper).frame_mn
HEAD_PREFIXES = ("strong_head.", "weak_head.")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class FrameMnLoadReport:
    checkpoint_sha256: str
    loaded_tensors: int
    loaded_parameters: int
    ignored_keys: tuple[str, ...]


def frame_mn_frontend() -> AugmentMelSTFT:
    """`FrameMNWrapper.mel`, argument for argument."""
    return AugmentMelSTFT(n_mels=128, sr=16_000, win_length=400, hopsize=160, n_fft=512,
                          freqm=0, timem=0, htk=False, fmin=0.0, fmax=None, norm=1,
                          fmin_aug_range=10, fmax_aug_range=2000, fast_norm=True, preamp=True,
                          padding="center", periodic_window=False)


def encoder_state_from_checkpoint(state: dict[str, Tensor]) -> tuple[dict[str, Tensor],
                                                                     tuple[str, ...]]:
    """Frame-MobileNet weights (prefix stripped) and the AudioSet head keys that are dropped."""
    encoder = {key.removeprefix(CHECKPOINT_PREFIX): value for key, value in state.items()
               if key.startswith(CHECKPOINT_PREFIX)}
    ignored = tuple(sorted(key for key in state if not key.startswith(CHECKPOINT_PREFIX)))
    unexpected = [key for key in ignored if not key.startswith(HEAD_PREFIXES)]
    if unexpected or not encoder:
        raise ValueError("not a PretrainedSED frame_mn checkpoint: "
                         f"unexpected keys {unexpected[:5]}")
    return encoder, ignored


class FrameMnSED(nn.Module):
    """`[batch, samples]` 16 kHz waveforms -> logits `[batch, output_frames, classes]`."""

    def __init__(self, classes: int, *, output_frames: int = 1000,
                 width_mult: float = WIDTH_MULT) -> None:
        super().__init__()
        if output_frames <= 0:
            raise ValueError("output_frames must be positive")
        self.output_frames = output_frames
        self.mel = frame_mn_frontend()
        with contextlib.redirect_stdout(io.StringIO()):  # get_model prints the whole network
            self.encoder = get_model(width_mult=width_mult)
        self.head = nn.Linear(self.encoder.lastconv_output_channels, classes)

    def train(self, mode: bool = True) -> FrameMnSED:
        super().train(mode)
        self.mel.train(False)  # no fmin/fmax jitter (see module docstring)
        return self

    def embed(self, waveforms: Tensor) -> Tensor:
        if waveforms.dim() != 2:
            raise ValueError(f"expected [batch, samples], got {tuple(waveforms.shape)}")
        with torch.autocast(device_type=waveforms.device.type, enabled=False):
            mel = self.mel(waveforms.float())
        steps = self.encoder(mel)
        # PretrainedSED PredictionsWrapper: pool (or stretch) the sequence to 250 steps.
        if steps.shape[1] > SEQUENCE_LENGTH:
            steps = nn.functional.adaptive_avg_pool1d(steps.transpose(1, 2),
                                                      SEQUENCE_LENGTH).transpose(1, 2)
        elif steps.shape[1] < SEQUENCE_LENGTH:
            steps = nn.functional.interpolate(steps.transpose(1, 2), size=SEQUENCE_LENGTH,
                                              mode="linear").transpose(1, 2)
        return steps

    def forward(self, waveforms: Tensor) -> Tensor:
        logits = self.head(self.embed(waveforms))
        return nn.functional.interpolate(logits.transpose(1, 2), size=self.output_frames,
                                         mode="nearest").transpose(1, 2)

    def load_pretrained(self, path: Path, expected_sha256: str | None = FRAME_MN10_STRONG_1_SHA256
                        ) -> FrameMnLoadReport:
        """Load the Frame-MobileNet part of a PretrainedSED checkpoint, strict on every tensor."""
        digest = sha256_of(path)
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError(f"{path} has SHA-256 {digest}, expected {expected_sha256} "
                             "(ADR-0032: frame_mn10_strong_1.pt, PretrainedSED v0.0.1)")
        state = torch.load(path, map_location="cpu", weights_only=True)
        encoder, ignored = encoder_state_from_checkpoint(state)
        self.encoder.load_state_dict(encoder, strict=True)
        return FrameMnLoadReport(
            checkpoint_sha256=digest,
            loaded_tensors=len(encoder),
            loaded_parameters=sum(p.numel() for p in self.encoder.parameters()),
            ignored_keys=ignored,
        )
