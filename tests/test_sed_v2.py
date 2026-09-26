"""SED v2 (ADR-0030): recipe knobs, architecture options, optimizer/scheduler, random crop."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from ml.datasets.features import SedFeatureDataset
from ml.models import PannsCNN14Encoder, SoundEventDetector
from ml.models.sed_factory import V1_ARCHITECTURE, sed_model
from ml.training.sed import SedTrainingConfig, build_optimizer, build_scheduler
from scripts.train_sed import RECIPES, resolve_recipe

SMALL = (4, 8, 16, 32, 64, 128)


def _args(recipe: str = "v1", **overrides) -> Namespace:
    knobs = dict.fromkeys(RECIPES["v1"])
    knobs.update(overrides)
    return Namespace(recipe=recipe, **knobs)


def test_v1_recipe_reproduces_the_rq1_training_defaults():
    knobs = resolve_recipe(_args())
    defaults = SedTrainingConfig()
    assert knobs["epochs"] == defaults.epochs == 8
    assert knobs["learning_rate"] == defaults.learning_rate
    assert knobs["encoder_learning_rate"] is defaults.encoder_learning_rate is None
    assert knobs["pos_weight_cap"] == 50.0
    assert {k: knobs[k] for k in V1_ARCHITECTURE} == V1_ARCHITECTURE
    assert not knobs["random_crop"] and knobs["mixup_p"] == knobs["filter_augment_p"] == 0.0


def test_explicit_flags_override_one_knob_of_the_recipe():
    knobs = resolve_recipe(_args("v2", time_pooling="2,2,2,2,2,2", mixup_p=0.0))
    assert knobs["time_pooling"] == [2, 2, 2, 2, 2, 2]
    assert knobs["mixup_p"] == 0.0
    assert knobs["pos_weight_cap"] == 10.0  # untouched knobs keep the v2 value


def test_time_pooling_sets_the_encoder_frame_rate():
    encoder = PannsCNN14Encoder(channels=SMALL, time_pooling=(2, 2, 2, 1, 1, 1))
    assert encoder.time_reduction == 8
    assert encoder(torch.rand(2, 1, 64, 1000)).shape == (2, 128, 125)
    with pytest.raises(ValueError):
        PannsCNN14Encoder(time_pooling=(2, 2, 2))


def test_after_rnn_detector_runs_the_gru_at_encoder_rate_and_returns_label_rate():
    encoder = PannsCNN14Encoder(channels=SMALL, time_pooling=(2, 2, 2, 1, 1, 1))
    model = SoundEventDetector(classes=21, encoder=encoder, hidden_size=16, rnn_layers=2,
                               upsample="after_rnn")
    logits = model(torch.rand(2, 1, 64, 1000))
    assert logits.shape == (2, 1000, 21)
    # Nearest repeat of the 125 encoder-rate outputs: each block of 8 frames is constant.
    assert torch.equal(logits[:, :8], logits[:, :1].expand(-1, 8, -1))


def test_factory_builds_v1_when_the_manifest_has_no_architecture_keys():
    v1 = SoundEventDetector(classes=21, encoder=PannsCNN14Encoder())
    rebuilt = sed_model({}, classes=21)
    rebuilt.load_state_dict(v1.state_dict())  # strict: same parameters, same shapes
    assert rebuilt.encoder.time_pooling == (2, 2, 2, 2, 2, 2)
    assert rebuilt.upsample == "before_rnn"


def test_factory_reads_the_v2_architecture_from_config():
    model = sed_model({k: RECIPES["v2"][k] for k in V1_ARCHITECTURE}, classes=21)
    assert model.encoder.time_reduction == 8
    assert model.temporal.num_layers == 2 and model.temporal.hidden_size == 256


def test_optimizer_gives_the_encoder_its_own_learning_rate():
    model = SoundEventDetector(classes=3, encoder=PannsCNN14Encoder(channels=SMALL))
    v1 = build_optimizer(model, SedTrainingConfig())
    assert len(v1.param_groups) == 1
    v2 = build_optimizer(model, SedTrainingConfig(learning_rate=1e-3,
                                                  encoder_learning_rate=1e-4))
    assert [group["lr"] for group in v2.param_groups] == [1e-4, 1e-3]
    grouped = sum(len(group["params"]) for group in v2.param_groups)
    assert grouped == len(list(model.parameters()))


def test_scheduler_warms_up_then_decays_to_zero():
    model = torch.nn.Linear(2, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=1.0)
    config = SedTrainingConfig(epochs=4, warmup_epochs=1, cosine_decay=True)
    scheduler = build_scheduler(optimizer, config, steps_per_epoch=10)
    rates = []
    for _ in range(40):
        rates.append(optimizer.param_groups[0]["lr"])
        optimizer.step()
        scheduler.step()
    assert rates[0] == pytest.approx(0.1) and rates[9] == pytest.approx(1.0)
    assert rates[10] == pytest.approx(1.0) and rates[-1] < 0.01
    assert build_scheduler(optimizer, SedTrainingConfig(), steps_per_epoch=10) is None


def test_training_config_rejects_unknown_selection_metric():
    with pytest.raises(ValueError):
        SedTrainingConfig(select_metric="event_f1")


def test_random_crop_keeps_labels_aligned_with_features(tmp_path: Path):
    frames = 300
    feature = np.tile(np.arange(frames, dtype=np.float32), (4, 1))  # value = frame index
    np.save(tmp_path / "r1.npy", feature)
    recordings = pd.DataFrame([{"recording_id": "r1", "feature_relative_path": "r1.npy",
                                "frames": frames}])
    events = pd.DataFrame([{"recording_id": "r1", "class_id": "birds", "onset_s": 1.0,
                            "offset_s": 2.0}])
    dataset = SedFeatureDataset(recordings, events, feature_root=tmp_path,
                                class_ids=("birds",), frame_rate=100.0, window_frames=100,
                                hop_frames=100, random_crop=True)
    np.random.seed(0)
    starts = set()
    for _ in range(20):
        features, target, valid = dataset[0]
        start = int(features[0, 0, 0])
        starts.add(start)
        active = {start + i for i in np.flatnonzero(target[:, 0].numpy())}
        assert active == set(range(100, 200)) & set(range(start, start + 100))
        assert bool(valid.all())
    assert len(starts) > 1
