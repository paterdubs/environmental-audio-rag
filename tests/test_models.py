import pytest
import torch

from ml.models import AudioClassifier, SoundEventDetector


def test_models_preserve_expected_dimensions() -> None:
    inputs = torch.rand(2, 1, 64, 50)

    classification = AudioClassifier(classes=22)(inputs)
    detection = SoundEventDetector(classes=21)(inputs)

    assert classification.shape == (2, 22)
    assert detection.shape == (2, 50, 21)


def test_sound_event_detector_accepts_cnn14_and_restores_frame_rate() -> None:
    """CNN14 nén T còn T/64 — output phải phục hồi về đúng T của input (ADR-0014)."""
    from ml.models.panns import PannsCNN14Encoder

    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    model = SoundEventDetector(classes=21, encoder=encoder)
    inputs = torch.rand(2, 1, 64, 128)

    detection = model(inputs)

    assert detection.shape == (2, 128, 21)


def test_cnn14_backed_detector_upsamples_by_nearest_repeat() -> None:
    """Mỗi frame đã pool lặp lại nguyên giá trị, không nội suy tuyến tính bịa ra giá trị mới."""
    from ml.models.panns import PannsCNN14Encoder

    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    inputs = torch.rand(1, 1, 64, 128)
    pooled = encoder(inputs)

    restored = torch.nn.functional.interpolate(pooled, size=128, mode="nearest")

    assert torch.equal(restored[:, :, :64], pooled[:, :, :1].expand(-1, -1, 64))


def test_encoder_too_short_for_cnn14_raises_a_clear_error() -> None:
    from ml.models.panns import PannsCNN14Encoder

    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))

    with pytest.raises(ValueError, match="frame"):
        encoder(torch.rand(1, 1, 64, 32))


def test_load_classifier_encoder_rejects_a_mismatched_encoder_type() -> None:
    """Checkpoint của CNN14 nạp vào model dùng AudioEncoder phải vỡ với thông báo rõ."""
    from ml.models.panns import PannsCNN14Encoder

    source = SoundEventDetector(classes=21, encoder=PannsCNN14Encoder())
    target = SoundEventDetector(classes=21)

    with pytest.raises(ValueError, match="don't match"):
        target.load_classifier_encoder({"model_state": source.state_dict()})


def test_load_classifier_encoder_still_accepts_a_matching_audio_encoder() -> None:
    source = SoundEventDetector(classes=21)
    target = SoundEventDetector(classes=21)

    target.load_classifier_encoder({"model_state": source.state_dict()})
