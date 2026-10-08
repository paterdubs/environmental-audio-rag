"""Synthetic WAV and metadata fixtures, no real dataset access."""

import numpy as np
import pandas as pd
import pytest
import soundfile as sf

from ml.taxonomy import load_taxonomy
from scripts import report_datasec_pool as report


def test_synthetic_wav_activity_and_gain_invariance(tmp_path):
    sample_rate = report.SAMPLE_RATE
    waveform = np.zeros(sample_rate)
    waveform[6400:12800] = .4 * np.sin(2 * np.pi * 1000 * np.arange(6400) / sample_rate)
    path = tmp_path / 'burst.wav'
    sf.write(path, waveform, sample_rate, subtype='FLOAT')
    row = {'relative_path': path.name, 'sha256': report.sha256_file(path), 'duration_s': 1.}
    result = report.profile_file(row, tmp_path)
    assert result['rms_frames'] == 50
    assert result['energy_active_frames'] == 10
    assert result['energy_active_frame_fraction'] == .2
    assert result['energy_first_active_s'] == .2
    assert result['energy_last_active_s'] == .4
    assert result['energy_longest_active_s'] == .2
    assert result['energy_last_to_clip_end_s'] == .6
    assert report.energy_profile(waveform / 10)['energy_active_frame_fraction'] == .2


def test_silence_constant_and_partial_tail():
    for waveform in (np.zeros(640), np.ones(640)):
        result = report.energy_profile(waveform)
        assert result['energy_active_frames'] == 0
        assert result['energy_first_active_s'] is None
        assert result['energy_longest_active_s'] == 0
    waveform = np.r_[np.zeros(4 * 640), np.ones(320)]
    result = report.energy_profile(waveform)
    assert result['rms_frames'] == 5
    assert result['energy_active_duration_s'] == .01
    assert result['energy_last_active_s'] == len(waveform) / report.SAMPLE_RATE


@pytest.mark.parametrize('waveform', [[], [[1]], [float('nan')]])
def test_bad_waveform(waveform):
    with pytest.raises(ValueError):
        report.energy_profile(np.array(waveform))


def test_pool_intersection_exclusion_wind_and_hash_validation():
    taxonomy = load_taxonomy(report.ROOT / 'ml/configs/taxonomy.yaml')
    paths = ['DATASEC/Bells/Bells-0001.wav', 'DATASEC/Bells/Bells-0002.wav',
             'DATASEC/Bells/Bells-0003.wav', 'DATASEC/Wind turbine/Wind-0001.wav',
             'DATASEC/Bells/Bells-0004.wav']
    ids = [f'datasec:{p}' for p in paths]
    inventory = pd.DataFrame({'file_id': ids, 'relative_path': paths,
                              'duration_s': [1.] * 5, 'sha256': ['a'] * 5})
    split = pd.DataFrame({'file_id': ids, 'leakage_group': ids,
                          'split': ['train'] * 4 + ['validation']})
    members = inventory.loc[[0, 1, 3, 4], ['file_id', 'sha256']].copy()
    exclusions = pd.DataFrame({'file_id': [ids[1], 'datased:any']})
    source = {'version': 'v4', 'doi': 'doi', 'license': 'cc-by-nc-sa-4.0',
              'license_source': 'Zenodo record'}
    pool, stages = report.build_pool(inventory, split, members, exclusions, taxonomy, source)
    assert list(pool['file_id']) == [ids[0]]
    assert stages == {'train': 4, 'train_intersect_v4': 3, 'after_exclusions': 2,
                      'polyphonic_pool': 1}
    assert pool.iloc[0]['annotation_type'] == 'clip_tag_only'
    members.loc[0, 'sha256'] = 'b'
    with pytest.raises(ValueError, match='khác hash'):
        report.build_pool(inventory, split, members, exclusions, taxonomy, source)


def test_audio_hash_guard_and_path_escape(tmp_path):
    path = tmp_path / 'test.wav'
    sf.write(path, np.zeros(640), 32000)
    with pytest.raises(ValueError, match='hash audio'):
        report.profile_file({'relative_path': path.name, 'sha256': 'bad'}, tmp_path)
    with pytest.raises(ValueError, match='ra ngoài'):
        report.profile_file({'relative_path': '../outside.wav'}, tmp_path)


def test_short_flag_uses_only_train_profile():
    columns = ['class_id', 'duration_s', 'energy_active_frame_fraction',
               'energy_longest_active_s', 'energy_active_frames']
    pool = pd.DataFrame([['bells', 1, .2, .2, 1]], columns=columns)
    profile = {'poly_by_class_split': [
        {'class_id': 'bells', 'split': 'train', 'quantiles': {'0.5': 3}},
        {'class_id': 'bells', 'split': 'validation', 'quantiles': {'0.5': 99}}]}
    row = report.summarize(pool, profile, ('bells',))[0]
    assert row['short_class']
    assert row['datased_train_event_median_s'] == 3
