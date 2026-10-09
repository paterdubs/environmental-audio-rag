"""Queue uses fake subprocesses only: no models, GPU, or test predictions."""
import json
import subprocess
from pathlib import Path

import pytest

from scripts import run_oof_queue as queue


class FakeCommands:
    def __init__(self, root):
        self.root, self.calls, self.fail = root, [], {}
        self.fold_path = root / queue.FOLDS
        self.fold_path.parent.mkdir(parents=True)
        self.fold_path.write_text('recording_id,fold\nr0,0\n', encoding='utf-8')
        self.shared = dict.fromkeys(
            ('split_sha256', 'taxonomy_sha256', 'data_manifest_sha256'), 'a'*64)

    @staticmethod
    def write(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding='utf-8')

    def prediction(self, run, content=b'synthetic placeholder; never loaded'):
        (run/'predictions').mkdir(exist_ok=True)
        (run/'predictions/dev.npz').write_bytes(content)

    def train(self, command):
        fold = int(command[command.index('--cv-fold') + 1])
        if self.fail.get('fold') == fold:
            return subprocess.CompletedProcess(command, 127, 'simulated failure')
        run = self.root / 'ml/runs' / f'train_{fold}'
        manifest = {'complete': True, 'git': {'dirty': False}, **self.shared,
                    'config': {'cv_fold': fold, 'seed': 20260922,
                               'window_frames': 1000, 'hop_frames': 1000, 'frame_rate': 100.,
                               'cv_folds_sha256': queue.digest(self.fold_path)}}
        if self.fail.get('manifest'):
            section, key, value = self.fail['manifest']
            (manifest[section] if section else manifest)[key] = value
        self.write(run/'manifest.json', manifest)
        self.prediction(run)
        return subprocess.CompletedProcess(command, 0, 'epoch logs\n' +
                                           json.dumps({'run': str(run)}))

    def dump(self, command):
        source = Path(command[3])
        fold = int(source.name.removeprefix('train_'))
        if self.fail.get('rewindow') == fold:
            return subprocess.CompletedProcess(command, 1, 'rewindow failed')
        run = self.root/'ml/runs'/f'rewindow_{fold}'
        hop = float(command[command.index('--hop-seconds') + 1])
        config = {'source_run': source.name, 'hop_seconds': hop,
                  'hop_frames': round(hop * 100), 'window_frames': 1000, 'frame_rate': 100.,
                  'window_weighting': command[command.index('--weighting') + 1]}
        if self.fail.get('rewindow_config'):
            key, value = self.fail['rewindow_config']
            config[key] = value
        self.write(run/'manifest.json', {'task': 'sed_rewindow', 'complete': True,
                   'git': {'dirty': False}, 'config': config, **self.shared})
        self.prediction(run)
        return subprocess.CompletedProcess(command, 0, json.dumps({'run_dir': str(run)}))

    def build(self, command):
        label = command[command.index('--label') + 1]
        if self.fail.get('build') == label:
            return subprocess.CompletedProcess(command, 1, 'build failed')
        run = self.root/'ml/runs'/('oof' if label == 'B0' else f'oof_{label}')
        self.write(run/'manifest.json', {'task': 'sed_oof', 'complete': True,
                   'git': {'dirty': False}, 'config': {
                       'cv_folds_sha256': queue.digest(self.fold_path),
                       'members': [Path(p).name for p in command[-5:]]}})
        self.prediction(run)
        return subprocess.CompletedProcess(command, 0, json.dumps({'run_dir': str(run)}))

    def __call__(self, command, root):
        assert root == self.root
        self.calls.append(command)
        module = command[2].removeprefix('scripts.')
        if module in ('train_sed', 'dump_predictions', 'build_oof'):
            return {'train_sed': self.train, 'dump_predictions': self.dump,
                    'build_oof': self.build}[module](command)
        if self.fail.get('selector') == module or self.fail.get('selector_branch') == (
                module, Path(command[3]).name):
            return subprocess.CompletedProcess(command, 1, 'selector failed')
        run = Path(command[3])
        prefix = 'postproc' if module == 'select_postproc_cv' else 'sebb'
        self.write(run/f'{prefix}_cv_selection_annotated.json',
                   {'run': run.name, 'eval_set': 'annotated', 'git': {'dirty': False}})
        if prefix == 'postproc':
            self.write(run/'postproc_cv_annotated.json', {'fixture_refit': .5})
        return subprocess.CompletedProcess(command, 0, 'selected')


@pytest.fixture
def fake(tmp_path):
    runner = FakeCommands(tmp_path)
    return tmp_path, runner.calls, runner.fail, runner


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
    assert calls[6][-6:] == ['--modes', 'global', '--workers', '2', '--eval-set', 'annotated']
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
    assert 'scripts.build_oof' in output and output.count('--workers 2') == 2
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


def test_rewindow_full_order_labels_and_no_subprocess_on_resume(fake):
    root, calls, _, _ = fake
    state = execute(fake, rewindow='5:triangular:0.3')
    assert state['complete']
    assert [c[2] for c in calls] == ['scripts.train_sed']*5 + ['scripts.dump_predictions']*5 + [
        'scripts.build_oof']*2 + ['scripts.select_postproc_cv', 'scripts.select_sebb_cv']*2
    for fold, command in enumerate(calls[5:10]):
        assert command[3] == str(root / 'ml/runs' / f'train_{fold}')
        assert command[4:] == ['--split', 'dev', '--hop-seconds', '5', '--weighting',
                               'triangular:0.3', '--label', f'B0_f{fold}_h5']
    assert calls[10][4] == 'B0_h10' and calls[11][4] == 'B0_h5'
    assert len(state['steps']) == 11
    calls.clear()
    assert execute(fake, rewindow='5:triangular:0.3')['complete'] and not calls


@pytest.mark.parametrize('stage', ['dump', 'build', 'select'])
def test_rewindow_resume_at_each_stage_without_repeating_success(fake, stage):
    _, calls, fail, _ = fake
    if stage == 'dump':
        fail['rewindow'] = 2
    elif stage == 'build':
        fail['build'] = 'B0_h5'
    else:
        fail['selector_branch'] = ('select_sebb_cv', 'oof_B0_h5')
    with pytest.raises(RuntimeError):
        execute(fake, rewindow='5:triangular:0.3')
    calls.clear()
    fail.clear()
    execute(fake, rewindow='5:triangular:0.3')
    modules = [c[2] for c in calls]
    assert modules.count('scripts.train_sed') == 0
    assert modules.count('scripts.dump_predictions') == (3 if stage == 'dump' else 0)
    assert modules.count('scripts.build_oof') == {'dump': 2, 'build': 1, 'select': 0}[stage]
    assert len(calls) == {'dump': 9, 'build': 5, 'select': 1}[stage]


@pytest.mark.parametrize('value', ['0:uniform', '10:uniform', '-1:uniform', 'nan:uniform',
                                  'inf:uniform', '5', '5:unknown', '5:triangular:1.2'])
def test_bad_rewindow_rejected_without_side_effect(fake, value):
    root, calls, _, _ = fake
    with pytest.raises(ValueError):
        execute(fake, rewindow=value)
    assert not calls and not (root/'ml/runs').exists()


def test_rewindow_dry_run_order_and_completed_steps_are_omitted(fake, capsys):
    root, calls, _, _ = fake
    execute(fake, rewindow='2.5:uniform', dry_run=True)
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 16
    assert all('train_sed' in row for row in lines[:5])
    assert all('dump_predictions' in row and '--split dev' in row for row in lines[5:10])
    assert 'B0_h10' in lines[10] and 'B0_h2.5' in lines[11]
    assert all('select_' in row for row in lines[12:])
    assert '--weighting uniform' in lines[5] and 'B0_f0_h2.5' in lines[5]
    assert not calls and not (root/'ml/runs').exists()
    execute(fake, rewindow='2.5:uniform')
    capsys.readouterr()
    calls.clear()
    execute(fake, rewindow='2.5:uniform', dry_run=True)
    assert not capsys.readouterr().out and not calls


def test_rewindow_changed_options_and_prediction_bytes_refused(fake):
    root, calls, _, _ = fake
    execute(fake, rewindow='5:triangular:0.3')
    calls.clear()
    for option in (None, '2.5:triangular:0.3', '5:uniform'):
        with pytest.raises(ValueError, match='resume khác'):
            execute(fake, rewindow=option)
    (root/'ml/runs/rewindow_0/predictions/dev.npz').write_bytes(b'changed')
    with pytest.raises(ValueError, match='predictions dev rewindow đã đổi'):
        execute(fake, rewindow='5:triangular:0.3')
    assert not calls


@pytest.mark.parametrize('change', [('source_run', 'other'), ('hop_seconds', 2.5),
                                  ('window_weighting', 'uniform'), ('hop_frames', 250),
                                  ('frame_rate', 50.), ('window_frames', 500)])
def test_rewindow_wrong_derived_provenance_stops_before_build(fake, change):
    _, calls, fail, _ = fake
    fail['rewindow_config'] = change
    with pytest.raises(ValueError, match='provenance rewindow'):
        execute(fake, rewindow='5:triangular:0.3')
    assert len(calls) == 6 and calls[-1][2] == 'scripts.dump_predictions'


@pytest.mark.parametrize('relative', ['train_0/predictions/dev.npz',
                                    'oof_B0_h10/predictions/dev.npz',
                                    'oof_B0_h5/postproc_cv_annotated.json'])
def test_rewindow_resume_rejects_changed_raw_oof_or_refit(fake, relative):
    root, calls, _, _ = fake
    execute(fake, rewindow='5:triangular:0.3')
    calls.clear()
    path = root/'ml/runs'/relative
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='đã đổi'):
        execute(fake, rewindow='5:triangular:0.3')
    assert not calls


def test_raw_h10_branch_rejects_source_with_different_window_or_hop(fake):
    _, calls, fail, _ = fake
    fail['manifest'] = ('config', 'hop_frames', 500)
    with pytest.raises(ValueError, match='nhánh thô h10'):
        execute(fake, rewindow='5:triangular:0.3')
    assert len(calls) == 5 and all(c[2] == 'scripts.train_sed' for c in calls)


def test_existing_non_rewindow_queue_cannot_enable_rewindow_mid_resume(fake):
    _, calls, _, _ = fake
    execute(fake)
    calls.clear()
    with pytest.raises(ValueError, match='resume khác'):
        execute(fake, rewindow='5:triangular:0.3')
    assert not calls


def test_skip_raw_cv_builds_both_but_selects_overlap_only_and_resumes(fake):
    root, calls, _, _ = fake
    state = execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True)
    assert len(calls) == 14 and state['complete'] and state['skip_raw_cv']
    assert calls[10][4] == 'B0_h10' and calls[11][4] == 'B0_h5'
    assert all(c[3].endswith('oof_B0_h5') for c in calls[12:])
    assert calls[12][-6:] == ['--modes', 'global', '--workers', '2', '--eval-set', 'annotated']
    assert calls[13][-4:] == ['--workers', '2', '--eval-set', 'annotated']
    assert 'select_postproc_cv_h10' not in state['steps']
    assert not (root/'ml/runs/oof_B0_h10/postproc_cv_selection_annotated.json').exists()
    calls.clear()
    execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True)
    assert not calls
    with pytest.raises(ValueError, match='resume khác'):
        execute(fake, rewindow='5:triangular:0.3')


def test_skip_raw_cv_dry_run_is_fourteen_commands_without_side_effects(fake, capsys):
    root, calls, _, _ = fake
    execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True, dry_run=True)
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 14
    assert all('train_sed' in c for c in lines[:5])
    assert all('dump_predictions' in c for c in lines[5:10])
    assert 'B0_h10' in lines[10] and 'B0_h5' in lines[11]
    assert all('<oof_h5-run>' in c and '--workers 2' in c for c in lines[12:])
    assert not calls and not (root/'ml/runs').exists()


def test_skip_raw_cv_requires_rewindow_before_writing_state(fake):
    root, calls, _, _ = fake
    with pytest.raises(ValueError, match='cần --rewindow'):
        execute(fake, skip_raw_cv=True)
    assert not calls and not (root/'ml/runs').exists()


def test_skip_raw_cv_cannot_be_enabled_on_existing_full_cv_state(fake):
    _, calls, _, _ = fake
    execute(fake, rewindow='5:triangular:0.3')
    calls.clear()
    with pytest.raises(ValueError, match='resume khác'):
        execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True)
    assert not calls


def test_skip_raw_cv_resumes_failed_overlap_selector_without_rebuild(fake):
    _, calls, fail, _ = fake
    fail['selector_branch'] = ('select_sebb_cv', 'oof_B0_h5')
    with pytest.raises(RuntimeError):
        execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True)
    calls.clear()
    fail.clear()
    execute(fake, rewindow='5:triangular:0.3', skip_raw_cv=True)
    assert len(calls) == 1 and calls[0][2] == 'scripts.select_sebb_cv'
