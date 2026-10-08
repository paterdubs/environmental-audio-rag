"""Pool O-F và hồ sơ năng lượng: chỉ mô tả clip train, không tạo nhãn mạnh.

Ngưỡng RMS median + 6 dB là tương đối trong clip, không xác định lớp đang phát.
Tái sử dụng loader mono/resample của D3; không giải nén hoặc sửa audio/annotation.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ml.dataops.datasec_labels import path_labels
from ml.dataops.fingerprint import load_pcm
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 32_000
FRAME_SAMPLES = 640
THRESHOLD_DB = 6.0


def build_pool(inventory: pd.DataFrame, split: pd.DataFrame, members: pd.DataFrame,
               exclusions: pd.DataFrame, taxonomy, source: dict) -> tuple[pd.DataFrame, dict]:
    for frame, name in ((inventory, 'inventory'), (split, 'split'), (members, 'v4')):
        if frame['file_id'].duplicated().any():
            raise ValueError(f'{name}: file_id lặp')
    train = split.loc[split['split'] == 'train', ['file_id', 'leakage_group']]
    selected = train.merge(inventory, on='file_id', validate='one_to_one')
    if len(selected) != len(train):
        raise ValueError('train thiếu inventory')
    selected = selected.merge(members[['file_id', 'sha256']].rename(columns={'sha256': 'v4_sha'}),
                              on='file_id', validate='one_to_one')
    if (selected['sha256'] != selected['v4_sha']).any():
        raise ValueError('v4 khác hash inventory; không tái sử dụng audio v3')
    stages = {'train': len(train), 'train_intersect_v4': len(selected)}
    excluded = set(exclusions.loc[exclusions['file_id'].str.startswith('datasec:'), 'file_id'])
    selected = selected[~selected['file_id'].isin(excluded)].copy()
    stages['after_exclusions'] = len(selected)
    labels = [path_labels(str(p), taxonomy) for p in selected['relative_path']]
    selected['class_id'] = [c for c, _ in labels]
    selected['subclass_id'] = [s for _, s in labels]
    selected = selected[selected['class_id'].isin(taxonomy.polyphonic_class_ids)].copy()
    stages['polyphonic_pool'] = len(selected)
    selected['dataset_version'] = source['version']
    selected['dataset_doi'] = source['doi']
    selected['license'] = source['license']
    selected['license_source'] = source['license_source']
    selected['annotation_type'] = 'clip_tag_only'
    columns = ['file_id', 'class_id', 'subclass_id', 'duration_s', 'relative_path', 'sha256',
               'leakage_group', 'dataset_version', 'dataset_doi', 'license', 'license_source',
               'annotation_type']
    return selected[columns].sort_values('file_id').reset_index(drop=True), stages


def energy_profile(waveform: np.ndarray) -> dict:
    waveform = np.asarray(waveform, dtype=np.float64)
    if waveform.ndim != 1 or not waveform.size or not np.isfinite(waveform).all():
        raise ValueError('cần waveform mono hữu hạn, không rỗng')
    starts = np.arange(0, waveform.size, FRAME_SAMPLES)
    lengths = np.minimum(FRAME_SAMPLES, waveform.size - starts)
    rms = np.sqrt(np.add.reduceat(waveform ** 2, starts) / lengths)
    median = float(np.median(rms))
    threshold = median * 10 ** (THRESHOLD_DB / 20)
    active = rms > threshold
    edges = np.diff(np.pad(active.astype(np.int8), (1, 1)))
    begins, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    duration = waveform.size / SAMPLE_RATE
    onset = offset = longest_on = longest_off = None
    longest = 0.0
    if begins.size:
        on_samples = begins * FRAME_SAMPLES
        off_samples = np.minimum(ends * FRAME_SAMPLES, waveform.size)
        best = int(np.argmax(off_samples - on_samples))
        onset, offset = float(on_samples[0] / SAMPLE_RATE), float(off_samples[-1] / SAMPLE_RATE)
        longest_on = float(on_samples[best] / SAMPLE_RATE)
        longest_off = float(off_samples[best] / SAMPLE_RATE)
        longest = longest_off - longest_on
    return {'decoded_duration_s': duration, 'rms_frames': len(rms), 'rms_median': median,
            'rms_activity_threshold': threshold, 'energy_active_frames': int(active.sum()),
            'energy_active_frame_fraction': float(active.mean()),
            'energy_active_duration_s': float(lengths[active].sum() / SAMPLE_RATE),
            'energy_longest_active_s': longest, 'energy_first_active_s': onset,
            'energy_last_active_s': offset,
            'energy_first_active_fraction': onset / duration if onset is not None else None,
            'energy_last_active_fraction': offset / duration if offset is not None else None,
            'energy_last_to_clip_end_s': duration - offset if offset is not None else None,
            'energy_longest_on_s': longest_on, 'energy_longest_off_s': longest_off}


def profile_file(row: dict, audio_root: Path) -> dict:
    path = (audio_root / row['relative_path']).resolve()
    if not path.is_relative_to(audio_root.resolve()):
        raise ValueError('relative_path ra ngoài audio_root')
    if sha256_file(path) != row['sha256']:
        raise ValueError(f'{path}: hash audio khác inventory/v4')
    profile = energy_profile(load_pcm(path, sample_rate=SAMPLE_RATE))
    if abs(profile['decoded_duration_s'] - row['duration_s']) > 2 / SAMPLE_RATE:
        raise ValueError(f'{path}: duration decode khác inventory')
    return {**row, **profile}


def summarize(pool: pd.DataFrame, profile: dict, class_ids: tuple) -> list[dict]:
    medians = {r['class_id']: r['quantiles']['0.5'] for r in profile['poly_by_class_split']
               if r['split'] == 'train'}
    if set(class_ids) - medians.keys():
        raise ValueError('data_profile thiếu trung vị event train')
    rows = []
    for label in class_ids:
        group = pool[pool['class_id'] == label]
        rows.append({'class_id': label, 'count': len(group),
                     'hours': float(group['duration_s'].sum() / 3600),
                     'median_clip_s': float(group['duration_s'].median()) if len(group) else None,
                     'median_energy_active_fraction': float(
                         group['energy_active_frame_fraction'].median()) if len(group) else None,
                     'median_longest_active_s':
                         float(group['energy_longest_active_s'].median()) if len(group) else None,
                     'zero_active_clips': int((group['energy_active_frames'] == 0).sum()),
                     'datased_train_event_median_s': medians[label],
                     'short_class': medians[label] <= 3.0})
    return rows


def render(result: dict) -> str:
    lines = ['# DataSEC v4 — pool O-F và hồ sơ năng lượng', '',
             '> Chỉ train ∩ v4 − exclusion, giữ 21 lớp polyphonic. Không tạo nhãn mạnh. '
             'RMS 20 ms không chồng lấn, mono 32 kHz; khung cuối dùng số mẫu thật. '
             'Hoạt động khi RMS > median(RMS) × 10^(6/20), tương đương median + 6 dB. '
             'Im lặng không có vùng hoạt động; tie vùng dài nhất lấy vùng đầu.', '',
             '**Giới hạn:** ngưỡng tương đối có thể cho 0 khung ở âm thanh liên tục; '
             'tỷ lệ hoạt động thường ≤ 0,5 theo định nghĩa median. Đây là độ nổi bật năng lượng '
             'trong clip, không phải độ phủ của sự kiện hoặc độ tin cậy nhãn.', '',
             f"Pool: **{result['count']} clip**, **{result['hours']:.4f} giờ**. "
             f"SHA-256 CSV: `{result['pool_sha256']}`.", '',
             '| Lớp | Clip | Giờ | Median clip (s) | Median tỷ lệ RMS hoạt động | '
             'Median vùng dài nhất (s) | Clip không hoạt động | Event train ≤3s |',
             '|---|---:|---:|---:|---:|---:|---:|:---:|']
    for r in result['by_class']:
        values = ['—' if r[k] is None else f'{r[k]:.4f}' for k in
                  ('median_clip_s', 'median_energy_active_fraction', 'median_longest_active_s')]
        lines.append(f"| `{r['class_id']}` | {r['count']} | {r['hours']:.4f} | "
                     + ' | '.join(values) + f" | {r['zero_active_clips']} | "
                     + ('có' if r['short_class'] else '—') + ' |')
    lines += ['', 'Các cột `energy_*` trong CSV chỉ là mô tả năng lượng, không được đưa trực tiếp '
              'vào annotation. Onset/offset RMS là đầu khung/cuối khung (độ phân giải 20 ms); '
              'giá trị trống nghĩa là không có khung vượt ngưỡng. '
              'Clip được kiểm byte SHA-256 với inventory/v4 trước decode.', '']
    return '\n'.join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio-root', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'docs/measurements')
    parser.add_argument('--pool-output', type=Path,
                        default=ROOT / 'data/manifests/datasec_o_f_pool.csv')
    args = parser.parse_args()
    out = args.out_dir / f'datasec_pool_{datetime.now(UTC):%Y%m%d}.json'
    if args.pool_output.exists() or out.exists() or out.with_suffix('.md').exists():
        raise FileExistsError('pool/report đã tồn tại; dùng output khác')
    git = git_state(ROOT)
    paths = [ROOT / p for p in ['data/manifests/datasec_inventory.csv',
             'data/splits/datasec_classification.csv', 'data/manifests/datasec_v4_members.csv',
             'data/manifests/exclusions.csv']]
    profile_path = ROOT / 'docs/measurements/data_profile_20261008_lf.json'
    version_path = ROOT / 'docs/measurements/datasec_v4_diff_20261008_lf.json'
    source = json.loads(version_path.read_text(encoding='utf-8'))['source']
    taxonomy_path = ROOT / 'ml/configs/taxonomy.yaml'
    taxonomy = load_taxonomy(taxonomy_path)
    pool, stages = build_pool(*(pd.read_csv(p) for p in paths), taxonomy, source)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(profile_file, r, args.audio_root) for r in
                   pool.to_dict(orient='records')]
        rows = []
        for i, future in enumerate(futures, 1):
            rows.append(future.result())
            if i % 200 == 0:
                print(f'Đã kiểm/decode {i}/{len(pool)}', flush=True)
    pool = pd.DataFrame(rows)
    by_class = summarize(pool, json.loads(profile_path.read_text(encoding='utf-8')),
                         taxonomy.polyphonic_class_ids)
    args.pool_output.parent.mkdir(parents=True, exist_ok=True)
    pool.to_csv(args.pool_output, index=False, lineterminator='\n')
    result = {'git': git, 'source': source, 'stages': stages, 'count': len(pool),
              'hours': float(pool['duration_s'].sum() / 3600), 'by_class': by_class,
              'audio_root': str(args.audio_root.resolve()), 'sample_rate': SAMPLE_RATE,
              'rms_frame_samples': FRAME_SAMPLES, 'threshold_db_above_median': THRESHOLD_DB,
              'pool_path': str(args.pool_output), 'pool_sha256': sha256_file(args.pool_output),
              'sources_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in
                                 [*paths, profile_path, version_path, taxonomy_path]}}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    out.with_suffix('.md').write_text(render(result), encoding='utf-8')
    print(render(result))


if __name__ == '__main__':
    main()
