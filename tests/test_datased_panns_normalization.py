from __future__ import annotations

import numpy as np

from scripts.build_datased_panns_normalization import stream_statistics


def test_stream_statistics_returns_population_per_mel_values(tmp_path) -> None:
    first = np.full((64, 2), 1.0, dtype=np.float32)
    second = np.full((64, 2), 3.0, dtype=np.float32)
    first_path = tmp_path / "first.npy"
    second_path = tmp_path / "second.npy"
    np.save(first_path, first)
    np.save(second_path, second)

    mean, std, frames = stream_statistics([first_path, second_path])

    assert frames == 4
    assert np.allclose(mean, 2.0)
    assert np.allclose(std, 1.0)
