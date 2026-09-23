import numpy as np

from ml.features.logmel import (
    LogMelConfig,
    PannsLogMelConfig,
    load_logmel_config,
    waveform_to_logmel,
)


def test_logmel_shape_and_range() -> None:
    config = LogMelConfig()
    time = np.arange(config.sample_rate, dtype=np.float32) / config.sample_rate
    waveform = np.sin(2 * np.pi * 440 * time)

    feature = waveform_to_logmel(waveform, config)

    assert feature.shape[0] == config.n_mels
    assert 49 <= feature.shape[1] <= 51
    assert feature.dtype == np.float32
    assert np.all((feature >= 0) & (feature <= 1))


def test_panns_config_matches_frontend_parameters() -> None:
    config = PannsLogMelConfig()

    assert config.name == "logmel_panns_v1"
    assert config.sample_rate == 32_000
    assert config.n_fft == 1_024
    assert config.hop_length == 320
    assert config.n_mels == 64
    assert config.fmin == 50.0
    assert config.fmax == 14_000.0
    assert config.frame_rate == 100.0


def test_panns_feature_shape_and_yaml_loading() -> None:
    config = load_logmel_config("logmel_panns_v1")
    time = np.arange(config.sample_rate, dtype=np.float32) / config.sample_rate
    waveform = np.sin(2 * np.pi * 440 * time)

    feature = waveform_to_logmel(waveform, config)

    assert isinstance(config, PannsLogMelConfig)
    assert feature.shape == (64, 101)
    assert feature.dtype == np.float32
    assert np.all((feature >= 0) & (feature <= 1))
