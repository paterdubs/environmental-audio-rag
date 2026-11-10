"""Phục vụ LBR (ADR-0045, ADR-0046 §5): bật bằng biến môi trường, mặc định ưu tiên phát hiện."""

import json

import numpy as np
import pytest

from ml.inference import engine
from ml.inference.sed import SERVED_ID, ServedSed
from ml.postprocessing.boundary_refine import LbrConfig, save_bundle
from ml.postprocessing.lbr_apply import load_lbr
from ml.postprocessing.lbr_crossfit import build_data, fit_lbr, micro_f1_objective
from ml.postprocessing.sebb import SebbParams

FR = 25.0
CLASSES = ("a", "b")
PARAMS = SebbParams(step_filter_s=0.32, merge_abs=0.3)
FAST = LbrConfig(max_iter=30, max_leaf_nodes=7, min_samples_leaf=2)


def test_lbr_disabled_by_default(monkeypatch):
    monkeypatch.delenv("EARAG_SERVED_LBR", raising=False)
    monkeypatch.delenv("EARAG_SERVED_MODE", raising=False)
    assert engine.lbr_settings() == (None, None)


def test_lbr_defaults_to_recall_first_and_validates_mode(monkeypatch):
    monkeypatch.setenv("EARAG_SERVED_LBR", "ml/runs/sed_lbr_x")
    monkeypatch.delenv("EARAG_SERVED_MODE", raising=False)
    run, mode = engine.lbr_settings()
    assert run == (engine.ROOT / "ml/runs/sed_lbr_x").resolve() and mode == "recall_first"
    monkeypatch.setenv("EARAG_SERVED_MODE", "f1")
    assert engine.lbr_settings()[1] == "f1"
    monkeypatch.setenv("EARAG_SERVED_MODE", "f2")
    with pytest.raises(ValueError):
        engine.lbr_settings()
    monkeypatch.setenv("EARAG_SERVED_LBR", "../outside")
    monkeypatch.setenv("EARAG_SERVED_MODE", "f1")
    with pytest.raises(ValueError):
        engine.lbr_settings()


def frozen_run(tmp_path):
    probabilities, reference, folds = {}, {}, {}
    for fold in range(3):
        for i in range(4):
            rid = f"r{fold}_{i}"
            p = np.full((int(30 * FR), 2), 0.02)
            for c, start in ((0, 3.0 + i), (1, 12.0 + i)):
                p[int(start * FR):int((start + 3.0) * FR), c] = 0.95
                reference.setdefault(rid, []).append(
                    {"class_id": CLASSES[c], "onset": start + 0.3, "offset": start + 3.0})
            p[int(24 * FR):int(25.5 * FR), 0] = 0.7
            probabilities[rid], folds[rid] = p, fold
    data = build_data(probabilities, reference, folds, class_ids=CLASSES, frame_rate=FR,
                      params=PARAMS, config=FAST)
    objective = micro_f1_objective(reference, CLASSES)
    model = fit_lbr(data, fit_folds={0, 1, 2}, variant="v1",
                    objectives={"f1": objective, "recall_first": objective}, config=FAST)
    sha = save_bundle(tmp_path / "lbr_model.pkl", {
        "variant": "v1", "refiner_on": model.refiner_on, "refiner_off": model.refiner_off,
        "rescorer": None, "thresholds": dict(model.thresholds), "n_classes": 2, "config": FAST,
        "class_ids": list(CLASSES), "sebb_params": PARAMS, "source_run": "src"})
    (tmp_path / "manifest.json").write_text(json.dumps(
        {"run_id": "sed_lbr_t", "task": "sed_lbr", "complete": True,
         "config": {"model_sha256": sha}}), encoding="utf-8")
    return probabilities["r0_0"]


def test_served_events_use_lbr_when_enabled(tmp_path):
    probabilities = frozen_run(tmp_path)
    sed = ServedSed.__new__(ServedSed)  # bỏ qua nạp model mạng: chỉ kiểm hậu xử lý
    sed.class_ids, sed.postproc_family = CLASSES, "csebb"
    sed.sebb_params, sed.sebb_threshold = PARAMS, 0.9
    sed.config = type("C", (), {"frame_rate": FR})()
    sed.model_version = "sed_served_B0"
    before = sed.events(probabilities)
    sed.enable_lbr(load_lbr(tmp_path, class_ids=CLASSES), mode="f1")
    after = sed.events(probabilities)
    assert [round(e["onset"], 2) for e in before if e["class_id"] == "a"][0] == 3.0
    assert abs([e["onset"] for e in after if e["class_id"] == "a"][0] - 3.3) <= 0.2
    assert all(e["recording_id"] == SERVED_ID for e in after)
    assert all(0 <= e["onset_s"] < e["offset_s"] <= probabilities.shape[0] / FR for e in after)
    assert sed.model_version == "sed_served_B0+sed_lbr_t:f1"
    sed.enable_lbr(load_lbr(tmp_path, class_ids=CLASSES), mode="recall_first")
    assert sed.model_version == "sed_served_B0+sed_lbr_t:recall_first"  # không chồng hậu tố
    with pytest.raises(ValueError):
        sed.enable_lbr(load_lbr(tmp_path, class_ids=CLASSES), mode="f2")


def test_inference_import_does_not_pull_sklearn():
    import subprocess
    import sys

    code = ("import sys; import ml.inference.engine, ml.inference.sed; "
            "print('sklearn' in sys.modules)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         cwd=engine.ROOT, check=True)
    assert out.stdout.strip() == "False"


def test_engine_modes_match_lbr_operating_points():
    from ml.postprocessing.lbr_apply import OPERATING_POINTS

    assert engine.LBR_MODES == OPERATING_POINTS
