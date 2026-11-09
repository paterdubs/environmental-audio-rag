"""Nhánh LBR của evaluate_run: một lượt tính cả hai điểm vận hành và so ghép cặp với B0."""

import json

import numpy as np

from ml.postprocessing.boundary_refine import LbrConfig, save_bundle
from ml.postprocessing.lbr_crossfit import build_data, fit_lbr, micro_f1_objective
from ml.postprocessing.sebb import SebbParams
from scripts import lbr_test_section

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


def frozen_run(tmp_path):
    probabilities, reference, folds = dataset()
    data = build_data(probabilities, reference, folds, class_ids=CLASSES, frame_rate=FR,
                      params=PARAMS, config=FAST)
    objective = micro_f1_objective(reference, CLASSES)
    model = fit_lbr(data, fit_folds={0, 1, 2}, variant="v1",
                    objectives={"f1": objective, "recall_first": objective}, config=FAST)
    sha = save_bundle(tmp_path / "lbr_model.pkl", {
        "variant": "v1", "refiner_on": model.refiner_on, "refiner_off": model.refiner_off,
        "rescorer": None, "thresholds": dict(model.thresholds), "n_classes": 2,
        "config": FAST, "class_ids": list(CLASSES), "sebb_params": PARAMS, "source_run": "src"})
    (tmp_path / "manifest.json").write_text(json.dumps(
        {"run_id": "sed_lbr_t", "task": "sed_lbr", "complete": True,
         "config": {"model_sha256": sha}}), encoding="utf-8")
    return probabilities, reference


def test_one_opening_covers_both_points_vn_set_and_paired_delta(tmp_path):
    probabilities, reference = frozen_run(tmp_path)
    lbr = lbr_test_section.estimate(tmp_path, probabilities, class_ids=CLASSES, frame_rate=FR)
    assert len(lbr["psds_events"]) == 8  # lưới λ của V1
    sec = lbr_test_section.section(lbr, reference, probabilities, class_ids=CLASSES,
                                   frame_rate=FR, baseline=(PARAMS, 0.9))
    assert set(sec["points"]) == {"f1", "recall_first"}
    assert set(sec["points"]["f1"]) == {"all", "vn"}
    assert "counts" not in sec["points"]["f1"]["all"]
    assert sec["points"]["f1"]["all"]["micro_f1"] > 0.9
    assert sec["baseline"]["all"]["micro_f1"] == 0.0  # box gốc sớm 0.3 s > collar
    assert sec["delta_micro_vs_baseline"]["lower"] > 0
    text = "\n".join(lbr_test_section.render(sec))
    assert "LBR — recall_first" in text and "19 lớp Việt Nam" in text
