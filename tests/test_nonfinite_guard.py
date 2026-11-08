"""ADR-0043 P3: run_epoch drops a non-finite training batch and keeps BatchNorm stats clean."""

import torch
from torch import nn

from ml.training.sed import run_epoch


class _Poisonable(nn.Module):
    """Frame model `[B, 1, T, F] -> [B, T, C]` whose forward turns NaN on a flagged input."""

    def __init__(self, classes: int = 2) -> None:
        super().__init__()
        self.norm = nn.BatchNorm1d(4)
        self.head = nn.Linear(4, classes)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        x = features.squeeze(1)  # [B, T, F]
        x = self.norm(x.transpose(1, 2)).transpose(1, 2)
        return self.head(x)


def _batch(poison: bool) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    features = torch.randn(3, 1, 5, 4)
    if poison:
        features[0, 0, 0, 0] = float("nan")
    targets = (torch.rand(3, 5, 2) > 0.5).float()
    return features, targets, torch.ones(3, 5)


def test_nonfinite_batch_is_skipped_and_batchnorm_restored() -> None:
    torch.manual_seed(0)
    model = _Poisonable()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    loader = [_batch(False), _batch(True), _batch(False)]
    metrics = run_epoch(model, loader, device=torch.device("cpu"), pos_weight=torch.ones(2),
                        optimizer=optimizer, scaler=None, threshold=0.5)
    assert metrics["nonfinite_batches_skipped"] == 1
    assert all(torch.isfinite(b).all() for b in model.buffers() if b.is_floating_point())
    assert all(torch.isfinite(p).all() for p in model.parameters())
    assert torch.isfinite(torch.tensor(metrics["loss"]))


def test_finite_epoch_matches_unguarded_update() -> None:
    torch.manual_seed(1)
    loader = [_batch(False), _batch(False)]
    model = _Poisonable()
    reference = _Poisonable()
    reference.load_state_dict(model.state_dict())
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    metrics = run_epoch(model, loader, device=torch.device("cpu"), pos_weight=torch.ones(2),
                        optimizer=optimizer, scaler=None, threshold=0.5)
    ref_optimizer = torch.optim.SGD(reference.parameters(), lr=0.1)
    reference.train()
    for features, targets, _valid in loader:
        ref_optimizer.zero_grad()
        logits = reference(features)
        loss = nn.functional.binary_cross_entropy_with_logits(logits, targets)
        loss.backward()
        ref_optimizer.step()
    assert metrics["nonfinite_batches_skipped"] == 0
    for a, b in zip(model.state_dict().values(), reference.state_dict().values(), strict=True):
        assert torch.allclose(a.float(), b.float(), atol=1e-6)
