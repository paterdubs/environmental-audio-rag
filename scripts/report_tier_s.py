"""Summarize complete annotated-dev screening runs against all three T2b seeds."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean, stdev

from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts.report_s13_ranking import best_family, load_families
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
                or (re.fullmatch(r'sed_polyphonic_\d{8}T\d{6}Z', name)
                    and name >= 'sed_polyphonic_20261008T000000Z')):
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


def recipe_key(config: dict) -> tuple:
    return (config.get('recipe'), bool(config.get('train_fixes')),
            config.get('window_sampling', {}).get('mode', 'uniform'),
            config.get('boundary_head'))


def same_recipe(a: tuple, b: tuple) -> bool:
    # Train fixes are part of B0's OOF protocol, even when absent in tier S training.
    return (a[0], a[2], a[3]) == (b[0], b[2], b[3])


def source_recipes(folder: Path, runs: Path, visiting: tuple = ()) -> tuple[set, dict]:
    folder = folder.resolve()
    if not folder.is_relative_to(runs.resolve()) or folder in visiting:
        raise ValueError(f'OOF source outside runs or cyclic: {folder}')
    path = folder / 'manifest.json'
    manifest = read(path)
    config = manifest.get('config', {})
    hashes = {str(path): sha256_file(path)}
    if not manifest.get('complete'):
        raise ValueError(f'incomplete OOF source: {folder}')
    sources = config.get('members', [])
    if manifest.get('task') == 'sed_rewindow':
        sources = [config['source_run']]
    if not sources:
        if config.get('recipe') is None:
            raise ValueError(f'source has no recipe: {folder}')
        return {recipe_key(config)}, hashes
    keys = set()
    for member in sources:
        found, provenance = source_recipes(runs / member, runs, (*visiting, folder))
        keys.update(found)
        hashes.update(provenance)
    return keys, hashes


def tier_c(runs: Path, rows: list[dict]) -> dict:
    output, pending, unmatched = [], [], []
    folds_hash = sha256_file(ROOT / 'data/splits/datased_trainval_folds.csv')
    for folder in sorted(runs.glob('sed_oof_*')):
        manifest = read(folder / 'manifest.json')
        missing = [name for name in SELECTIONS if not (folder / name).is_file()]
        if missing or not manifest.get('complete'):
            pending.append({'run': str(folder.resolve()), 'missing': missing})
            continue
        if manifest.get('task') != 'sed_oof' or manifest['config'].get(
                'cv_folds_sha256') != folds_hash:
            raise ValueError(f'{folder}: invalid OOF task/fold hash')
        families = load_families(folder, 'annotated', validate_provenance=True)
        if {f.family for f in families} != {'theta', 'csebb'}:
            raise ValueError(f'{folder}: requires both OOF families')
        for score in families:
            if len(score.folds) != 5 or abs(mean(score.folds) - score.mean) > 1e-12 or (
                    abs(stdev(score.folds) - score.sd) > 1e-12):
                raise ValueError(f'{folder}: inconsistent OOF CV scores')
        keys, hashes = source_recipes(folder, runs)
        matches = [r for r in rows if not r['is_seed'] and any(
            same_recipe(recipe_key(r['config']), key) for key in keys)]
        if len(keys) != 1 or not matches:
            unmatched.append({'run': str(folder.resolve()),
                              'reason': 'mixed recipes or no screening recipe match',
                              'source_manifests_sha256': hashes})
            continue
        sources = {name: sha256_file(folder / name) for name in SELECTIONS}
        counts = {read(folder / name)['dev_recordings'] for name in SELECTIONS
                  if 'dev_recordings' in read(folder / name)}
        if counts != {564}:
            raise ValueError(f'{folder}: expected 564 annotated OOF recordings')
        for row in matches:
            output.append({'screening_run': row['screening']['run'],
                           'screening_winner': row['screening']['winner'],
                           'oof_run': str(folder.resolve()),
                           'oof_winner': asdict(best_family(families)),
                           'oof_families': [asdict(f) for f in families],
                           'oof_recipe_signature': list(next(iter(keys))),
                           'train_fixes_differ': recipe_key(row['config'])[1] !=
                           next(iter(keys))[1],
                           'n_oof_recordings': 564, 'sources_sha256': sources,
                           'source_manifests_sha256': hashes})
    return {'rows': output, 'pending': pending, 'unmatched': unmatched,
            'note': 'stored selected-family CV; dev134 vs OOF564, inference may differ; '
                    'recipe matched by recipe/window_sampling/boundary_head; '
                    'train_fixes differences explicit; '
                    'not a paired comparison or a selection decision'}


def render_tier_c(result: dict) -> list[str]:
    section = result.get('tier_c', {'rows': [], 'pending': [], 'unmatched': []})
    lines = ['', '## Tầng S → tầng C (chỉ mô tả)', '',
             'CV đã lưu: tầng S dev134 so tầng C OOF564. Ghép recipe từ manifest nguồn '
             '(recipe, window_sampling, boundary_head), không ghép theo tên nhãn. '
             '**train_fixes có thể khác giữa S/C**, ghi riêng; không coi hai pipeline giống nhau. '
             'Suy luận raw/chồng lấn có thể khác; đây không phải Δ ghép cặp, '
             'không kết luận chọn hoặc khẳng định tổng quát hóa.', '',
             '| Run tầng S | Recipe/cờ S | Điểm S / họ | Run OOF | Điểm C / họ |',
             '|---|---|---:|---|---:|']
    recipes = {r['screening']['run']: r['recipe'] for r in result['rows']}
    for row in section['rows']:
        s, c = row['screening_winner'], row['oof_winner']
        lines.append(f"| {Path(row['screening_run']).name} | {recipes[row['screening_run']]} | "
                     f"{s['mean']:.4f}±{s['sd']:.4f} / {s['family']} | "
                     f"{Path(row['oof_run']).name}; train_fixes="
                     f"{row['oof_recipe_signature'][1]} (khác S={row['train_fixes_differ']}) | "
                     f"{c['mean']:.4f}±{c['sd']:.4f} / {c['family']} |")
    lines.append('')
    for item in section['pending']:
        lines.append(f"- OOF đang chờ `{item['run']}`: {', '.join(item['missing']) or 'complete'}.")
    for item in section['unmatched']:
        lines.append(f"- OOF chưa ghép `{item['run']}`: {item['reason']}.")
    return lines


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
    lines += render_tier_c(result)
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
    result['tier_c'] = tier_c(args.runs_dir, result['rows'])
    result['git'] = git_state(ROOT)
    print(write_report(result, 'tier_s', args.stamp, args.out_dir, render))


if __name__ == '__main__':
    main()
