"""Kaldi fbank (ADR-0032): the BEATs frontend must reproduce torchaudio's compliance.kaldi.

`tests/fixtures/kaldi_fbank_reference.npz` holds what torchaudio 2.11.0 returned for
`reference_signal()` (generated once, outside the repo's environment -- torchaudio is not a
dependency). On the machine that generated it the match was bit-exact; the tolerance only
absorbs cross-platform ulp differences in `np.sin`/FFT.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from ml.features.kaldi_fbank import EPSILON, kaldi_fbank, kaldi_mel_banks

FIXTURE = Path(__file__).parent / "fixtures" / "kaldi_fbank_reference.npz"
SAMPLE_RATE = 16_000


def reference_signal(duration_s: float = 0.5) -> np.ndarray:
    """0.1 s digital silence, then two tones plus a 100 -> 7900 Hz linear chirp. No RNG."""
    t = np.arange(round(SAMPLE_RATE * duration_s), dtype=np.float64) / SAMPLE_RATE
    chirp = np.sin(2 * np.pi * (100 * t + (7900 - 100) / (2 * duration_s) * t**2))
    signal = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.sin(2 * np.pi * 3000 * t) + 0.05 * chirp
    signal[: SAMPLE_RATE // 10] = 0.0
    return signal.astype(np.float32)


def _fbank(waveform: torch.Tensor) -> torch.Tensor:
    return kaldi_fbank(waveform, num_mel_bins=128, sample_frequency=16000, frame_length=25,
                       frame_shift=10)


def _reference_input() -> torch.Tensor:
    return torch.from_numpy(reference_signal()).unsqueeze(0) * 2**15  # as BEATs.preprocess


def test_matches_torchaudio_reference_values() -> None:
    expected = np.load(FIXTURE)["fbank"]
    ours = _fbank(_reference_input())[0].numpy()
    assert ours.shape == expected.shape == (48, 128)
    np.testing.assert_allclose(ours, expected, rtol=0, atol=1e-4)


def test_ten_seconds_gives_998_snip_edges_frames() -> None:
    assert _fbank(torch.zeros(2, 160_000)).shape == (2, 998, 128)


def test_digital_silence_sits_on_the_epsilon_floor() -> None:
    silent = _fbank(torch.zeros(1, 1_600))
    assert torch.equal(silent, torch.full_like(silent, float(np.log(EPSILON))))


def test_batch_rows_are_computed_independently() -> None:
    first = _reference_input()
    second = torch.flip(first, dims=[1]) * 0.5
    batched = _fbank(torch.cat([first, second]))
    assert torch.equal(batched[0], _fbank(first)[0])
    assert torch.equal(batched[1], _fbank(second)[0])


def test_stays_float32_under_an_ambient_autocast() -> None:
    plain = _fbank(_reference_input())
    with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
        inside = _fbank(_reference_input())
    assert inside.dtype == torch.float32
    assert torch.equal(inside, plain)


def test_mel_banks_are_nonnegative_triangles_with_a_zero_nyquist_column() -> None:
    banks = kaldi_mel_banks(128, 512, 16000.0)
    assert banks.shape == (128, 257)
    assert bool((banks >= 0).all()) and bool((banks <= 1).all())
    assert bool((banks[:, -1] == 0).all())


def test_the_beats_configuration_has_exactly_one_empty_mel_filter() -> None:
    # At 128 bins over 20 Hz..8 kHz with a 512-point FFT (31.25 Hz per bin), filter 3 is narrower
    # than the FFT bin spacing and catches no bin: BEATs input channel 3 is always log(epsilon).
    # torchaudio does the same (the reference fixture is bit-identical); this pins the fact.
    sums = kaldi_mel_banks(128, 512, 16000.0).sum(dim=1)
    assert torch.nonzero(sums == 0).flatten().tolist() == [3]
    assert bool((_fbank(_reference_input())[0, :, 3] == float(np.log(EPSILON))).all())


def test_rejects_input_shorter_than_one_window() -> None:
    with pytest.raises(ValueError, match="at least 400 samples"):
        _fbank(torch.zeros(1, 399))
    with pytest.raises(ValueError, match=r"\[batch, samples\]"):
        _fbank(torch.zeros(160_000))
