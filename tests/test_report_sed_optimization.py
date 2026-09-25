import json
from pathlib import Path

import pytest

from scripts.report_sed_optimization import (
    candidate_label,
    load_dev,
    load_test,
    render,
    render_dev,
    select_system,
)


def cand(run_id: str, score: float, n_models: int, sd: float = 0.01) -> dict:
    return {"run_id": run_id, "label": run_id, "n_models": n_models,
            "score": score, "score_sd": sd}


def test_selects_highest_dev_cv_mean() -> None:
    choice = select_system([cand("a", 0.10, 1), cand("b", 0.15, 3), cand("c", 0.12, 7)])
    assert choice["run_id"] == "b"
    assert choice["runner_up"] == "c"
    assert choice["margin"] == pytest.approx(0.03)


def test_exact_tie_prefers_fewer_models() -> None:
    assert select_system([cand("ens", 0.15, 7), cand("single", 0.15, 1)])["run_id"] == "single"


def test_margin_within_fold_sd_is_flagged() -> None:
    choice = select_system([cand("a", 0.150, 3, sd=0.02), cand("b", 0.145, 1)])
    assert choice["run_id"] == "a"
    assert choice["margin_exceeds_fold_sd"] is False


def test_candidate_label_distinguishes_ensemble_and_single_run() -> None:
    ensemble = {"task": "sed_ensemble", "config": {"ensemble_label": "BC", "members": [1, 2]}}
    single = {"config": {"weight_source": "datasec:ml/runs/x/best.pt"}}
    assert candidate_label(ensemble, "sed_ensemble_BC_x") == ("ensemble BC", 2)
    assert candidate_label(single, "sed_polyphonic_20260924T061000Z") == (
        "run đơn C `20260924T061000Z`", 1)


def _evaluation(f1: float, postproc: str) -> dict:
    return {"postproc": postproc, "event_based_f1": {"f_measure": f1},
            "event_based_f1_bootstrap": {"lower": f1 - 0.01, "upper": f1 + 0.01},
            "psds": {"psds_1": 0.3, "psds_2": 0.7}}


def write_run(tmp_path: Path, *, cv_postproc: str = "postproc_cv.json") -> Path:
    run = tmp_path / "sed_polyphonic_20260924T054531Z"
    run.mkdir()
    files = {
        "manifest.json": {"config": {"weight_source": "audioset"}, "git": {"dirty": False}},
        "postproc_cv_selection.json": {
            "selected": {"threshold_mode": "global", "g_max_percentile": 25.0},
            "cv": {key: {"mean": 0.1, "sd": 0.01} for key in
                   ("per_class|50", "per_class|25", "global|50", "global|25")},
        },
        "evaluation.json": _evaluation(0.06, str(run / "postproc.json")),
        "evaluation_cv.json": _evaluation(0.09, str(run / cv_postproc)),
    }
    for name, payload in files.items():
        (run / name).write_text(json.dumps(payload), encoding="utf-8")
    return run


def test_dev_loading_does_not_need_test_files(tmp_path: Path) -> None:
    run = write_run(tmp_path)
    (run / "evaluation.json").unlink()
    (run / "evaluation_cv.json").unlink()
    loaded = load_dev(run)
    assert loaded["selected_config"] == "global|25"
    assert loaded["label"] == "run đơn B `20260924T054531Z`"


def test_rejects_cv_evaluation_with_other_postproc(tmp_path: Path) -> None:
    run = write_run(tmp_path, cv_postproc="postproc.json")
    with pytest.raises(SystemExit, match="postproc_cv.json"):
        load_test(run)


def test_dev_only_render_has_no_test_section(tmp_path: Path) -> None:
    run = write_run(tmp_path)
    candidate = load_dev(run)  # no "test" key: rendering must not need it
    text = "\n".join(render_dev([candidate], select_system([candidate]), "cmd"))
    assert "## 2." in text and "## 3." not in text and "◀" not in text


def test_render_reports_every_candidate_and_marks_choice(tmp_path: Path) -> None:
    run = write_run(tmp_path)
    candidate = {**load_dev(run), "test": load_test(run)}
    other = {**candidate, "run_id": "other", "label": "ensemble X", "score": 0.05}
    lines = render([candidate, other], select_system([candidate, other]), "cmd")
    text = "\n".join(lines)
    assert text.count("◀ chọn") == 2  # hai dòng (mặc định + CV) của ứng viên được chọn
    assert "ensemble X" in text and "0.0900" in text
