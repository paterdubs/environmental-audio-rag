"""Batch augmentation for SED training (ADR-0030): mixup and FilterAugment.

Both act on a batch of normalised log-mel windows ``[batch, 1, mel, frames]`` on the
training device, after loading and before the model. Features are `power_to_db` scaled to
[0, 1] with 1 unit = `top_db` dB (`ml/features/logmel.py`), so a filter gain of g dB is an
**additive** g / top_db — the log-domain form of applying a filter.

* **Mixup** (Zhang et al. 2018; applied to log-mel as in PANNs, Kong et al. 2020): each
  window is mixed with a shuffled partner, λ ~ Beta(α, α); targets mix with the same λ
  (soft labels); the loss mask keeps frames valid in both windows.
* **FilterAugment** (Nam et al., ICASSP 2022): the mel axis is split into random bands,
  each gets a random gain in [-6, 6] dB — constant per band ("step") or linearly
  interpolated between band edges ("linear"), chosen with equal probability as in the
  authors' ICASSP 2022 variant.
"""

from __future__ import annotations

import torch
from torch import Tensor

TOP_DB = 80.0


def mixup(features: Tensor, targets: Tensor, valid: Tensor, *, alpha: float = 0.2
          ) -> tuple[Tensor, Tensor, Tensor]:
    batch = features.shape[0]
    lam = torch.distributions.Beta(alpha, alpha).sample((batch,)).to(features.device)
    partner = torch.randperm(batch, device=features.device)
    weight_x = lam.view(batch, 1, 1, 1).to(features.dtype)
    weight_y = lam.view(batch, 1, 1).to(targets.dtype)
    mixed = weight_x * features + (1 - weight_x) * features[partner]
    mixed_targets = weight_y * targets + (1 - weight_y) * targets[partner]
    return mixed, mixed_targets, valid * valid[partner]


def _band_edges(mel_bins: int, bands: int, min_width: int) -> Tensor:
    while min_width > 1 and mel_bins - bands * min_width + 1 <= 0:
        min_width -= 1
    inner = torch.sort(torch.randint(0, mel_bins - bands * min_width + 1, (bands - 1,)))[0]
    inner = inner + torch.arange(1, bands) * min_width
    return torch.cat([torch.tensor([0]), inner, torch.tensor([mel_bins])])


def filter_gains_db(batch: int, mel_bins: int, *, db_range: float = 6.0) -> Tensor:
    """Per-window gain curve over the mel axis, in dB: ``[batch, mel_bins]``."""
    step = bool(torch.rand(1).item() < 0.5)
    low, high, min_width = (2, 5, 4) if step else (3, 6, 6)
    bands = int(torch.randint(low, high, (1,)).item())
    edges = _band_edges(mel_bins, bands, min_width)
    if step:
        levels = (torch.rand(batch, bands) * 2 - 1) * db_range
        widths = torch.diff(edges)
        return torch.repeat_interleave(levels, widths, dim=1)
    levels = (torch.rand(batch, bands + 1) * 2 - 1) * db_range  # gain at each band edge
    curve = torch.empty(batch, mel_bins)
    for band in range(bands):
        start, stop = int(edges[band]), int(edges[band + 1])
        fraction = torch.arange(stop - start) / (stop - start)
        left, right = levels[:, band:band + 1], levels[:, band + 1:band + 2]
        curve[:, start:stop] = left + fraction * (right - left)
    return curve


def filter_augment(features: Tensor, *, db_range: float = 6.0) -> Tensor:
    batch, _, mel_bins, _ = features.shape
    gains = filter_gains_db(batch, mel_bins, db_range=db_range).to(features)
    shifted = features + (gains / TOP_DB).view(batch, 1, mel_bins, 1)
    return shifted.clamp_min(0.0)  # below the top_db floor does not exist in real features


def augment_batch(features: Tensor, targets: Tensor, valid: Tensor, *, mixup_p: float,
                  filter_augment_p: float) -> tuple[Tensor, Tensor, Tensor]:
    """Apply each augmentation to the whole batch with its probability (training only)."""
    if filter_augment_p > 0 and torch.rand(1).item() < filter_augment_p:
        features = filter_augment(features)
    if mixup_p > 0 and torch.rand(1).item() < mixup_p:
        features, targets, valid = mixup(features, targets, valid)
    return features, targets, valid
