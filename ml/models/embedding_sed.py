"""SED head on a frozen embedding sequence (Track 2a, ADR-0032 §2).

Same head as SED v2 (`SoundEventDetector` with `upsample="after_rnn"`, ADR-0030 §1): a BiGRU at
the encoder's own step rate, dropout, a linear layer per step, then each step's logits repeated
(nearest) onto the label grid. Only the input differs -- `[batch, steps, dim]` embeddings from a
frozen encoder instead of a trainable CNN14 -- so a T2a vs v2 difference measures the encoder.
"""

from __future__ import annotations

from torch import Tensor, nn


class EmbeddingSequenceSED(nn.Module):
    """`[batch, steps, input_size]` -> logits `[batch, output_frames, classes]`."""

    def __init__(self, classes: int, *, input_size: int, output_frames: int,
                 hidden_size: int = 256, rnn_layers: int = 2, dropout: float = 0.2) -> None:
        super().__init__()
        if output_frames <= 0:
            raise ValueError("output_frames must be positive")
        self.output_frames = output_frames
        self.temporal = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=rnn_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if rnn_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(2 * hidden_size, classes)

    def forward(self, embeddings: Tensor) -> Tensor:
        if embeddings.dim() != 3:
            raise ValueError(f"expected [batch, steps, dim], got {tuple(embeddings.shape)}")
        contextual, _ = self.temporal(embeddings)
        logits = self.head(self.dropout(contextual))
        if logits.shape[1] != self.output_frames:
            logits = nn.functional.interpolate(
                logits.transpose(1, 2), size=self.output_frames, mode="nearest"
            ).transpose(1, 2)
        return logits
