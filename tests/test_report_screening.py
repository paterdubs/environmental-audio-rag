"""Screening fixtures: real NPZ ID audit, same-fold comparison and missing family."""

import json
from copy import deepcopy
from statistics import mean, stdev

import numpy as np
import pandas as pd
import pytest

from scripts import report_screening as report


@pytest.fixture
def runs(tmp_path, monkeypatch):
    monkeypatch.setattr(report, 'ROOT', tmp_path)
    split = tmp_path / 'data/splits'
    split.mkdir(parents=True)
    ids = [f'r{i}' for i in range(12)]
    frame = pd.DataFrame({'recording_id': ids, 'leakage_group': ids,
                          'split': ['validation'] * 12})
    frame.to_csv(split / 'datased_polyphonic.csv', index=False)
    monkeypatch.setattr(report, 'restrict', lambda ids, _: ids)

    def create(name, scores, *, sebb=True, recordings=ids):
        run = tmp_path / name
        (run / 'predictions').mkdir(parents=True)
        (run / 'manifest.json').write_text(json.dumps({'complete': True, 'taxonomy_sha256': 't'}))
        np.savez(run / 'predictions/dev.npz', recording_ids=recordings,
                 metadata_json=json.dumps({'split': 'dev', 'taxonomy_sha256': 't'}))
        for family, prefix in [('theta', 'postproc'), ('csebb', 'sebb')]:
            if family == 'csebb' and not sebb:
                continue
            key = 'global|25' if family == 'theta' else 'tau=.32'
            chosen = {'threshold_mode': 'global', 'g_max_percentile': 25} if family == 'theta' \
                else {'config': key}
            payload = {'run': name, 'eval_set': 'annotated', 'git': {'dirty': False},
                       'grouping': 'leakage_group', 'folds': 5, 'selected': chosen,
                       'cv': {key: {'mean': mean(scores), 'sd': stdev(scores), 'folds': scores}}}
            (run / f'{prefix}_cv_selection_annotated.json').write_text(json.dumps(payload))
        return f'{name}={run}'
    return create


def test_same_family_and_winner_comparisons_and_tie(runs):
    baseline = report.load_run(runs('base', [.1, .2, .3, .4, .5]))
    candidate = report.load_run(runs('candidate', [.11, .21, .31, .41, .51]))
    assert candidate['winner']['family'] == 'theta'
    result = report.compare(baseline, [candidate])
    assert set(result['comparisons']['candidate']['same_family']) == {'theta', 'csebb'}
    assert result['comparisons']['candidate']['winner']['folds_greater'] == 5
    assert result['comparisons']['candidate']['winner']['warning'] == 'trong nhiễu fold'
    assert 'trong nhiễu fold' in report.render(result)


def test_optional_missing_family(runs):
    run = report.load_run(runs('one', [.1, .2, .3, .4, .5], sebb=False))
    assert list(run['families']) == ['theta']


def test_refuse_different_recording_set_despite_same_count(runs):
    a = report.load_run(runs('base', [.1, .2, .3, .4, .5]))
    b = deepcopy(a)
    b['label'] = 'other'
    b['recordings'][-1] = 'different'
    with pytest.raises(ValueError, match='tập recording'):
        report.compare(a, [b])


def test_refuse_wrong_means_and_dirty(runs):
    spec = runs('bad', [.1, .2, .3, .4, .5], sebb=False)
    path = report.Path(spec.partition('=')[2]) / 'postproc_cv_selection_annotated.json'
    payload = json.loads(path.read_text())
    payload['cv']['global|25']['mean'] = .99
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='không nhất quán'):
        report.load_run(spec)
    payload['git']['dirty'] = True
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='tree sạch'):
        report.load_run(spec)
