"""Hàng đợi tầng C: năm fold → OOF → θ/cSEBB annotated, không đánh giá test.

Ví dụ: python -m scripts.run_oof_queue --label B0 --seed 20260922 --dry-run --
    --encoder frame_mn --recipe t2b --train-fixes
GPU thuộc người vận hành; script này không tự chọn hoặc thay đổi thiết bị.
Mỗi label chạy bằng một tiến trình điều phối; không chạy hai queue cùng label.
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


def execute_queue(label: str, seed: int, forwarded: list[str], *, dry_run: bool = False,
                  root: Path = ROOT, runner: Runner = subprocess_runner) -> dict:
    validate_arguments(label, forwarded)
    root = root.resolve()
    folds_hash = digest(root / FOLDS)
    identity = {'label': label, 'seed': seed, 'train_args': forwarded,
                'cv_folds_sha256': folds_hash}
    path = root / 'ml/runs' / f'oof_queue_{label}.json'
    state = read(path) if path.exists() else {**identity, 'folds': {}, 'steps': {}}
    if any(state.get(k) != v for k, v in identity.items()):
        raise ValueError('resume khác label/seed/tham số/hash fold; cần label mới')
    python = sys.executable

    def command(module, *args):
        return [python, '-m', f'scripts.{module}', *map(str, args)]

    if dry_run:
        members = []
        for fold in range(5):
            existing = state['folds'].get(str(fold))
            if existing:
                validate_fold(Path(existing['run']), fold, folds_hash, seed)
            else:
                print(subprocess.list2cmdline(command('train_sed', *forwarded,
                      '--seed', seed, '--cv-fold', fold)))
            members.append(existing['run'] if existing else f'<fold-{fold}-run>')
        oof = state['steps'].get('build_oof', {}).get('run', '<oof-run>')
        print(subprocess.list2cmdline(command('build_oof', '--label', label, *members)))
        print(subprocess.list2cmdline(command('select_postproc_cv', oof, '--modes', 'global',
                                             '--workers', 3, '--eval-set', 'annotated')))
        print(subprocess.list2cmdline(command('select_sebb_cv', oof, '--workers', 2,
                                             '--eval-set', 'annotated')))
        return state

    path.parent.mkdir(parents=True, exist_ok=True)

    def save():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
        os.replace(temporary, path)

    def invoke(name, cmd):
        state['active'] = {'stage': name, 'command': cmd}
        state['complete'] = False
        save()
        result = runner(cmd, root)
        print(result.stdout or '', flush=True)
        state['active'].update(returncode=result.returncode,
                               output_tail=(result.stdout or '')[-32000:])
        save()
        if result.returncode != 0:
            raise RuntimeError(f'{name}: mã thoát {result.returncode}; đã dừng queue')
        return result.stdout or ''

    try:
        members = []
        for fold in range(5):
            entry = state['folds'].get(str(fold))
            if entry:
                run = Path(entry['run'])
                validate_fold(run, fold, folds_hash, seed)
                if digest(run/'manifest.json') != entry['manifest_sha256']:
                    raise ValueError(f'{run}: manifest đã đổi sau khi queue ghi nhận')
            else:
                stdout = invoke(f'fold_{fold}', command('train_sed', *forwarded,
                    '--seed', seed, '--cv-fold', fold))
                run = reported_run(stdout, 'run', root)
                validate_fold(run, fold, folds_hash, seed)
                state['folds'][str(fold)] = {'run': str(run),
                                            'manifest_sha256': digest(run/'manifest.json')}
                save()
            members.append(run)

        entry = state['steps'].get('build_oof')
        if entry:
            oof = Path(entry['run'])
            if digest(oof/'manifest.json') != entry['manifest_sha256']:
                raise ValueError('manifest OOF đã đổi')
        else:
            stdout = invoke('build_oof', command('build_oof', '--label', label, *members))
            oof = reported_run(stdout, 'run_dir', root)
        manifest = read(oof/'manifest.json')
        config = manifest.get('config', {})
        if (manifest.get('task') != 'sed_oof' or manifest.get('complete') is not True
                or manifest.get('git', {}).get('dirty') is not False
                or config.get('cv_folds_sha256') != folds_hash
                or config.get('members') != [p.name for p in members]
                or not (oof/'predictions/dev.npz').is_file()):
            raise ValueError('manifest OOF không hợp lệ')
        state['steps']['build_oof'] = {'run': str(oof),
                                     'manifest_sha256': digest(oof/'manifest.json')}
        save()
        for module, prefix, knobs in [
            ('select_postproc_cv', 'postproc', ['--modes', 'global', '--workers', '3']),
            ('select_sebb_cv', 'sebb', ['--workers', '2']),
        ]:
            output = oof / f'{prefix}_cv_selection_annotated.json'
            entry = state['steps'].get(module)
            if entry:
                if digest(output) != entry['sha256']:
                    raise ValueError(f'{output}: selection đã đổi')
            else:
                invoke(module, command(module, oof, *knobs, '--eval-set', 'annotated'))
            selected = read(output)
            if (selected.get('run') != oof.name or selected.get('eval_set') != 'annotated'
                    or selected.get('git', {}).get('dirty') is not False):
                raise ValueError(f'{output}: provenance selection không hợp lệ')
            state['steps'][module] = {'path': str(output), 'sha256': digest(output)}
            save()
        state.pop('active', None)
        state.pop('error', None)
        state['complete'] = True
        save()
        return state
    except BaseException as error:
        state['error'] = f'{type(error).__name__}: {error}'
        state['complete'] = False
        save()
        raise


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
