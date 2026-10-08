"""Tách nhận dạng và định vị của RQ1 trên dev để kiểm cơ chế transfer DataSEC.

Đọc lịch sử và dự đoán đã lưu, không nạp model. Hậu xử lý chọn trên dev:
mọi F1 ở đây là in-sample, không phải ước lượng độc lập hay phép chọn model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from scipy.special import expit
from sklearn.metrics import average_precision_score

from ml.evaluation.predictions import PredictionArtifact, load_predictions
from ml.postprocessing import process_recordings
from ml.postprocessing.calibration import priors_from_postproc, stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_sed_ceilings import f1, load_tables, reference_events, segment_f1

ROOT = Path(__file__).resolve().parents[1]
EPOCHS = (1, 3, 5, 10, 30)
HISTORY_METRICS = ("macro_average_precision", "macro_f1", "loss")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def learning_curve(path: Path) -> dict:
    history = json.loads(path.read_text(encoding="utf-8"))["epochs"]
    numbers = [int(row["epoch"]) for row in history]
    if not numbers or len(set(numbers)) != len(numbers):
        raise ValueError("History phải có epoch duy nhất, không rỗng")
    history = sorted(history, key=lambda row: row["epoch"])
    curve = [{"epoch": int(row["epoch"]),
              **{key: float(row["validation"][key]) for key in HISTORY_METRICS}}
             for row in history]
    sampled = {str(epoch): next((r for r in curve if r["epoch"] == epoch), None)
               for epoch in EPOCHS}
    best = {}
    for key in HISTORY_METRICS:
        selected = (min if key == "loss" else max)(curve, key=lambda row: row[key])
        best[key] = {"epoch": selected["epoch"], "value": selected[key]}
    return {"curve": curve, "selected_epochs": sampled, "best": best}


def frame_map(artifact: PredictionArtifact, recording_ids: list[str]) -> dict:
    keep = artifact.mask & np.isin(artifact.recording_ids, recording_ids)[:, None]
    target = artifact.targets[keep]
    scores = expit(artifact.logits[keep].astype(np.float64))
    active = np.flatnonzero(target.sum(axis=0) > 0)
    if not len(active):
        raise ValueError("Dev annotated không có frame positive")
    per_class = {artifact.class_ids[i]: float(average_precision_score(target[:, i], scores[:, i]))
                 for i in active}
    return {"value": float(np.mean(list(per_class.values()))), "per_class": per_class,
            "n_valid_window_frames": int(keep.sum()), "n_active_classes": len(active),
            "aggregation": "window frames trên mask; frame chồng cửa sổ vẫn được giữ"}


def decompose(run: Path, reference: dict, class_ids: tuple[str, ...]) -> dict:
    prediction_path = run / "predictions/dev.npz"
    postproc_path = run / "postproc_cv.json"
    artifact = load_predictions(prediction_path, expected_class_ids=class_ids)
    if artifact.split != "dev":
        raise ValueError("Chỉ chấp nhận prediction dev")
    postproc = json.loads(postproc_path.read_text(encoding="utf-8"))
    if postproc["class_ids"] != list(class_ids) or postproc["calibrated_on"] != "dev":
        raise ValueError("Hậu xử lý phải đúng class order và calibrated_on=dev")
    probabilities = stack_predictions_by_recording(artifact)
    missing = set(reference) - probabilities.keys()
    if missing:
        raise ValueError(f"Thiếu recording dev annotated: {sorted(missing)}")
    estimate = process_recordings(
        {rid: probabilities[rid] for rid in reference}, class_ids=class_ids,
        thresholds={c: postproc["per_class"][c]["theta"] for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids), frame_rate=1 / artifact.frame_hop_s)
    ap = frame_map(artifact, list(reference))
    return {"metrics": {
        "frame_map": ap["value"], "segment_f1_1s": segment_f1(reference, estimate, class_ids),
        "event_f1_collar_1s": f1(reference, estimate, class_ids, t_collar=1.0,
                                  percentage_of_length=0.5),
        "event_f1_offset_only": f1(reference, estimate, class_ids, evaluate_onset=False),
        "event_f1_onset_only": f1(reference, estimate, class_ids, evaluate_offset=False),
        "event_f1": f1(reference, estimate, class_ids)}, "frame_ap_details": ap,
        "n_annotated_recordings": len(reference),
        "inputs": {str(p): sha256(p) for p in (prediction_path, postproc_path)}}


def branch_summary(runs: list[dict]) -> dict:
    metrics = {key: float(np.mean([run["metrics"][key] for run in runs]))
               for key in runs[0]["metrics"]}
    epochs = {}
    for epoch in EPOCHS:
        available = [run["learning"]["selected_epochs"][str(epoch)] for run in runs]
        available = [row for row in available if row is not None]
        epochs[str(epoch)] = {"n_runs": len(available), **{
            key: float(np.mean([row[key] for row in available])) if available else None
            for key in HISTORY_METRICS}}
    best = {key: float(np.mean([run["learning"]["best"][key]["value"] for run in runs]))
            for key in HISTORY_METRICS}
    return {"n_runs": len(runs), "metrics": metrics, "selected_epochs": epochs,
            "mean_of_run_best": best}


def compare_branches(branches: dict[str, list[dict]]) -> dict:
    means = {branch: branch_summary(runs) for branch, runs in branches.items()}
    comparison = {}
    for key in means["B"]["metrics"]:
        wins = sum(c["metrics"][key] > b["metrics"][key]
                   for b in branches["B"] for c in branches["C"])
        comparison[key] = {"delta_c_minus_b": means["C"]["metrics"][key]
                           - means["B"]["metrics"][key], "c_gt_b_pairs": wins,
                           "total_pairs": len(branches["B"]) * len(branches["C"])}
    return {"branch_means": means, "comparison": comparison}


def plot_curves(branches: dict[str, list[dict]], out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))
    styles = ("-", "--", ":", "-.")
    for branch, runs in branches.items():
        for index, run in enumerate(runs):
            curve = run["learning"]["curve"]
            ax.plot([r["epoch"] for r in curve], [r["macro_average_precision"] for r in curve],
                    color={"B": "#1674b8", "C": "#df6d14"}[branch],
                    linestyle=styles[index % len(styles)], label=f"{branch}: {run['run']}")
    ax.set(xlabel="Epoch", ylabel="Validation frame mAP", title="RQ1: learning curves (dev)")
    ax.legend(fontsize=6)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def render(result: dict, image_name: str) -> str:
    lines = ["# Cơ chế RQ1: nhận dạng và định vị", "",
             "Sinh bởi `scripts.report_rq1_mechanism`; chỉ history + prediction dev.", "",
             "**Dev annotated, in-sample:** hậu xử lý được chọn trên dev. Chỉ dùng so B với C; "
             "không dùng chọn hệ thống hoặc tuyên bố suy rộng. Event/segment-F1 là micro; "
             "frame mAP là macro trên lớp có positive. Frame AP lấy window frames hợp lệ "
             "trong mask, còn F1 dùng xác suất ghép theo recording, bỏ recording thiếu GT.", "",
             "Collar chuẩn: onset 0.2 s, offset max(0.2 s, 20% độ dài). Collar 1 s: onset "
             "1 s, offset max(1 s, 50% độ dài). Chỉ onset/offset giữ collar chuẩn.", "",
             f"![Đường cong học]({image_name})", "", "## Phân rã dev", "",
             "| Metric | B mean | C mean | C − B | C>B / tổng cặp |",
             "|---|---:|---:|---:|---:|"]
    means = result["branch_means"]
    for key, row in result["comparison"].items():
        lines.append(f"| {key} | {means['B']['metrics'][key]:.6f} | "
                     f"{means['C']['metrics'][key]:.6f} | {row['delta_c_minus_b']:+.6f} | "
                     f"{row['c_gt_b_pairs']}/{row['total_pairs']} |")
    lines += ["", "## Lịch sử validation", "",
              "Giá trị tốt nhất được lấy riêng theo từng metric (loss lấy min); "
              "không đồng nghĩa checkpoint đã chọn. Thiếu epoch ghi null, không nội suy.", "",
              "| Nhánh/run | Epoch | mAP | Macro-F1 | Loss |", "|---|---|---|---|---|"]
    for branch, runs in result["runs"].items():
        for run in runs:
            for epoch, row in run["learning"]["selected_epochs"].items():
                values = [row[key] if row else None for key in HISTORY_METRICS]
                lines.append(f"| {branch}/{run['run']} | {epoch} | "
                             + " | ".join(str(v) for v in values) + " |")
            lines.append(f"| {branch}/{run['run']} | best | " + " | ".join(
                str(run["learning"]["best"][key]) for key in HISTORY_METRICS) + " |")
        for epoch, row in means[branch]["selected_epochs"].items():
            lines.append(f"| {branch} mean (n={row['n_runs']}) | {epoch} | " + " | ".join(
                str(row[key]) for key in HISTORY_METRICS) + " |")
        lines.append(f"| {branch} mean best | best | " + " | ".join(
            str(means[branch]["mean_of_run_best"][key]) for key in HISTORY_METRICS) + " |")
    lines += ["", "Chi tiết mỗi run, AP theo lớp, SHA-256 nguồn và git provenance ở JSON."]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-b", type=Path, nargs="+", required=True)
    parser.add_argument("--branch-c", type=Path, nargs="+", required=True)
    parser.add_argument("--date", default=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
                        .strftime("%Y%m%d"))
    args = parser.parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    recordings, events = load_tables()
    annotated = recordings[(recordings["split"] == "validation")
                            & recordings["recording_id"].isin(events["recording_id"])]
    reference = reference_events(events, annotated["recording_id"].tolist())
    branches = {}
    for branch, paths in (("B", args.branch_b), ("C", args.branch_c)):
        branches[branch] = []
        for path in paths:
            path = path.resolve()
            history_path = path / "logs/history.json"
            row = {"run": path.name, "path": str(path), "learning": learning_curve(history_path),
                   "history_sha256": sha256(history_path), **decompose(path, reference, class_ids)}
            branches[branch].append(row)
            print(f"{branch}: {path.name}: {row['metrics']}", flush=True)
    result = {"git": git_state(ROOT), "runs": branches, **compare_branches(branches),
              "annotated_recording_ids": list(reference), "source_sha256": {
                  name: sha256(ROOT / name) for name in (
                      "data/manifests/datased_recordings.csv", "data/splits/datased_polyphonic.csv",
                      "data/annotations/datased_polyphonic_events.csv",
                      "ml/configs/taxonomy.yaml")}}
    out = ROOT / f"docs/measurements/rq1_mechanism_{args.date}"
    plot_curves(branches, out.with_suffix(".png"))
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    out.with_suffix(".md").write_text(render(result, out.with_suffix(".png").name),
                                      encoding="utf-8")


if __name__ == "__main__":
    main()
