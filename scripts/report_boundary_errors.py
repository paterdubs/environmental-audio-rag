"""Phân bố xác suất frame và sai số biên có dấu của hệ thống SED — **chỉ dev** (PLAN nợ #22).

    .venv/Scripts/python.exe -m scripts.report_boundary_errors \\
        --run "v1 ensemble C=ml/runs/sed_ensemble_C_clean_20260925T045631Z" \\
        --run "v2 seed 20260922=ml/runs/<run>"            # hậu xử lý: postproc_cv.json

Hai câu hỏi cho paper (PAPER_NOTES §4):

1. **Posterior có bão hoà không?** Theo lớp: trung vị và tỉ lệ frame **âm** có p ≥ 0.5 / 0.9 /
   0.95; trung vị và tỉ lệ frame **dương** vượt các ngưỡng đó; báo macro theo lớp.
2. **Onset/offset lệch về phía nào?** Mỗi event tham chiếu ghép với event dự đoán cùng lớp chồng
   lấn nhiều nhất (hậu xử lý đã chọn của run): sai số có dấu (dự đoán − tham chiếu), trung vị,
   tứ phân vị, tỉ lệ trong ±0.2 s, trễ > 0.2 s, sớm < −0.2 s.

Đo 26/09 trên v1 (bản nháp): frame âm có trung vị 0.008, onset lệch **đối xứng** (IQR −0.39…
+0.51 s) — bác bỏ giả thuyết "posterior bão hoà làm onset trễ" của bản đầu ADR-0030.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ml.evaluation.predictions import load_predictions
from ml.postprocessing import process_recordings
from ml.postprocessing.calibration import priors_from_postproc, stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_sed_ceilings import ground_truth_frames, load_tables, reference_events

ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = (0.5, 0.9, 0.95)
COLLAR_S = 0.2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="append", required=True,
                        help="'nhãn=ml/runs/<run>' hoặc 'nhãn=ml/runs/<run>:postproc_file.json'")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "measurements")
    return parser.parse_args()


def score_distribution(probabilities: dict, truth: dict, class_ids: tuple[str, ...]) -> dict:
    """Per class: quantiles of p on negative and on positive frames (dev)."""
    rows = {}
    for index, class_id in enumerate(class_ids):
        neg = np.concatenate([p[: len(truth[r]), index][truth[r][: len(p), index] == 0]
                              for r, p in probabilities.items()])
        pos = np.concatenate([p[: len(truth[r]), index][truth[r][: len(p), index] == 1]
                              for r, p in probabilities.items()])
        rows[class_id] = {
            "neg_median": float(np.median(neg)),
            **{f"neg_ge_{t}": float((neg >= t).mean()) for t in THRESHOLDS},
            "pos_median": float(np.median(pos)) if pos.size else float("nan"),
            **{f"pos_ge_{t}": float((pos >= t).mean()) if pos.size else float("nan")
               for t in THRESHOLDS},
            "n_pos_frames": int(pos.size)}
    return rows


def signed_errors(reference: dict, estimate: dict) -> tuple[np.ndarray, np.ndarray]:
    """Onset and offset errors (estimate − reference) of each reference event's best match."""
    onsets, offsets = [], []
    for recording_id, refs in reference.items():
        candidates = estimate.get(recording_id, [])
        for ref in refs:
            same = [e for e in candidates if e["class_id"] == ref["event_label"]]
            overlaps = [min(ref["offset"], e["offset_s"]) - max(ref["onset"], e["onset_s"])
                        for e in same]
            if overlaps and max(overlaps) > 0:
                best = same[int(np.argmax(overlaps))]
                onsets.append(best["onset_s"] - ref["onset"])
                offsets.append(best["offset_s"] - ref["offset"])
    return np.asarray(onsets), np.asarray(offsets)


def summarize(errors: np.ndarray) -> dict:
    if errors.size == 0:
        return {"n": 0}
    return {"n": int(errors.size), "median": float(np.median(errors)),
            "q25": float(np.percentile(errors, 25)), "q75": float(np.percentile(errors, 75)),
            "within_collar": float((np.abs(errors) <= COLLAR_S).mean()),
            "late": float((errors > COLLAR_S).mean()), "early": float((errors < -COLLAR_S).mean())}


def analyse(spec: str, class_ids: tuple[str, ...], tables: tuple) -> dict:
    label, _, target = spec.partition("=")
    path, separator, postproc_name = target.rpartition(":")
    if not separator or not postproc_name.endswith(".json"):  # "D:/…" is a drive, not a suffix
        path, postproc_name = target, "postproc_cv.json"
    run_dir = Path(path)
    artifact = load_predictions(run_dir / "predictions/dev.npz", expected_class_ids=class_ids)
    probabilities = stack_predictions_by_recording(artifact)
    recordings, events = tables
    dev = recordings[recordings["split"] == "validation"]
    reference = reference_events(events, dev["recording_id"].tolist())
    durations = dict(zip(dev["recording_id"], dev["duration_s"], strict=True))
    truth = {r: ground_truth_frames(reference[r], durations[r], class_ids) for r in probabilities}
    postproc = json.loads((run_dir / postproc_name).read_text(encoding="utf-8"))
    estimate = process_recordings(
        probabilities, class_ids=class_ids,
        thresholds={c: postproc["per_class"][c]["theta"] for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids), frame_rate=1.0 / artifact.frame_hop_s)
    per_class = score_distribution(probabilities, truth, class_ids)
    onsets, offsets = signed_errors(reference, estimate)
    macro = {key: float(np.nanmean([row[key] for row in per_class.values()]))
             for key in next(iter(per_class.values())) if key != "n_pos_frames"}
    return {"label": label, "run": run_dir.name, "postproc": postproc_name, "macro": macro,
            "per_class": per_class, "onset": summarize(onsets), "offset": summarize(offsets)}


def render(results: list[dict], git: dict) -> str:
    lines = [
        "# Phân bố xác suất và sai số biên — dev (PLAN nợ #22)", "",
        "> Sinh bởi `scripts.report_boundary_errors`. Chỉ dev; hậu xử lý = file đã chọn trên dev "
        f"của từng run (in-sample). git `{git['revision'][:7]}`.", "",
        "## 1. Xác suất trên frame âm / dương (macro theo lớp)", "",
        "| Hệ thống | âm: trung vị | âm ≥ 0.5 | âm ≥ 0.95 | dương: trung vị | dương ≥ 0.5 | "
        "dương ≥ 0.95 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in results:
        m = r["macro"]
        lines.append(f"| {r['label']} | {m['neg_median']:.3f} | {m['neg_ge_0.5']:.3f} | "
                     f"{m['neg_ge_0.95']:.3f} | {m['pos_median']:.3f} | {m['pos_ge_0.5']:.3f} | "
                     f"{m['pos_ge_0.95']:.3f} |")
    lines += ["", "## 2. Sai số biên có dấu (dự đoán − tham chiếu, giây)", "",
              "| Hệ thống | Biên | n | trung vị | [q25, q75] | trong ±0.2 s | trễ > 0.2 s | "
              "sớm < −0.2 s |", "|---|---|---:|---:|---|---:|---:|---:|"]
    for r in results:
        for side in ("onset", "offset"):
            s = r[side]
            if s["n"]:
                lines.append(f"| {r['label']} | {side} | {s['n']} | {s['median']:+.2f} | "
                             f"[{s['q25']:+.2f}, {s['q75']:+.2f}] | {s['within_collar']:.3f} | "
                             f"{s['late']:.3f} | {s['early']:.3f} |")
    lines += ["", "Chi tiết theo lớp trong file `.json` đi kèm."]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    tables = load_tables()
    results = [analyse(spec, class_ids, tables) for spec in args.run]
    git = git_state(ROOT)
    out = args.out_dir / f"boundary_errors_{datetime.now(UTC):%Y%m%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps({"results": results, "git": git}, indent=1,
                                                   ensure_ascii=False), encoding="utf-8")
    out.write_text(render(results, git), encoding="utf-8")
    print(render(results, git))


if __name__ == "__main__":
    main()
