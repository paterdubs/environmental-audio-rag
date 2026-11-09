"""Tầng C cho LBR (ADR-0045 §5–§7) kèm thước ứng dụng (ADR-0046). Chỉ đọc predictions/dev.npz.

So B0 với LBR V1/V2 trên cùng OOF và cùng fold; kiểm chuyển sang OOF ensemble P1×3; áp luật
§6; nếu có ứng viên đạt thì fit model cuối trên đủ 5 fold và lưu kèm SHA-256. Không đọc test.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import sklearn

from ml.evaluation.application_metrics import (
    RECALL_FIRST_PRECISION_FLOOR,
    event_f1_collar,
    intersection_counts,
    intersection_metrics,
    recall_first_objective,
    restrict_classes,
    segment_f1,
    vn_class_ids,
)
from ml.evaluation.multirun import micro_f1, paired_branch_bootstrap
from ml.evaluation.sed_metrics import event_based_f1, event_counts_per_recording
from ml.postprocessing.boundary_refine import (
    LbrConfig,
    candidate_boxes,
    save_bundle,
)
from ml.postprocessing.lbr_crossfit import (
    LAMBDA_GRID,
    T_GRID,
    VARIANTS,
    build_data,
    crossfit_lbr_multi,
    fit_lbr,
    micro_f1_objective,
    select_threshold,
)
from ml.postprocessing.sebb import SebbParams
from ml.provenance import git_state
from ml.training.common import sha256_file
from scripts import select_sebb_cv as sebb_cv
from scripts.report_annotation_consistency import identical_pairs
from scripts.report_oof import FOLDS, output_name
from scripts.report_sed_ceilings import load_tables, reference_events

ROOT = Path(__file__).resolve().parents[1]
N_FOLDS = 5
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")
POINTS = ("f1", "recall_first")
TIE = 0.005  # ADR-0045 §6: chênh < 0.005 thì chọn V1


def load(run: Path) -> dict:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("task") != "sed_oof" or not manifest.get("complete"):
        raise ValueError(f"{run}: cần run sed_oof hoàn tất")
    if manifest["config"].get("cv_folds_sha256") != sha256_file(FOLDS):
        raise ValueError(f"{run}: hash file fold không khớp")
    ctx = sebb_cv.load_context(run, N_FOLDS, "annotated")
    ctx["durations"] = {r: p.shape[0] / ctx["frame_rate"] for r, p in ctx["probabilities"].items()}
    return {**ctx, "manifest": manifest, "run": run}


def sebb_params(run: Path) -> SebbParams:
    selected = json.loads((run / "sebb_cv_selection_annotated.json").read_text(
        encoding="utf-8"))["selected"]
    return SebbParams(step_filter_s=selected["step_filter_s"], merge_abs=selected["merge_abs"],
                      merge_rel=selected["merge_rel"])


def objectives(ctx: dict) -> dict:
    return {"f1": micro_f1_objective(ctx["reference"], ctx["class_ids"]),
            "recall_first": recall_first_objective(ctx["reference"], ctx["class_ids"],
                                                   ctx["durations"])}


def baseline_events(ctx: dict, params: SebbParams, objs: dict) -> dict:
    """cSEBB không tinh chỉnh; λ (lưới của select_sebb_cv) chọn trên các fold còn lại."""
    boxes = candidate_boxes(ctx["probabilities"], class_ids=ctx["class_ids"],
                            frame_rate=ctx["frame_rate"], params=params, min_score=0.0)
    box_fold = np.array([ctx["folds"][b.recording_id] for b in boxes])
    scores = np.array([b.score for b in boxes])
    events = {point: {} for point in objs}
    for k in sorted(set(ctx["folds"].values())):
        fit = [r for r in ctx["recordings"] if ctx["folds"][r] != k]
        held = [r for r in ctx["recordings"] if ctx["folds"][r] == k]
        idx = np.flatnonzero(box_fold != k)
        own = np.flatnonzero(box_fold == k)
        for point, objective in objs.items():
            threshold = select_threshold([boxes[i] for i in idx], scores[idx],
                                         tuple(sebb_cv.LAMBDAS), objective, fit)
            for r in held:
                events[point][r] = []
            for i in own:
                if scores[i] >= threshold:
                    events[point][boxes[i].recording_id].append(_row(boxes[i]))
    return events


def _row(box) -> dict:
    return {"recording_id": box.recording_id, "class_id": box.class_id,
            "event_label": box.class_id, "onset": box.onset_s, "offset": box.offset_s,
            "score": box.score}


def evaluate(ctx: dict, events: dict, class_ids: tuple[str, ...]) -> dict:
    """Thước chính (micro/macro, đếm theo recording) và ba thước ứng dụng của ADR-0046."""
    ref = restrict_classes(ctx["reference"], class_ids)
    est = restrict_classes({r: events.get(r, []) for r in ctx["recordings"]}, class_ids)
    counts = event_counts_per_recording(ref, est, event_label_list=list(class_ids))
    nref, nsys, ntp = (sum(c[i] for c in counts.values()) for i in range(3))
    primary = event_based_f1(ref, est, event_label_list=list(class_ids))
    segment = segment_f1(ref, est, class_ids)
    return {"micro_f1": micro_f1(nref, nsys, ntp), "macro_f1": primary["macro"]["f_measure"],
            "nref": nref, "nsys": nsys, "ntp": ntp, "recall": ntp / nref if nref else None,
            "counts": counts, "event_f1_collar_1s": event_f1_collar(ref, est, class_ids),
            "segment_f1_1s": {k: segment[k] for k in ("micro", "macro")},
            "intersection": intersection_metrics(
                intersection_counts(ref, est, class_ids, ctx["durations"]))}


def human_ceiling(class_ids: tuple[str, ...]) -> dict:
    """Cùng các thước trên 8 cặp recording trùng, trung bình hai chiều (D6)."""
    recordings, events = load_tables()
    durations = recordings.set_index("recording_id")["duration_s"].to_dict()
    pairs = identical_pairs(recordings)
    rows = []
    for left, right in ((0, 1), (1, 0)):
        ref = {f"pair{i}": reference_events(events, [p[left]])[p[left]]
               for i, p in enumerate(pairs)}
        est = {f"pair{i}": reference_events(events, [p[right]])[p[right]]
               for i, p in enumerate(pairs)}
        ctx = {"reference": ref, "recordings": sorted(ref),
               "durations": {f"pair{i}": float(durations[p[left]]) for i, p in enumerate(pairs)}}
        rows.append(evaluate(ctx, est, class_ids))
    keys = ("micro_f1", "macro_f1")
    return {"pairs": len(pairs), **{k: float(np.mean([r[k] for r in rows])) for k in keys},
            "event_f1_collar_1s": float(np.mean([r["event_f1_collar_1s"]["micro"] for r in rows])),
            "segment_f1_1s": float(np.mean([r["segment_f1_1s"]["micro"] for r in rows])),
            "intersection_f1": float(np.mean([r["intersection"]["micro"]["f1"] for r in rows]))}


def bootstrap(results: dict, pairs: list[tuple[str, str]]) -> dict:
    """Δ micro (thước chính, 21 lớp, điểm F1) theo cặp (baseline, ứng viên), ghép theo recording."""
    out = {}
    for base, cand in pairs:
        counts = {n: results[n]["f1"]["all"]["counts"] for n in (base, cand)}
        diff = paired_branch_bootstrap(counts, {base: [base], cand: [cand]})["differences"]
        out[cand] = {**diff[f"{cand}-{base}"], "baseline": base}
    return out


def select_candidate(results: dict, deltas: dict) -> str | None:
    """Luật ADR-0045 §6: cận dưới CI > 0 ở nguồn và ở phép kiểm chuyển; hòa → V1."""
    passing = [v for v in VARIANTS
               if deltas[f"LBR_{v}"]["lower"] > 0 and deltas[f"LBR_{v}_on_P1x3"]["lower"] > 0]
    if not passing:
        return None
    best = max(passing, key=lambda v: results[f"LBR_{v}"]["f1"]["all"]["micro_f1"])
    if "v1" in passing and best != "v1":
        gap = (results[f"LBR_{best}"]["f1"]["all"]["micro_f1"]
               - results["LBR_v1"]["f1"]["all"]["micro_f1"])
        if gap < TIE:
            return "v1"
    return best


def run_all(src: dict, tgt: dict, params: SebbParams, config: LbrConfig) -> dict:
    data = {name: build_data(ctx["probabilities"], ctx["reference"], ctx["folds"],
                             class_ids=ctx["class_ids"], frame_rate=ctx["frame_rate"],
                             params=params, config=config) for name, ctx in (("src", src),
                                                                           ("tgt", tgt))}
    objs = objectives(src)
    events = {"B0": baseline_events(src, params, objs),
              "P1x3": baseline_events(tgt, params, objectives(tgt))}
    thresholds = {}
    for variant in VARIANTS:
        out = crossfit_lbr_multi(data["src"], variant=variant, objectives=objs, config=config,
                                 targets={"src": data["src"], "tgt": data["tgt"]})
        events[f"LBR_{variant}"] = out["src"].events
        events[f"LBR_{variant}_on_P1x3"] = out["tgt"].events
        thresholds[f"LBR_{variant}"] = {str(k): v for k, v in out["src"].thresholds.items()}
        print(f"LBR {variant}: xong cross-fit", flush=True)
    return {"data": data, "objectives": objs, "events": events, "thresholds": thresholds}


def score_all(src: dict, tgt: dict, events: dict) -> dict:
    class_sets = {"all": src["class_ids"], "vn": vn_class_ids(src["class_ids"])}
    return {name: {point: {s: evaluate(tgt if "P1x3" in name else src, ev[point], ids)
                           for s, ids in class_sets.items()} for point in POINTS}
            for name, ev in events.items()}


def _strip(results: dict) -> dict:
    """Bỏ bảng đếm theo recording (chỉ cần cho bootstrap) khỏi artifact JSON."""
    return {n: {p: {s: {k: v for k, v in m.items() if k != "counts"} for s, m in sets.items()}
                for p, sets in points.items()} for n, points in results.items()}


def _fmt(value: float | None) -> str:
    return "—" if value is None or not np.isfinite(value) else f"{value:.4f}"


def render(result: dict) -> str:
    res, deltas = result["results"], result["deltas"]
    lines = ["# Tầng C — LBR (ADR-0045) và thước ứng dụng (ADR-0046)", "",
             "> OOF 564 recording annotated, 5 fold, cross-fit lồng nhau; λ/t chọn trên các fold "
             "còn lại. CI ghép cặp 1000 lần, seed 20260922, có điều kiện trên thiết kế LBR — thiết "
             "kế đã được thăm dò trên chính OOF này (ADR-0045, Evidence). Không đọc test.", "",
             "## Thước chính — 21 lớp, điểm vận hành F1", "",
             "| Hệ thống | Macro | Micro | Nsys/Nref | Recall | Δ micro [95% CI] |",
             "|---|---:|---:|---:|---:|---|"]
    for name, points in res.items():
        m = points["f1"]["all"]
        d = deltas.get(name)
        delta = (f"{d['estimate']:+.4f} [{d['lower']:+.4f}, {d['upper']:+.4f}] vs {d['baseline']}"
                 if d else "—")
        lines.append(f"| {name} | {_fmt(m['macro_f1'])} | {_fmt(m['micro_f1'])} | "
                     f"{m['nsys']}/{m['nref']} | {_fmt(m['recall'])} | {delta} |")
    for set_name, title in (("all", "21 lớp"), ("vn", "19 lớp Việt Nam")):
        lines += ["", f"## Thước ứng dụng — {title} (báo kèm, không dùng để chọn)", "",
                  "| Hệ thống | Điểm | Micro chính | Collar 1 s | Segment 1 s | Giao nhau P | "
                  "Giao nhau R | Giao nhau F1 | Giao nhau macro |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for name, points in res.items():
            for point in POINTS:
                m = points[point][set_name]
                i = m["intersection"]
                lines.append(f"| {name} | {point} | {_fmt(m['micro_f1'])} | "
                             f"{_fmt(m['event_f1_collar_1s']['micro'])} | "
                             f"{_fmt(m['segment_f1_1s']['micro'])} | "
                             f"{_fmt(i['micro']['precision'])} | {_fmt(i['micro']['recall'])} | "
                             f"{_fmt(i['micro']['f1'])} | {_fmt(i['macro_f1'])} |")
        h = result["human_ceiling"][set_name]
        lines.append(f"| Người–người ({h['pairs']} cặp) | — | {_fmt(h['micro_f1'])} | "
                     f"{_fmt(h['event_f1_collar_1s'])} | {_fmt(h['segment_f1_1s'])} | — | — | "
                     f"{_fmt(h['intersection_f1'])} | — |")
    chosen = result["selected"] or "không ứng viên nào đạt — giữ B0, không mở test"
    return "\n".join([*lines, "", f"Lựa chọn theo luật ADR-0045 §6: **{chosen}**.",
                      f"Sàn precision điểm ưu tiên phát hiện: {RECALL_FIRST_PRECISION_FLOOR}.", ""])


def save_final(out: Path, run: dict, variant: str, src: dict, params: SebbParams,
               config: LbrConfig) -> str:
    """ADR-0045 §7: model cuối fit trên đủ 5 fold OOF; trả SHA-256 của bundle."""
    folds = set(run["data"]["src"].recordings_by_fold)
    model = fit_lbr(run["data"]["src"], fit_folds=folds, variant=variant,
                    objectives=run["objectives"], config=config)
    return save_bundle(out / "lbr_model.pkl", {
        "variant": variant, "refiner_on": model.refiner_on, "refiner_off": model.refiner_off,
        "rescorer": model.rescorer, "thresholds": dict(model.thresholds),
        "n_classes": model.n_classes, "config": config, "class_ids": list(src["class_ids"]),
        "sebb_params": params, "source_run": src["run"].name})


def build_manifest(out: Path, src: dict, tgt: dict, params: SebbParams, config: LbrConfig,
                   selected: str | None, model_sha: str | None) -> dict:
    return {
        "run_id": out.name, "task": "sed_lbr", "complete": True,
        "command": ["python", "-m", "scripts.fit_lbr_oof", *sys.argv[1:]],
        "class_ids": list(src["class_ids"]), **{k: src["manifest"][k] for k in SHARED},
        "config": {"source_run": src["run"].name, "transfer_run": tgt["run"].name,
                   "sebb_params": params.__dict__, "lbr_config": config.__dict__,
                   "lambda_grid": list(LAMBDA_GRID), "t_grid": list(T_GRID),
                   "cv_folds_sha256": sha256_file(FOLDS),
                   "source_dev_sha256": src["dev_predictions_sha256"],
                   "transfer_dev_sha256": tgt["dev_predictions_sha256"],
                   "selected_variant": selected, "model_sha256": model_sha},
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scikit_learn": sklearn.__version__},
        "git": git_state(ROOT),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="OOF B0 (nguồn train)")
    parser.add_argument("--transfer", type=Path, required=True, help="OOF P1×3 (kiểm chuyển)")
    parser.add_argument("--label", default="B0")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/measurements")
    parser.add_argument("--tag", default="LBR")
    args = parser.parse_args()
    now = datetime.now(UTC)
    measurement = args.out_dir / output_name(now, args.tag)
    if measurement.exists() or measurement.with_suffix(".md").exists():
        raise FileExistsError(measurement)
    src, tgt = load(args.source), load(args.transfer)
    if src["recordings"] != tgt["recordings"] or src["folds"] != tgt["folds"]:
        raise ValueError("nguồn và đích kiểm chuyển phải cùng recording và fold")
    params, config = sebb_params(args.source), LbrConfig()
    run = run_all(src, tgt, params, config)
    results = score_all(src, tgt, run["events"])
    deltas = bootstrap(results, [("B0", "LBR_v1"), ("B0", "LBR_v2"),
                                 ("P1x3", "LBR_v1_on_P1x3"), ("P1x3", "LBR_v2_on_P1x3")])
    selected = select_candidate(results, deltas)
    out = ROOT / "ml/runs" / f"sed_lbr_{args.label}_{now:%Y%m%dT%H%M%SZ}"
    out.mkdir(parents=True)
    model_sha = save_final(out, run, selected, src, params, config) if selected else None
    manifest = build_manifest(out, src, tgt, params, config, selected, model_sha)
    result = {"run": out.name, "selected": selected, "deltas": deltas,
              "results": _strip(results), "git": manifest["git"],
              "human_ceiling": {"all": human_ceiling(src["class_ids"]),
                                "vn": human_ceiling(vn_class_ids(src["class_ids"]))},
              "fold_thresholds": run["thresholds"]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    payload = json.dumps(result, ensure_ascii=False, indent=2, default=float)
    (out / "lbr_selection_annotated.json").write_text(payload, encoding="utf-8")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    measurement.write_text(payload, encoding="utf-8")
    measurement.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(measurement)


if __name__ == "__main__":
    main()
