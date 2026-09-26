import numpy as np
import pytest

from ml.postprocessing.sebb import (
    SebbParams,
    change_point_events,
    csebbs,
    hysteresis_runs,
    step_delta,
)

FPS = 100.0


def step(lengths_values: list[tuple[int, float]]) -> np.ndarray:
    return np.concatenate([np.full(length, value) for length, value in lengths_values])


def test_step_delta_peaks_exactly_at_a_rising_edge():
    scores = step([(50, 0.0), (50, 1.0)])
    delta = step_delta(scores, half_frames=16)
    assert delta.shape == (101,)  # one value per frame boundary 0..T
    assert int(np.argmax(delta)) == 50
    assert delta[50] == pytest.approx(1.0)


def test_isolated_event_boundaries_land_on_the_true_edges():
    # A non-zero baseline must not open a spurious event at the clip start (edge padding).
    scores = step([(40, 0.02), (30, 0.9), (40, 0.02)])
    events = change_point_events(scores, half_frames=16)
    assert events == [(40, 70)]


def test_event_active_at_clip_start_and_end_is_closed_by_the_clip():
    scores = step([(30, 0.8), (40, 0.0), (30, 0.7)])
    assert change_point_events(scores, half_frames=8) == [(0, 30), (70, 100)]


def test_flat_silence_produces_no_event():
    assert change_point_events(np.zeros(200), half_frames=16) == []


def test_shallow_dip_is_merged_but_deep_gap_is_not():
    shallow = step([(20, 0.0), (30, 0.9), (10, 0.7), (30, 0.8), (20, 0.0)])
    deep = step([(20, 0.0), (30, 0.9), (10, 0.05), (30, 0.8), (20, 0.0)])
    params = SebbParams(step_filter_s=0.1, merge_abs=0.3)
    merged = csebbs(shallow, frame_rate=FPS, params=params)
    split = csebbs(deep, frame_rate=FPS, params=params)
    assert [(on, off) for on, off, _ in merged] == [(20, 90)]
    assert [(on, off) for on, off, _ in split] == [(20, 50), (60, 90)]


def test_merge_requires_both_neighbours_close_to_the_gap():
    # Left event 0.9, gap 0.5, right event 0.55: right is close to the gap but left is not.
    scores = step([(20, 0.0), (30, 0.9), (10, 0.5), (30, 0.55), (20, 0.0)])
    events = csebbs(scores, frame_rate=FPS, params=SebbParams(step_filter_s=0.1, merge_abs=0.2))
    assert len(events) == 2


def test_relative_merge_threshold():
    scores = step([(20, 0.0), (30, 0.9), (10, 0.5), (30, 0.8), (20, 0.0)])
    loose = csebbs(scores, frame_rate=FPS, params=SebbParams(step_filter_s=0.1, merge_rel=2.0))
    strict = csebbs(scores, frame_rate=FPS, params=SebbParams(step_filter_s=0.1, merge_rel=1.5))
    assert len(loose) == 1 and len(strict) == 2


def test_confidence_is_the_mean_score_over_the_box():
    scores = step([(20, 0.0), (50, 0.6), (20, 0.0)])
    [(on, off, confidence)] = csebbs(scores, frame_rate=FPS, params=SebbParams(0.1, 0.2))
    assert (on, off) == (20, 70)
    assert confidence == pytest.approx(0.6)


def test_params_need_exactly_one_merge_threshold():
    with pytest.raises(ValueError):
        SebbParams(step_filter_s=0.32)
    with pytest.raises(ValueError):
        SebbParams(step_filter_s=0.32, merge_abs=0.2, merge_rel=2.0)


def test_hysteresis_extends_to_low_threshold_and_needs_a_high_peak():
    scores = step([(10, 0.0), (10, 0.4), (10, 0.95), (10, 0.4), (10, 0.0), (10, 0.45), (10, 0.0)])
    assert hysteresis_runs(scores, high=0.9, low=0.3) == [(10, 40)]
