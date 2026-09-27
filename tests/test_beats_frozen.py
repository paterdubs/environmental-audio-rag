"""Frozen BEATs embedder (Track 2a, ADR-0032 §2): shapes, freezing, checkpoint loading."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from ml.models.beats_frozen import (
    BEATS_STRONG_1_SHA256,
    SEQUENCE_LENGTH,
    WINDOW_SAMPLES,
    FrozenBeatsEncoder,
    encoder_state_from_checkpoint,
)
from ml.models.external.beats import BEATsConfig

REAL_CHECKPOINT = Path(__file__).resolve().parents[1] / "artifacts/checkpoints/BEATs_strong_1.pt"
TINY = {"embed_dim": 16, "encoder_layers": 2, "encoder_embed_dim": 32,
        "encoder_ffn_embed_dim": 64, "encoder_attention_heads": 4, "conv_pos": 16,
        "conv_pos_groups": 4}


def _tiny() -> FrozenBeatsEncoder:
    torch.manual_seed(0)
    return FrozenBeatsEncoder(BEATsConfig(TINY))


def _waveforms(batch: int = 2) -> torch.Tensor:
    return torch.randn(batch, WINDOW_SAMPLES, generator=torch.Generator().manual_seed(1)) * 0.1


def _pretrainedsed_state(encoder: FrozenBeatsEncoder) -> dict[str, torch.Tensor]:
    state = {f"model.model.{key}": value.clone() for key, value in
             encoder.beats.state_dict().items()}
    state["strong_head.weight"] = torch.zeros(447, 32)
    state["strong_head.bias"] = torch.zeros(447)
    return state


def test_ten_second_windows_become_250_steps() -> None:
    with torch.no_grad():
        embeddings = _tiny()(_waveforms())
    assert embeddings.shape == (2, SEQUENCE_LENGTH, 32)
    with pytest.raises(ValueError, match=r"\[batch, samples\]"):
        _tiny()(torch.zeros(WINDOW_SAMPLES))


def test_encoder_is_frozen_and_stays_in_eval_mode() -> None:
    encoder = _tiny()
    assert not any(parameter.requires_grad for parameter in encoder.parameters())
    encoder.train()
    assert not encoder.training and not encoder.beats.training
    assert not any(module.training for module in encoder.modules())


def test_forward_leaves_the_global_numpy_rng_alone() -> None:
    # NOTICE.md #3: upstream layerdrop drew from np.random on every forward, even in eval,
    # which would shift the dataset's random crops.
    encoder = _tiny()
    np.random.seed(123)
    before = np.random.get_state()[1].copy()
    with torch.no_grad():
        encoder(_waveforms(1))
    assert np.array_equal(np.random.get_state()[1], before)


def test_forward_is_deterministic() -> None:
    encoder = _tiny()
    with torch.no_grad():
        assert torch.equal(encoder(_waveforms()), encoder(_waveforms()))


def test_checkpoint_state_split_keeps_encoder_and_ignores_only_heads() -> None:
    state = _pretrainedsed_state(_tiny())
    encoder_state, ignored = encoder_state_from_checkpoint(state)
    assert ignored == ("strong_head.bias", "strong_head.weight")
    assert not any(key.startswith("model.") for key in encoder_state)
    with pytest.raises(ValueError, match="unexpected keys"):
        encoder_state_from_checkpoint({**state, "model.mel_transform.x": torch.zeros(1)})


def test_load_pretrained_restores_weights_and_checks_the_hash(tmp_path: Path) -> None:
    source = _tiny()
    for parameter in source.beats.parameters():
        parameter.data.normal_()
    path = tmp_path / "beats.pt"
    torch.save(_pretrainedsed_state(source), path)

    target = _tiny()
    report = target.load_pretrained(path, expected_sha256=None)
    assert report.loaded_tensors == len(source.beats.state_dict())
    assert report.ignored_keys == ("strong_head.bias", "strong_head.weight")
    with torch.no_grad():
        assert torch.equal(target(_waveforms()), source(_waveforms()))
    with pytest.raises(ValueError, match="SHA-256"):
        _tiny().load_pretrained(path, expected_sha256="0" * 64)

    incomplete = _pretrainedsed_state(source)
    incomplete.pop(next(key for key in incomplete if key.startswith("model.model.")))
    torch.save(incomplete, tmp_path / "incomplete.pt")
    with pytest.raises(RuntimeError, match="Missing key"):
        _tiny().load_pretrained(tmp_path / "incomplete.pt", expected_sha256=None)


@pytest.mark.skipif(not REAL_CHECKPOINT.exists(), reason="BEATs_strong_1.pt not downloaded")
def test_real_pretrainedsed_checkpoint_loads_every_encoder_tensor() -> None:
    report = FrozenBeatsEncoder().load_pretrained(REAL_CHECKPOINT)
    assert report.checkpoint_sha256 == BEATS_STRONG_1_SHA256
    assert (report.loaded_tensors, report.loaded_parameters) == (250, 90_354_032)
    assert report.ignored_keys == ("strong_head.bias", "strong_head.weight",
                                   "weak_head.bias", "weak_head.weight")
