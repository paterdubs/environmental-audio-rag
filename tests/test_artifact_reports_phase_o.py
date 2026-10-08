"""Ledger/freeze fixtures for derived and fold runs; legacy rows must stay identical."""

import json
from pathlib import Path

import pytest

from scripts import freeze_artifacts as freeze
from scripts import report_test_ledger as ledger


def write_run(root, name, *, task='sed_polyphonic', config=None, complete=True):
    run = root / name
    run.mkdir()
    manifest = {'run_id': name, 'task': task, 'complete': complete,
                'config': config or {'weight_source': 'audioset', 'seed': 1},
                'git': {'dirty': False}}
    (run / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return run


def evaluate(run, *, split='test', filename='evaluation.json'):
    path = run / filename
    path.write_text(json.dumps({'split': split, 'event_based_f1': {'f_measure': .25},
                                'psds': {'psds_1': .1, 'psds_2': .2}}), encoding='utf-8')
    return path


def test_legacy_row_and_markdown_unchanged(tmp_path):
    run = write_run(tmp_path, 'old')
    row = ledger.sed_row(evaluate(run))
    expected = {'run': 'old', 'evaluation': 'evaluation.json', 'branch': 'B', 'seed': 1,
                'pos_weight_cap': '50 (mặc định)', 'postproc': 'postproc.json',
                'git_dirty': False, 'event_f1': .25, 'psds_1': .1, 'psds_2': .2}
    assert row == expected
    line = '| `old` | `evaluation.json` | B | 1 | 50 (mặc định) | `postproc.json` '
    line += '| không | 0.2500 | 0.1000 | 0.2000 |'
    assert line in ledger.render({'sed': [row], 'other': {}}).splitlines()


def test_only_evaluated_test_adds_rows(tmp_path):
    original = write_run(tmp_path, 'old')
    evaluate(original)
    before = ledger.collect_sed(tmp_path)
    derived = write_run(tmp_path, 'rewindow', task='sed_rewindow',
                        config={'source_run': 'old', 'hop_seconds': 2.5,
                                'window_weighting': 'triangular:0.3'})
    fold = write_run(tmp_path, 'fold', config={'cv_fold': 0})
    oof = write_run(tmp_path, 'oof', task='sed_oof',
                    config={'members': ['fold'], 'fold_of_member': [0]})
    evaluate(fold, split='dev')
    # Run mới chỉ có dev/manifest không thêm dòng sổ test.
    assert ledger.collect_sed(tmp_path) == before
    row = ledger.sed_row(evaluate(derived))
    assert row['task'] == 'sed_rewindow'
    assert row['hop_seconds'] == 2.5
    assert row['window_weighting'] == 'triangular:0.3'
    assert ledger.run_details(oof)['cv_fold'] == [0]
    assert len(ledger.collect_sed(tmp_path)) == 2
    assert before[0] in ledger.collect_sed(tmp_path)
    assert ledger.verify_legacy(ledger.collect_sed(tmp_path), {'sed': before}) == {
        'previous_rows': 1, 'unchanged_rows': 1, 'added_rows': 1}
    with pytest.raises(ValueError, match='bị đổi'):
        ledger.verify_legacy([], {'sed': before})


def test_inherited_hop_weighting_fold_and_recursive_freeze(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze, 'RUNS', tmp_path)
    fold = write_run(tmp_path, 'fold', config={'cv_fold': 0})
    (fold / 'checkpoints').mkdir()
    (fold / 'checkpoints/best.pt').write_bytes(b'fake')
    derived = write_run(tmp_path, 'rewindow', task='sed_rewindow',
                        config={'source_run': 'fold', 'hop_seconds': 5,
                                'window_weighting': 'uniform'})
    oof = write_run(tmp_path, 'oof', task='sed_oof',
                    config={'members': ['rewindow'], 'fold_of_member': [0]})
    (oof / 'predictions').mkdir()
    (oof / 'predictions/dev.npz').write_bytes(b'fake dev')
    (oof / 'predictions/test.npz').write_bytes(b'must not open')
    original = freeze.sha256_file

    def guard(path):
        assert path.name != 'test.npz'
        return original(path)

    monkeypatch.setattr(freeze, 'sha256_file', guard)
    entry = freeze.run_entry('OOF', 'oof', skip_test_predictions=True)
    assert entry['hop_seconds'] == 5
    assert entry['window_weighting'] == 'uniform'
    assert entry['cv_fold'] == [0]
    assert all(a['exists'] for a in entry['artifacts'])
    assert not any(a['path'].endswith('test.npz') for a in entry['artifacts'])
    assert [a['path'] for a in entry['artifacts'] if a['kind'] == 'best_checkpoint'] == [
        str(fold / 'checkpoints/best.pt')]
    dependency_paths = {a['path'] for a in entry['artifacts'] if a['kind'] == 'dependency_manifest'}
    assert dependency_paths == {str(fold / 'manifest.json'), str(derived / 'manifest.json')}


def test_discover_only_complete_new_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze, 'RUNS', tmp_path)
    write_run(tmp_path, 'old')
    write_run(tmp_path, 'fold', config={'cv_fold': 0})
    write_run(tmp_path, 'unfinished', task='sed_oof', complete=False)
    write_run(tmp_path, 'derived', task='sed_rewindow', config={'source_run': 'old'})
    found = set(freeze.phase_o_runs().values())
    assert found == {'fold', 'derived'}


def test_cycles_rejected_and_missing_dependencies_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze, 'RUNS', tmp_path)
    cyclic = write_run(tmp_path, 'cycle', task='sed_rewindow', config={'source_run': 'cycle'})
    with pytest.raises(ValueError, match='cycle'):
        ledger.run_details(cyclic)
    with pytest.raises(ValueError, match='cycle'):
        list(freeze.member_runs(cyclic, json.loads((cyclic / 'manifest.json').read_text())))
    write_run(tmp_path, 'missing', task='sed_rewindow', config={'source_run': 'absent'})
    entry = freeze.run_entry('missing', 'missing', skip_test_predictions=True)
    missing = [a for a in entry['artifacts'] if not a['exists']]
    assert {a['kind'] for a in missing} == {'dependency_manifest', 'best_checkpoint'}


def test_freeze_render_explains_skip_and_recipe():
    result = {'git': {'revision': 'r', 'dirty': False}, 'runs': [], 'external': [],
              'frozen_inputs': [], 'skip_test_predictions': True}
    assert 'không mở hoặc hash' in freeze.render(result)


def test_dependency_dag_does_not_duplicate_checkpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze, 'RUNS', tmp_path)
    write_run(tmp_path, 'source')
    write_run(tmp_path, 'r1', task='sed_rewindow', config={'source_run': 'source'})
    write_run(tmp_path, 'r2', task='sed_rewindow', config={'source_run': 'source'})
    write_run(tmp_path, 'ensemble', task='sed_ensemble', config={'members': ['r1', 'r2']})
    entry = freeze.run_entry('ensemble', 'ensemble', skip_test_predictions=True)
    checkpoints = [a for a in entry['artifacts'] if a['kind'] == 'best_checkpoint']
    assert len(checkpoints) == 1
    assert Path(checkpoints[0]['path']).parent.parent.name == 'source'
