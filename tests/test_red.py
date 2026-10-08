"""ADR-0041 O-E1: RED recurrence, boundary targets and loss, and the FrameMnSED RED head."""

from __future__ import annotations

import pytest
import torch

from ml.models.frame_mn_finetune import FrameMnSED
from ml.models.red import (
    INITIAL_LOG_PRESENCE,
    boundary_targets,
    focal_boundary_loss,
    red_log_recurrence,
)
from scripts.train_sed import RECIPES


def _naive(start: torch.Tensor, end: torch.Tensor) -> tuple[torch.Tensor, ...]:
    """Eqs. (1)-(2) in probability space, float64, p_{-1} = e^INITIAL_LOG_PRESENCE."""
    s, q = start.double().sigmoid(), end.double().sigmoid()
    previous = torch.full_like(s[:, 0], float(torch.tensor(INITIAL_LOG_PRESENCE).exp()))
    presence, onsets, offsets = [], [], []
    for t in range(s.shape[1]):
        onsets.append(s[:, t] * (1 - previous))
        offsets.append(q[:, t] * previous)
        previous = s[:, t] * (1 - previous) + (1 - q[:, t]) * previous
        presence.append(previous)
    return tuple(torch.stack(x, dim=1) for x in (presence, onsets, offsets))


def test_log_space_recurrence_matches_the_paper_equations() -> None:
    torch.manual_seed(0)
    start, end = torch.randn(3, 40, 5) * 3, torch.randn(3, 40, 5) * 3
    log_p, log_not_p, log_o, log_f = red_log_recurrence(start, end)
    presence, onsets, offsets = _naive(start, end)
    assert torch.allclose(log_p.exp().double(), presence, atol=1e-5)
    assert torch.allclose(log_o.exp().double(), onsets, atol=1e-5)
    assert torch.allclose(log_f.exp().double(), offsets, atol=1e-5)
    # the two states stay a probability pair, and p_t = p_{t-1} + o_t - f_t
    assert torch.allclose(log_p.exp() + log_not_p.exp(), torch.ones_like(log_p), atol=1e-5)
    p = log_p.exp()
    assert torch.allclose(p[:, 1:], p[:, :-1] + log_o.exp()[:, 1:] - log_f.exp()[:, 1:],
                          atol=1e-5)


def test_recurrence_and_loss_have_finite_gradients_at_extreme_logits() -> None:
    start = (torch.randn(2, 30, 4) * 60).requires_grad_()
    end = (torch.randn(2, 30, 4) * 60).requires_grad_()
    _, _, log_o, log_f = red_log_recurrence(start, end)
    target = torch.zeros(2, 30, 4)
    target[:, 10, 1] = 1.0
    mask = torch.ones(2, 30)
    loss = focal_boundary_loss(log_o, target, mask) + focal_boundary_loss(log_f, target, mask)
    loss.backward()
    assert torch.isfinite(loss) and torch.isfinite(start.grad).all()
    assert torch.isfinite(end.grad).all()


def test_boundary_targets_on_the_step_grid_with_censored_edges_and_padding() -> None:
    presence = torch.zeros(1, 40, 2)
    presence[0, 8:20, 0] = 1.0  # steps 2..4 (4 label frames per step)
    presence[0, 0:6, 1] = 1.0  # active from the window start: no onset, offset at step 2
    valid = torch.ones(1, 40)
    valid[0, 36:] = 0.0  # last step is padding
    onset, offset, mask = boundary_targets(presence, valid, steps=10)
    assert onset[0, :, 0].nonzero().flatten().tolist() == [2]
    assert offset[0, :, 0].nonzero().flatten().tolist() == [5]
    assert onset[0, :, 1].sum() == 0 and offset[0, :, 1].nonzero().flatten().tolist() == [2]
    assert mask[0].tolist() == [0.0] + [1.0] * 8 + [0.0]


def test_soft_presence_gives_soft_boundaries() -> None:
    presence = torch.zeros(1, 8, 1)
    presence[0, 4:, 0] = 0.5  # one of two merged annotations (DO-3) or a mixup
    onset, _, _ = boundary_targets(presence, torch.ones(1, 8), steps=4)
    assert onset[0, :, 0].tolist() == [0.0, 0.0, 0.5, 0.0]
    with pytest.raises(ValueError, match="pool evenly"):
        boundary_targets(presence, torch.ones(1, 8), steps=3)


def test_focal_loss_is_small_when_right_and_large_when_wrong() -> None:
    target, mask = torch.tensor([[[1.0], [0.0]]]), torch.ones(1, 2)
    right = torch.log(torch.tensor([[[0.99], [0.01]]]))
    wrong = torch.log(torch.tensor([[[0.01], [0.99]]]))
    assert focal_boundary_loss(right, target, mask) < 1e-3
    assert focal_boundary_loss(wrong, target, mask) > 1.0


def test_frame_mn_red_head_outputs_presence_logits_and_a_boundary_loss() -> None:
    torch.manual_seed(0)
    model = FrameMnSED(21, boundary_head="red")
    waveforms = torch.randn(2, 160_000) * 0.1
    logits = model(waveforms)
    assert tuple(logits.shape) == (2, 1000, 21)
    targets = torch.zeros(2, 1000, 21)
    targets[:, 200:400, 3] = 1.0
    loss = model.boundary_loss(targets, torch.ones(2, 1000))
    assert loss is not None and torch.isfinite(loss)
    (logits.mean() + loss).backward()
    assert FrameMnSED(21).boundary_loss(targets, torch.ones(2, 1000)) is None
    with pytest.raises(ValueError, match="boundary_head"):
        FrameMnSED(21, boundary_head="epn")


def test_oe_red_recipe_differs_from_t2b_only_by_the_red_head() -> None:
    t2b, red = dict(RECIPES["t2b"]), dict(RECIPES["oe_red"])
    assert red.pop("boundary_head") == "red"
    assert {key for key in t2b if t2b[key] != red[key]} == {"model_version"}
