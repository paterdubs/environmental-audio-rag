import json

import pytest

from scripts import report_tier_s as report
from scripts.report_s13_ranking import FamilyScore, best_family


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
