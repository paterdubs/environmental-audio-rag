import json

import numpy as np
import pytest

from scripts import report_screening_per_class as report


def event(cid, on, off):
    return {'event_label': cid, 'onset': on, 'offset': off}


def test_per_class_standard_f1_and_estimate_only_false_positive():
    refs = {'r': [event('a', 0, 1), event('b', 3, 4)]}
    ests = {'r': [event('a', .1, 1.1)], 's': [event('a', 5, 6)]}
    score = report.class_scores(refs, ests, ('a', 'b', 'c'))
    assert score['per_class']['a'] == {'f1': pytest.approx(2/3), 'nsys': 2, 'nref': 1}
    assert score['per_class']['b'] == {'f1': None, 'nsys': 0, 'nref': 1}
    assert score['per_class']['c'] == {'f1': None, 'nsys': 0, 'nref': 0}
    assert score['micro_f1'] == .5
    json.dumps(score, allow_nan=False)


def test_deltas_keep_undefined_and_reject_reference_or_order_changes():
    base = {'a': {'f1': .5, 'nsys': 3, 'nref': 2}, 'b': {'f1': None, 'nsys': 0, 'nref': 0}}
    candidate = {'a': {'f1': .8, 'nsys': 2, 'nref': 2},
                 'b': {'f1': 0., 'nsys': 1, 'nref': 0}}
    delta = report.per_class_deltas(base, candidate)
    assert delta['a']['f1'] == pytest.approx(.3)
    assert delta['a']['nsys'] == -1 and delta['a']['nref'] == 0
    assert delta['b']['f1'] is None
    with pytest.raises(ValueError, match='order'):
        report.per_class_deltas(base, dict(reversed(list(candidate.items()))))
    candidate['a']['nref'] = 3
    with pytest.raises(ValueError, match='reference'):
        report.per_class_deltas(base, candidate)


def test_reconstruct_routes_selected_csebb_without_theta_refit(tmp_path, monkeypatch):
    selection = {'selected': {'config': 'tau0.32_abs0.3', 'step_filter_s': .32,
                             'merge_abs': .3, 'merge_rel': None, 'threshold': .5},
                 'cv': {'tau0.32_abs0.3': {'lambda_full_dev': .5}}}
    (tmp_path/'sebb_cv_selection_annotated.json').write_text(json.dumps(selection))
    (tmp_path/'predictions').mkdir()
    np.savez(tmp_path/'predictions/dev.npz', content_sha256=np.asarray('fixture-content-hash'))
    run = {'run': str(tmp_path), 'label': 'fixture', 'winner': {'family': 'csebb'}}
    monkeypatch.setattr(report, 'load_dev', lambda _: (
        {'r': np.array([[.1], [.9], [.9], [.1]])}, {'r': [event('a', .1, .3)]}, ('a',), 10))
    monkeypatch.setattr(report, 'validate_theta_refit', lambda *a: pytest.fail('theta called'))
    out = report.reconstruct(run)
    assert out['per_class']['a']['nref'] == 1
    assert out['postproc_source'].endswith('sebb_cv_selection_annotated.json')
    assert out['dev_predictions_sha256'] == 'fixture-content-hash'
    assert out['dev_predictions_file_sha256'] != out['dev_predictions_sha256']


def test_theta_refit_rejects_other_predictions_before_reading_priors(monkeypatch):
    monkeypatch.setattr(report, 'validate_postproc_artifact', lambda *a, **kw: None)
    monkeypatch.setattr(report, 'load_taxonomy', lambda _: type('Taxonomy', (), {
        'polyphonic_class_ids': ('a',)})())
    postproc = {'threshold_mode': 'global', 'taxonomy_sha256': 'x', 'split_sha256': 'y',
                'data_manifest_sha256': 'z', 'dev_predictions_sha256': 'old'}
    run = {'winner': {'config': 'global|25'}, 'manifest': {
        'taxonomy_sha256': 'x', 'split_sha256': 'y', 'data_manifest_sha256': 'z'}}
    with pytest.raises(ValueError, match='different dev'):
        report.validate_theta_refit(postproc, run, 100, 'new')
