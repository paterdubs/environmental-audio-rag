"""ADR-0041 §10 O-F: pseudo-labelled DataSEC clips, fold guard and train_sed wiring."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

from ml.datasets.datasec_pseudo import check_fold, clip_table, keep_tag_class, load_pseudo_run
from scripts.train_sed import load_pseudo


def test_clip_table_uses_the_100_fps_label_grid() -> None:
    cache = pd.DataFrame({"file_id": ["a"], "feature_relative_path": ["A/a.npy"],
                          "samples": [160_000]})
    table = clip_table(cache)
    assert table.loc[0, "frames"] == 1001 and table.loc[0, "recording_id"] == "a"


def test_only_the_tag_class_survives_and_empty_clips_are_dropped() -> None:
    events = {"a": [{"event_label": "bells", "onset": 1.0, "offset": 2.0},
                    {"event_label": "voices", "onset": 0.0, "offset": 3.0}],
              "b": [{"event_label": "voices", "onset": 0.5, "offset": 1.0}]}
    rows, dropped = keep_tag_class(events, {"a": "bells", "b": "horn", "c": "music"})
    assert rows == [{"recording_id": "a", "class_id": "bells", "onset_s": 1.0, "offset_s": 2.0}]
    assert dropped == ["b", "c"]


def test_student_fold_must_match_teacher_fold() -> None:
    check_fold({"config": {"teacher_cv_fold": 2}}, 2)
    check_fold({"config": {"teacher_cv_fold": None}}, None)
    with pytest.raises(SystemExit, match="ADR-0041"):
        check_fold({"config": {"teacher_cv_fold": None}}, 0)  # tier-S labels in a fold run
    with pytest.raises(SystemExit, match="ADR-0041"):
        check_fold({"config": {"teacher_cv_fold": 1}}, 2)


def _pseudo_run(tmp_path: Path, fold: int | None, extra_event: bool = False) -> Path:
    run = tmp_path / "pseudo"
    run.mkdir()
    (run / "manifest.json").write_text(json.dumps({
        "task": "pseudo_labels", "complete": True,
        "config": {"teacher": "t", "teacher_cv_fold": fold}}), encoding="utf-8")
    pd.DataFrame({"file_id": ["a"], "class_id": ["bells"], "feature_relative_path": ["a.npy"],
                  "samples": [16_000]}).to_csv(run / "clips.csv", index=False)
    rows = [("a", "bells", 0.1, 0.5)] + ([("z", "bells", 0.0, 1.0)] if extra_event else [])
    pd.DataFrame(rows, columns=["recording_id", "class_id", "onset_s", "offset_s"]).to_csv(
        run / "events.csv", index=False)
    return run


def test_load_pseudo_run_checks_task_fold_and_dropped_clips(tmp_path: Path) -> None:
    pseudo = load_pseudo_run(_pseudo_run(tmp_path, 3), 3)
    assert pseudo["info"]["clips"] == 1 and pseudo["info"]["teacher_cv_fold"] == 3
    with pytest.raises(SystemExit, match="ADR-0041"):
        load_pseudo_run(tmp_path / "pseudo", None)


def test_events_of_dropped_clips_are_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="clip đã bị bỏ"):
        load_pseudo_run(_pseudo_run(tmp_path, None, extra_event=True), None)


def test_train_sed_guards(tmp_path: Path) -> None:
    run = _pseudo_run(tmp_path, None)
    assert load_pseudo(Namespace(pseudo_labels=None, cv_fold=None),
                       is_waveform=True, balanced=False) is None
    assert load_pseudo(Namespace(pseudo_labels=run, cv_fold=None),
                       is_waveform=True, balanced=False)["info"]["events"] == 1
    with pytest.raises(SystemExit, match="waveform"):
        load_pseudo(Namespace(pseudo_labels=run, cv_fold=None), is_waveform=False,
                    balanced=False)
    with pytest.raises(SystemExit, match="DO-4"):
        load_pseudo(Namespace(pseudo_labels=run, cv_fold=None), is_waveform=True,
                    balanced=True)
