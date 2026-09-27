"""Kaldi `compute-fbank-feats` log-mel filterbank in plain PyTorch, batched (ADR-0032).

BEATs was pre-trained on `torchaudio.compliance.kaldi.fbank` features, so a frozen BEATs only sees
the input it was trained on if that path is reproduced exactly. torchaudio is not a dependency of
this repository, so this module reimplements the one configuration BEATs uses -- Kaldi defaults
except `num_mel_bins` -- following torchaudio 2.11.0 `compliance/kaldi.py` step by step:
snip-edges framing, per-frame DC removal, pre-emphasis 0.97 with the first sample replicated,
Povey window, zero padding to a power of two, power spectrum, Kaldi mel banks (20 Hz to Nyquist),
natural log floored at float32 epsilon. No dither, no energy column.

Parity with torchaudio is pinned by `tests/test_kaldi_fbank.py` against reference values that
torchaudio 2.11.0 produced once; the measured difference on real DataSED audio is in ADR-0032.
"""

from __future__ import annotations

import math

import torch
from torch import Tensor

MILLISECONDS_TO_SECONDS = 0.001
PREEMPHASIS = 0.97
POVEY_POWER = 0.85  # Povey window = symmetric Hann ** 0.85
LOW_FREQ_HZ = 20.0
EPSILON = torch.finfo(torch.float32).eps


def _mel(frequency: Tensor) -> Tensor:
    return 1127.0 * (1.0 + frequency / 700.0).log()


def _mel_scalar(frequency: float) -> float:
    return 1127.0 * math.log(1.0 + frequency / 700.0)


def kaldi_mel_banks(num_bins: int, padded_window: int, sample_frequency: float,
                    low_freq: float = LOW_FREQ_HZ, high_freq: float = 0.0) -> Tensor:
    """Triangular Kaldi mel filters `[num_bins, padded_window // 2 + 1]`, float32.

    Same arithmetic, in the same order, as torchaudio's `get_mel_banks` without VTLN warping;
    the Nyquist FFT bin gets zero weight (the reference pads that column after building the
    banks over `padded_window / 2` bins).
    """
    if num_bins <= 3 or padded_window % 2:
        raise ValueError("need more than 3 mel bins and an even padded window")
    num_fft_bins = padded_window / 2
    nyquist = 0.5 * sample_frequency
    if high_freq <= 0.0:
        high_freq += nyquist
    if not 0.0 <= low_freq < high_freq <= nyquist:
        raise ValueError(f"bad mel range {low_freq}..{high_freq} Hz for Nyquist {nyquist} Hz")
    fft_bin_width = sample_frequency / padded_window
    mel_low = _mel_scalar(low_freq)
    mel_delta = (_mel_scalar(high_freq) - mel_low) / (num_bins + 1)
    index = torch.arange(num_bins).unsqueeze(1)
    left = mel_low + index * mel_delta
    center = mel_low + (index + 1.0) * mel_delta
    right = mel_low + (index + 2.0) * mel_delta
    mel = _mel(fft_bin_width * torch.arange(num_fft_bins)).unsqueeze(0)
    up_slope = (mel - left) / (center - left)
    down_slope = (right - mel) / (right - center)
    banks = torch.max(torch.zeros(1), torch.min(up_slope, down_slope))
    return torch.nn.functional.pad(banks, (0, 1), mode="constant", value=0)


def kaldi_fbank(waveform: Tensor, *, num_mel_bins: int = 23, sample_frequency: float = 16000.0,
                frame_length: float = 25.0, frame_shift: float = 10.0) -> Tensor:
    """Log-mel filterbank `[batch, frames, num_mel_bins]` of `waveform` `[batch, samples]`.

    Frames follow Kaldi `snip_edges`: `1 + (samples - window) // shift`. Computed in the dtype of
    `waveform` with autocast disabled, whatever the caller's context.
    """
    if waveform.dim() != 2:
        raise ValueError(f"expected [batch, samples], got {tuple(waveform.shape)}")
    # Same expression order as the reference, so the int() truncation matches (400.00000000000006).
    window_shift = int(sample_frequency * frame_shift * MILLISECONDS_TO_SECONDS)
    window_size = int(sample_frequency * frame_length * MILLISECONDS_TO_SECONDS)
    padded_window = 2 ** (window_size - 1).bit_length()
    if not 2 <= window_size <= waveform.shape[-1]:
        raise ValueError(f"need at least {window_size} samples, got {waveform.shape[-1]}")
    with torch.autocast(device_type=waveform.device.type, enabled=False):
        frames = waveform.unfold(-1, window_size, window_shift)
        frames = frames - frames.mean(dim=-1, keepdim=True)
        previous = torch.nn.functional.pad(frames, (1, 0), mode="replicate")[..., :-1]
        frames = frames - PREEMPHASIS * previous
        window = torch.hann_window(window_size, periodic=False, device=waveform.device,
                                   dtype=waveform.dtype).pow(POVEY_POWER)
        frames = torch.nn.functional.pad(frames * window, (0, padded_window - window_size))
        spectrum = torch.fft.rfft(frames).abs().pow(2.0)
        banks = kaldi_mel_banks(num_mel_bins, padded_window, sample_frequency)
        energies = torch.matmul(spectrum, banks.to(device=waveform.device, dtype=waveform.dtype).T)
        floor = torch.tensor(EPSILON, device=waveform.device, dtype=waveform.dtype)
        return torch.max(energies, floor).log()
