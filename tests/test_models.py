import torch

from ml.models import AudioClassifier, SoundEventDetector


def test_models_preserve_expected_dimensions() -> None:
    inputs = torch.rand(2, 1, 64, 50)

    classification = AudioClassifier(classes=22)(inputs)
    detection = SoundEventDetector(classes=21)(inputs)

    assert classification.shape == (2, 22)
    assert detection.shape == (2, 50, 21)
