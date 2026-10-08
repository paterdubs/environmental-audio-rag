"""EfficientSED rotary gated attention, adapted to torch only; see NOTICE.md."""

import torch
from torch import nn
from torch.nn import functional as F

from .rotary import RotaryEmbedding


class RMSNorm(nn.Module):
    def __init__(self, size: int):
        super().__init__()
        self.scale = size ** .5
        self.gamma = nn.Parameter(torch.ones(size))

    def forward(self, x):
        return F.normalize(x, dim=-1) * self.scale * self.gamma


class Attend(nn.Module):
    def __init__(self, dropout: float = 0.):
        super().__init__()
        self.dropout = dropout

    def forward(self, q, k, v):
        return F.scaled_dot_product_attention(q, k, v,
                                             dropout_p=self.dropout if self.training else 0.)


class Attention(nn.Module):
    def __init__(self, dim: int, heads: int = 8, dim_head: int = 32,
                 dropout: float = .1, gating: bool = True):
        super().__init__()
        self.heads = heads
        self.pos_encoding = RotaryEmbedding(dim_head)
        self.attend = Attend(dropout)
        self.norm = RMSNorm(dim)
        self.to_qkv = nn.Linear(dim, heads * dim_head * 3, bias=False)
        self.to_gates = nn.Linear(dim, heads) if gating else None
        self.to_out = nn.Sequential(nn.Linear(heads * dim_head, dim, bias=False), nn.Dropout(dropout))

    def forward(self, x):
        x = self.norm(x)
        batch, length, _ = x.shape
        q, k, v = self.to_qkv(x).reshape(batch, length, 3, self.heads, -1).permute(2, 0, 3, 1, 4)
        q = self.pos_encoding.rotate_queries_or_keys(q)
        k = self.pos_encoding.rotate_queries_or_keys(k)
        out = self.attend(q, k, v)
        if self.to_gates is not None:
            gates = self.to_gates(x).permute(0, 2, 1).unsqueeze(-1).sigmoid()
            out = out * gates
        return self.to_out(out.permute(0, 2, 1, 3).reshape(batch, length, -1))
