"""Torch-only subset of rotary-embedding-torch 0.9.1 (MIT; see NOTICE.md).

Only the default language frequencies and rotate_queries_or_keys path used by
EfficientSED are supported. No XPos, learned/pixel frequencies or axial helper.
"""

import torch
from torch import nn


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    paired = x.reshape(*x.shape[:-1], -1, 2)
    first, second = paired.unbind(dim=-1)
    return torch.stack((-second, first), dim=-1).flatten(-2)


@torch.amp.autocast('cuda', enabled=False)
def apply_rotary_emb(freqs: torch.Tensor, t: torch.Tensor, start_index: int = 0,
                     scale: float = 1., seq_dim: int = -2,
                     freqs_seq_dim: int | None = None) -> torch.Tensor:
    dtype = t.dtype
    if freqs_seq_dim is None and (freqs.ndim == 2 or t.ndim == 3):
        freqs_seq_dim = 0
    if t.ndim == 3 or freqs_seq_dim is not None:
        slices = [slice(None)] * freqs.ndim
        slices[freqs_seq_dim] = slice(-t.shape[seq_dim], None)
        freqs = freqs[tuple(slices)]
    end_index = start_index + freqs.shape[-1]
    if start_index < 0 or end_index > t.shape[-1]:
        raise ValueError('rotary dimensions exceed the feature dimension')
    middle = t[..., start_index:end_index]
    rotated = middle * freqs.cos() * scale + rotate_half(middle) * freqs.sin() * scale
    return torch.cat((t[..., :start_index], rotated, t[..., end_index:]), dim=-1).to(dtype)


class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, theta: float = 10000., cache_if_possible: bool = True,
                 cache_max_seq_len: int = 8192):
        super().__init__()
        if dim < 4 or dim % 2:
            raise ValueError('rotary dimension must be even and >=4')
        freqs = 1. / (theta ** (torch.arange(0, dim, 2)[:dim // 2].float() / dim))
        self.freqs = nn.Parameter(freqs, requires_grad=False)
        self.register_buffer('cached_freqs', torch.zeros(cache_max_seq_len, dim), persistent=False)
        self.register_buffer('dummy', torch.tensor(0), persistent=False)
        self.cache_if_possible = cache_if_possible
        self.cache_max_seq_len = cache_max_seq_len
        self.cached_freqs_seq_len = 0

    @torch.amp.autocast('cuda', enabled=False)
    def forward(self, t: torch.Tensor, seq_len: int | None = None,
                offset: int = 0) -> torch.Tensor:
        should_cache = (self.cache_if_possible and seq_len is not None
                        and offset + seq_len <= self.cache_max_seq_len)
        if should_cache and offset + seq_len <= self.cached_freqs_seq_len:
            return self.cached_freqs[offset:offset + seq_len].detach()
        freqs = torch.einsum('..., f -> ... f', t.to(self.freqs.dtype), self.freqs)
        freqs = freqs.unsqueeze(-1).expand(*freqs.shape, 2).reshape(*freqs.shape[:-1], -1)
        if should_cache and offset == 0:
            self.cached_freqs[:seq_len] = freqs.detach()
            self.cached_freqs_seq_len = seq_len
        return freqs

    def rotate_queries_or_keys(self, t: torch.Tensor, seq_dim: int = -2,
                               offset: int = 0, scale: float | None = None) -> torch.Tensor:
        if seq_dim not in (-2, -3) or offset < 0:
            raise ValueError('supported sequence dimensions: -2/-3; offset must be nonnegative')
        seq_len = t.shape[seq_dim]
        seq = torch.arange(seq_len, device=t.device, dtype=t.dtype) + offset
        freqs = self.forward(seq, seq_len=seq_len, offset=offset)
        if seq_dim == -3:
            freqs = freqs.unsqueeze(1)
        return apply_rotary_emb(freqs, t, scale=1. if scale is None else scale, seq_dim=seq_dim)
