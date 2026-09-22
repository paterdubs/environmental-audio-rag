import numpy as np

from ml.features.logmel import LogMelConfig, waveform_to_logmel


def test_logmel_shape_and_range() -> None:
    config = LogMelConfig()
    time = np.arange(config.sample_rate, dtype=np.float32) / config.sample_rate
    waveform = np.sin(2 * np.pi * 440 * time)

    feature = waveform_to_logmel(waveform, config)

    assert feature.shape[0] == config.n_mels
    assert 49 <= feature.shape[1] <= 51
    assert feature.dtype == np.float32
    assert np.all((feature >= 0) & (feature <= 1))
