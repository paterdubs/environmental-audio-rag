import torch

from ml.training.sed import masked_bce


def test_masked_bce_ignores_padded_frames() -> None:
    logits = torch.zeros(1, 3, 2)
    targets = torch.zeros_like(logits)
    valid = torch.tensor([[1.0, 1.0, 0.0]])
    pos_weight = torch.ones(2)
    baseline = masked_bce(logits, targets, valid, pos_weight)
    targets[:, 2, :] = 1.0

    changed_padding = masked_bce(logits, targets, valid, pos_weight)

    assert torch.equal(baseline, changed_padding)
