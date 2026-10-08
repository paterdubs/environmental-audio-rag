"""Báo cáo tầng C: fit θ/λ bỏ từng fold và bootstrap ghép cặp theo recording.

Cấu hình/họ được chọn từ CV đã có; CI có điều kiện trên lựa chọn này, không bao
gồm độ bất định do chọn họ, cấu hình hoặc train lại model. Chỉ đọc predictions/dev.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.multirun import micro_f1, paired_branch_bootstrap
from ml.evaluation.sed_metrics import event_based_f1, event_counts_per_recording
from ml.postprocessing import process_recordings
from ml.postprocessing.sebb import SebbParams, sebb_candidates, select_boxes
from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts import select_postproc_cv as theta_cv
from scripts import select_sebb_cv as sebb_cv
from scripts.report_s13_ranking import best_family, load_families

ROOT = Path(__file__).resolve().parents[1]
FOLDS = ROOT / 'data/splits/datased_trainval_folds.csv'


def theta_events(ctx: dict, config: str) -> tuple[dict, list[dict]]:
    mode, percentile = config.split('|')
    if mode != 'global':
        raise ValueError('tầng C yêu cầu theta global')
    priors = ctx['priors_by_p'][float(percentile)]
    events, fits = {}, []
    for fold in sorted(set(ctx['folds'].values())):
        fit_ids = [r for r, f in ctx['folds'].items() if f != fold]
        held = {r: ctx['probabilities'][r] for r, f in ctx['folds'].items() if f == fold}
        thresholds = theta_cv.fit(
            mode, {r: ctx['probabilities'][r] for r in fit_ids},
            {r: ctx['reference'][r] for r in fit_ids}, ctx['class_ids'], priors,
            ctx['frame_rate'], ctx['taxonomy'])
        events.update(process_recordings(held, class_ids=ctx['class_ids'], thresholds=thresholds,
                                         priors=priors, frame_rate=ctx['frame_rate']))
        fits.append({'fold': fold, 'fit_ids': fit_ids, 'held_ids': sorted(held),
                     'thresholds': thresholds})
    return events, fits


def sebb_events(ctx: dict, selected: dict) -> tuple[dict, list[dict]]:
    params = SebbParams(**{k: selected[k] for k in ('step_filter_s', 'merge_abs', 'merge_rel')})
    candidates = sebb_candidates(ctx['probabilities'], class_ids=ctx['class_ids'],
                                 frame_rate=ctx['frame_rate'], params=params)
    table = sebb_cv.count_table(ctx, params)
    fold_of = np.array([ctx['folds'][r] for r in ctx['recordings']])
    events, fits = {}, []
    for fold in sorted(set(fold_of)):
        index = int(np.argmax(sebb_cv.micro_f1(table[:, fold_of != fold].sum(axis=1))))
        threshold = sebb_cv.LAMBDAS[index]
        held = {r: candidates[r] for r in ctx['recordings'] if ctx['folds'][r] == fold}
        events.update(select_boxes(held, threshold))
        fits.append({'fold': int(fold), 'threshold': threshold, 'held_ids': sorted(held),
                     'fit_ids': [r for r in ctx['recordings'] if ctx['folds'][r] != fold]})
    return events, fits


def summarize(reference: dict, events: dict, class_ids: tuple) -> dict:
    counts = event_counts_per_recording(reference, events, event_label_list=list(class_ids))
    total = [sum(row[i] for row in counts.values()) for i in range(3)]
    metric = event_based_f1(reference, events, event_label_list=list(class_ids))
    per_class = {}
    for label in class_ids:
        ref = {r: [e for e in rows if e.get('class_id', e.get('event_label')) == label]
               for r, rows in reference.items()}
        est = {r: [e for e in rows if e.get('class_id', e.get('event_label')) == label]
               for r, rows in events.items()}
        per_class[label] = event_counts_per_recording(ref, est, event_label_list=[label])
    return {'micro_f1': micro_f1(*total), 'macro_f1': metric['macro']['f_measure'],
            'nref': total[0], 'nsys': total[1], 'ntp': total[2],
            'recall': total[2] / total[0] if total[0] else None,
            'event_ratio': total[1] / total[0] if total[0] else None,
            'counts': counts, 'per_class_counts': per_class, 'per_class': metric['per_class']}


def load_system(run: Path) -> dict:
    manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('task') != 'sed_oof' or not manifest.get('complete'):
        raise ValueError(f'{run}: cần run sed_oof hoàn tất')
    if manifest['config'].get('cv_folds_sha256') != sha256_file(FOLDS):
        raise ValueError(f'{run}: hash file fold không khớp')
    families = load_families(run, 'annotated', validate_provenance=True)
    chosen = best_family(families)
    selection = json.loads((run / ('postproc_cv_selection_annotated.json'
                                   if chosen.family == 'theta' else
                                   'sebb_cv_selection_annotated.json')).read_text(encoding='utf-8'))
    k = int(selection['folds'])
    loader = theta_cv.load_context if chosen.family == 'theta' else sebb_cv.load_context
    ctx = loader(run, k, 'annotated')
    expected = set(pd.read_csv(FOLDS)['recording_id'].astype(str))
    if set(ctx['probabilities']) != expected or set(ctx['folds'].values()) != set(range(k)):
        raise ValueError(f'{run}: thiếu recording/fold OOF')
    if any(len(f.folds) != k for f in families):
        raise ValueError(f'{run}: số fold selection không khớp')
    events, fits = (theta_events(ctx, chosen.config) if chosen.family == 'theta'
                    else sebb_events(ctx, selection['selected']))
    return {'run': str(run.resolve()), 'family': asdict(chosen),
            'families': [asdict(f) for f in families], 'fits': fits,
            'manifest': manifest, 'folds': ctx['folds'],
            'sources_sha256': {p.name: sha256_file(p) for p in
                               (run / 'manifest.json', run / 'predictions/dev.npz',
                                run / 'postproc_cv_selection_annotated.json',
                                run / 'sebb_cv_selection_annotated.json')},
            **summarize(ctx['reference'], events, ctx['class_ids'])}


def compare(systems: dict[str, dict], baseline: str) -> dict:
    base = systems[baseline]
    for name, system in systems.items():
        if set(system['counts']) != set(base['counts']):
            raise ValueError(f'{name}: tập recording khác baseline')
        if any(system['counts'][r][0] != base['counts'][r][0] for r in base['counts']):
            raise ValueError(f'{name}: reference counts khác baseline')
        if system.get('folds') != base.get('folds'):
            raise ValueError(f'{name}: phép gán fold khác baseline')
        for key in ('split_sha256', 'data_manifest_sha256', 'taxonomy_sha256'):
            if system.get('manifest', {}).get(key) != base.get('manifest', {}).get(key):
                raise ValueError(f'{name}: {key} khác baseline')
    bootstrap = paired_branch_bootstrap(
        {n: s['counts'] for n, s in systems.items()}, {n: [n] for n in systems})
    differences = {name: bootstrap['differences'][f'{name}-{baseline}']
                   for name in systems if name != baseline}
    eligible = [n for n, d in differences.items() if d['lower'] > 0]
    selected = max(eligible, key=lambda n: systems[n]['micro_f1']) if eligible else baseline
    return {'baseline': baseline, 'selected': selected, 'systems': systems,
            'differences': {n: {**d, 'passes_adr0041': d['lower'] > 0}
                            for n, d in differences.items()}, 'bootstrap': bootstrap}


def render(result: dict) -> str:
    lines = ['# Tầng C — cross-fitted OOF', '',
             '> θ/λ fit trên các fold khác; cấu hình và họ đã chọn bằng CV trên toàn OOF. '
             'CI ghép cặp 1000 lần, seed 20260922, có điều kiện trên lựa chọn đó; '
             'không đo bất định do chọn model/họ/cấu hình. Prior giữ từ train gốc theo selector. '
             'Macro theo sed_eval (bỏ NaN). Không đọc test.', '',
             '| Hệ thống | Họ | Macro | Micro | Nsys/Nref | Recall | Δ micro [95% CI] | Đạt luật |',
             '|---|---|---:|---:|---:|---:|---|:---:|']
    for name, s in result['systems'].items():
        d = result['differences'].get(name)
        delta = f"{d['estimate']:+.4f} [{d['lower']:+.4f}, {d['upper']:+.4f}]" if d else '—'
        recall = f"{s['recall']:.4f}" if s['recall'] is not None else '—'
        lines.append(f"| {name} | {s['family']['family']} | {s['macro_f1']:.4f} | "
                     f"{s['micro_f1']:.4f} | {s['nsys']}/{s['nref']} | {recall} | {delta} | "
                     f"{'có' if d and d['passes_adr0041'] else '—'} |")
    return '\n'.join([*lines, '', f"Lựa chọn theo luật: **{result['selected']}**.", ''])


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', action='append', required=True)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    git = git_state(ROOT)
    systems = {'B0': load_system(args.baseline)}
    for spec in args.candidate:
        label, sep, path = spec.partition('=')
        if not sep or not label or label in systems:
            raise ValueError('candidate cần nhãn duy nhất=đường dẫn')
        systems[label] = load_system(Path(path))
    result = {**compare(systems, 'B0'), 'git': git}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f'oof_selection_{datetime.now(UTC):%Y%m%d}.json'
    if out.exists() or out.with_suffix('.md').exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    out.with_suffix('.md').write_text(render(result), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
