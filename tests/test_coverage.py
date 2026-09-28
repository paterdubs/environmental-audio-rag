"""ADR-0034: scoring only recordings that have polyphonic ground truth."""

from pathlib import Path

import pandas as pd
import pytest

from ml.evaluation.coverage import (
    UNANNOTATED_MANIFEST,
    eval_suffix,
    restrict,
    unannotated_recordings,
)

ROOT = Path(__file__).resolve().parents[1]


def test_all_keeps_everything_and_annotated_drops_listed_recordings() -> None:
    scores = {"S-1": 1, "S-2": 2, "S-3": 3}
    assert restrict(scores, "all", frozenset({"S-2"})) == scores
    assert restrict(scores, "annotated", frozenset({"S-2"})) == {"S-1": 1, "S-3": 3}


def test_suffix_never_collides_with_historical_files() -> None:
    assert eval_suffix("all") == ""
    assert eval_suffix("annotated") == "_annotated"
    with pytest.raises(ValueError, match="eval_set"):
        eval_suffix("test")


def test_restrict_refuses_to_score_nothing() -> None:
    with pytest.raises(ValueError, match="no annotated"):
        restrict({"S-1": 1}, "annotated", frozenset({"S-1"}))


def test_manifest_is_exactly_the_recordings_without_polyphonic_events() -> None:
    listed = unannotated_recordings(UNANNOTATED_MANIFEST)
    assert listed == {f"S-{i:04d}" for i in range(704, 718)}
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    recordings = pd.read_csv(ROOT / "data" / "manifests" / "datased_recordings.csv")
    without_events = set(recordings["recording_id"]) - set(events["recording_id"])
    assert listed == without_events
    splits = pd.read_csv(UNANNOTATED_MANIFEST)["split"].value_counts().to_dict()
    assert splits == {"train": 8, "validation": 3, "test": 3}
