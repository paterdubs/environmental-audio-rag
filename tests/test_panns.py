import pytest
import torch

from ml.models import PannsAudioClassifier, PannsCNN14Encoder, PannsConfig, safe_batch_size


def audioset_block_state(encoder: PannsCNN14Encoder) -> dict[str, torch.Tensor]:
    names = {0: "conv1", 1: "bn1", 3: "conv2", 4: "bn2"}
    state: dict[str, torch.Tensor] = {}
    for key, value in encoder.blocks.state_dict().items():
        block, _, layer, suffix = key.split(".", maxsplit=3)
        state[f"conv_block{int(block) + 1}.{names[int(layer)]}.{suffix}"] = value
    return state


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


def test_load_audioset_blocks_is_strict_and_reports_transfer(tmp_path) -> None:
    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    state = audioset_block_state(encoder)
    state["fc1.weight"] = torch.ones(3, 3)
    checkpoint = tmp_path / "audioset.pth"
    torch.save({"model": state}, checkpoint)

    report = encoder.load_audioset_pretrained(checkpoint)

    assert report.transplanted_tensors == len(encoder.blocks.state_dict())
    expected_parameters = sum(value.numel() for value in encoder.blocks.state_dict().values())
    assert report.transplanted_parameters == expected_parameters
    assert report.parameter_fraction < 1.0


def test_load_audioset_blocks_rejects_missing_tensor(tmp_path) -> None:
    encoder = PannsCNN14Encoder(channels=(4, 8, 16, 32, 64, 128))
    state = audioset_block_state(encoder)
    state.pop("conv_block1.conv1.weight")
    checkpoint = tmp_path / "missing.pth"
    torch.save({"model": state}, checkpoint)

    with pytest.raises(RuntimeError, match="0.layers.0.weight"):
        encoder.load_audioset_pretrained(checkpoint)
