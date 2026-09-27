"""Frozen BEATs frame embedder for Track 2a (ADR-0032 §2).

`BEATs_strong_1.pt` (PretrainedSED release v0.0.1) is BEATs fine-tuned on AudioSet Strong at a
nominal 40 ms resolution. This module turns a batch of 10 s, 16 kHz waveforms into the 250-step
embedding sequence the checkpoint's strong head was trained on, and nothing else: the encoder is
always in eval mode, never receives gradients, and its weights never enter a run checkpoint.

The forward path mirrors PretrainedSED's `BEATsWrapper` + `PredictionsWrapper` (read at commit
1aa47e48, see `ml/models/external/beats/NOTICE.md`):

    waveform * 2**15 -> Kaldi fbank (128 mel, 25/10 ms; 998 frames per 10 s)
      -> (fbank - 15.41663) / (2 * 6.55582)
      -> BEATs patch embedding 16x16 -> 62 time x 8 frequency = 496 tokens, 768-d
      -> adaptive average pooling over the flattened token sequence -> 250 x 768

The "40 ms" is the index grid after that pooling, not a 40 ms patch: BEATs patches are 160 ms long
and the 496 tokens are time-major with 8 frequency patches per time step. The strong fine-tuning
trained each pooled position to predict its own 40 ms frame, so position i is used as frame i.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn

from ml.features.kaldi_fbank import kaldi_fbank
from ml.models.external.beats import BEATs, BEATsConfig

SAMPLE_RATE = 16_000
WINDOW_SECONDS = 10
WINDOW_SAMPLES = SAMPLE_RATE * WINDOW_SECONDS
SEQUENCE_LENGTH = 250  # 40 ms steps per 10 s window (PretrainedSED `seq_len`)
EMBED_DIM = 768
FBANK_MEAN = 15.41663  # BEATs.preprocess defaults
FBANK_STD = 6.55582
# PretrainedSED release v0.0.1, asset `BEATs_strong_1.pt` (364,091,999 bytes), hashed 27/09/2026.
BEATS_STRONG_1_SHA256 = "db13a79ae90a0cfd0f9911a6a1d8cdb89324322bee642dcfe32de022123b8b54"
CHECKPOINT_PREFIX = "model.model."  # PretrainedSED: PredictionsWrapper.model(BEATsWrapper).model
HEAD_PREFIXES = ("strong_head.", "weak_head.")


@dataclass(frozen=True)
class BeatsLoadReport:
    checkpoint_sha256: str
    loaded_tensors: int
    loaded_parameters: int
    ignored_keys: tuple[str, ...]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encoder_state_from_checkpoint(state: dict[str, Tensor]) -> tuple[dict[str, Tensor],
                                                                     tuple[str, ...]]:
    """Split a PretrainedSED state dict into BEATs weights (prefix stripped) and ignored keys.

    Only the AudioSet heads may be left out; any other key outside the encoder means the file
    is not a PretrainedSED BEATs student and loading stops.
    """
    encoder = {key.removeprefix(CHECKPOINT_PREFIX): value for key, value in state.items()
               if key.startswith(CHECKPOINT_PREFIX)}
    ignored = tuple(sorted(key for key in state if not key.startswith(CHECKPOINT_PREFIX)))
    unexpected = [key for key in ignored if not key.startswith(HEAD_PREFIXES)]
    if unexpected or not encoder:
        raise ValueError(f"not a PretrainedSED BEATs checkpoint: unexpected keys {unexpected[:5]}")
    return encoder, ignored


class FrozenBeatsEncoder(nn.Module):
    """`[batch, 160000]` waveforms (16 kHz, 10 s) -> `[batch, 250, 768]` BEATs embeddings."""

    output_channels = EMBED_DIM

    def __init__(self, config: BEATsConfig | None = None,
                 sequence_length: int = SEQUENCE_LENGTH) -> None:
        super().__init__()
        self.beats = BEATs(config or BEATsConfig())
        self.sequence_length = sequence_length
        self.beats.requires_grad_(False)
        self.train(False)

    def train(self, mode: bool = True) -> FrozenBeatsEncoder:
        """Always eval: no dropout, no layerdrop, whatever the caller asks for."""
        return super().train(False)

    def fbank(self, waveforms: Tensor) -> Tensor:
        features = kaldi_fbank(waveforms.float() * 2**15, num_mel_bins=128,
                               sample_frequency=SAMPLE_RATE, frame_length=25, frame_shift=10)
        return (features - FBANK_MEAN) / (2 * FBANK_STD)

    def forward(self, waveforms: Tensor) -> Tensor:
        if waveforms.dim() != 2:
            raise ValueError(f"expected [batch, samples], got {tuple(waveforms.shape)}")
        features = self.fbank(waveforms).unsqueeze(1)  # [batch, 1, frames, mel]
        tokens = self.beats.extract_features(features, do_preprocess=False)[0]
        # PretrainedSED PredictionsWrapper: pool (or stretch) the token sequence to 250 steps.
        if tokens.shape[1] > self.sequence_length:
            tokens = nn.functional.adaptive_avg_pool1d(tokens.transpose(1, 2),
                                                       self.sequence_length).transpose(1, 2)
        elif tokens.shape[1] < self.sequence_length:
            tokens = nn.functional.interpolate(tokens.transpose(1, 2), size=self.sequence_length,
                                               mode="linear").transpose(1, 2)
        return tokens

    def load_pretrained(self, path: Path,
                        expected_sha256: str | None = BEATS_STRONG_1_SHA256) -> BeatsLoadReport:
        """Load the BEATs part of a PretrainedSED checkpoint; strict on every encoder tensor."""
        digest = sha256_of(path)
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError(f"{path} has SHA-256 {digest}, expected {expected_sha256} "
                             "(ADR-0032: BEATs_strong_1.pt, PretrainedSED v0.0.1)")
        state = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
        encoder, ignored = encoder_state_from_checkpoint(state)
        self.beats.load_state_dict(encoder, strict=True)
        return BeatsLoadReport(
            checkpoint_sha256=digest,
            loaded_tensors=len(encoder),
            loaded_parameters=sum(value.numel() for value in encoder.values()),
            ignored_keys=ignored,
        )
