"""Track 2b (ADR-0032 §3): fine-tuned frame_mn10 model, its checkpoint loading and CLI guards."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest
import torch

from ml.models.external.frame_mn.conv_norm import ConvNormActivation
from ml.models.frame_mn_finetune import (
    EMBED_DIM,
    SEQUENCE_LENGTH,
    FrameMnSED,
    encoder_state_from_checkpoint,
)
from ml.training.augment import mixup
from scripts.train_sed import (
    ENCODER_FEATURE_SET,
    ENCODER_FRAME_RATE,
    RECIPES,
    WAVEFORM_ENCODERS,
    validate_checkpoint_flags,
    validate_track2b,
)

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "checkpoints" / "frame_mn10_strong_1.pt"


@pytest.fixture(scope="module")
def model() -> FrameMnSED:
    torch.manual_seed(0)
    return FrameMnSED(21, output_frames=1000).eval()


def test_ten_seconds_become_250_steps_of_960_then_the_1000_frame_label_grid(model) -> None:
    waveforms = torch.randn(2, 160_000) * 0.1
    with torch.no_grad():
        assert tuple(model.mel(waveforms).shape) == (2, 1, 128, 1000)
        assert tuple(model.embed(waveforms).shape) == (2, SEQUENCE_LENGTH, EMBED_DIM)
        logits = model(waveforms)
    assert tuple(logits.shape) == (2, 1000, 21)
    # nearest upsampling: every 40 ms step covers exactly four 10 ms frames
    assert torch.equal(logits[:, 0::4], logits[:, 3::4])


def test_frontend_stays_deterministic_while_the_network_trains(model) -> None:
    model.train()
    try:
        assert not model.mel.training
        assert model.encoder.training and model.head.training
        waveforms = torch.randn(1, 160_000) * 0.1
        assert torch.equal(model.mel(waveforms), model.mel(waveforms))
    finally:
        model.eval()


def test_every_parameter_trains(model) -> None:
    assert all(parameter.requires_grad for parameter in model.parameters())


def test_conv_norm_keeps_torchvision_module_order_and_padding() -> None:
    block = ConvNormActivation(4, 8, kernel_size=5, stride=(2, 1), dilation=(1, 2),
                               norm_layer=torch.nn.BatchNorm2d,
                               activation_layer=torch.nn.Hardswish)
    assert [type(layer) for layer in block] == [torch.nn.Conv2d, torch.nn.BatchNorm2d,
                                                torch.nn.Hardswish]
    assert block[0].padding == (2, 4) and block[0].bias is None
    assert ConvNormActivation(4, 8, norm_layer=None, activation_layer=None)[0].bias is not None


def test_checkpoint_split_rejects_anything_but_encoder_and_audioset_heads() -> None:
    tensor = torch.zeros(1)
    encoder, ignored = encoder_state_from_checkpoint(
        {"model.frame_mn.features.0.0.weight": tensor, "strong_head.bias": tensor})
    assert list(encoder) == ["features.0.0.weight"] and ignored == ("strong_head.bias",)
    with pytest.raises(ValueError, match="unexpected keys"):
        encoder_state_from_checkpoint({"model.frame_mn.a": tensor, "seq_model.w": tensor})


@pytest.mark.skipif(not CHECKPOINT.exists(), reason="frame_mn10_strong_1.pt not downloaded")
def test_release_checkpoint_loads_strictly_and_is_hash_checked(tmp_path: Path) -> None:
    model = FrameMnSED(21)
    report = model.load_pretrained(CHECKPOINT)
    assert report.loaded_tensors == 308
    assert report.loaded_parameters == 2_971_664
    assert report.ignored_keys == ("strong_head.bias", "strong_head.weight",
                                   "weak_head.bias", "weak_head.weight")
    other = tmp_path / "other.pt"
    other.write_bytes(b"not the release")
    with pytest.raises(ValueError, match="SHA-256"):
        model.load_pretrained(other)


def test_mixup_on_waveforms_matches_the_logmel_formula() -> None:
    waveforms, targets, valid = torch.randn(4, 16), torch.rand(4, 3, 2), torch.ones(4, 3)
    torch.manual_seed(1)
    mixed, _, _ = mixup(waveforms, targets, valid)
    torch.manual_seed(1)
    as_logmel, _, _ = mixup(waveforms.view(4, 1, 1, 16), targets, valid)
    assert mixed.shape == waveforms.shape
    assert torch.equal(mixed, as_logmel.view(4, 16))


def _args(**overrides) -> Namespace:
    base = {"encoder": "frame_mn", "recipe": "t2b", "evaluate_test": False,
            "audioset_checkpoint": None, "datasec_checkpoint": None, "beats_checkpoint": None,
            "frame_mn_checkpoint": Path("f.pt")}
    base.update(overrides)
    return Namespace(**base)


def test_frame_mn_uses_the_shared_waveform_input_and_label_grid() -> None:
    assert "frame_mn" in WAVEFORM_ENCODERS
    assert ENCODER_FEATURE_SET["frame_mn"] == ENCODER_FEATURE_SET["panns"]
    assert ENCODER_FRAME_RATE["frame_mn"] == ENCODER_FRAME_RATE["panns"]


def test_frame_mn_checkpoint_flags() -> None:
    validate_checkpoint_flags(_args())
    with pytest.raises(SystemExit, match="cần --frame-mn-checkpoint"):
        validate_checkpoint_flags(_args(frame_mn_checkpoint=None))
    with pytest.raises(SystemExit, match="cần --frame-mn-checkpoint"):
        validate_checkpoint_flags(_args(beats_checkpoint=Path("b.pt")))
    with pytest.raises(SystemExit, match="chỉ dùng với --encoder frame_mn"):
        validate_checkpoint_flags(_args(encoder="beats", beats_checkpoint=Path("b.pt")))


def test_t2b_recipe_and_guards() -> None:
    knobs = dict(RECIPES["t2b"])
    assert knobs["mixup_p"] == 0.5 and knobs["filter_augment_p"] == 0.0
    assert knobs["encoder_learning_rate"] is None and knobs["epochs"] == 30
    validate_track2b(_args(), knobs)  # must not raise
    with pytest.raises(SystemExit, match="không --evaluate-test"):
        validate_track2b(_args(evaluate_test=True), knobs)
    with pytest.raises(SystemExit, match="FilterAugment"):
        validate_track2b(_args(), {**knobs, "filter_augment_p": 0.5})
    with pytest.raises(SystemExit, match="một lr"):
        validate_track2b(_args(), {**knobs, "encoder_learning_rate": 1e-4})
    with pytest.raises(SystemExit, match="--recipe t2b"):
        validate_track2b(_args(recipe="v2"), knobs)
    with pytest.raises(SystemExit, match="--recipe t2b"):
        validate_track2b(_args(encoder="panns"), knobs)
    validate_track2b(_args(encoder="panns", recipe="v2"), dict(RECIPES["v2"]))
