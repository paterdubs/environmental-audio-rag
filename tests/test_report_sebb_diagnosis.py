import numpy as np
import pytest

from scripts.report_sebb_diagnosis import (
    distribution,
    event_diagnostics,
    overlap_degrees,
    posterior_summary,
    raster_reference,
    selected_csebb,
    threshold_runs,
)


def event(on, off, label='a'):
    return {'onset': on, 'offset': off, 'event_label': label}


def test_posterior_uses_union_gt_and_excludes_recording_jumps():
    p = {'r': np.array([[.6, .1], [.7, .8], [.4, .9]]),
         's': np.array([[.9, .9], [.9, .9]])}
    refs = {'r': [event(.5, 1.5), event(1, 2)], 's': []}
    out = posterior_summary(p, refs, ('a', 'b'), 1)
    assert out['positive']['n'] == 2
    assert out['positive']['median'] == pytest.approx(.65)
    assert out['negative']['n'] == 8
    assert out['abs_adjacent_delta']['n'] == 6
    assert out['recordings']['r']['segments_over_0_5'] == 2
    assert distribution(np.array([]))['median'] is None


def test_raster_clips_bounds_and_threshold_is_strict():
    target = raster_reference([event(-1, .5), event(1.5, 4, 'b')], (3, 2), ('a', 'b'), 1)
    np.testing.assert_array_equal(target, [[1, 0], [0, 1], [0, 1]])
    assert threshold_runs(np.array([[.5], [.6], [.7], [.5], [.6]])).tolist() == [2]


def test_matching_uses_sed_eval_optimal_assignment_and_boundary_errors():
    refs = {'r': [event(0, 1), event(.1, 1.1)]}
    est = {'r': [event(.15, 1.15), event(.02, 1.02)], 'empty': []}
    # A nonempty estimate-only recording must contribute false positives.
    refs['empty'] = []
    est['empty'] = [event(3, 4)]
    out = event_diagnostics(refs, est, ('a',))
    assert (out['nref'], out['nsys'], out['tp']) == (2, 3, 2)
    assert out['micro_f1'] == .8
    assert out['onset_error_s']['n'] == 2
    assert len(out['matched_pairs']) == 2


def test_overlap_is_same_class_strict_positive_and_counts_entities():
    refs = [event(0, 1), event(2, 3), event(4, 5, 'b')]
    est = [event(0, 3), event(.2, .5), event(3, 4)]
    assert overlap_degrees(refs, est) == (1, 1)
    assert overlap_degrees([event(0, 1)], [event(1, 2)]) == (0, 0)


def test_zero_true_positives_has_no_fabricated_boundary_stats():
    out = event_diagnostics({'r': [event(0, 1)]}, {'r': [event(2, 3)]}, ('a',))
    assert out['tp'] == 0
    assert out['onset_error_s']['n'] == 0
    assert out['offset_error_s']['iqr'] is None


def test_csebb_checks_chosen_config_against_saved_full_dev_threshold():
    selection = {'selected': {'config': 'tau0.32_abs0.3', 'step_filter_s': .32,
                             'merge_abs': .3, 'merge_rel': None, 'threshold': .5},
                 'cv': {'tau0.32_abs0.3': {'lambda_full_dev': .6}}}
    with pytest.raises(ValueError, match='mismatch'):
        selected_csebb({'r': np.ones((5, 1))}, ('a',), 1, selection)
    selection['cv']['tau0.32_abs0.3']['lambda_full_dev'] = .5
    assert isinstance(selected_csebb({'r': np.array([[.1], [.9], [.9], [.1]])},
                                    ('a',), 10, selection)['r'], list)
