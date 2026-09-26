import torch

from ml.training.augment import (
    TOP_DB,
    augment_batch,
    filter_augment,
    filter_gains_db,
    mixup,
)


def test_mixup_mixes_features_and_targets_with_the_same_weight():
    torch.manual_seed(0)
    features = torch.stack([torch.zeros(1, 4, 6), torch.ones(1, 4, 6)])
    targets = torch.stack([torch.zeros(6, 2), torch.ones(6, 2)])
    valid = torch.ones(2, 6)
    mixed, mixed_targets, mixed_valid = mixup(features, targets, valid, alpha=0.4)
    # With inputs 0/1, the mixed value equals the weight given to the "ones" window, and the
    # target must carry exactly the same weight.
    assert torch.allclose(mixed[:, 0, 0, 0], mixed_targets[:, 0, 0])
    assert mixed_valid.shape == valid.shape


def test_mixup_keeps_only_frames_valid_in_both_windows():
    torch.manual_seed(1)
    features = torch.rand(2, 1, 4, 6)
    targets = torch.zeros(2, 6, 2)
    valid = torch.tensor([[1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1]], dtype=torch.float32)
    for _ in range(10):
        _, _, mixed_valid = mixup(features, targets, valid)
        assert torch.all(mixed_valid <= valid)


def test_filter_gains_stay_in_range_and_cover_every_mel_bin():
    torch.manual_seed(2)
    for _ in range(50):
        gains = filter_gains_db(3, 64, db_range=6.0)
        assert gains.shape == (3, 64)
        assert torch.all(gains.abs() <= 6.0 + 1e-6)


def test_filter_augment_is_an_additive_db_shift_per_mel_band():
    torch.manual_seed(3)
    features = torch.full((2, 1, 64, 10), 0.5)
    out = filter_augment(features, db_range=6.0)
    shift_db = (out - features) * TOP_DB
    # Same shift for every frame of a mel bin (a filter, not a time-varying gain) …
    assert torch.allclose(shift_db, shift_db[..., :1].expand_as(shift_db))
    # … bounded by the dB range.
    assert torch.all(shift_db.abs() <= 6.0 + 1e-4)


def test_filter_augment_never_goes_below_the_top_db_floor():
    torch.manual_seed(4)
    out = filter_augment(torch.zeros(4, 1, 64, 5))
    assert torch.all(out >= 0)


def test_augment_batch_with_zero_probabilities_is_identity():
    features = torch.rand(2, 1, 64, 8)
    targets = torch.rand(2, 8, 3)
    valid = torch.ones(2, 8)
    out = augment_batch(features, targets, valid, mixup_p=0.0, filter_augment_p=0.0)
    assert out[0] is features and out[1] is targets and out[2] is valid
