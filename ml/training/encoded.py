"""Frozen encoder in the data path (Track 2a, ADR-0032 §2).

`EncodedLoader` wraps a DataLoader of raw inputs and yields `(encoder(inputs), targets, valid)`.
The frozen encoder therefore never enters the trained model: `train_sed`, `run_epoch` and
`collect_predictions` see an ordinary loader and a small head, checkpoints hold only the head,
and every epoch encodes fresh random crops exactly as SED v2 crops log-mel windows.

Targets and masks stay on the CPU as the wrapped loader produced them (`collect_predictions`
reads them with `.numpy()`); only the encoded inputs live on `device`.
"""

from __future__ import annotations

from collections.abc import Iterator

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, Dataset, Sampler


class EncodedLoader:
    def __init__(self, loader: DataLoader, encoder: nn.Module, device: torch.device) -> None:
        if any(parameter.requires_grad for parameter in encoder.parameters()):
            raise ValueError("EncodedLoader expects a frozen encoder (requires_grad=False)")
        self.loader = loader
        self.encoder = encoder.to(device).eval()
        self.device = device

    @property
    def dataset(self) -> Dataset:
        return self.loader.dataset

    @property
    def sampler(self) -> Sampler:
        return self.loader.sampler

    @property
    def drop_last(self) -> bool:
        return self.loader.drop_last

    @property
    def batch_size(self) -> int | None:
        return self.loader.batch_size

    def __len__(self) -> int:
        return len(self.loader)

    def __iter__(self) -> Iterator[tuple[Tensor, Tensor, Tensor]]:
        for inputs, targets, valid in self.loader:
            with torch.no_grad(), torch.amp.autocast(device_type=self.device.type,
                                                     enabled=self.device.type == "cuda"):
                encoded = self.encoder(inputs.to(self.device, non_blocking=True))
            yield encoded.float(), targets, valid
