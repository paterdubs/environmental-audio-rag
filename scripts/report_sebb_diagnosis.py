"""Describe cSEBB behavior on annotated dev without changing selection rules."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.coverage import restrict
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_counts_per_recording
from ml.postprocessing.calibration import stack_predictions_by_recording
from ml.postprocessing.sebb import SebbParams, sebb_candidates, select_boxes
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file
from scripts.report_screening import compare, load_run
from scripts.sweep_threshold import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]
QUANTILES = (0., .01, .05, .25, .5, .75, .95, .99, 1.)


def distribution(values: np.ndarray) -> dict:
    values = np.asarray(values).reshape(-1)
    if not len(values):
        return {'n': 0, 'mean': None, 'median': None, 'iqr': None, 'quantiles': {}}
    q = np.quantile(values, QUANTILES)
    return {'n': len(values), 'mean': float(np.mean(values)), 'median': float(q[4]),
            'iqr': float(q[5] - q[3]),
            'quantiles': {f'{p:g}': float(v) for p, v in zip(QUANTILES, q, strict=True)}}


def raster_reference(events: list[dict], shape: tuple, class_ids: tuple,
                     frame_rate: float) -> np.ndarray:
    target = np.zeros(shape, dtype=bool)
    for event in events:
        index = class_ids.index(event['event_label'])
        start = max(0, min(shape[0], math.floor(event['onset'] * frame_rate)))
        stop = max(0, min(shape[0], math.ceil(event['offset'] * frame_rate)))
        target[start:stop, index] = True
    return target


def threshold_runs(probabilities: np.ndarray) -> np.ndarray:
    active = probabilities > .5
    starts = active & ~np.concatenate([np.zeros_like(active[:1]), active[:-1]])
    return starts.sum(axis=0)


def posterior_summary(probabilities: dict, reference: dict, class_ids: tuple,
                      frame_rate: float) -> dict:
    positive, negative, differences, recordings = [], [], [], {}
    for rid, p in sorted(probabilities.items()):
        target = raster_reference(reference[rid], p.shape, class_ids, frame_rate)
        positive.append(p[target])
        negative.append(p[~target])
        differences.append(np.abs(np.diff(p, axis=0)).reshape(-1))
        runs = threshold_runs(p)
        recordings[rid] = {'frames': len(p), 'segments_over_0_5': int(runs.sum()),
                           'segments_by_class': dict(zip(class_ids, map(int, runs), strict=True)),
                           'mean_abs_delta': float(np.abs(np.diff(p, axis=0)).mean())
                           if len(p) > 1 else None}
    return {'positive': distribution(np.concatenate(positive)),
            'negative': distribution(np.concatenate(negative)),
            'abs_adjacent_delta': distribution(np.concatenate(differences)),
            'segments_per_recording': distribution(np.array(
                [r['segments_over_0_5'] for r in recordings.values()])),
            'recordings': recordings}


def matching_pairs(reference: list[dict], estimate: list[dict]) -> list[tuple[int, int]]:
    """Use sed_eval's validators and optimal bipartite matcher, including tie order."""
    from sed_eval.sound_event import EventBasedMetrics
    from sed_eval.util import bipartite_match

    graph = {}
    for j, ref in enumerate(reference):
        for i, est in enumerate(estimate):
            if (ref['event_label'] == est['event_label']
                    and EventBasedMetrics.validate_onset(ref, est, t_collar=.2)
                    and EventBasedMetrics.validate_offset(ref, est, t_collar=.2,
                                                          percentage_of_length=.2)):
                graph.setdefault(i, []).append(j)
    return sorted(bipartite_match(graph).items())


def overlap_degrees(reference: list[dict], estimate: list[dict]) -> tuple[int, int]:
    """Geometric many-to-one/one-to-many indicators; not proof of algorithmic merges."""
    ref_degree, est_degree = np.zeros(len(reference)), np.zeros(len(estimate))
    for j, ref in enumerate(reference):
        for i, est in enumerate(estimate):
            if (ref['event_label'] == est['event_label']
                    and min(ref['offset'], est['offset']) > max(ref['onset'], est['onset'])):
                ref_degree[j] += 1
                est_degree[i] += 1
    return int((est_degree >= 2).sum()), int((ref_degree >= 2).sum())


def event_diagnostics(reference: dict, estimate: dict, class_ids: tuple) -> dict:
    counts = event_counts_per_recording(reference, estimate, event_label_list=list(class_ids))
    onset, offset, records, pairs = [], [], {}, []
    for rid in sorted(reference):
        refs, ests = reference[rid], estimate[rid]
        matches = matching_pairs(refs, ests)
        assert len(matches) == counts[rid][2], 'diagnostic pairing differs from sed_eval'
        merged, split = overlap_degrees(refs, ests)
        records[rid] = {'nref': counts[rid][0], 'nsys': counts[rid][1],
                        'tp': counts[rid][2], 'merged_system_events': merged,
                        'split_reference_events': split}
        for j, i in matches:
            on, off = ests[i]['onset'] - refs[j]['onset'], ests[i]['offset'] - refs[j]['offset']
            onset.append(on)
            offset.append(off)
            pairs.append({'recording_id': rid, 'class_id': refs[j]['event_label'],
                          'reference_index': j, 'system_index': i,
                          'onset_error_s': on, 'offset_error_s': off})
    nref, nsys, tp = map(int, np.sum(list(counts.values()), axis=0))
    return {'nref': nref, 'nsys': nsys, 'tp': tp, 'nsys_over_nref': nsys/nref if nref else None,
            'micro_f1': 2*tp/(nref+nsys) if nref+nsys else None,
            'onset_error_s': distribution(np.array(onset)),
            'offset_error_s': distribution(np.array(offset)),
            'absolute_onset_error_s': distribution(np.abs(onset)),
            'absolute_offset_error_s': distribution(np.abs(offset)),
            'merged_system_events': sum(r['merged_system_events'] for r in records.values()),
            'split_reference_events': sum(r['split_reference_events'] for r in records.values()),
            'recordings': records, 'matched_pairs': pairs}


def load_dev(run: dict) -> tuple[dict, dict, tuple, float]:
    taxonomy = load_taxonomy(ROOT / 'ml/configs/taxonomy.yaml')
    artifact = load_predictions(Path(run['run']) / 'predictions/dev.npz',
                                expected_class_ids=taxonomy.polyphonic_class_ids)
    if artifact.split != 'dev' or artifact.taxonomy_sha256 != taxonomy.checksum:
        raise ValueError('prediction split/taxonomy mismatch')
    split = pd.read_csv(ROOT / 'data/splits/datased_polyphonic.csv')
    expected = restrict(dict.fromkeys(split.loc[split['split'] == 'validation',
                                               'recording_id'].astype(str)), 'annotated')
    if set(run['recordings']) != set(expected):
        raise ValueError('requires the complete annotated dev recording set')
    stacked = stack_predictions_by_recording(artifact)
    probabilities = {rid: stacked[rid] for rid in run['recordings']}
    return (probabilities, load_events_by_recording(set(probabilities)),
            taxonomy.polyphonic_class_ids, 1 / artifact.frame_hop_s)


def selected_csebb(probabilities: dict, class_ids: tuple, frame_rate: float,
                   selection: dict) -> dict:
    chosen = selection['selected']
    params = SebbParams(**{key: chosen[key] for key in
                          ('step_filter_s', 'merge_abs', 'merge_rel')})
    if params.label != chosen['config'] or chosen['threshold'] != selection['cv'][
            params.label]['lambda_full_dev']:
        raise ValueError('selected cSEBB params/refit threshold mismatch')
    boxes = sebb_candidates(probabilities, class_ids=class_ids,
                            frame_rate=frame_rate, params=params)
    return select_boxes(boxes, chosen['threshold'])


def diagnose(run: dict) -> dict:
    probabilities, reference, class_ids, rate = load_dev(run)
    path = Path(run['run']) / 'sebb_cv_selection_annotated.json'
    selection = json.loads(path.read_text('utf-8'))
    if len(selection['cv']) != 30:
        raise ValueError('expected complete 30-config cSEBB grid')
    print(f"{run['label']}: posterior, {len(probabilities)} recordings", flush=True)
    posterior = posterior_summary(probabilities, reference, class_ids, rate)
    estimate = selected_csebb(probabilities, class_ids, rate, selection)
    events = event_diagnostics(reference, estimate, class_ids)
    expected = selection['cv'][selection['selected']['config']]['f1_full_dev_in_sample']
    if not math.isclose(events['micro_f1'], expected, abs_tol=1e-12):
        raise ValueError('reconstructed cSEBB F1 differs from selection full-dev F1')
    return {'screening': run, 'frame_rate': rate, 'class_ids': class_ids,
            'posterior': posterior, 'selected': selection['selected'],
            'events': events, 'cv_grid': selection['cv'],
            'dev_predictions_sha256': sha256_file(Path(run['run']) / 'predictions/dev.npz')}


def format_stat(stat: dict) -> str:
    return '—' if not stat['n'] else f"{stat['median']:.6g} / {stat['iqr']:.6g}"


def render(result: dict) -> str:
    lines = ['# Chẩn đoán cSEBB O-C so T2b', '',
             '> Chỉ dev annotated, in-sample: λ refit toàn dev của cấu hình đã chọn bằng CV. '
             'Không đổi luật chọn. Phân vị gộp frame×class (không cân bằng recording/lớp); '
             'frame dương = union GT raster floor(onset)/ceil(offset), frame âm = phần bù. '
             '|Δp| chỉ trong recording đã gộp cửa sổ, không nối recording. '
             'Đoạn vượt 0.5 tính riêng từng lớp rồi cộng.', '',
             '| Run | CV θ | CV cSEBB | Nsys/Nref | TP | F1 toàn dev | Gộp / tách hình học |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for label, r in result['runs'].items():
        e, f = r['events'], r['screening']['families']
        lines.append(f"| {label} | {f['theta']['mean']:.4f} | {f['csebb']['mean']:.4f} | "
                     f"{e['nsys']}/{e['nref']} | {e['tp']} | {e['micro_f1']:.4f} | "
                     f"{e['merged_system_events']} / {e['split_reference_events']} |")
    lines += ['', '| Run | Posterior dương median / IQR | Âm median / IQR | '
              'abs Δp median / IQR | Đoạn/recording median / IQR |',
              '|---|---:|---:|---:|---:|']
    for label, r in result['runs'].items():
        p = r['posterior']
        stats = [p[k] for k in ('positive', 'negative', 'abs_adjacent_delta',
                               'segments_per_recording')]
        lines.append(f"| {label} | " + ' | '.join(map(format_stat, stats)) + ' |')
    lines += ['', '| Run | Lỗi onset signed median / IQR (s) | Offset signed median / IQR (s) |',
              '|---|---:|---:|']
    for label, r in result['runs'].items():
        lines.append(f"| {label} | {format_stat(r['events']['onset_error_s'])} | "
                     f"{format_stat(r['events']['offset_error_s'])} |")
    return '\n'.join([*lines, *render_quantiles(result), *render_grid(result),
                      '', *result['notes'], ''])


def render_quantiles(result: dict) -> list[str]:
    lines = ['', '## Phân vị posterior và abs Δp (gộp frame×class)', '',
             '| Run | Đại lượng | ' + ' | '.join(f'q{p:g}' for p in QUANTILES) + ' |',
             '|---|---|' + '---:|' * len(QUANTILES)]
    for label, run in result['runs'].items():
        for key in ('positive', 'negative', 'abs_adjacent_delta'):
            q = run['posterior'][key]['quantiles']
            lines.append(f'| {label} | {key} | ' +
                         ' | '.join(f'{q[f"{p:g}"]:.6g}' for p in QUANTILES) + ' |')
    return lines


def render_grid(result: dict) -> list[str]:
    lines = ['', '## Đủ 30 cấu hình mỗi run', '',
             '| Run | Cấu hình | CV mean ± sd | λ full dev | F1 full dev | λ theo fold |',
             '|---|---|---:|---:|---:|---|']
    for label, r in result['runs'].items():
        for config, row in sorted(r['cv_grid'].items()):
            lines.append(f"| {label} | {config} | {row['mean']:.4f} ± {row['sd']:.4f} | "
                         f"{row['lambda_full_dev']:g} | {row['f1_full_dev_in_sample']:.4f} | "
                         f"{', '.join(map(str, row['lambda_by_fold']))} |")
    return lines


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--label', default='oc')
    parser.add_argument('--stamp', default='20261008')
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    args = parser.parse_args()
    if not re.fullmatch(r'[\w.-]+', args.label) or not re.fullmatch(r'\d{8}', args.stamp):
        raise ValueError('invalid label/stamp')
    base, candidate = load_run(args.baseline), load_run(args.candidate)
    comparison = compare(base, [candidate])
    output = args.out_dir / f'sebb_diagnosis_{args.label}_{args.stamp}.json'
    if output.exists() or output.with_suffix('.md').exists():
        raise FileExistsError(output)
    result = {'eval_set': 'annotated', 'split': 'dev', 'in_sample': True,
              'git': git_state(ROOT), 'comparison': comparison,
              'annotations_sha256': sha256_file(
                  ROOT / 'data/annotations/datased_polyphonic_events.csv'),
              'runs': {r['label']: diagnose(r) for r in (base, candidate)},
              'notes': ['Gộp = số event dự đoán overlap thời gian dương với ≥2 GT cùng lớp; '
                        'tách = số GT overlap ≥2 dự đoán cùng lớp. Đây là chỉ báo hình học, '
                        'không chứng minh cSEBB thật sự gộp/tách; '
                        'overlap nhỏ và GT chồng nhau có thể góp số.',
                        'Lỗi biên chỉ trên TP theo collar sed_eval 0.2s/20%; thiên lệch về event '
                        'đã khớp. Ghép tối ưu có thể có nhiều nghiệm; dùng thứ tự của sed_eval.',
                        'Giả thuyết cần kiểm thêm: posterior hoặc độ mượt khác nhau có thể '
                        'tương tác với step-filter/gộp cSEBB. '
                        'Các thống kê mô tả không chứng minh quan hệ nhân quả.']}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), 'utf-8')
    output.with_suffix('.md').write_text(render(result), 'utf-8')
    print(output)


if __name__ == '__main__':
    main()
