"""Độ phủ ground truth polyphonic của DataSED và đối chiếu với bài báo (nợ #21, phát hiện 27/09).

    .venv/Scripts/python.exe -m scripts.report_polyphonic_coverage \
        --run "(c) v2 ×3=ml/runs/sed_ensemble_v2_20260926T155630Z" ...

Chỉ đọc: hai CSV ground truth gốc trong archive, manifest recording, split đã đóng băng,
annotation đã chuẩn hoá, và Bảng 3 của bài Scientific Data
(`data/reference/datased_paper_table3_monophonic.csv`, trích bằng code từ HTML PMC). Với `--run`:
chỉ **dev** (`predictions/dev.npz` + `postproc_cv.json` của run) — event-F1 micro khi giữ và khi
bỏ các recording không có ground truth polyphonic. In-sample (hậu xử lý chọn trên dev), chỉ để
đo cỡ ảnh hưởng. Không mở test, không đổi split hay annotation.

Ghi `docs/measurements/polyphonic_coverage_<date>.{md,json}`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import (
    priors_from_postproc,
    process_recordings,
    stack_predictions_by_recording,
)
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]
RAW = (ROOT / "data" / "raw" / "datased" / "extracted"
       / "DataSED - DataSED - Dataset for Sound Event Detection of environmental noise"
       / "SED_ground_truth")
TABLE3 = ROOT / "data" / "reference" / "datased_paper_table3_monophonic.csv"
# Fredianelli et al. 2025, Scientific Data, doi:10.1038/s41597-025-05991-w — văn bản mục "Data
# Record" và "Background & Summary", đọc trực tiếp 27/09/2026.
PAPER = {"files": 712, "last_id": "S-0712", "min_s": 2.29, "max_s": 285.0, "mean_s": 87.18,
         "total_h": 17.02, "polyphonic_labels": 4034, "monophonic_labels": 4309}
TABLE3_ALIASES = {"Cat fights and moans": "Cat fight and moans"}  # tên trong bảng ≠ nhãn archive


def raw_recordings(name: str) -> set[str]:
    table = pd.read_csv(RAW / f"{name}_sound_detection.csv")
    return set(table["sound_name"].str.extract(r"(S-\d{4})")[0])


def archive_facts(recordings: pd.DataFrame, mono: pd.DataFrame, poly: pd.DataFrame
                  ) -> dict[str, object]:
    durations = recordings["duration_s"]
    return {"files": len(recordings), "last_id": recordings["recording_id"].max(),
            "min_s": float(durations.min()), "max_s": float(durations.max()),
            "mean_s": float(durations.mean()), "total_h": float(durations.sum() / 3600),
            "polyphonic_labels": len(poly), "monophonic_labels": len(mono)}


def table3_comparison(mono: pd.DataFrame) -> list[dict[str, object]]:
    table = pd.read_csv(TABLE3)
    lengths = mono.assign(length=mono["offset_s"] - mono["onset_s"]).groupby("raw_class_label")
    archive = lengths["length"].agg(["size", "sum"])
    rows = []
    for row in table.itertuples(index=False):
        label = TABLE3_ALIASES.get(row.class_name, row.class_name)
        if label not in archive.index:
            raise SystemExit(f"Bảng 3: lớp {row.class_name!r} không khớp nhãn nào trong archive")
        rows.append({"class_name": row.class_name, "paper_labels": int(row.n_labels),
                     "archive_labels": int(archive.loc[label, "size"]),
                     "paper_sum_s": float(row.duration_sum_s),
                     "archive_sum_s": float(archive.loc[label, "sum"])})
    return rows


def uncovered_summary(recordings: pd.DataFrame, splits: pd.Series, mono: pd.DataFrame,
                      covered: set[str], class_ids: tuple[str, ...]) -> dict[str, object]:
    missing = sorted(set(recordings["recording_id"]) - covered)
    in_classes = mono[mono["recording_id"].isin(missing) & mono["class_id"].isin(class_ids)]
    per_split = {}
    for split in ("train", "validation", "test"):
        ids = [rid for rid in missing if splits[rid] == split]
        per_split[split] = {
            "recordings": ids,
            "hours": float(recordings.set_index("recording_id").loc[ids, "duration_s"].sum()
                           / 3600) if ids else 0.0,
            "mono_events_in_polyphonic_classes": int(in_classes["recording_id"].isin(ids).sum()),
        }
    only_wind = set(mono.loc[mono["class_id"] == "wind_turbine", "recording_id"])
    return {"recordings": missing, "per_split": per_split,
            "wind_turbine_recordings_equal_uncovered": only_wind == set(missing)}


def dev_impact(label: str, run: Path, class_ids: tuple[str, ...], uncovered: set[str]
               ) -> dict[str, object]:
    artifact = load_predictions(run / "predictions" / "dev.npz", expected_class_ids=class_ids)
    if artifact.split != "dev":
        raise SystemExit(f"{run}: cần predictions dev, nhận {artifact.split!r}")
    postproc = json.loads((run / "postproc_cv.json").read_text(encoding="utf-8"))
    probabilities = stack_predictions_by_recording(artifact)
    estimate = process_recordings(
        probabilities, class_ids=class_ids,
        thresholds={c: postproc["per_class"][c]["theta"] for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids),
        frame_rate=1.0 / artifact.frame_hop_s)
    reference = load_events_by_recording(set(probabilities))
    kept = {rid for rid in probabilities if rid not in uncovered}

    def micro(ids: set[str]) -> float:
        result = event_based_f1({r: reference[r] for r in ids},
                                {r: estimate.get(r, []) for r in ids},
                                event_label_list=list(class_ids))
        return float(result["f_measure"]["f_measure"])

    return {"label": label, "run": run.name, "dev_recordings": len(probabilities),
            "micro_all": micro(set(probabilities)), "micro_without_uncovered": micro(kept),
            "predicted_events_in_uncovered": sum(len(estimate.get(r, [])) for r in uncovered
                                                 if r in probabilities),
            "predicted_events_total": sum(len(v) for v in estimate.values())}


def to_markdown(result: dict[str, object]) -> str:
    paper, archive = result["paper"], result["archive"]
    title = "Độ phủ ground truth polyphonic DataSED và đối chiếu bài báo"
    lines = [f"# {title} — {result['date']}", "",
             "Sinh bởi `scripts/report_polyphonic_coverage.py`. Chỉ đọc; không mở test, không đổi "
             "split hay annotation.", "",
             "## 1. Độ phủ ground truth gốc", "",
             f"- `Polyphonic_sound_detection.csv` phủ **{result['polyphonic_recordings']}** "
             f"recording; `Monophonic_sound_detection.csv` phủ {result['monophonic_recordings']}; "
             f"archive có {archive['files']} WAV.",
             "- Recording có trong split polyphonic nhưng **không có dòng nào** trong ground "
             f"truth polyphonic: {len(result['uncovered']['recordings'])} "
             f"({result['uncovered']['recordings'][0]}…{result['uncovered']['recordings'][-1]}).",
             "- Tập này trùng đúng tập recording có nhãn monophonic `wind_turbine`: "
             f"{result['uncovered']['wind_turbine_recordings_equal_uncovered']}.", "",
             "| Split | Recording | Giờ | Nhãn monophonic thuộc 21 lớp polyphonic |",
             "|---|---|---:|---:|"]
    for split, row in result["uncovered"]["per_split"].items():
        lines.append(f"| {split} | {', '.join(row['recordings'])} | {row['hours']:.3f} | "
                     f"{row['mono_events_in_polyphonic_classes']} |")
    lines += ["", "Trong benchmark hiện tại, các recording này được coi là **không có sự kiện "
              "nào**: dự đoán ở đó tính là FP, sự kiện thật không tính là FN, và khi train "
              "chúng là mẫu âm.",
              "", "## 2. Bài báo và archive", "",
              "| | Bài báo (văn bản) | Archive đo được |", "|---|---:|---:|"]
    for key in PAPER:
        value = archive[key]
        shown = f"{value:.2f}" if isinstance(value, float) else str(value)
        lines.append(f"| {key} | {paper[key]} | {shown} |")
    rows = result["table3"]
    lines += ["", f"Bảng 3 của bài (monophonic): tổng {sum(r['paper_labels'] for r in rows)} nhãn, "
              f"trong khi văn bản bài ghi {paper['monophonic_labels']}.", "",
              "| Lớp (tên trong bài) | Nhãn bài | Nhãn archive | Tổng s bài | Tổng s archive |",
              "|---|---:|---:|---:|---:|"]
    lines += [f"| {r['class_name']} | {r['paper_labels']} | {r['archive_labels']} | "
              f"{r['paper_sum_s']:.1f} | {r['archive_sum_s']:.1f} |" for r in rows]
    if result["dev_impact"]:
        lines += ["", "## 3. Cỡ ảnh hưởng trên dev (in-sample, hậu xử lý `postproc_cv.json`)", "",
                  "| Ứng viên | Event-F1 micro dev, 137 recording | Bỏ recording thiếu GT | "
                  "Dự đoán rơi vào recording thiếu GT / tổng |", "|---|---:|---:|---:|"]
        lines += [f"| {d['label']} | {d['micro_all']:.4f} | {d['micro_without_uncovered']:.4f} | "
                  f"{d['predicted_events_in_uncovered']} / {d['predicted_events_total']} |"
                  for d in result["dev_impact"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="append", default=[], help="nhãn=đường dẫn run")
    args = parser.parse_args()
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    recordings = pd.read_csv(ROOT / "data" / "manifests" / "datased_recordings.csv")
    splits = pd.read_csv(ROOT / "data" / "splits" / "datased_polyphonic.csv").set_index(
        "recording_id")["split"]
    mono = pd.read_csv(ROOT / "data" / "annotations" / "datased_monophonic_events.csv")
    poly = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    covered = raw_recordings("Polyphonic")
    uncovered = uncovered_summary(recordings, splits, mono, covered, class_ids)
    result = {
        "date": date.today().isoformat(),
        "polyphonic_recordings": len(covered),
        "monophonic_recordings": len(raw_recordings("Monophonic")),
        "uncovered": uncovered,
        "paper": PAPER, "archive": archive_facts(recordings, mono, poly),
        "table3": table3_comparison(mono),
        "dev_impact": [dev_impact(label, ROOT / path, class_ids, set(uncovered["recordings"]))
                       for label, path in (re.split(r"=", spec, maxsplit=1) for spec in args.run)],
    }
    stem = ROOT / "docs" / "measurements" / f"polyphonic_coverage_{date.today():%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(to_markdown(result), encoding="utf-8")
    print(to_markdown(result))


if __name__ == "__main__":
    main()
