from pathlib import Path

import pytest
import torch

from ml.models.external.efficientsed_tf import build_tf256
from ml.models.external.efficientsed_tf.rotary import RotaryEmbedding, apply_rotary_emb

CHECKPOINTS = (Path(__file__).resolve().parents[2] / 'environmental-audio-rag'
               / 'artifacts/checkpoints/efficientsed')


@pytest.mark.parametrize('name', ['fmn10+tf-256_strong.pt',
                                 'fmn10+tf-256_advanced-kd-weak-strong.pt'])
def test_real_sequence_checkpoint_loads_strictly_and_forwards_on_cpu(name):
    path = CHECKPOINTS / name
    if not path.is_file():
        pytest.skip(f'checkpoint not downloaded: {name}')
    data = torch.load(path, map_location='cpu', weights_only=True)
    state = {k.removeprefix('net.seq_model.'): v for k, v in data.items()
             if k.startswith('net.seq_model.')}
    assert len(state) == 25
    model = build_tf256().eval()
    loaded = model.load_state_dict(state, strict=True)
    assert not loaded.missing_keys and not loaded.unexpected_keys
    with torch.inference_mode():
        out = model(torch.randn(2, 250, 960, generator=torch.Generator().manual_seed(20260922)))
    assert out.shape == (2, 250, 256)
    assert out.device.type == 'cpu' and torch.isfinite(out).all()
    assert all(not m.freqs.requires_grad for m in model.modules() if isinstance(m, RotaryEmbedding))


def test_sequence_backward_and_strict_rejects_missing_rotary_key():
    model = build_tf256(dropout=0.)
    x = torch.randn(2, 7, 960, requires_grad=True)
    model(x).square().mean().backward()
    assert torch.isfinite(x.grad).all() and x.grad.abs().sum() > 0
    state = model.state_dict()
    state.pop('1.layers.0.0.pos_encoding.freqs')
    with pytest.raises(RuntimeError, match='Missing key'):
        model.load_state_dict(state, strict=True)


def test_rotary_cache_offsets_long_sequence_and_state_dict():
    rotary = RotaryEmbedding(32, cache_max_seq_len=5)
    x = torch.randn(2, 8, 5, 32)
    first = rotary.rotate_queries_or_keys(x)
    assert torch.equal(first, rotary.rotate_queries_or_keys(x))
    offset = rotary.rotate_queries_or_keys(x[:, :, :2], offset=2)
    fresh = RotaryEmbedding(32, cache_if_possible=False)
    assert torch.equal(offset, fresh.rotate_queries_or_keys(x[:, :, :2], offset=2))
    long = torch.randn(1, 8, 9, 32)
    assert torch.equal(rotary.rotate_queries_or_keys(long), fresh.rotate_queries_or_keys(long))
    assert list(rotary.state_dict()) == ['freqs']


def test_rotary_preserves_unrotated_features_and_rotation_norm():
    x = torch.randn(2, 8, 10, 40)
    freqs = torch.randn(10, 16).repeat_interleave(2, dim=-1)
    out = apply_rotary_emb(freqs, x, start_index=4)
    assert torch.equal(out[..., :4], x[..., :4])
    assert torch.equal(out[..., 36:], x[..., 36:])
    torch.testing.assert_close(out[..., 4:36].square().sum(-1), x[..., 4:36].square().sum(-1))
    q = torch.randn(2, 10, 8, 32)
    a, b = RotaryEmbedding(32), RotaryEmbedding(32)
    assert torch.equal(a.rotate_queries_or_keys(q, seq_dim=-3),
                       b.rotate_queries_or_keys(q.transpose(1, 2)).transpose(1, 2))
