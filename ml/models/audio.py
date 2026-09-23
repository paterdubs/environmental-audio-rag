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
    """Frame-level SED head. Contract: output có **đúng** T frame của input.

    `AudioEncoder` giữ nguyên T (chỉ pool tần số). `PannsCNN14Encoder` pool cả
    hai chiều 6 lần — T giảm còn T/64. Cắm thẳng CNN14 vào mà không xử lý gì sẽ
    làm GRU nhận sai số frame và loss vỡ shape so với target 50 fps
    ([ADR-0014](../../docs/decisions/ADR-0014-doi-chieu-do-phan-giai-thoi-gian-cnn14.md)).
    """

    def __init__(
        self,
        classes: int,
        encoder: nn.Module | None = None,
        hidden_size: int = 128,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.encoder = encoder or AudioEncoder()
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
        target_frames = inputs.shape[-1]
        encoded = self.encoder(inputs)
        if encoded.shape[-1] != target_frames:
            # CNN14 nén T còn T/64. Phục hồi bằng nearest-neighbor thay vì linear:
            # mỗi frame đã pool mang thông tin của một cửa sổ ~64 frame gốc, và
            # nearest lặp lại đúng giá trị đó thay vì bịa ra giá trị trung gian
            # không tồn tại. Đây là cách chính PANNs dùng để khôi phục
            # framewise output sau pooling (Kong et al., 2020).
            encoded = nn.functional.interpolate(encoded, size=target_frames, mode="nearest")
        contextual, _ = self.temporal(encoded.transpose(1, 2))
        return self.head(self.dropout(contextual))

    def load_classifier_encoder(self, checkpoint: dict) -> None:
        """Nạp trọng số encoder từ checkpoint classifier cùng kiến trúc.

        `strict=True` là đúng đắn **miễn là** encoder của checkpoint và encoder
        hiện tại (`AudioEncoder` hoặc `PannsCNN14Encoder`, tuỳ constructor) cùng
        kiểu. Nạp nhầm kiểu sẽ vỡ ở đây với thông báo rõ, thay vì im lặng bỏ qua
        vài layer hay vỡ bằng lỗi PyTorch khó đọc.
        """
        state = checkpoint.get("model_state", checkpoint)
        encoder = {
            key.removeprefix("encoder."): value
            for key, value in state.items()
            if key.startswith("encoder.")
        }
        if not encoder:
            raise ValueError("Checkpoint has no classifier encoder weights")
        expected = set(self.encoder.state_dict())
        given = set(encoder)
        if expected != given:
            raise ValueError(
                "Checkpoint encoder keys don't match this model's encoder type "
                f"({type(self.encoder).__name__}): "
                f"missing={sorted(expected - given)[:3]} unexpected={sorted(given - expected)[:3]}"
            )
        self.encoder.load_state_dict(encoder, strict=True)
