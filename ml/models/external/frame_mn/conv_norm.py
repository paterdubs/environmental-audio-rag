"""Stand-in for `torchvision.ops.misc.ConvNormActivation`, the only torchvision symbol frame_mn uses.

Written for this repository (not copied): the behaviour frame_mn relies on is a `Sequential` of
Conv2d (padding `(k - 1) // 2 * dilation` per dimension, bias only without a norm layer), the norm
layer, then the activation with `inplace=True`. Keeping that module order keeps the state-dict keys
(`<i>.0.weight`, `<i>.1.running_mean`, ...), so the checkpoint loads with `strict=True`.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from torch import nn


def _pair(value: int | Sequence[int]) -> tuple[int, int]:
    return (value, value) if isinstance(value, int) else (int(value[0]), int(value[1]))


class ConvNormActivation(nn.Sequential):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3,
                 stride: int | Sequence[int] = 1, padding: int | Sequence[int] | None = None,
                 groups: int = 1,
                 norm_layer: Callable[..., nn.Module] | None = nn.BatchNorm2d,
                 activation_layer: Callable[..., nn.Module] | None = nn.ReLU,
                 dilation: int | Sequence[int] = 1, inplace: bool | None = True,
                 bias: bool | None = None) -> None:
        if padding is None:
            kernel, dil = _pair(kernel_size), _pair(dilation)
            padding = tuple((kernel[i] - 1) // 2 * dil[i] for i in range(2))
        if bias is None:
            bias = norm_layer is None
        layers: list[nn.Module] = [nn.Conv2d(in_channels, out_channels, kernel_size, stride,
                                             padding, dilation=dilation, groups=groups,
                                             bias=bias)]
        if norm_layer is not None:
            layers.append(norm_layer(out_channels))
        if activation_layer is not None:
            layers.append(activation_layer(**({} if inplace is None else {"inplace": inplace})))
        super().__init__(*layers)
        self.out_channels = out_channels
