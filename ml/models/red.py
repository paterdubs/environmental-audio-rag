"""Recurrent Event Detection (RED) and its onset/offset loss (ADR-0041 O-E1).

Schmid et al., "Sound Event Detection with Boundary-Aware Optimization and Inference", IEEE SPL
2026 (arXiv 2601.04178v2, §II-A/B, eqs. (1)-(3); notes in `docs/notes/red_epn_spec.md`). Per
class and frame the network emits two logits: start `z_s` (P(active | inactive before)) and end
`z_e` (P(inactive | active before)). With p the presence probability:

    p_t = s_t (1 - p_{t-1}) + (1 - q_t) p_{t-1},   o_t = s_t (1 - p_{t-1}),   f_t = q_t p_{t-1}

computed here in log space (two states, simultaneous update) and in float32. Choices the paper
leaves open, fixed for O-E1 before any run:
  * presence before a window starts is ~0 (log p = INITIAL_LOG_PRESENCE), so a window starting
    inside an event opens with an onset; that first frame is excluded from the boundary loss;
  * boundary targets come from the presence targets of the same batch (after mixup), on the
    model's step grid: y_on_t = max(0, y_t - y_{t-1}), y_off_t = max(0, y_{t-1} - y_t), t >= 1.
    Soft presence targets (mixup, merged duplicates) give soft boundary targets;
  * a step counts only if all of its label frames are valid (padding is never a boundary);
  * loss (3) = focal with exponent 2 on o and f, mean over valid steps x classes, weight 100.
The model's output logit is log p - log(1 - p), so sigmoid(output) = p and every downstream step
(prediction artifacts, window merging, θ / cSEBB) is unchanged.
"""

from __future__ import annotations

import torch
from torch import Tensor, nn

INITIAL_LOG_PRESENCE = -30.0  # p_{-1} = e^-30: "inactive" without log(0)
LOG_FLOOR = -30.0  # clamp for log o / log f inside the loss
BOUNDARY_WEIGHT = 100.0  # lambda_ool of eq. (5)
FOCAL_EXPONENT = 2.0  # "alpha = 2" in eq. (3)


def red_log_recurrence(start_logits: Tensor, end_logits: Tensor
                       ) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    """`[batch, steps, classes]` start/end logits -> (log p, log(1-p), log o, log f)."""
    if start_logits.shape != end_logits.shape or start_logits.dim() != 3:
        raise ValueError("start/end logits must share a [batch, steps, classes] shape")
    log_s, log_not_s = nn.functional.logsigmoid(start_logits), nn.functional.logsigmoid(
        -start_logits)
    log_q, log_not_q = nn.functional.logsigmoid(end_logits), nn.functional.logsigmoid(
        -end_logits)
    batch, steps, classes = start_logits.shape
    on = start_logits.new_full((batch, classes), INITIAL_LOG_PRESENCE)
    off = torch.log1p(-torch.exp(on))
    presence, absence, onsets, offsets = [], [], [], []
    for t in range(steps):
        onset = log_s[:, t] + off
        offset = log_q[:, t] + on
        on, off = (torch.logaddexp(onset, log_not_q[:, t] + on),
                   torch.logaddexp(log_not_s[:, t] + off, offset))
        presence.append(on)
        absence.append(off)
        onsets.append(onset)
        offsets.append(offset)
    return tuple(torch.stack(x, dim=1) for x in (presence, absence, onsets, offsets))


def boundary_targets(presence: Tensor, valid: Tensor, steps: int
                     ) -> tuple[Tensor, Tensor, Tensor]:
    """Label-grid presence `[batch, frames, classes]` and valid `[batch, frames]` ->
    (onset target, offset target, step mask), all on a `steps`-long grid."""
    batch, frames, classes = presence.shape
    if frames % steps:
        raise ValueError(f"{frames} label frames do not pool evenly into {steps} steps")
    factor = frames // steps
    y = presence.reshape(batch, steps, factor, classes).amax(dim=2)
    mask = valid.reshape(batch, steps, factor).amin(dim=2)
    previous = torch.cat([y[:, :1], y[:, :-1]], dim=1)  # t = 0 compares with itself: no boundary
    onset = (y - previous).clamp_min(0.0)
    offset = (previous - y).clamp_min(0.0)
    mask = mask.clone()
    mask[:, 0] = 0.0  # presence before the window is unknown: the first step is censored
    return onset, offset, mask


def focal_boundary_loss(log_u: Tensor, target: Tensor, mask: Tensor) -> Tensor:
    """Eq. (3) for one of o / f: `[batch, steps, classes]` log-probabilities and targets."""
    log_u = log_u.clamp(min=LOG_FLOOR, max=0.0)
    u = log_u.exp()
    log_not_u = torch.log1p(-u.clamp(max=1.0 - 1e-6))
    loss = -(target * (1.0 - u) ** FOCAL_EXPONENT * log_u
             + (1.0 - target) * u ** FOCAL_EXPONENT * log_not_u)
    weights = mask.unsqueeze(-1).expand_as(loss)
    return (loss * weights).sum() / weights.sum().clamp_min(1.0)


class RedHead(nn.Module):
    """Linear start/end logits per class + RED. Keeps the last onset/offset log-probabilities
    so the training loop can add the boundary loss after the presence loss."""

    def __init__(self, in_features: int, classes: int) -> None:
        super().__init__()
        self.classes = classes
        self.linear = nn.Linear(in_features, 2 * classes)
        self.last_boundaries: tuple[Tensor, Tensor] | None = None

    def forward(self, steps: Tensor) -> Tensor:
        """`[batch, steps, features]` -> presence logits `[batch, steps, classes]`."""
        logits = self.linear(steps).float().reshape(*steps.shape[:2], self.classes, 2)
        with torch.autocast(device_type=steps.device.type, enabled=False):
            log_p, log_not_p, log_o, log_f = red_log_recurrence(logits[..., 0], logits[..., 1])
        self.last_boundaries = (log_o, log_f)
        return log_p - log_not_p

    def boundary_loss(self, targets: Tensor, valid: Tensor) -> Tensor:
        if self.last_boundaries is None:
            raise RuntimeError("boundary_loss needs a forward pass first")
        log_o, log_f = self.last_boundaries
        onset, offset, mask = boundary_targets(targets.float(), valid.float(), log_o.shape[1])
        return BOUNDARY_WEIGHT * (focal_boundary_loss(log_o, onset, mask)
                                  + focal_boundary_loss(log_f, offset, mask))
