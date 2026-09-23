import torch

from ml.models import PannsAudioClassifier, PannsCNN14Encoder, PannsConfig, safe_batch_size


def test_panns_encoder_returns_temporal_embeddings() -> None:
    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    embeddings = encoder(torch.rand(2, 1, 64, 128))
    assert embeddings.shape == (2, 128, 2)


def test_panns_classifier_and_config_are_explicit() -> None:
    config = PannsConfig()
    classifier = PannsAudioClassifier(
        classes=22, encoder=PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    )
    assert config.sample_rate == 32_000
    assert config.window_seconds == 5.0
    assert classifier(torch.rand(2, 1, 64, 128)).shape == (2, 22)


def test_vram_policy_is_conservative_for_eight_gb() -> None:
    assert safe_batch_size(5.0) == 4
    assert safe_batch_size(10.0) == 2
    assert safe_batch_size(10.0, max_vram_gb=6.0) == 1
