"""Reconstruct the CV-winning family's full-dev events for in-sample diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import derive_duration_priors, priors_from_postproc, process_recordings
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file
from scripts.report_screening import compare, load_run
from scripts.report_sebb_diagnosis import load_dev, selected_csebb
from scripts.sweep_threshold import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]


def finite(value: float) -> float | None:
    return float(value) if math.isfinite(value) else None


def class_scores(reference: dict, estimate: dict, class_ids: tuple) -> dict:
    metric = event_based_f1(reference, estimate, event_label_list=list(class_ids))
    rows = {}
    for cid in class_ids:
        row = metric['per_class'][cid]
        rows[cid] = {'f1': finite(row['f_measure']['f_measure']),
                     'nsys': int(row['count']['Nsys']), 'nref': int(row['count']['Nref'])}
    return {'per_class': rows, 'micro_f1': finite(metric['f_measure']['f_measure']),
            'macro_f1': finite(metric['macro']['f_measure']), 'metric_config': metric['config']}


def validate_theta_refit(postproc: dict, run: dict, rate: float, digest: str) -> dict:
    taxonomy = load_taxonomy(ROOT / 'ml/configs/taxonomy.yaml')
    class_ids = taxonomy.polyphonic_class_ids
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    mode, percentile = run['winner']['config'].split('|')
    if mode != postproc['threshold_mode']:
        raise ValueError('saved theta threshold mode differs from winning configuration')
    for key in ('taxonomy_sha256', 'split_sha256', 'data_manifest_sha256'):
        if postproc[key] != run['manifest'][key]:
            raise ValueError(f'theta provenance mismatch: {key}')
    if postproc['dev_predictions_sha256'] != digest:
        raise ValueError('saved theta belongs to different dev predictions')
    split = pd.read_csv(ROOT / 'data/splits/datased_polyphonic.csv')
    ids = set(split.loc[split['split'] == 'train', 'recording_id'].astype(str))
    expected = derive_duration_priors(load_events_by_recording(ids), class_ids=class_ids,
                                     frame_rate=rate, source_split='train', taxonomy=taxonomy,
                                     g_max_percentile=float(percentile))
    priors = priors_from_postproc(postproc, class_ids)
    for cid in class_ids:
        actual, want = priors[cid], expected[cid]
        if (actual.median_w != want.median_w or actual.n_events != want.n_events
                or not math.isclose(actual.d_min_s, want.d_min_s, abs_tol=1e-12)
                or not math.isclose(actual.g_max_s, want.g_max_s, abs_tol=1e-12)):
            raise ValueError(f'saved priors differ from winning percentile: {cid}')
    return priors


def reconstruct(run: dict) -> dict:
    probabilities, reference, class_ids, rate = load_dev(run)
    folder = Path(run['run'])
    prediction_path = folder / 'predictions/dev.npz'
    file_digest = sha256_file(prediction_path)
    # load_dev/load_predictions đã kiểm digest nội dung; đây không phải SHA của ZIP/NPZ.
    with np.load(prediction_path, allow_pickle=False) as archive:
        digest = str(archive['content_sha256'].item())
    if run['winner']['family'] == 'csebb':
        source = folder / 'sebb_cv_selection_annotated.json'
        selection = json.loads(source.read_text('utf-8'))
        estimate = selected_csebb(probabilities, class_ids, rate, selection)
    else:
        source = folder / 'postproc_cv_annotated.json'
        postproc = json.loads(source.read_text('utf-8'))
        priors = validate_theta_refit(postproc, run, rate, digest)
        thresholds = {cid: postproc['per_class'][cid]['theta'] for cid in class_ids}
        estimate = process_recordings(probabilities, class_ids=class_ids, thresholds=thresholds,
                                      priors=priors, frame_rate=rate)
    print(f"{run['label']}: {run['winner']['family']}, {len(reference)} annotated dev", flush=True)
    return {'screening': run, 'class_ids': class_ids, 'frame_rate': rate,
            'postproc_source': str(source), 'postproc_sha256': sha256_file(source),
            'dev_predictions_sha256': digest, 'dev_predictions_file_sha256': file_digest,
            **class_scores(reference, estimate, class_ids)}


def per_class_deltas(baseline: dict, candidate: dict) -> dict:
    if tuple(baseline) != tuple(candidate):
        raise ValueError('class order differs')
    output = {}
    for cid, base in baseline.items():
        row = candidate[cid]
        if base['nref'] != row['nref']:
            raise ValueError(f'reference count differs: {cid}')
        output[cid] = {key: row[key] - base[key]
                       if row[key] is not None and base[key] is not None else None
                       for key in ('f1', 'nsys', 'nref')}
    return output


def fmt(value: float | None, signed: bool = False) -> str:
    if value is None:
        return '—'
    return f'{value:+.4f}' if signed else f'{value:.4f}'


def render(result: dict) -> str:
    base = result['baseline']
    lines = ['# Tầng S — per-class trên toàn dev', '',
             '> **In-sample dev annotated**, không phải CV/OOF/test: họ/cấu hình chọn bằng '
             'CV mean đã lưu, θ/λ refit trên toàn dev. Không quét hoặc chọn lại. '
             'F1 onset+offset collar0.2s/20% qua sed_eval; null/— khi không xác định, '
             'kể cả lớp có GT nhưng Nsys=0; không tự quy về0. Macro dùng nanmean của '
             'sed_eval, bỏ lớp NaN. Δ=ứng viên−baseline, không có kiểm định ý nghĩa thống kê.', '',
             '| Run | Họ thắng CV | Cấu hình | CV mean | Micro full dev | Macro full dev |',
             '|---|---|---|---:|---:|---:|']
    for run in [base, *result['candidates']]:
        s, w = run['screening'], run['screening']['winner']
        config = w['config'].replace('|', '\\|')
        lines.append(f"| {s['label']} | {w['family']} | {config} | {w['mean']:.4f} | "
                     f"{fmt(run['micro_f1'])} | {fmt(run['macro_f1'])} |")
    for run in result['candidates']:
        label = run['screening']['label']
        changed = base['screening']['winner']['family'] != run['screening']['winner']['family']
        lines += ['', f'## {label} so {base["screening"]["label"]}', '',
                  'Cảnh báo đổi họ thắng.' if changed else 'Cùng họ thắng.', '',
                  '| Lớp | F1 baseline | Nsys/Nref baseline | F1 ứng viên | '
                  'Nsys/Nref ứng viên | ΔF1 | ΔNsys | ΔNref |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|']
        for cid in base['class_ids']:
            b, c, d = base['per_class'][cid], run['per_class'][cid], result['deltas'][label][cid]
            lines.append(f"| {cid} | {fmt(b['f1'])} | {b['nsys']}/{b['nref']} | "
                         f"{fmt(c['f1'])} | {c['nsys']}/{c['nref']} | {fmt(d['f1'], True)} | "
                         f"{d['nsys']:+d} | {d['nref']:+d} |")
    return '\n'.join([*lines, ''])


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', action='append', required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--stamp', default='20261008')
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    if not re.fullmatch(r'[\w.-]+', args.label) or not re.fullmatch(r'\d{8}', args.stamp):
        raise ValueError('invalid label/stamp')
    base, candidates = load_run(args.baseline), [load_run(c) for c in args.candidate]
    comparison = compare(base, candidates)
    if any(set(r['families']) != {'theta', 'csebb'} for r in [base, *candidates]):
        raise ValueError('requires both annotated selection families')
    out = args.out_dir / f'screening_per_class_{args.label}_{args.stamp}.json'
    if out.exists() or out.with_suffix('.md').exists():
        raise FileExistsError(out)
    baseline, reconstructed = reconstruct(base), [reconstruct(c) for c in candidates]
    result = {'split': 'dev', 'eval_set': 'annotated', 'in_sample': True, 'git': git_state(ROOT),
              'annotations_sha256': sha256_file(
                  ROOT / 'data/annotations/datased_polyphonic_events.csv'),
              'comparison': comparison, 'baseline': baseline, 'candidates': reconstructed,
              'deltas': {c['screening']['label']: per_class_deltas(baseline['per_class'],
                                                                 c['per_class'])
                         for c in reconstructed}}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), 'utf-8')
    out.with_suffix('.md').write_text(render(result), 'utf-8')
    print(out)


if __name__ == '__main__':
    main()
