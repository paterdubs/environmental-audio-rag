import json
from pathlib import Path

import numpy as np
import pytest
from jsonschema import Draft202012Validator

from ml.evaluation.predictions import PredictionArtifact
from ml.postprocessing import (
    DurationPrior,
    build_postproc_artifact,
    derive_duration_priors,
    probabilities_to_events,
    stack_predictions_by_recording,
    sweep_global_threshold,
    sweep_per_class_thresholds,
    validate_postproc_artifact,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
CLASS_IDS = TAXONOMY.polyphonic_class_ids


def _priors() -> dict[str, DurationPrior]:
    return {
        class_id: DurationPrior(median_w=1, d_min_s=0.0, g_max_s=0.0, n_events=1)
        for class_id in CLASS_IDS
    }


def _train_events() -> dict[str, list[dict[str, float | str]]]:
    events = []
    for index, class_id in enumerate(CLASS_IDS):
        start = float(index * 10)
        events.extend(
            [
                {"class_id": class_id, "onset_s": start, "offset_s": start + 1.0},
                {"class_id": class_id, "onset_s": start + 3.0, "offset_s": start + 5.0},
            ]
        )
    return {"datased:S-train": events}


def test_stack_predictions_by_recording_concatenates_windows_and_trims_padding():
    """H2: two windows for r1 (second one padded), one window for r2."""
    n_classes = len(CLASS_IDS)
    logits = np.zeros((3, 4, n_classes), dtype=np.float32)
    logits[0] = 10.0  # r1, window 0: fully valid, sigmoid(10) ~ 1
    logits[1, :2] = -10.0  # r1, window 1: only first 2 frames valid, sigmoid(-10) ~ 0
    logits[2] = 5.0  # r2, window 0: fully valid
    mask = np.array(
        [[True, True, True, True], [True, True, False, False], [True, True, True, True]]
    )
    artifact = PredictionArtifact(
        logits=logits,
        targets=np.zeros_like(logits, dtype=np.uint8),
        recording_ids=np.array(["r1", "r1", "r2"]),
        frame_offsets_s=np.array([0.0, 4.0, 0.0]),
        mask=mask,
        class_ids=CLASS_IDS,
        split="dev",
        model_version="sed-v1.0",
        frame_hop_s=0.02,
        taxonomy_sha256=TAXONOMY.checksum,
    )

    stacked = stack_predictions_by_recording(artifact)

    assert set(stacked) == {"r1", "r2"}
    assert stacked["r1"].shape == (6, n_classes)  # 4 (window 0) + 2 valid (window 1)
    assert stacked["r2"].shape == (4, n_classes)
    assert np.all(stacked["r1"][:4] > 0.99)  # sigmoid(10)
    assert np.all(stacked["r1"][4:6] < 0.01)  # sigmoid(-10), padding excluded
    assert np.allclose(stacked["r2"], 1.0 / (1.0 + np.exp(-5.0)))


def test_only_classes_produces_identical_output_to_filtering_after_the_fact():
    """H2 performance fix (2026-09-23): `sweep_per_class_thresholds` was
    measured at ~4.3s per call (399 calls in a real sweep, ~30 min total)
    purely from reprocessing 20 always-suppressed classes per candidate.
    `only_classes` skips that work — this locks that the class actually being
    computed gets byte-identical output whether or not the other 20 columns
    are also processed, since each class's median filter/run detection is
    column-independent."""
    rng = np.random.default_rng(20260923)
    probabilities = rng.random((200, len(CLASS_IDS))).astype(np.float32)
    priors = _priors()
    thresholds = dict.fromkeys(CLASS_IDS, 0.5)
    target = CLASS_IDS[3]

    full = probabilities_to_events(
        probabilities, recording_id="r1", class_ids=CLASS_IDS,
        thresholds=thresholds, priors=priors, frame_rate=10.0,
    )
    full_for_target = [event for event in full if event.class_id == target]

    restricted = probabilities_to_events(
        probabilities, recording_id="r1", class_ids=CLASS_IDS,
        thresholds=thresholds, priors=priors, frame_rate=10.0,
        only_classes=frozenset({target}),
    )

    assert restricted == full_for_target
    assert {event.class_id for event in restricted} <= {target}


def test_probabilities_to_events_applies_filter_gap_merge_and_minimum_duration():
    probabilities = np.asarray(
        [
            [0.0],
            [0.9],
            [0.9],
            [0.0],
            [0.9],
            [0.9],
            [0.0],
            [0.0],
            [0.0],
            [0.9],
            [0.0],
        ],
        dtype=np.float32,
    )
    events = probabilities_to_events(
        probabilities,
        recording_id="datased:S-0001",
        class_ids=["birds"],
        thresholds={"birds": 0.5},
        priors={"birds": DurationPrior(median_w=1, d_min_s=0.3, g_max_s=0.2)},
        frame_rate=10.0,
    )

    assert len(events) == 1
    assert events[0].onset_s == pytest.approx(0.1)
    assert events[0].offset_s == pytest.approx(0.6)
    assert events[0].score == pytest.approx(0.9)


def test_median_filter_suppresses_isolated_active_frame():
    events = probabilities_to_events(
        np.asarray([[0.0], [0.9], [0.0]], dtype=np.float32),
        recording_id="datased:S-0001",
        class_ids=["birds"],
        thresholds={"birds": 0.5},
        priors={"birds": DurationPrior(median_w=3, d_min_s=0.0, g_max_s=0.0)},
        frame_rate=10.0,
    )
    assert events == []


def test_duration_priors_are_train_only_and_cover_polyphonic_taxonomy():
    priors = derive_duration_priors(
        _train_events(), class_ids=CLASS_IDS, frame_rate=50.0, source_split="train"
    )
    assert tuple(priors) == CLASS_IDS
    assert priors["bells"].d_min_s == pytest.approx(1.05)
    assert priors["bells"].g_max_s == pytest.approx(2.0)
    assert priors["bells"].median_w % 2 == 1

    with pytest.raises(ValueError, match="only be derived"):
        derive_duration_priors(
            _train_events(), class_ids=CLASS_IDS, frame_rate=50.0, source_split="dev"
        )
    with pytest.raises(ValueError, match="exact order"):
        derive_duration_priors(
            _train_events(),
            class_ids=tuple(reversed(CLASS_IDS)),
            frame_rate=50.0,
            source_split="train",
        )


def test_duration_prior_percentiles_are_configurable_and_bounded():
    """Nợ kỹ thuật #8: percentile 5/50 were picked without empirical backing —
    exposed as parameters so an ablation can sweep alternatives through this
    exact function. Defaults must stay 5/50 (locked by the test above)."""
    priors_p0 = derive_duration_priors(
        _train_events(),
        class_ids=CLASS_IDS,
        frame_rate=50.0,
        source_split="train",
        d_min_percentile=0.0,
    )
    priors_p100 = derive_duration_priors(
        _train_events(),
        class_ids=CLASS_IDS,
        frame_rate=50.0,
        source_split="train",
        d_min_percentile=100.0,
    )
    assert priors_p0["bells"].d_min_s == pytest.approx(1.0)
    assert priors_p100["bells"].d_min_s == pytest.approx(2.0)

    with pytest.raises(ValueError, match="d_min_percentile"):
        derive_duration_priors(
            _train_events(),
            class_ids=CLASS_IDS,
            frame_rate=50.0,
            source_split="train",
            d_min_percentile=101.0,
        )
    with pytest.raises(ValueError, match="g_max_percentile"):
        derive_duration_priors(
            _train_events(),
            class_ids=CLASS_IDS,
            frame_rate=50.0,
            source_split="train",
            g_max_percentile=-1.0,
        )


def test_threshold_sweeps_are_dev_only_and_deterministic():
    probabilities = np.zeros((2, len(CLASS_IDS)), dtype=np.float32)
    probabilities[0, :] = 0.6
    predictions = {"datased:S-dev": probabilities}

    best_global, global_curve = sweep_global_threshold(
        predictions,
        class_ids=CLASS_IDS,
        priors=_priors(),
        frame_rate=10.0,
        score_fn=lambda events: float(sum(len(rows) for rows in events.values())),
        split="dev",
        grid=[0.5, 0.7],
    )
    assert best_global == 0.5
    assert global_curve == {0.5: 21.0, 0.7: 0.0}

    thresholds, curves = sweep_per_class_thresholds(
        predictions,
        class_ids=CLASS_IDS,
        priors=_priors(),
        frame_rate=10.0,
        score_fn=lambda events, class_id: float(
            sum(row["class_id"] == class_id for rows in events.values() for row in rows)
        ),
        split="dev",
        grid=[0.5, 0.7],
    )
    assert set(thresholds.values()) == {0.5}
    assert all(curve == {0.5: 1.0, 0.7: 0.0} for curve in curves.values())

    with pytest.raises(ValueError, match="split='dev'"):
        sweep_global_threshold(
            predictions,
            class_ids=CLASS_IDS,
            priors=_priors(),
            frame_rate=10.0,
            score_fn=lambda events: 0.0,
            split="test",
            grid=[0.5],
        )


def test_postproc_artifact_schema_provenance_and_semantic_guards():
    digest = "a" * 64
    artifact = build_postproc_artifact(
        class_ids=CLASS_IDS,
        thresholds=dict.fromkeys(CLASS_IDS, 0.5),
        priors=_priors(),
        taxonomy_sha256=TAXONOMY.checksum,
        split_sha256=digest,
        data_manifest_sha256=digest,
        dev_predictions_sha256=digest,
        threshold_mode="per_class",
        threshold_grid=[0.5],
    )
    schema = json.loads((ROOT / "contracts" / "postproc.schema.json").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(artifact)
    assert artifact["class_ids"] == list(CLASS_IDS)
    assert list(artifact["per_class"]) == list(CLASS_IDS)

    leaked = dict(artifact, calibrated_on="test")
    with pytest.raises(ValueError, match="calibrated on dev"):
        validate_postproc_artifact(leaked)
    leaked = dict(artifact, duration_prior_from="dev")
    with pytest.raises(ValueError, match="come from train"):
        validate_postproc_artifact(leaked)
    wrong_taxonomy = dict(artifact, taxonomy_sha256=digest)
    with pytest.raises(ValueError, match="active taxonomy"):
        validate_postproc_artifact(wrong_taxonomy)
