from __future__ import annotations

import pytest

from scripts.report_duration_polyphony import duration_bin, onset_polyphony, polyphony_bin


@pytest.mark.parametrize(
    ("duration", "expected"),
    [(0.9, "<1s"), (1.0, "1-3s"), (2.99, "1-3s"), (3.0, "3-10s"), (10.0, "3-10s"), (10.01, ">10s")],
)
def test_duration_bins_are_boundary_explicit(duration: float, expected: str) -> None:
    assert duration_bin(duration) == expected


def test_onset_polyphony_and_bins() -> None:
    events = [
        {"onset": 0.0, "offset": 2.0},
        {"onset": 0.5, "offset": 1.0},
        {"onset": 3.0, "offset": 4.0},
    ]
    assert onset_polyphony(events[0], events) == 1
    assert onset_polyphony(events[1], events) == 2
    assert polyphony_bin(1) == "1"
    assert polyphony_bin(2) == "2"
    assert polyphony_bin(4) == ">=3"
