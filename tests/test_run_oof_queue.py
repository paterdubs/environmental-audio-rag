"""Queue uses fake subprocesses only: no models, GPU, or test predictions."""
import json
import subprocess
from pathlib import Path

import pytest

from scripts import run_oof_queue as queue


@pytest.fixture
def fake(tmp_path):
    fold_path = tmp_path / queue.FOLDS
    fold_path.parent.mkdir(parents=True)
    fold_path.write_text('recording_id,fold\nr0,0\n', encoding='utf-8')
    calls = []
    fail = {}

    def write(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding='utf-8')

    def runner(command, root):
        calls.append(command)
        module = command[2].removeprefix('scripts.')
        if module == 'train_sed':
            fold = int(command[command.index('--cv-fold') + 1])
            if fail.get('fold') == fold:
                return subprocess.CompletedProcess(command, 127, 'simulated failure')
            run = root / 'ml/runs' / f'train_{fold}'
            manifest = {'complete': True, 'git': {'dirty': False},
                        'config': {'cv_fold': fold, 'seed': 20260922,
                                   'cv_folds_sha256': queue.digest(fold_path)}}
            if fail.get('manifest'):
                section, key, value = fail['manifest']
                (manifest[section] if section else manifest)[key] = value
            write(run/'manifest.json', manifest)
            (run/'predictions').mkdir(exist_ok=True)
            (run/'predictions/dev.npz').write_bytes(b'synthetic placeholder; never opened')
            return subprocess.CompletedProcess(command, 0, 'epoch logs\n' +
                                               json.dumps({'run': str(run)}))
        if module == 'build_oof':
            run = root/'ml/runs/oof'
            write(run/'manifest.json', {'task': 'sed_oof', 'complete': True,
                  'git': {'dirty': False}, 'config': {
                      'cv_folds_sha256': queue.digest(fold_path),
                      'members': [Path(p).name for p in command[-5:]]}})
            (run/'predictions').mkdir(exist_ok=True)
            (run/'predictions/dev.npz').write_bytes(b'not read')
            return subprocess.CompletedProcess(command, 0, json.dumps({'run_dir': str(run)}))
        if fail.get('selector') == module:
            return subprocess.CompletedProcess(command, 1, 'selector failed')
        run = Path(command[3])
        prefix = 'postproc' if module == 'select_postproc_cv' else 'sebb'
        write(run/f'{prefix}_cv_selection_annotated.json',
              {'run': run.name, 'eval_set': 'annotated', 'git': {'dirty': False}})
        return subprocess.CompletedProcess(command, 0, 'selected')
    return tmp_path, calls, fail, runner


def execute(fake, **kwargs):
    root, _, _, runner = fake
    return queue.execute_queue('B0', 20260922, ['--encoder', 'frame_mn', '--recipe', 't2b'],
                               root=root, runner=runner, **kwargs)


def test_full_order_and_resume_without_any_subprocess(fake):
    state = execute(fake)
    root, calls, _, _ = fake
    assert state['complete']
    assert [c[2] for c in calls] == ['scripts.train_sed']*5 + [
        'scripts.build_oof', 'scripts.select_postproc_cv', 'scripts.select_sebb_cv']
    assert [c[-1] for c in calls[:5]] == list('01234')
    assert calls[6][-6:] == ['--modes', 'global', '--workers', '3', '--eval-set', 'annotated']
    assert calls[7][-4:] == ['--workers', '2', '--eval-set', 'annotated']
    before = (root/'ml/runs/oof_queue_B0.json').read_bytes()
    calls.clear()
    assert execute(fake)['complete'] and not calls
    assert (root/'ml/runs/oof_queue_B0.json').read_bytes() == before


def test_resume_mid_fold_failure_and_stop_nonzero_even_127(fake):
    root, calls, fail, _ = fake
    fail['fold'] = 2
    with pytest.raises(RuntimeError, match='127'):
        execute(fake)
    state = queue.read(root/'ml/runs/oof_queue_B0.json')
    assert set(state['folds']) == {'0', '1'} and not state['complete']
    assert len(calls) == 3
    assert not (root/'ml/runs/oof_queue_B0.lock').exists()
    calls.clear()
    fail.clear()
    execute(fake)
    assert [c[-1] for c in calls[:3]] == ['2', '3', '4']
    assert len(calls) == 6


def test_resume_selector_failure_does_not_rebuild_oof(fake):
    _, calls, fail, _ = fake
    fail['selector'] = 'select_sebb_cv'
    with pytest.raises(RuntimeError, match='select_sebb_cv'):
        execute(fake)
    calls.clear()
    fail.clear()
    execute(fake)
    assert len(calls) == 1 and calls[0][2] == 'scripts.select_sebb_cv'


@pytest.mark.parametrize('change', [('', 'complete', False), ('git', 'dirty', True),
    ('config', 'cv_fold', 4), ('config', 'cv_fold', False),
    ('config', 'cv_folds_sha256', 'wrong'), ('config', 'seed', 2)])
def test_invalid_manifest_stops_before_next_fold(fake, change):
    _, calls, fail, _ = fake
    fail['manifest'] = change
    with pytest.raises(ValueError, match='manifest fold'):
        execute(fake)
    assert len(calls) == 1


@pytest.mark.parametrize('argument', ['--evaluate-test', '--evaluate-test=true',
    '--evaluate-t', '--evaluate', '--cv-fold=2', '--cv-f', '--seed=2'])
def test_reject_test_and_managed_args_including_argparse_abbreviations(fake, argument):
    root, calls, _, runner = fake
    with pytest.raises(ValueError, match='không chuyển tiếp'):
        queue.execute_queue('B0', 20260922, [argument], root=root, runner=runner)
    assert not calls and not (root/'ml/runs').exists()


def test_dry_run_prints_commands_without_writing_or_running(fake, capsys):
    root, calls, _, _ = fake
    execute(fake, dry_run=True)
    output = capsys.readouterr().out
    assert output.count('scripts.train_sed') == 5
    assert 'scripts.build_oof' in output and '--workers 3' in output and '--workers 2' in output
    assert '<fold-4-run>' in output and not calls and not (root/'ml/runs').exists()


def test_changed_resume_arguments_or_fold_hash_are_rejected(fake):
    root, calls, _, runner = fake
    execute(fake)
    calls.clear()
    with pytest.raises(ValueError, match='resume khác'):
        queue.execute_queue('B0', 2, [], root=root, runner=runner)
    (root/queue.FOLDS).write_text('changed')
    with pytest.raises(ValueError, match='resume khác'):
        execute(fake)
    assert not calls


def test_changed_manifest_or_selection_refused_on_resume(fake):
    root, calls, _, _ = fake
    execute(fake)
    calls.clear()
    selection = root/'ml/runs/oof/sebb_cv_selection_annotated.json'
    old = selection.read_text()
    selection.write_text(old+' ')
    with pytest.raises(ValueError, match='selection đã đổi'):
        execute(fake)
    selection.write_text(old)
    manifest = root/'ml/runs/train_0/manifest.json'
    manifest.write_text(manifest.read_text()+' ')
    with pytest.raises(ValueError, match='manifest đã đổi'):
        execute(fake)
    assert not calls


def test_subprocess_result_must_report_run_in_workspace(fake):
    root, _, _, _ = fake
    with pytest.raises(ValueError, match='run ngoài'):
        queue.reported_run(json.dumps({'run': str(root.parent/'other')}), 'run', root)
    with pytest.raises(ValueError, match='không trả JSON'):
        queue.reported_run('logs only', 'run', root)


def test_label_traversal(fake):
    root, calls, _, runner = fake
    with pytest.raises(ValueError, match='label'):
        queue.execute_queue('../other', 2, [], root=root, runner=runner)
    assert not calls and not (root/'ml/runs').exists()
