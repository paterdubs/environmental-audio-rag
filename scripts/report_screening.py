"""Tầng S: ghép cặp fold CV dev giữa các run, chỉ sàng lọc, không tuyên bố.

Đọc selection θ/cSEBB và ID trong predictions/dev.npz để từ chối so khác tập.
Không đọc logit, không chạy lại CV, không đọc artifact test.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, stdev

import numpy as np
import pandas as pd

from ml.evaluation.coverage import restrict
from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts.report_s13_ranking import _family_files, _family_score, best_family
from scripts.select_postproc_cv import assign_folds

ROOT = Path(__file__).resolve().parents[1]


def load_run(spec: str, eval_set: str = 'annotated') -> dict:
    label, sep, raw = spec.partition('=')
    if not sep or not label or not Path(raw).is_dir():
        raise ValueError(f'cần nhãn=đường/dẫn/run: {spec}')
    run = Path(raw)
    manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    if not manifest.get('complete'):
        raise ValueError(f'{run}: run chưa hoàn tất')
    families, sources, fold_counts = [], {}, set()
    for family, path in _family_files(run, eval_set):
        if not path.exists():
            continue
        score = _family_score(path, family, eval_set=eval_set)
        payload = json.loads(path.read_text(encoding='utf-8'))
        if payload['grouping'] != 'leakage_group' or payload['run'] != run.name:
            raise ValueError(f'{path}: run/grouping không khớp')
        if (payload['folds'] != len(score.folds) or len(score.folds) < 2
                or not np.isfinite([score.mean, score.sd, *score.folds]).all()
                or abs(mean(score.folds) - score.mean) > 1e-12
                or abs(stdev(score.folds) - score.sd) > 1e-12):
            raise ValueError(f'{path}: mean/sd/folds không nhất quán')
        families.append(score)
        fold_counts.add(len(score.folds))
        sources[path.name] = sha256_file(path)
    if not families or len(fold_counts) != 1:
        raise ValueError(f'{run}: thiếu selection hoặc số fold khác nhau')
    with np.load(run / 'predictions/dev.npz', allow_pickle=False) as archive:
        ids = set(archive['recording_ids'].astype(str))
        metadata = json.loads(str(archive['metadata_json'].item()))
    if metadata['split'] != 'dev':
        raise ValueError(f'{run}: predictions không phải dev')
    if metadata['taxonomy_sha256'] != manifest['taxonomy_sha256']:
        raise ValueError(f'{run}: taxonomy prediction khác manifest')
    kept = restrict(dict.fromkeys(ids), eval_set)
    split = pd.read_csv(ROOT / 'data/splits/datased_polyphonic.csv')
    dev = split[split['split'] == 'validation']
    if not set(kept).issubset(set(dev['recording_id'])):
        raise ValueError(f'{run}: có recording ngoài dev')
    groups = dict(zip(dev['recording_id'].astype(str), dev['leakage_group'], strict=True))
    k = next(iter(fold_counts))
    folds = assign_folds(sorted(kept), groups, k)
    if set(folds.values()) != set(range(k)):
        raise ValueError(f'{run}: fold rỗng')
    return {'label': label, 'run': str(run.resolve()), 'manifest': manifest,
            'recordings': sorted(kept), 'fold_assignment': folds,
            'families': {f.family: asdict(f) for f in families},
            'winner': asdict(best_family(tuple(families))), 'sources_sha256': sources}


def delta(candidate: dict, baseline: dict) -> dict:
    diff = candidate['mean'] - baseline['mean']
    return {'mean': diff, 'folds_greater': sum(c > b for c, b in
            zip(candidate['folds'], baseline['folds'], strict=True)),
            'n_folds': len(baseline['folds']), 'baseline_sd': baseline['sd'],
            'warning': 'trong nhiễu fold' if diff < baseline['sd'] else ''}


def compare(baseline: dict, candidates: list[dict]) -> dict:
    labels = [baseline['label'], *(c['label'] for c in candidates)]
    if len(labels) != len(set(labels)):
        raise ValueError('nhãn run phải duy nhất')
    comparisons = {}
    for c in candidates:
        if c['recordings'] != baseline['recordings']:
            raise ValueError(f"{c['label']}: tập recording dev khác baseline")
        if c['fold_assignment'] != baseline['fold_assignment']:
            raise ValueError(f"{c['label']}: phép gán fold khác baseline")
        for key in ('split_sha256', 'taxonomy_sha256', 'data_manifest_sha256'):
            if c['manifest'].get(key) != baseline['manifest'].get(key):
                raise ValueError(f"{c['label']}: {key} khác baseline")
        same = {family: delta(score, baseline['families'][family])
                for family, score in c['families'].items() if family in baseline['families']}
        comparisons[c['label']] = {'same_family': same,
                                   'winner': delta(c['winner'], baseline['winner'])}
    return {'baseline': baseline, 'candidates': candidates, 'comparisons': comparisons}


def render(result: dict) -> str:
    lines = ['# Tầng S — sàng lọc bằng CV dev', '',
             '> Chỉ sàng lọc; không chọn hệ thống cuối hoặc tuyên bố cải thiện. '
             'Họ thắng theo CV mean (hòa giữ θ); ghép fold bằng cùng recording/leakage_group. '
             'Δ < sd baseline ghi trong nhiễu fold. Không đọc test.', '',
             '| Run | Họ | Cấu hình | Mean ± sd | 5 fold | Họ thắng |',
             '|---|---|---|---:|---|:---:|']
    for run in [result['baseline'], *result['candidates']]:
        for family, s in run['families'].items():
            config = s['config'].replace('|', '\\|')
            folds = ', '.join(f'{v:.4f}' for v in s['folds'])
            lines.append(f"| {run['label']} | {family} | `{config}` | "
                         f"{s['mean']:.4f} ± {s['sd']:.4f} | {folds} | "
                         f"{'có' if family == run['winner']['family'] else '—'} |")
    lines += ['', '| Ứng viên | So sánh | Δ mean | Fold cao hơn baseline | Cảnh báo |',
              '|---|---|---:|---:|---|']
    for label, comparison in result['comparisons'].items():
        for family, d in {**comparison['same_family'], 'họ thắng': comparison['winner']}.items():
            lines.append(f"| {label} | {family} | {d['mean']:+.4f} | "
                         f"{d['folds_greater']}/{d['n_folds']} | {d['warning']} |")
    return '\n'.join([*lines, ''])


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', action='append', required=True)
    parser.add_argument('--eval-set', choices=['annotated'], default='annotated')
    parser.add_argument('--label', required=True)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    if not re.fullmatch(r'[\w.-]+', args.label):
        raise ValueError('nhãn output không được chứa đường dẫn')
    git = git_state(ROOT)
    result = {**compare(load_run(args.baseline, args.eval_set),
                        [load_run(c, args.eval_set) for c in args.candidate]),
              'git': git, 'eval_set': args.eval_set}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f'screening_{args.label}_{datetime.now(UTC):%Y%m%d}.json'
    if out.exists() or out.with_suffix('.md').exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    out.with_suffix('.md').write_text(render(result), encoding='utf-8')
    print(render(result))


if __name__ == '__main__':
    main()
