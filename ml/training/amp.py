"""Mixed-precision inference forward with an fp32 retry (ADR-0043 §3, P3).

Validation, `collect_predictions` and serving run the model under fp16 autocast on CUDA. A rare
window can push an activation past the fp16 range (P3: `encoder.features.16.0`, input ~5e3 → inf),
turning the whole batch into NaN. Such a batch is recomputed in fp32. Batches that are finite in
fp16 return exactly what they always did, so every artifact produced before this guard is
unchanged (any non-finite batch would have crashed `frame_metrics` or poisoned the stitch).
"""

from __future__ import annotations

import torch
from torch import Tensor, nn


def amp_forward(model: nn.Module, features: Tensor) -> tuple[Tensor, bool]:
    """Logits under autocast (CUDA only) and whether the fp32 retry was needed."""
    device_type = features.device.type
    with torch.amp.autocast(device_type=device_type, enabled=device_type == "cuda"):
        logits = model(features)
    if device_type != "cuda" or torch.isfinite(logits).all():
        return logits, False
    with torch.amp.autocast(device_type=device_type, enabled=False):
        return model(features.float()), True
