import numpy as np
import pytest

from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import DurationPrior, process_recordings
from scripts import report_detection_gap as report


def test_posterior_smoothness_never_connects_recording_boundaries():
    p = {'a': np.array([[.9], [.9]]), 'b': np.array([[.1], [.1]])}
    measured = report.posterior_summary(p, {'a': [], 'b': []}, ('x',), 10.)
    assert measured['abs_adjacent_delta']['mean'] == 0.
    assert measured['abs_adjacent_delta']['n'] == 2
    assert measured['recordings']['a']['segments_over_0_5'] == 1
    assert measured['recordings']['b']['segments_over_0_5'] == 0
    assert measured['segments_per_recording']['median'] == .5


def test_cached_median_oracle_matches_native_grid_with_edges_gaps_and_min_duration():
    probabilities = {'r': np.array([[.8], [.8], [.1], [.9], [.9], [.1], [.7], [.7]])}
    reference = {'r': [{'event_label': 'x', 'onset': 0., 'offset': .8}]}
    prior = DurationPrior(median_w=3, d_min_s=.2, g_max_s=.11)
    grid = (.05, .5, .95)
    measured = report.oracle_class(probabilities, reference, 'x', 0, prior, 10., grid, .5)
    for theta in grid:
        native = process_recordings(probabilities, class_ids=('x',), thresholds={'x': theta},
                                    priors={'x': prior}, frame_rate=10.)
        score = event_based_f1(reference, native, event_label_list=['x'])
        assert measured['curve'][f'{theta:g}'] == report.finite(score['f_measure']['f_measure'])
        if theta == .5:
            assert native == measured['global_events']
    assert measured['theta'] == .05  # tie follows the existing sweep rule


def test_frame_ap_pools_without_crossing_recordings_and_strict_threshold():
    p = {'a': np.array([[.5], [.9]]), 'b': np.array([[.1], [.2]])}
    y = {'a': np.array([[True], [True]]), 'b': np.array([[False], [False]])}
    measured = report.frame_rows(p, y, ('x',), {'x': .5})['x']
    assert measured['frame_ap'] == 1.
    assert measured['posterior_gt_theta_fraction'] == .25
    assert measured['true_positive_frame_fraction'] == .5


def test_sed_eval_error_accounting_and_boundary_only_scores():
    reference = {'r': [{'event_label': 'x', 'onset': 1., 'offset': 2.},
                       {'event_label': 'x', 'onset': 3., 'offset': 4.}]}
    estimate = {'r': [{'event_label': 'y', 'onset': 1., 'offset': 2.},
                      {'event_label': 'x', 'onset': 3., 'offset': 5.},
                      {'event_label': 'y', 'onset': 8., 'offset': 9.}]}
    measured = report.event_errors(reference, estimate, ('x', 'y'))
    assert (measured['insertion'], measured['deletion'], measured['substitution']) == (2, 1, 1)
    assert measured['tp'] == 0
    assert measured['onset_only']['micro_f1'] > measured['offset_only']['micro_f1']


def test_undefined_ap_and_oracle_remain_null():
    p = {'r': np.zeros((3, 1))}
    row = report.frame_rows(p, {'r': p['r'].astype(bool)}, ('x',), {'x': .5})['x']
    assert row['frame_ap'] is None
    with pytest.warns(RuntimeWarning):
        result = report.oracle_class(p, {'r': []}, 'x', 0, DurationPrior(1, 0, 0),
                                     10., (.05, .5), .5)
    assert result['f1'] is None and result['theta'] == .05
