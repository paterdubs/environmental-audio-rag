"""Queue tier C: five folds, OOF assembly and annotated theta/cSEBB, without test evaluation.

Example: python -m scripts.run_oof_queue --label B0 --seed 20260922 --dry-run --
    --encoder frame_mn --recipe t2b --train-fixes
Device selection belongs to the operator; this script never changes GPU visibility.
Run a single orchestration process per label.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDS = Path('data/splits/datased_trainval_folds.csv')
Runner = Callable[[list[str], Path], subprocess.CompletedProcess]


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_arguments(label: str, forwarded: list[str]) -> None:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', label):
        raise ValueError('label chỉ gồm chữ/số/._-, không chứa đường dẫn')
    for arg in forwarded:
        option = arg.split('=', 1)[0]
        if option.startswith('--') and any(
            controlled.startswith(option) for controlled in
            ('--evaluate-test', '--cv-fold', '--seed')
        ):
            raise ValueError(f'không chuyển tiếp {option}: test bị cấm, seed/fold do queue quản lý')


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def validate_fold(run: Path, fold: int, folds_hash: str, seed: int) -> None:
    manifest = read(run / 'manifest.json')
    config = manifest.get('config', {})
    if (manifest.get('complete') is not True or manifest.get('git', {}).get('dirty') is not False
            or type(config.get('cv_fold')) is not int or config['cv_fold'] != fold
            or config.get('cv_folds_sha256') != folds_hash or config.get('seed') != seed):
        raise ValueError(f'{run}: manifest fold {fold} không hợp lệ '
                         '(complete/dirty/fold/hash/seed)')
    if not (run / 'predictions/dev.npz').is_file():
        raise ValueError(f'{run}: thiếu predictions/dev.npz')


def reported_run(stdout: str, key: str, root: Path) -> Path:
    decoder = json.JSONDecoder()
    matches = []
    for index, char in enumerate(stdout):
        if char != '{':
            continue
        try:
            value, _ = decoder.raw_decode(stdout[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get(key), str):
            matches.append(value[key])
    if not matches:
        raise ValueError(f'lệnh không trả JSON có {key}')
    run = Path(matches[-1])
    if not run.is_absolute():
        run = root / run
    run = run.resolve()
    if not run.is_relative_to((root / 'ml/runs').resolve()):
        raise ValueError(f'run ngoài ml/runs của cwd: {run}')
    return run


def subprocess_runner(command: list[str], root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=root, text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                          env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})


class OOFQueue:
    def __init__(self, label: str, seed: int, forwarded: list[str], root: Path, runner: Runner):
        validate_arguments(label, forwarded)
        self.root, self.runner = root.resolve(), runner
        self.label, self.seed, self.forwarded = label, seed, forwarded
        self.folds_hash = digest(self.root / FOLDS)
        identity = {'label': label, 'seed': seed, 'train_args': forwarded,
                    'cv_folds_sha256': self.folds_hash}
        self.path = self.root / 'ml/runs' / f'oof_queue_{label}.json'
        self.state = read(self.path) if self.path.exists() else {
            **identity, 'folds': {}, 'steps': {}}
        if any(self.state.get(k) != v for k, v in identity.items()):
            raise ValueError('resume khác label/seed/tham số/hash fold; cần label mới')

    @staticmethod
    def command(module, *args):
        return [sys.executable, '-m', f'scripts.{module}', *map(str, args)]

    def dry_run(self) -> dict:
        members = []
        for fold in range(5):
            existing = self.state['folds'].get(str(fold))
            if existing:
                validate_fold(Path(existing['run']), fold, self.folds_hash, self.seed)
            else:
                print(subprocess.list2cmdline(self.command('train_sed', *self.forwarded,
                      '--seed', self.seed, '--cv-fold', fold)))
            members.append(existing['run'] if existing else f'<fold-{fold}-run>')
        oof = self.state['steps'].get('build_oof', {}).get('run', '<oof-run>')
        print(subprocess.list2cmdline(self.command('build_oof', '--label', self.label, *members)))
        print(subprocess.list2cmdline(self.command('select_postproc_cv', oof, '--modes', 'global',
                                             '--workers', 3, '--eval-set', 'annotated')))
        print(subprocess.list2cmdline(self.command('select_sebb_cv', oof, '--workers', 2,
                                             '--eval-set', 'annotated')))
        return self.state

    def save(self) -> None:
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding='utf-8')
        os.replace(temporary, self.path)

    def invoke(self, name, cmd):
        self.state['active'] = {'stage': name, 'command': cmd}
        self.state['complete'] = False
        self.save()
        result = self.runner(cmd, self.root)
        print(result.stdout or '', flush=True)
        self.state['active'].update(returncode=result.returncode,
                                   output_tail=(result.stdout or '')[-32000:])
        self.save()
        if result.returncode != 0:
            raise RuntimeError(f'{name}: mã thoát {result.returncode}; đã dừng queue')
        return result.stdout or ''

    def train_fold(self, fold: int) -> Path:
        entry = self.state['folds'].get(str(fold))
        if entry:
            run = Path(entry['run'])
            validate_fold(run, fold, self.folds_hash, self.seed)
            if digest(run/'manifest.json') != entry['manifest_sha256']:
                raise ValueError(f'{run}: manifest đã đổi sau khi queue ghi nhận')
        else:
            stdout = self.invoke(f'fold_{fold}', self.command('train_sed', *self.forwarded,
                '--seed', self.seed, '--cv-fold', fold))
            run = reported_run(stdout, 'run', self.root)
            validate_fold(run, fold, self.folds_hash, self.seed)
            self.state['folds'][str(fold)] = {'run': str(run),
                                           'manifest_sha256': digest(run/'manifest.json')}
            self.save()
        return run

    def build_oof(self, members: list[Path]) -> Path:
        entry = self.state['steps'].get('build_oof')
        if entry:
            oof = Path(entry['run'])
            if digest(oof/'manifest.json') != entry['manifest_sha256']:
                raise ValueError('manifest OOF đã đổi')
        else:
            stdout = self.invoke('build_oof', self.command('build_oof', '--label',
                                                         self.label, *members))
            oof = reported_run(stdout, 'run_dir', self.root)
        manifest = read(oof/'manifest.json')
        config = manifest.get('config', {})
        if (manifest.get('task') != 'sed_oof' or manifest.get('complete') is not True
                or manifest.get('git', {}).get('dirty') is not False
                or config.get('cv_folds_sha256') != self.folds_hash
                or config.get('members') != [p.name for p in members]
                or not (oof/'predictions/dev.npz').is_file()):
            raise ValueError('manifest OOF không hợp lệ')
        self.state['steps']['build_oof'] = {'run': str(oof),
                                          'manifest_sha256': digest(oof/'manifest.json')}
        self.save()
        return oof

    def select(self, oof: Path, module: str, prefix: str, knobs: list[str]) -> None:
        output = oof / f'{prefix}_cv_selection_annotated.json'
        entry = self.state['steps'].get(module)
        if entry:
            if digest(output) != entry['sha256']:
                raise ValueError(f'{output}: selection đã đổi')
        else:
            self.invoke(module, self.command(module, oof, *knobs, '--eval-set', 'annotated'))
        selected = read(output)
        if (selected.get('run') != oof.name or selected.get('eval_set') != 'annotated'
                or selected.get('git', {}).get('dirty') is not False):
            raise ValueError(f'{output}: provenance selection không hợp lệ')
        self.state['steps'][module] = {'path': str(output), 'sha256': digest(output)}
        self.save()

    def run(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            members = [self.train_fold(fold) for fold in range(5)]
            oof = self.build_oof(members)
            self.select(oof, 'select_postproc_cv', 'postproc',
                        ['--modes', 'global', '--workers', '3'])
            self.select(oof, 'select_sebb_cv', 'sebb', ['--workers', '2'])
            self.state.pop('active', None)
            self.state.pop('error', None)
            self.state['complete'] = True
            self.save()
            return self.state
        except BaseException as error:
            self.state['error'] = f'{type(error).__name__}: {error}'
            self.state['complete'] = False
            self.save()
            raise


def execute_queue(label: str, seed: int, forwarded: list[str], *, dry_run: bool = False,
                  root: Path = ROOT, runner: Runner = subprocess_runner) -> dict:
    queue = OOFQueue(label, seed, forwarded, root, runner)
    return queue.dry_run() if dry_run else queue.run()


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    raw = sys.argv[1:]
    boundary = raw.index('--') if '--' in raw else len(raw)
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--label', required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(raw[:boundary])
    forwarded = raw[boundary+1:]
    execute_queue(args.label, args.seed, forwarded, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
