from __future__ import annotations

from torch import Tensor, nn


class ConvBlock(nn.Sequential):
    def __init__(self, input_channels: int, output_channels: int) -> None:
        super().__init__(
            nn.Conv2d(input_channels, output_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(output_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(output_channels, output_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(output_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1)),
        )


class AudioEncoder(nn.Module):
    """CNN encoder that preserves the input frame rate."""

    output_channels = 128

    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            ConvBlock(1, 32),
            ConvBlock(32, 64),
            ConvBlock(64, self.output_channels),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        encoded = self.network(inputs)
        return encoded.mean(dim=2)


class AudioClassifier(nn.Module):
    def __init__(self, classes: int, dropout: float = 0.2) -> None:
        super().__init__()
        self.encoder = AudioEncoder()
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.encoder.output_channels, classes),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.head(self.encoder(inputs).mean(dim=-1))


class SoundEventDetector(nn.Module):
    def __init__(self, classes: int, hidden_size: int = 128, dropout: float = 0.2) -> None:
        super().__init__()
        self.encoder = AudioEncoder()
        self.temporal = nn.GRU(
            input_size=self.encoder.output_channels,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(2 * hidden_size, classes)

    def forward(self, inputs: Tensor) -> Tensor:
        encoded = self.encoder(inputs).transpose(1, 2)
        contextual, _ = self.temporal(encoded)
        return self.head(self.dropout(contextual))

    def load_classifier_encoder(self, checkpoint: dict) -> None:
        state = checkpoint.get("model_state", checkpoint)
        encoder = {
            key.removeprefix("encoder."): value
            for key, value in state.items()
            if key.startswith("encoder.")
        }
        if not encoder:
            raise ValueError("Checkpoint has no classifier encoder weights")
        self.encoder.load_state_dict(encoder, strict=True)
