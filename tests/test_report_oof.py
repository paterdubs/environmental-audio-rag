"""OOF fixtures: held-out fitting, paired resampling and standard macro semantics."""

import numpy as np
import pytest

from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing.events import DurationPrior
from ml.taxonomy import load_taxonomy
from scripts import report_oof as report


def system(counts):
    return {'counts': counts, 'micro_f1': report.micro_f1(
        *(sum(c[i] for c in counts.values()) for i in range(3)))}


def test_paired_bootstrap_better_and_identical():
    base = system({f'r{i}': (2, 1, 1) for i in range(12)})
    good = system({f'r{i}': (2, 2, 2) for i in range(12)})
    result = report.compare({'B0': base, 'good': good, 'same': base}, 'B0')
    assert result['differences']['good']['lower'] > 0
    assert result['differences']['good']['passes_adr0041']
    assert result['selected'] == 'good'
    assert result['differences']['same'] == {
        'estimate': 0, 'lower': 0, 'upper': 0, 'passes_adr0041': False}
    assert report.compare({'B0': base, 'same': base}, 'B0')['selected'] == 'B0'


@pytest.mark.parametrize('other', [system({'different': (1, 1, 1)}),
                                 system({'r': (2, 1, 1)}),
                                 {**system({'r': (1, 1, 1)}), 'folds': {'r': 2}},
                                 {**system({'r': (1, 1, 1)}),
                                  'manifest': {'taxonomy_sha256': 'different'}}])
def test_refuse_unpaired_context(other):
    with pytest.raises(ValueError):
        report.compare({'B0': system({'r': (1, 1, 1)}), 'other': other}, 'B0')


def context():
    taxonomy = load_taxonomy(report.ROOT / 'ml/configs/taxonomy.yaml')
    classes = taxonomy.polyphonic_class_ids
    probabilities = {}
    for i in range(3):
        p = np.zeros((100, len(classes)))
        p[20:70, 0] = 0.9
        probabilities[f'r{i}'] = p
    reference = {r: [{'event_label': classes[0], 'onset': 0.8, 'offset': 2.8}]
                 for r in probabilities}
    return {'taxonomy': taxonomy, 'class_ids': classes, 'frame_rate': 25,
            'probabilities': probabilities, 'reference': reference,
            'recordings': sorted(probabilities), 'folds': {f'r{i}': i for i in range(3)},
            'priors_by_p': {25.: {c: DurationPrior(1, 0, 0, 1) for c in classes}}}


def test_theta_refits_without_held_recordings(monkeypatch):
    ctx = context()
    seen = []
    original = report.theta_cv.fit

    def checked(mode, predictions, reference, *args):
        seen.append(set(predictions))
        assert set(predictions) == set(reference)
        return original(mode, predictions, reference, *args)

    monkeypatch.setattr(report.theta_cv, 'fit', checked)
    events, fits = report.theta_events(ctx, 'global|25')
    assert len(seen) == 3
    for fit, ids in zip(fits, seen, strict=True):
        assert ids.isdisjoint(fit['held_ids'])
        assert ids | set(fit['held_ids']) == set(ctx['probabilities'])
    result = report.summarize(ctx['reference'], events, ctx['class_ids'])
    assert result['micro_f1'] == 1
    metric = event_based_f1(ctx['reference'], events, event_label_list=list(ctx['class_ids']))
    assert result['macro_f1'] == metric['macro']['f_measure']
    assert sum(c[2] for c in result['per_class_counts'][ctx['class_ids'][0]].values()) == 3


def test_csebb_refits_lambda_without_using_full_dev_threshold(monkeypatch):
    ctx = context()
    table = np.zeros((len(report.sebb_cv.LAMBDAS), 3, 3), dtype=int)
    table[:, :, :2] = 1
    # Một lambda riêng thắng trên từng recording: fit chỉ được nhìn hai recording khác.
    for i in range(3):
        table[i, i, 2] = 1
    monkeypatch.setattr(report.sebb_cv, 'count_table', lambda *args: table)
    selected = {'step_filter_s': .32, 'merge_abs': .2, 'merge_rel': None, 'threshold': .95}
    events, fits = report.sebb_events(ctx, selected)
    assert set(events) == set(ctx['reference'])
    for fit in fits:
        held = fit['fold']
        expected_index = next(i for i in range(3) if i != held)
        assert fit['threshold'] == report.sebb_cv.LAMBDAS[expected_index]
        assert set(fit['fit_ids']).isdisjoint(fit['held_ids'])


def test_reject_non_oof_manifest(tmp_path):
    (tmp_path / 'manifest.json').write_text('{"task": "sed_rewindow", "complete": true}')
    with pytest.raises(ValueError, match='sed_oof'):
        report.load_system(tmp_path)
