"""Event LBR cho caption/RAG (ADR-0047): test áp run đóng băng, dev chỉ nhận event cross-fit."""

import json
from pathlib import Path

import numpy as np
import pytest
from test_lbr_apply import CLASSES, FR, write_run

from ml.dataops.inventory import sha256_file
from ml.postprocessing.lbr_apply import (
    clip_events_to_duration,
    lbr_events,
    lbr_scored_boxes,
    load_lbr,
)
from ml.postprocessing.lbr_timeline import (
    EVENTS_FILE,
    OOF_EVENTS_TASK,
    is_lbr_postproc,
    lbr_postproc_events,
    model_version,
)
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import e2e_timelines

ROOT = Path(__file__).resolve().parents[1]


def _manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_oof_events(tmp_path: Path, events: dict, *, point="f1", split="dev",
                     sha: str | None = None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / EVENTS_FILE).write_text(json.dumps(events), encoding="utf-8")
    manifest = {"run_id": "oofevents", "task": OOF_EVENTS_TASK, "complete": True,
                "config": {"lbr_run": "sed_lbr_x", "point": point, "predictions_split": split,
                           "events_sha256": sha or sha256_file(tmp_path / EVENTS_FILE)}}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


@pytest.mark.parametrize("variant", ["v2", "v3"])
@pytest.mark.parametrize("point", ["f1", "recall_first"])
def test_frozen_run_on_test_matches_direct_application(tmp_path, variant, point):
    probabilities, _ = write_run(tmp_path, variant=variant)
    path = tmp_path / "manifest.json"
    events = lbr_postproc_events(_manifest(path), path, probabilities, class_ids=CLASSES,
                                 frame_rate=FR, split="test", point=point)
    bundle = load_lbr(tmp_path, class_ids=CLASSES)
    boxes, scores = lbr_scored_boxes(bundle, probabilities, frame_rate=FR)
    assert events == lbr_events(bundle, boxes, scores, point=point,
                                recordings=sorted(probabilities))


def test_frozen_run_refuses_dev_because_final_model_saw_it(tmp_path):
    probabilities, _ = write_run(tmp_path, variant="v2")
    path = tmp_path / "manifest.json"
    with pytest.raises(ValueError, match="cross-fit"):
        lbr_postproc_events(_manifest(path), path, probabilities, class_ids=CLASSES,
                            frame_rate=FR, split="dev", point="f1")


def test_oof_events_are_returned_for_exactly_the_posterior_recordings(tmp_path):
    events = {"a": [{"class_id": "a", "onset_s": 1.0, "offset_s": 2.0, "score": 0.9}], "b": []}
    path = write_oof_events(tmp_path, events)
    posterior = np.zeros((int(5 * FR), len(CLASSES)))
    got = lbr_postproc_events(_manifest(path), path, {"b": posterior, "a": posterior},
                              class_ids=CLASSES, frame_rate=FR, split="dev", point="f1")
    assert got == events and list(got) == ["a", "b"]
    assert model_version(_manifest(path), "f1") == "sed_lbr_x:f1"


@pytest.mark.parametrize(("kwargs", "probabilities", "match"), [
    ({"point": "recall_first"}, {"a": None}, "điểm"),
    ({"split": "test"}, {"a": None}, "split"),
    ({"sha": "0" * 64}, {"a": None}, "SHA-256"),
    ({}, {"a": None, "zz": None}, "lệch"),
])
def test_oof_events_reject_mismatched_artifacts(tmp_path, kwargs, probabilities, match):
    path = write_oof_events(tmp_path, {"a": []}, **kwargs)
    with pytest.raises(ValueError, match=match):
        lbr_postproc_events(_manifest(path), path, probabilities, class_ids=CLASSES,
                            frame_rate=FR, split="dev", point="f1")


def test_non_lbr_manifest_is_rejected(tmp_path):
    path = tmp_path / "postproc.json"
    path.write_text(json.dumps({"family": "csebb"}), encoding="utf-8")
    assert not is_lbr_postproc(_manifest(path))
    with pytest.raises(ValueError, match="không phải"):
        lbr_postproc_events(_manifest(path), path, {}, class_ids=CLASSES, frame_rate=FR,
                            split="test", point="f1")


def test_e2e_timelines_requires_point_exactly_for_lbr(tmp_path):
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lbr = write_oof_events(tmp_path / "lbr", {"a": []})
    with pytest.raises(SystemExit, match="lbr-point"):
        e2e_timelines(tmp_path, "dev", taxonomy, lbr, tmp_path)
    plain = tmp_path / "postproc.json"
    plain.write_text(json.dumps({"family": "csebb"}), encoding="utf-8")
    with pytest.raises(SystemExit, match="lbr-point"):
        e2e_timelines(tmp_path, "dev", taxonomy, plain, tmp_path, lbr_point="f1")


def test_clip_events_to_duration_keeps_inside_clips_overhang_and_drops_empty():
    rows = [{"class_id": "a", "onset_s": 1.0, "offset_s": 2.0, "score": 0.9},
            {"class_id": "a", "onset_s": 4.0, "offset_s": 5.5, "score": 0.8},
            {"class_id": "b", "onset_s": 5.2, "offset_s": 6.0, "score": 0.7},
            {"class_id": "b", "onset_s": -0.3, "offset_s": 1.0, "score": 0.6}]
    got = clip_events_to_duration(rows, 5.0)
    assert [(e["onset_s"], e["offset_s"]) for e in got] == [(1.0, 2.0), (4.0, 5.0), (0.0, 1.0)]
    assert rows[1]["offset_s"] == 5.5  # không sửa đầu vào
    pair = {"onset": 4.0, "offset": 5.5, "onset_s": 4.0, "offset_s": 5.5}
    both = clip_events_to_duration([pair], 5.0)
    assert both == [{"onset": 4.0, "offset": 5.0, "onset_s": 4.0, "offset_s": 5.0}]


def test_oof_events_beyond_the_recording_are_clipped_for_the_timeline(tmp_path):
    events = {"a": [{"class_id": "a", "onset_s": 4.0, "offset_s": 5.6, "score": 0.9}]}
    path = write_oof_events(tmp_path, events)
    posterior = np.zeros((int(5 * FR), len(CLASSES)))
    got = lbr_postproc_events(_manifest(path), path, {"a": posterior}, class_ids=CLASSES,
                              frame_rate=FR, split="dev", point="f1")
    assert got["a"][0]["offset_s"] == posterior.shape[0] / FR
