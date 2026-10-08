"""Summarize complete annotated-dev screening runs against all three T2b seeds."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts.report_screening import compare, delta, load_run
from scripts.report_screening_per_class import fmt, reconstruct

ROOT = Path(__file__).resolve().parents[1]
SEEDS = tuple(f'sed_polyphonic_20260927T{s}Z' for s in ('172924', '180358', '185137'))
SELECTIONS = ('postproc_cv_selection_annotated.json', 'sebb_cv_selection_annotated.json')


def read(path: Path) -> dict:
    return json.loads(path.read_text('utf-8'))


def discover(runs: Path) -> list[Path]:
    selected = []
    for folder in sorted(runs.iterdir()):
        if not folder.is_dir() or not (folder / 'manifest.json').is_file():
            continue
        name = folder.name
        if not (name in SEEDS or name == 'sed_ensemble_t2b_20260927T200914Z'
                or name.startswith('sed_ensemble_f2_h')
                or name.startswith('sed_polyphonic_20261008')):
            continue
        if read(folder / 'manifest.json').get('config', {}).get('cv_fold') is None:
            selected.append(folder)
    return selected


def recipe(manifest: dict) -> str:
    config = manifest.get('config', {})
    flags = [str(config.get('recipe', config.get('ensemble_label', 'unspecified')))]
    if config.get('train_fixes'):
        flags.append('--train-fixes')
    if config.get('window_sampling'):
        flags.append('window_sampling=' + config['window_sampling']['mode'])
    for key in ('sequence_model', 'weight_source', 'hop_seconds', 'weighting'):
        if key in config:
            flags.append(f'{key}={config[key]}')
    return '; '.join(flags)


def best_frame_map(folder: Path) -> dict:
    path = folder / 'metrics.json'
    metrics = read(path) if path.is_file() else {}
    value = metrics.get('best_validation') if metrics.get('select_metric') == (
        'macro_average_precision') else None
    return {'value': value, 'source': str(path),
            'sha256': sha256_file(path) if path.is_file() else None,
            'note': 'saved validation metric; not recomputed on annotated dev' if value is not None
            else 'not available in metrics.json; no member averaging'}


def summarize(folders: list[Path], seeds: list[Path]) -> dict:
    if len(seeds) != 3 or len(set(p.resolve() for p in seeds)) != 3:
        raise ValueError('requires three distinct T2b seeds')
    baseline_runs = []
    for folder in seeds:
        if any(not (folder / name).is_file() for name in SELECTIONS):
            raise ValueError(f'{folder}: seed missing annotated selection')
        baseline_runs.append(load_run(f'{folder.name}={folder.resolve()}'))
    compare(baseline_runs[0], baseline_runs[1:])
    best = max(baseline_runs, key=lambda row: row['winner']['mean'])
    baseline_by_path = {row['run']: row for row in baseline_runs}
    rows, pending = [], []
    for folder in dict.fromkeys([*seeds, *folders]):
        manifest = read(folder / 'manifest.json')
        missing = [name for name in SELECTIONS if not (folder / name).is_file()]
        if missing or not manifest.get('complete'):
            pending.append({'run': str(folder.resolve()), 'missing': missing,
                            'complete': manifest.get('complete', False),
                            'recipe': recipe(manifest)})
            continue
        run = baseline_by_path.get(str(folder.resolve()))
        if run is None:
            run = load_run(f'{folder.name}={folder.resolve()}')
        compare(best, [run] if run['label'] != best['label'] else [])
        if set(run['families']) != {'theta', 'csebb'}:
            raise ValueError('requires both annotated selection families')
        measured = reconstruct(run)
        difference = delta(run['winner'], best['winner'])
        rows.append({'screening': run, 'recipe': recipe(manifest), 'config': manifest.get('config'),
                     'frame_map': best_frame_map(folder), 'vs_best_seed': difference,
                     'passes_screening': difference['mean'] > 0,
                     'is_seed': str(folder.resolve()) in baseline_by_path,
                     'full_dev_in_sample': measured})
    return {'split': 'dev', 'eval_set': 'annotated', 'best_seed': best['label'],
            'best_seed_cv': best['winner'], 'seed_mean': sum(r['winner']['mean'] for r in
                                                           baseline_runs) / 3,
            'rows': rows, 'pending': pending}


def render(result: dict) -> str:
    lines = ['# Tầng S — mọi run so ba seed T2b', '',
             '> Chỉ sàng lọc, không chọn hệ thống cuối. Họ thắng theo CV mean, hòa giữ θ (S13). '
             'Qua khi CV mean **lớn hơn** seed T2b tốt nhất, dùng số đầy đủ. '
             'Macro/micro full-dev là **in-sample dev annotated**, refit đã lưu; '
             'không phải CV/OOF/test. Macro sed_eval bỏ NaN; Nsys/Nref và per-class có trong JSON. '
             'Frame mAP lấy metrics.json best_validation, '
             'khác phạm vi raster annotated dùng chấm event.',
             '', f"Seed tốt nhất: `{result['best_seed']}`; mean ba seed: "
             f"{result['seed_mean']:.6f}.", '',
             '| Run | Recipe/cờ manifest | Frame mAP tốt nhất | θ CV mean±sd | cSEBB CV mean±sd | '
             'Họ thắng/cấu hình | Δ seed tốt nhất | Qua | Fold cao hơn | '
             'Macro full-dev | Micro full-dev |',
             '|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|']
    for row in result['rows']:
        run, d, full = row['screening'], row['vs_best_seed'], row['full_dev_in_sample']
        t, c, w = run['families']['theta'], run['families']['csebb'], run['winner']
        config = w['config'].replace('|', '\\|')
        lines.append(f"| {run['label']} | {row['recipe']} | {fmt(row['frame_map']['value'])} | "
                     f"{t['mean']:.4f}±{t['sd']:.4f} | {c['mean']:.4f}±{c['sd']:.4f} | "
                     f"{w['family']}: {config} | {d['mean']:+.6f} | "
                     f"{'qua' if row['passes_screening'] else 'không qua'} | "
                     f"{d['folds_greater']}/{d['n_folds']} | {fmt(full['macro_f1'])} | "
                     f"{fmt(full['micro_f1'])} |")
    lines += ['', '## Đang chờ', '']
    lines += [f"- `{p['run']}`: thiếu {', '.join(p['missing']) or 'run complete'}; "
              f"complete={p['complete']}; {p['recipe']}" for p in result['pending']]
    if not result['pending']:
        lines.append('Không có.')
    return '\n'.join([*lines, ''])


def write_report(result: dict, name: str, stamp: str, out_dir: Path, renderer) -> Path:
    if not re.fullmatch(r'\d{8}', stamp):
        raise ValueError('stamp must be YYYYMMDD')
    output = out_dir / f'{name}_{stamp}.json'
    if output.exists() or output.with_suffix('.md').exists():
        raise FileExistsError(output)
    out_dir.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), 'utf-8')
    output.with_suffix('.md').write_text(renderer(result), 'utf-8')
    return output


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-dir', type=Path, required=True)
    parser.add_argument('--run', type=Path, action='append', help='explicit candidate paths')
    parser.add_argument('--seed-run', type=Path, action='append',
                        help='three explicit T2b seed paths')
    parser.add_argument('--stamp', default='20261009')
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    result = summarize(args.run if args.run is not None else discover(args.runs_dir),
                       args.seed_run or [args.runs_dir / name for name in SEEDS])
    result['git'] = git_state(ROOT)
    print(write_report(result, 'tier_s', args.stamp, args.out_dir, render))


if __name__ == '__main__':
    main()
