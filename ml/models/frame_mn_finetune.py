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

ADR-0041 O-C adds an optional sequence model between the 250 steps and the head: EfficientSED's
`fmn10+gru-256_strong.pt` (release v0.0.1, code @e3449bfd) is the same Frame-MobileNet followed
by a 2-layer bidirectional GRU (960 -> 256 per direction), both trained on AudioSet Strong, so
both load from the checkpoint and only the 21-class head starts fresh.
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
# EfficientSED release v0.0.1, `fmn10+gru-256_strong.pt` (26,139,225 bytes), XO-5 08/10/2026.
EFFICIENTSED_FMN10_GRU256_SHA256 = (
    "1c963930f92d7cd42ff01f4bff940701aa2db8f5c6d64601cf8c0d1d5d5bf007")
CHECKPOINT_PREFIX = "model.frame_mn."  # PredictionsWrapper.model(FrameMNWrapper).frame_mn
HEAD_PREFIXES = ("strong_head.", "weak_head.")
# EfficientSED wraps the same PredictionsWrapper in a Lightning module (`net.`), and its
# backbone sits directly under `model.` (no `frame_mn.` level).
EFFICIENTSED_PREFIX = "net.model."
EFFICIENTSED_SEQUENCE_PREFIX = "net.seq_model.0.gru."
EFFICIENTSED_HEAD_PREFIXES = ("net.strong_head.", "net.weak_head.")


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
    loaded_sequence_tensors: int = 0


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


def efficientsed_state(state: dict[str, Tensor]) -> tuple[dict[str, Tensor], dict[str, Tensor],
                                                         tuple[str, ...]]:
    """(Frame-MobileNet, GRU, dropped head keys) of an EfficientSED checkpoint, unprefixed."""
    def strip(prefix: str) -> dict[str, Tensor]:
        return {key.removeprefix(prefix): value for key, value in state.items()
                if key.startswith(prefix)}

    encoder, sequence = strip(EFFICIENTSED_PREFIX), strip(EFFICIENTSED_SEQUENCE_PREFIX)
    ignored = tuple(sorted(key for key in state
                           if not key.startswith((EFFICIENTSED_PREFIX,
                                                  EFFICIENTSED_SEQUENCE_PREFIX))))
    unexpected = [key for key in ignored if not key.startswith(EFFICIENTSED_HEAD_PREFIXES)]
    if unexpected or not encoder:
        raise ValueError(f"not an EfficientSED checkpoint: unexpected keys {unexpected[:5]}")
    return encoder, sequence, ignored


class FrameMnSED(nn.Module):
    """`[batch, samples]` 16 kHz waveforms -> logits `[batch, output_frames, classes]`."""

    def __init__(self, classes: int, *, output_frames: int = 1000,
                 width_mult: float = WIDTH_MULT, rnn_hidden: int | None = None,
                 rnn_layers: int | None = None) -> None:
        super().__init__()
        if output_frames <= 0:
            raise ValueError("output_frames must be positive")
        if (rnn_hidden is None) != (rnn_layers is None):
            raise ValueError("rnn_hidden and rnn_layers go together")
        self.output_frames = output_frames
        self.mel = frame_mn_frontend()
        with contextlib.redirect_stdout(io.StringIO()):  # get_model prints the whole network
            self.encoder = get_model(width_mult=width_mult)
        width = self.encoder.lastconv_output_channels
        self.sequence: nn.GRU | None = None
        if rnn_hidden is not None:
            self.sequence = nn.GRU(width, rnn_hidden, num_layers=int(rnn_layers),
                                   batch_first=True, bidirectional=True)
            width = 2 * rnn_hidden
        self.head = nn.Linear(width, classes)

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
        steps = self.embed(waveforms)
        if self.sequence is not None:
            steps, _ = self.sequence(steps)
        logits = self.head(steps)
        return nn.functional.interpolate(logits.transpose(1, 2), size=self.output_frames,
                                         mode="nearest").transpose(1, 2)

    def load_pretrained(self, path: Path, expected_sha256: str | None = FRAME_MN10_STRONG_1_SHA256
                        ) -> FrameMnLoadReport:
        """Load every pretrained tensor this model has, strict: the Frame-MobileNet of a
        PretrainedSED checkpoint, or the Frame-MobileNet + GRU of an EfficientSED one."""
        digest = sha256_of(path)
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError(f"{path} has SHA-256 {digest}, expected {expected_sha256} "
                             "(ADR-0032 / ADR-0041 O-C pinned checkpoint)")
        state = torch.load(path, map_location="cpu", weights_only=True)
        if any(key.startswith(EFFICIENTSED_PREFIX) for key in state):
            encoder, sequence, ignored = efficientsed_state(state)
        else:
            (encoder, ignored), sequence = encoder_state_from_checkpoint(state), {}
        # Never drop pretrained sequence weights silently, nor train a GRU from scratch while
        # the run claims a pretrained one.
        if bool(sequence) != (self.sequence is not None):
            raise ValueError(f"{path}: checkpoint has {len(sequence)} GRU tensors but the model "
                             f"{'has' if self.sequence is not None else 'has no'} GRU")
        self.encoder.load_state_dict(encoder, strict=True)
        if self.sequence is not None:
            self.sequence.load_state_dict(sequence, strict=True)
        loaded = [self.encoder] + ([self.sequence] if self.sequence is not None else [])
        return FrameMnLoadReport(
            checkpoint_sha256=digest,
            loaded_tensors=len(encoder) + len(sequence),
            loaded_parameters=sum(p.numel() for module in loaded for p in module.parameters()),
            ignored_keys=ignored,
            loaded_sequence_tensors=len(sequence),
        )
