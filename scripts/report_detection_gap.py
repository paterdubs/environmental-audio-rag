"""Describe frame/event gaps on annotated dev; per-class thresholds are diagnostic only."""
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import process_recordings
from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID, _best
from ml.postprocessing.events import _median_filter
from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts.report_screening import compare, load_run
from scripts.report_screening_per_class import class_scores, finite, fmt, validate_theta_refit
from scripts.report_sebb_diagnosis import (
    load_dev,
    posterior_summary,
    raster_reference,
    selected_csebb,
)
from scripts.report_tier_s import SELECTIONS, best_frame_map, read, write_report

ROOT = Path(__file__).resolve().parents[1]


def oracle_class(probabilities: dict, reference: dict, cid: str, index: int,
                 prior, rate: float, grid: tuple, global_theta: float) -> dict:
    # Median is independent of θ: cache the exact native filter, retaining train d_min/g_max.
    filtered = {rid: _median_filter(p[:, index], prior.median_w)[:, None]
                for rid, p in probabilities.items()}
    refs = {rid: [e for e in rows if e['event_label'] == cid]
            for rid, rows in reference.items()}
    curves, estimates = {}, {}
    for theta in sorted(set([*grid, global_theta])):
        estimate = process_recordings(filtered, class_ids=(cid,), thresholds={cid: theta},
                                      priors={cid: replace(prior, median_w=1)}, frame_rate=rate)
        score = event_based_f1(refs, estimate, event_label_list=[cid])
        curves[theta] = finite(score['f_measure']['f_measure'])
        estimates[theta] = estimate
    theta, objective = _best([(t, curves[t] if curves[t] is not None else 0.) for t in grid])
    return {'theta': theta, 'objective_nan_as_zero': objective, 'f1': curves[theta],
            'global_theta': global_theta, 'global_f1': curves[global_theta],
            'delta_f1': curves[theta] - curves[global_theta]
            if curves[theta] is not None and curves[global_theta] is not None else None,
            'curve': {f'{t:g}': curves[t] for t in grid},
            'oracle_events': estimates[theta], 'global_events': estimates[global_theta]}


def frame_rows(probabilities: dict, truth: dict, class_ids: tuple, thresholds: dict) -> dict:
    rows = {}
    for index, cid in enumerate(class_ids):
        p = np.concatenate([probabilities[r][:, index] for r in sorted(probabilities)])
        y = np.concatenate([truth[r][:, index] for r in sorted(probabilities)])
        rows[cid] = {'frame_ap': float(average_precision_score(y, p)) if y.any() else None,
                     'n_frames': len(y), 'n_positive_frames': int(y.sum()),
                     'true_positive_frame_fraction': float(y.mean()),
                     'posterior_gt_theta_fraction': float((p > thresholds[cid]).mean()),
                     'theta_global': thresholds[cid]}
    return rows


def event_errors(reference: dict, estimate: dict, class_ids: tuple) -> dict:
    both = event_based_f1(reference, estimate, event_label_list=list(class_ids))
    nref = sum(len(events) for events in reference.values())
    nsys = sum(len(events) for events in estimate.values())
    rates = both['overall']['error_rate']
    counts = {name: int(round(rates[f'{name}_rate'] * nref))
              for name in ('insertion', 'deletion', 'substitution')}
    tp = int(round(both['f_measure']['recall'] * nref))
    if nref != tp + counts['substitution'] + counts['deletion'] or (
            nsys != tp + counts['substitution'] + counts['insertion']):
        raise ValueError('sed_eval error count accounting mismatch')
    output = {'nref': nref, 'nsys': nsys, 'tp': tp, **counts, 'rates': rates}
    for name, onset, offset in [('onset_only', True, False), ('offset_only', False, True)]:
        measured = event_based_f1(reference, estimate, event_label_list=list(class_ids),
                                  evaluate_onset=onset, evaluate_offset=offset)
        output[name] = {'micro_f1': finite(measured['f_measure']['f_measure']),
                        'macro_f1': finite(measured['macro']['f_measure']),
                        'metric_config': measured['config']}
    return output


def theta_context(run: dict, rate: float, digest: str) -> tuple:
    source = Path(run['run']) / 'postproc_cv_annotated.json'
    postproc = read(source)
    theta_run = {**run, 'winner': run['families']['theta']}
    priors = validate_theta_refit(postproc, theta_run, rate, digest)
    if postproc['threshold_mode'] != 'global':
        raise ValueError('diagnostic requires the saved global theta family')
    thresholds = {cid: item['theta'] for cid, item in postproc['per_class'].items()}
    if len(set(thresholds.values())) != 1:
        raise ValueError('saved global thresholds differ by class')
    grid = tuple(postproc['threshold_grid'])
    if grid != DEFAULT_THRESHOLD_GRID:
        raise ValueError('saved threshold grid differs from existing grid')
    return priors, thresholds, grid, source


def diagnose(run: dict) -> dict:
    p, reference, class_ids, rate = load_dev(run)
    path = Path(run['run']) / 'predictions/dev.npz'
    with np.load(path, allow_pickle=False) as archive:
        digest = str(archive['content_sha256'].item())
    priors, thresholds, grid, source = theta_context(run, rate, digest)
    truth = {rid: raster_reference(reference[rid], values.shape, class_ids, rate)
             for rid, values in p.items()}
    rows = frame_rows(p, truth, class_ids, thresholds)
    oracle, global_events = {rid: [] for rid in p}, {rid: [] for rid in p}
    for index, cid in enumerate(class_ids):
        diagnostic = oracle_class(p, reference, cid, index, priors[cid], rate,
                                  grid, thresholds[cid])
        for rid in p:
            oracle[rid].extend(diagnostic['oracle_events'][rid])
            global_events[rid].extend(diagnostic['global_events'][rid])
        rows[cid]['theta_oracle_in_sample'] = {key: value for key, value in diagnostic.items()
                                              if not key.endswith('_events')}
        print(f"{run['label']}: {cid} diagnostic complete", flush=True)
    winner_events = global_events if run['winner']['family'] == 'theta' else selected_csebb(
        p, class_ids, rate, read(Path(run['run']) / 'sebb_cv_selection_annotated.json'))
    winner = class_scores(reference, winner_events, class_ids)
    for cid in class_ids:
        rows[cid]['winning_family_events'] = winner['per_class'][cid]
    return {'screening': run, 'n_recordings': len(p), 'class_ids': class_ids,
            'posterior': posterior_summary(p, reference, class_ids, rate),
            'frame_map_saved': best_frame_map(Path(run['run'])),
            'frame_map_annotated_stacked': float(np.mean([r['frame_ap'] for r in rows.values()
                                                         if r['frame_ap'] is not None])),
            'winner_in_sample': winner, 'theta_global_in_sample': class_scores(
                reference, global_events, class_ids),
            'theta_oracle_in_sample_not_for_selection': class_scores(reference, oracle, class_ids),
            'event_errors_winner': event_errors(reference, winner_events, class_ids),
            'per_class': rows, 'theta_postproc_sha256': sha256_file(source),
            'dev_predictions_sha256': digest, 'dev_predictions_file_sha256': sha256_file(path)}


def render(result: dict) -> str:
    lines = ['# Khoảng cách frame AP và event-F1 — dev annotated', '',
             '> **Chỉ mô tả, in-sample dev**, không chứng minh nhân quả. '
             'Giữ họ/config CV đã lưu. θ per-class là oracle trên cùng dev để đo khoảng cách; '
             '**không dùng để chọn**, không lưu postproc, không đổi A2/S13. Prior từ train, '
             'percentile theo họ θ đã chọn; hòa oracle giữ θ nhỏ nhất, '
             'NaN objective→0 như sweep gốc. '
             'F1 chuẩn sed_eval; macro bỏ NaN, null/— giữ nguyên trong bảng. '
             'AP dùng sigmoid đã gộp cửa sổ, raster floor/ceil hợp GT trên 134 recording; '
             'khác best_validation (window/mask validation) trong metrics.json. '
             'Tỷ lệ p>θ tính posterior thô, khác hậu xử lý dùng median và ≥θ. '
             'Nếu cSEBB thắng, θ là họ θ global đồng hành, không phải λ cSEBB.', '',
             '| Run | mAP metrics | AP macro annotated | Họ | Macro event | Micro event | '
             'Micro θ global | Micro θ oracle | I/D/S | Onset-only micro/macro | '
             'Offset-only micro/macro |', '|---|---:|---:|---|---:|---:|---:|---:|---|---|---|']
    for row in result['runs']:
        w, errors = row['winner_in_sample'], row['event_errors_winner']
        on, off = errors['onset_only'], errors['offset_only']
        lines.append(f"| {row['screening']['label']} | {fmt(row['frame_map_saved']['value'])} | "
                     f"{row['frame_map_annotated_stacked']:.4f} | "
                     f"{row['screening']['winner']['family']} | {fmt(w['macro_f1'])} | "
                     f"{fmt(w['micro_f1'])} | {fmt(row['theta_global_in_sample']['micro_f1'])} | "
                     f"{fmt(row['theta_oracle_in_sample_not_for_selection']['micro_f1'])} | "
                     f"{errors['insertion']}/{errors['deletion']}/{errors['substitution']} | "
                     f"{fmt(on['micro_f1'])}/{fmt(on['macro_f1'])} | "
                     f"{fmt(off['micro_f1'])}/{fmt(off['macro_f1'])} |")
    lines += render_smoothness(result['runs'])
    for row in result['runs']:
        lines += ['', f"## {row['screening']['label']}", '',
                  '| Lớp | Frame AP | F1 họ thắng | Nsys/Nref | p>θ | Frame GT+ | '
                  'θ global | θ oracle | F1 θ global | F1 θ oracle | Δ oracle |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for cid, item in row['per_class'].items():
            oracle, events = item['theta_oracle_in_sample'], item['winning_family_events']
            lines.append(f"| {cid} | {fmt(item['frame_ap'])} | {fmt(events['f1'])} | "
                         f"{events['nsys']}/{events['nref']} | "
                         f"{item['posterior_gt_theta_fraction']:.4f} | "
                         f"{item['true_positive_frame_fraction']:.4f} | "
                         f"{oracle['global_theta']:g} | {oracle['theta']:g} | "
                         f"{fmt(oracle['global_f1'])} | {fmt(oracle['f1'])} | "
                         f"{fmt(oracle['delta_f1'], True)} |")
    lines += ['', '## Đang chờ', '']
    lines += [f"- `{item['run']}`: thiếu {', '.join(item['missing'])}."
              for item in result['pending']] or ['Không có.']
    lines += ['', 'I/D/S là số sed_eval error-rate × Nref: substitution ghép sai lớp nhưng '
              'khớp collar; không phải mọi confusion theo overlap. Lỗi biên có thể thành I+D. '
              '**Giả thuyết:** frame AP cao hơn có thể cùng tồn tại với biên chưa khớp collar '
              'hoặc operating point chưa phù hợp; các bảng này không tách được tác động nhân quả.']
    return '\n'.join([*lines, ''])


def render_smoothness(rows: list[dict]) -> list[str]:
    lines = ['', '## Độ mượt posterior (cùng phép đo XO-17)', '',
             '| Run | Mean / median / IQR của \\|Δp\\| | Median / IQR đoạn >0.5 mỗi recording |',
             '|---|---:|---:|']
    for row in rows:
        p = row['posterior']
        d, s = p['abs_adjacent_delta'], p['segments_per_recording']
        lines.append(f"| {row['screening']['label']} | "
                     f"{fmt(d['mean'])} / {fmt(d['median'])} / {fmt(d['iqr'])} | "
                     f"{fmt(s['median'])} / {fmt(s['iqr'])} |")
    lines += ['', '|Δp| chỉ giữa frame liền kề **trong cùng recording**, gộp mọi lớp/frame. '
              'Đoạn dùng strict p>0.5, đếm riêng từng lớp rồi cộng trong mỗi recording; '
              'không nối qua biên recording. Quantile và từng recording trong JSON. '
              '**Giả thuyết:** độ mượt có thể tương tác với hậu xử lý/biên; '
              'các thống kê này không chứng minh nguyên nhân.']
    return lines


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True, help='label=absolute run path')
    parser.add_argument('--stamp', default='20261009')
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    runs, pending = [], []
    for spec in args.run:
        label, sep, raw = spec.partition('=')
        if not sep or not label:
            raise ValueError('requires label=run')
        folder = Path(raw)
        missing = [name for name in [*SELECTIONS, 'postproc_cv_annotated.json']
                   if not (folder / name).is_file()]
        if missing or not read(folder / 'manifest.json').get('complete'):
            pending.append({'run': str(folder.resolve()), 'missing': missing})
        else:
            runs.append(load_run(spec))
    if not runs:
        raise ValueError('no complete annotated-dev runs')
    compare(runs[0], runs[1:])
    result = {'split': 'dev', 'eval_set': 'annotated', 'in_sample': True,
              'not_for_selection': True, 'git': git_state(ROOT),
              'annotations_sha256': sha256_file(
                  ROOT / 'data/annotations/datased_polyphonic_events.csv'),
              'runs': [diagnose(run) for run in runs], 'pending': pending}
    print(write_report(result, 'detection_gap', args.stamp, args.out_dir, render))


if __name__ == '__main__':
    main()
