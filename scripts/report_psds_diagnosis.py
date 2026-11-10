"""Chẩn đoán PSDS v1/v2 trên dev (ADR-0048 §2, PAPER_NOTES S21) — không đọc test.

    .venv/Scripts/python.exe -m scripts.report_psds_diagnosis [--eval-set annotated|all] \\
        [--runs-root <ml/runs>] [--system nhãn=<run posterior>:<postproc>]...

Mặc định bốn hệ thống của ADR-0048 (v1, v2, f2, B0) với hậu xử lý đã khóa. Mỗi hệ thống: PSDS-1/2
trên lưới tuyến tính (`DEFAULT_THRESHOLD_GRID`, như `evaluate_run`) và lưới log ghi trước
(`PSDS_GRID_LOG`, ADR-0047); PSDS khi `alpha_st = 0`; PSDS-1 với DTC = GTC = 0.5; TPR trung bình tại
eFPR {5, 10, 30, 60, 100}/giờ; AUC theo lớp; vị trí điểm vận hành đã chọn. Luật H1–H4 áp đúng như
ADR-0048 (`ml.evaluation.psds_diagnosis.evaluate_hypotheses`).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ml.evaluation import psds_diagnosis as diag
from ml.evaluation.coverage import EVAL_SETS, eval_suffix, restrict
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import (
    priors_from_postproc,
    process_recordings,
    stack_predictions_by_recording,
)
from ml.postprocessing.calibration import DEFAULT_THRESHOLD_GRID, validate_postproc_artifact
from ml.postprocessing.sebb import sebb_candidates, select_boxes
from ml.provenance import git_state
from ml.taxonomy import Taxonomy, load_taxonomy
from scripts.evaluate_run import (
    PSDS_SCENARIOS,
    load_events_by_recording,
    sebb_params,
    to_reference_frame,
)
from scripts.report_lbr_psds_grid import PSDS_GRID_LOG
from scripts.report_psds_diagnosis_render import render_markdown

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {**PSDS_SCENARIOS,
             "psds_1_dtc05": {**PSDS_SCENARIOS["psds_1"], "dtc_threshold": 0.5,
                              "gtc_threshold": 0.5}}
GRIDS = {"linear": tuple(DEFAULT_THRESHOLD_GRID), "log": PSDS_GRID_LOG}
# ADR-0048 §2 — ghi trước khi đo; đường dẫn tương đối --runs-root.
DEFAULT_SYSTEMS = {
    "v1": ("sed_ensemble_C_clean_20260925T045631Z",
           "sed_ensemble_C_clean_20260925T045631Z/postproc_cv.json"),
    "v2": ("sed_ensemble_v2_20260926T155630Z",
           "sed_ensemble_v2_20260926T150934Z/postproc_cv.json"),
    "f2": ("sed_ensemble_t2b_20260927T200914Z",
           "sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json"),
    "B0": ("sed_filtered_B0_oof_dev_20261107T181008Z",
           "sed_filtered_B0_oof_dev_20261107T181008Z/sebb_cv_selection_annotated.json"),
}
Events = Mapping[str, list[dict[str, Any]]]


def theta_family(probabilities: Mapping[str, Any], postproc: dict, *, class_ids: tuple[str, ...],
                 frame_rate: float) -> tuple[Callable[[float], Events], Events]:
    """θ chung cho mọi lớp ở mỗi điểm lưới (như `psds_operating_points`), prior đóng băng."""
    priors = priors_from_postproc(postproc, class_ids)

    def run(thresholds: dict[str, float]) -> Events:
        return process_recordings(probabilities, class_ids=class_ids, thresholds=thresholds,
                                  priors=priors, frame_rate=frame_rate)

    chosen = {c: float(postproc["per_class"][c]["theta"]) for c in class_ids}
    return (lambda t: run(dict.fromkeys(class_ids, t))), run(chosen)


def sebb_family(probabilities: Mapping[str, Any], postproc: dict, *, class_ids: tuple[str, ...],
                frame_rate: float) -> tuple[Callable[[float], Events], Events]:
    """Box cSEBB dựng một lần; mỗi điểm lưới chỉ đổi ngưỡng confidence (như `evaluate_run`)."""
    params, threshold = sebb_params(postproc, eval_set=postproc.get("eval_set"))
    candidates = sebb_candidates(probabilities, class_ids=class_ids, frame_rate=frame_rate,
                                 params=params)
    return (lambda t: select_boxes(candidates, t)), select_boxes(candidates, threshold)


def system_result(events_at: Callable[[float], Events], estimate: Events, *,
                  reference: Mapping[str, list[dict[str, Any]]], durations: Mapping[str, float],
                  class_ids: tuple[str, ...], grids: Mapping[str, tuple[float, ...]] = GRIDS
                  ) -> dict[str, Any]:
    recordings = sorted(durations)
    ground_truth = to_reference_frame(reference)
    metadata = pd.DataFrame({"filename": recordings,
                             "duration": [durations[r] for r in recordings]})
    f1 = event_based_f1(reference, estimate, event_label_list=list(class_ids))
    selected = diag.detection_frame(estimate)
    result: dict[str, Any] = {
        "event_f1_micro": float(f1["f_measure"]["f_measure"]),
        "n_events_estimate": len(selected),
        "selected": {s: diag.operating_position(ground_truth, metadata, SCENARIOS[s], selected)
                     for s in ("psds_1", "psds_2")},
        "grids": {},
    }
    for name, grid in grids.items():
        points, sizes = diag.grid_points(events_at, grid)
        result["grids"][name] = {
            "n_grid": len(grid), "n_points": len(points),
            "events_at_lowest_threshold": sizes[0] if sizes else 0,
            "events_at_highest_threshold": sizes[-1] if sizes else 0,
            "scenarios": {s: diag.curve_stats(diag.build_evaluator(ground_truth, metadata,
                                                                   scenario, points), scenario)
                          for s, scenario in SCENARIOS.items()},
        }
    return result


def load_system(pred_run: Path, postproc_path: Path, *, taxonomy: Taxonomy, eval_set: str
                ) -> tuple[Callable[[float], Events], Events, dict, dict[str, float], dict]:
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(pred_run / "predictions" / "dev.npz",
                                expected_class_ids=class_ids)
    if artifact.split != "dev":
        raise SystemExit(f"{pred_run}: split={artifact.split!r} — chẩn đoán chỉ trên dev")
    probabilities = restrict(stack_predictions_by_recording(artifact), eval_set)
    frame_rate = 1.0 / artifact.frame_hop_s
    postproc = json.loads(postproc_path.read_text(encoding="utf-8"))
    if postproc.get("family") == "csebb":
        family = sebb_family
    else:
        validate_postproc_artifact(postproc, taxonomy=taxonomy)
        if postproc["taxonomy_sha256"] != taxonomy.checksum:
            raise SystemExit(f"{postproc_path}: taxonomy khác taxonomy đang dùng")
        family = theta_family
    events_at, estimate = family(probabilities, postproc, class_ids=class_ids,
                                 frame_rate=frame_rate)
    durations = {r: probabilities[r].shape[0] / frame_rate for r in probabilities}
    reference = load_events_by_recording(set(probabilities))
    return events_at, estimate, reference, durations, {
        "predictions": pred_run.name, "postproc": postproc_path.relative_to(
            postproc_path.parents[1]).as_posix(), "family": postproc.get("family", "theta"),
        "n_recordings": len(probabilities)}


def consistency_check(label: str, pred_run: Path, eval_set: str, result: dict) -> dict | None:
    """v1 có `dev_evaluation_cv.json` (evaluate_run --split dev, eval set all): phải trùng."""
    path = pred_run / "dev_evaluation_cv.json"
    if label != "v1" or eval_set != "all" or not path.exists():
        return None
    stored = json.loads(path.read_text(encoding="utf-8"))["psds"]
    ours = {s: result["grids"]["linear"]["scenarios"][s]["psds"] for s in ("psds_1", "psds_2")}
    return {"file": path.name, "stored": stored, "recomputed": ours,
            "match": all(abs(stored[s] - ours[s]) < 1e-9 for s in ours)}


def parse_systems(values: list[str]) -> dict[str, tuple[str, str]]:
    systems = {}
    for value in values:
        label, _, rest = value.partition("=")
        pred, _, postproc = rest.partition(":")
        if not (label and pred and postproc):
            raise SystemExit(f"--system cần nhãn=<run>:<postproc>, nhận {value!r}")
        systems[label] = (pred, postproc)
    return systems


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "ml/runs")
    parser.add_argument("--system", action="append", default=[])
    parser.add_argument("--tag", default="")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    systems = parse_systems(args.system) if args.system else DEFAULT_SYSTEMS
    results, inputs, checks = {}, {}, {}
    for label, (pred, postproc) in systems.items():
        pred_run = args.runs_root / pred
        events_at, estimate, reference, durations, info = load_system(
            pred_run, args.runs_root / postproc, taxonomy=taxonomy, eval_set=args.eval_set)
        print(f"[{label}] {info['n_recordings']} recording, {info['family']}", flush=True)
        results[label] = system_result(events_at, estimate, reference=reference,
                                       durations=durations,
                                       class_ids=taxonomy.polyphonic_class_ids)
        inputs[label] = info
        check = consistency_check(label, pred_run, args.eval_set, results[label])
        if check is not None:
            checks[label] = check
            if not check["match"]:
                raise SystemExit(f"PSDS v1 tính lại lệch {check['file']}: {check}")
    hypotheses = (diag.evaluate_hypotheses(results) if {"v1", "v2"} <= set(results) else None)
    out = {"split": "dev", "eval_set": args.eval_set, "inputs": inputs, "grids": {
        k: list(v) for k, v in GRIDS.items()}, "scenarios": SCENARIOS,
        "efpr_points": list(diag.EFPR_POINTS), "results": results, "hypotheses": hypotheses,
        "consistency_checks": checks, "git": git_state(ROOT),
        "created_at": datetime.now(UTC).isoformat()}
    stem = f"psds_diagnosis_{datetime.now(UTC):%Y%m%d}{eval_suffix(args.eval_set)}{args.tag}"
    out_dir = ROOT / "docs" / "measurements"
    (out_dir / f"{stem}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    (out_dir / f"{stem}.md").write_text(render_markdown(out), encoding="utf-8")
    print(render_markdown(out))


if __name__ == "__main__":
    main()
