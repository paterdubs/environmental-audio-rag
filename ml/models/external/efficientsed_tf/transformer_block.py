"""EfficientSED residual transformer blocks (MIT; see NOTICE.md)."""

from torch import nn

from .attention import Attention, RMSNorm


class FeedForward(nn.Module):
    def __init__(self, dim: int, mult: float = 4., dropout: float = .1):
        super().__init__()
        self.net = nn.Sequential(RMSNorm(dim), nn.Linear(dim, int(dim * mult)), nn.GELU(),
                                 nn.Dropout(dropout), nn.Linear(int(dim * mult), dim),
                                 nn.Dropout(dropout))

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, *, dim: int, depth: int, dim_head: int = 32, heads: int = 8,
                 attn_dropout: float = .1, ff_dropout: float = .1, ff_mult: float = 4.,
                 norm_output: bool = True, gating: bool = True):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.ModuleList([Attention(dim, heads, dim_head, attn_dropout, gating),
                           FeedForward(dim, ff_mult, ff_dropout)]) for _ in range(depth)])
        self.norm = RMSNorm(dim) if norm_output else nn.Identity()

    def forward(self, x):
        for attention, feed_forward in self.layers:
            x = attention(x) + x
            x = feed_forward(x) + x
        return self.norm(x)
