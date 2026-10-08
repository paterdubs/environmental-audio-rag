"""Minimal EfficientSED TF256 sequence layers; no frontend or model wrapper.

See NOTICE.md for pinned upstream sources, changes, and MIT notices.
"""

from torch import nn

from .transformer_block import TransformerBlock


def build_tf256(input_dim: int = 960, dropout: float = .1) -> nn.Sequential:
    """Return upstream ``seq_model`` layout: [B,T,input_dim] -> [B,T,256].

    Load checkpoint keys after stripping only ``net.seq_model.`` with strict=True.
    The caller owns interpolation, classifier, masks, eval/train mode and device.
    """
    return nn.Sequential(
        nn.Linear(input_dim, 256) if input_dim != 256 else nn.Identity(),
        TransformerBlock(dim=256, depth=2, heads=8, dim_head=32,
                         attn_dropout=dropout, ff_dropout=dropout),
    )


__all__ = ['TransformerBlock', 'build_tf256']
