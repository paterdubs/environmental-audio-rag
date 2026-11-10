"""Áp run LBR đã đóng băng: kiểm task/SHA/lớp, tái tạo đúng điểm vận hành (ADR-0045 §7–§8)."""

import json

import numpy as np
import pytest

from ml.postprocessing.boundary_refine import LbrConfig, save_bundle
from ml.postprocessing.lbr_apply import is_lbr_run, lbr_events, lbr_scored_boxes, load_lbr
from ml.postprocessing.lbr_crossfit import build_data, fit_lbr, micro_f1_objective
from ml.postprocessing.sebb import SebbParams

FR = 25.0
CLASSES = ("a", "b")
PARAMS = SebbParams(step_filter_s=0.32, merge_abs=0.3)
FAST = LbrConfig(max_iter=30, max_leaf_nodes=7, min_samples_leaf=2)


def dataset():
    probabilities, reference, folds = {}, {}, {}
    for fold in range(3):
        for i in range(4):
            rid = f"r{fold}_{i}"
            p = np.full((int(30 * FR), 2), 0.02)
            events = []
            for c, start in ((0, 3.0 + i), (1, 12.0 + i)):
                p[int(start * FR):int((start + 3.0) * FR), c] = 0.95
                events.append({"class_id": CLASSES[c], "onset": start + 0.3,
                               "offset": start + 3.0})
            p[int(24 * FR):int(25.5 * FR), 0] = 0.7
            probabilities[rid], reference[rid], folds[rid] = p, events, fold
    return probabilities, reference, folds


def write_run(tmp_path, *, variant="v1", task="sed_lbr", corrupt=False):
    probabilities, reference, folds = dataset()
    data = build_data(probabilities, reference, folds, class_ids=CLASSES, frame_rate=FR,
                      params=PARAMS, config=FAST)
    objective = micro_f1_objective(reference, CLASSES)
    model = fit_lbr(data, fit_folds={0, 1, 2}, variant=variant,
                    objectives={"f1": objective, "recall_first": objective}, config=FAST)
    sha = save_bundle(tmp_path / "lbr_model.pkl", {
        "variant": variant, "refiner_on": model.refiner_on, "refiner_off": model.refiner_off,
        "rescorer": model.rescorer, "thresholds": dict(model.thresholds),
        "n_classes": model.n_classes, "config": FAST, "class_ids": list(CLASSES),
        "sebb_params": PARAMS, "source_run": "src"})
    manifest = {"task": task, "complete": True,
                "config": {"model_sha256": "0" * 64 if corrupt else sha}}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return probabilities, reference


@pytest.mark.parametrize("variant", ["v1", "v2", "v3"])
def test_frozen_run_reproduces_refined_events(tmp_path, variant):
    probabilities, reference = write_run(tmp_path, variant=variant)
    bundle = load_lbr(tmp_path, class_ids=CLASSES)
    boxes, scores = lbr_scored_boxes(bundle, probabilities, frame_rate=FR)
    events = lbr_events(bundle, boxes, scores, point="f1", recordings=sorted(probabilities))
    assert set(events) == set(probabilities)
    assert micro_f1_objective(reference, CLASSES)(events, sorted(probabilities)) > 0.9


def test_refuses_wrong_sha_task_or_class_order(tmp_path):
    write_run(tmp_path, corrupt=True)
    with pytest.raises(ValueError):
        load_lbr(tmp_path, class_ids=CLASSES)
    write_run(tmp_path, task="sed_oof")
    with pytest.raises(ValueError):
        load_lbr(tmp_path, class_ids=CLASSES)
    write_run(tmp_path)
    with pytest.raises(ValueError):
        load_lbr(tmp_path, class_ids=("b", "a"))
    assert is_lbr_run({"task": "sed_lbr"}) and not is_lbr_run({"family": "csebb"})


def test_unknown_operating_point_rejected(tmp_path):
    probabilities, _ = write_run(tmp_path)
    bundle = load_lbr(tmp_path, class_ids=CLASSES)
    boxes, scores = lbr_scored_boxes(bundle, probabilities, frame_rate=FR)
    with pytest.raises(ValueError):
        lbr_events(bundle, boxes, scores, point="f2", recordings=sorted(probabilities))
