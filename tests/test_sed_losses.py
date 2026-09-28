import torch

from ml.training.sed import masked_bce, masked_focal, masked_loss


def test_focal_value_matches_hand_calculation() -> None:
    logits = torch.tensor([[[0.0], [2.0]]])
    targets = torch.tensor([[[1.0], [0.0]]])
    valid = torch.ones(1, 2)
    probability = logits.sigmoid()
    expected = (
        -torch.log(probability[0, 0, 0]) * (1 - probability[0, 0, 0]) ** 2
        - torch.log(1 - probability[0, 1, 0]) * probability[0, 1, 0] ** 2
    ) / 2
    torch.testing.assert_close(masked_focal(logits, targets, valid, gamma=2.0), expected)


def test_focal_gamma_zero_is_bce_without_pos_weight() -> None:
    logits = torch.tensor([[[-1.0, 0.5], [2.0, -2.0]]])
    targets = torch.tensor([[[0.0, 1.0], [1.0, 0.0]]])
    valid = torch.tensor([[1.0, 0.0]])
    bce = masked_bce(logits, targets, valid, torch.ones(2))
    focal = masked_focal(logits, targets, valid, gamma=0.0)
    assert focal == bce
    assert masked_loss(logits, targets, valid, torch.ones(2), loss="focal", focal_gamma=0) == bce


def test_new_losses_have_finite_gradients() -> None:
    for name in ("focal", "asl"):
        logits = torch.tensor([[[-0.2, 1.1], [0.7, -1.4]]], requires_grad=True)
        targets = torch.tensor([[[0.0, 1.0], [1.0, 0.0]]])
        valid = torch.ones(1, 2)
        loss = masked_loss(logits, targets, valid, torch.ones(2), loss=name)
        loss.backward()
        assert torch.isfinite(loss)
        assert logits.grad is not None and torch.isfinite(logits.grad).all()


def test_focal_stays_finite_for_saturated_logits() -> None:
    logits = torch.tensor([[[1000.0], [-1000.0]]], requires_grad=True)
    targets = torch.tensor([[[1.0], [0.0]]])
    valid = torch.ones(1, 2)
    loss = masked_focal(logits, targets, valid, gamma=0.5)
    assert torch.isfinite(loss)
    loss.backward()
    assert logits.grad is not None and torch.isfinite(logits.grad).all()
