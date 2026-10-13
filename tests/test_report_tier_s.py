import json

import pytest

from scripts import report_tier_s as report
from scripts.report_s13_ranking import FamilyScore, best_family


def oof_fixture(tmp_path, monkeypatch):
    def write(name, value):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), 'utf-8')
    write('fold/manifest.json', {'complete': True, 'config': {
        'recipe': 'oc_tf_kd', 'train_fixes': {'dropped': ['r']}}})
    write('rewindow/manifest.json', {'complete': True, 'task': 'sed_rewindow',
                                    'config': {'source_run': 'fold'}})
    config = {'members': ['rewindow'], 'cv_folds_sha256': report.sha256_file(
        report.ROOT / 'data/splits/datased_trainval_folds.csv')}
    write('sed_oof_KD_h5/manifest.json', {'complete': True, 'task': 'sed_oof', 'config': config})
    for name in report.SELECTIONS:
        write(f'sed_oof_KD_h5/{name}', {'dev_recordings': 564})
    families = tuple(FamilyScore(f, 'global|25', .2, 0., (.2,)*5)
                     for f in ('theta', 'csebb'))
    monkeypatch.setattr(report, 'load_families', lambda *a, **k: families)
    rows = [{'config': {'recipe': 'oc_tf_kd', 'train_fixes': True}, 'is_seed': False,
             'screening': {'run': 'KD', 'winner': {'mean': .27}}},
            {'config': {'recipe': 't2b', 'train_fixes': True}, 'is_seed': False,
             'screening': {'run': 'OB'}}]
    return rows


def test_tier_c_matches_source_recipe_through_rewindow_not_label(tmp_path, monkeypatch):
    rows = oof_fixture(tmp_path, monkeypatch)
    result = report.tier_c(tmp_path, rows)
    assert len(result['rows']) == 1
    row = result['rows'][0]
    assert row['screening_run'] == 'KD' and row['oof_winner']['family'] == 'theta'
    assert len(row['source_manifests_sha256']) == 3
    assert row['n_oof_recordings'] == 564
    rows[0]['config']['train_fixes'] = False
    row = report.tier_c(tmp_path, rows)['rows'][0]
    assert row['train_fixes_differ'] is True
    assert row['oof_recipe_signature'][1] is True


def test_tier_c_missing_selection_pending_and_wrong_scope_refused(tmp_path, monkeypatch):
    rows = oof_fixture(tmp_path, monkeypatch)
    path = tmp_path / 'sed_oof_KD_h5' / report.SELECTIONS[0]
    path.write_text(json.dumps({'dev_recordings': 134}))
    with pytest.raises(ValueError, match='564'):
        report.tier_c(tmp_path, rows)
    path.unlink()
    assert report.tier_c(tmp_path, rows)['pending'][0]['missing'] == [report.SELECTIONS[0]]


def test_source_recipe_cycles_and_traversal_refused(tmp_path):
    p = tmp_path / 'manifest.json'
    p.write_text(json.dumps({'complete': True, 'config': {'members': ['.']}}))
    with pytest.raises(ValueError, match='cyclic'):
        report.source_recipes(tmp_path, tmp_path)
    with pytest.raises(ValueError, match='outside'):
        report.source_recipes(tmp_path.parent, tmp_path)


def test_discovery_excludes_cv_folds_and_includes_pending(tmp_path):
    names = [*report.SEEDS, 'sed_polyphonic_20261008T131138Z',
             'sed_polyphonic_20261008T092903Z', 'sed_oof_B0_h10_x',
             'sed_polyphonic_20261009T010000Z', 'sed_polyphonic_20261007T010000Z']
    for name in names:
        folder = tmp_path / name
        folder.mkdir()
        (folder / 'manifest.json').write_text(json.dumps({'config': {
            'cv_fold': 0} if '092903Z' in name else {}}))
    assert {p.name for p in report.discover(tmp_path)} == {*names[:4], names[6]}


def test_saved_frame_map_missing_not_member_average_and_recipe(tmp_path):
    assert report.best_frame_map(tmp_path)['value'] is None
    (tmp_path / 'metrics.json').write_text(json.dumps({
        'select_metric': 'macro_average_precision', 'best_validation': 0.743}))
    assert report.best_frame_map(tmp_path)['value'] == .743
    assert '--train-fixes' in report.recipe({'config': {'recipe': 't2b',
        'train_fixes': {'dropped_unannotated': ['r']},
        'window_sampling': {'mode': 'class_balanced'}}})


def test_s13_tie_keeps_theta_and_strict_delta():
    scores = tuple(FamilyScore(family=f, config='x', mean=.2, sd=.1, folds=(.1, .3))
                   for f in ('theta', 'csebb'))
    assert best_family(scores).family == 'theta'
    score = {'mean': .233026, 'sd': .1, 'folds': [.2, .266052]}
    assert report.delta(score, score)['mean'] == 0


def test_report_refuses_overwrite_and_bad_stamp(tmp_path):
    report.write_report({'x': 1}, 'tier_s', '20261009', tmp_path, lambda r: 'fixture')
    with pytest.raises(FileExistsError):
        report.write_report({}, 'tier_s', '20261009', tmp_path, str)
    with pytest.raises(ValueError, match='stamp'):
        report.write_report({}, 'tier_s', '../escape', tmp_path, str)
