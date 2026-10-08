"""Đo hồ sơ dữ liệu từ bảng đóng băng để kiểm lại chẩn đoán giai đoạn O.

Không đọc audio hay prediction; thống kê test chỉ mô tả annotation đã có,
không suy duration prior hoặc chọn cấu hình từ các thống kê này.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from ml.dataops.datasec_labels import path_labels
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_annotation_consistency import identical_pairs

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "recordings": "data/manifests/datased_recordings.csv",
    "splits": "data/splits/datased_polyphonic.csv",
    "poly": "data/annotations/datased_polyphonic_events.csv",
    "mono": "data/annotations/datased_monophonic_events.csv",
    "clips": "data/manifests/datasec_inventory.csv",
    "taxonomy": "ml/configs/taxonomy.yaml",
}
QUANTILES = (0, 0.05, 0.25, 0.5, 0.75, 0.95, 1)


def summary(values) -> dict:
    values = np.asarray(list(values), dtype=float)
    return {"count": len(values), "mean": float(values.mean()) if len(values) else None,
            "quantiles": {f"{q:g}": float(np.quantile(values, q)) if len(values) else None
                          for q in QUANTILES}}


def event_summary(events: pd.DataFrame) -> dict:
    durations = events["offset_s"] - events["onset_s"]
    return {**summary(durations), "under_0_5s": int((durations < 0.5).sum()),
            "under_1s": int((durations < 1).sum()),
            "percent_under_1s": float((durations < 1).mean() * 100) if len(events) else None}


def grid_coverage(recordings: pd.DataFrame, events: pd.DataFrame) -> dict:
    """Đếm event (kể cả cùng lớp) tại t=0,0.1,…<duration; khoảng [onset,offset)."""
    counts = np.zeros(4, dtype=np.int64)
    groups = {rid: group for rid, group in events.groupby("recording_id")}
    for row in recordings.itertuples(index=False):
        times = np.arange(math.ceil(row.duration_s / 0.1)) * 0.1
        changes = np.zeros(len(times) + 1, dtype=np.int64)
        group = groups.get(row.recording_id)
        if group is not None:
            starts = np.searchsorted(times, group["onset_s"].to_numpy(), side="left")
            stops = np.searchsorted(times, group["offset_s"].to_numpy(), side="left")
            np.add.at(changes, starts, 1)
            np.add.at(changes, stops, -1)
        active = np.cumsum(changes[:-1])
        counts += np.bincount(np.minimum(active, 3), minlength=4)
    total = int(counts.sum())
    return {"grid_step_s": 0.1, "points": total, "counts": counts.tolist(),
            "fractions": (counts / total).tolist() if total else [None] * 4}


def gap_summary(events: pd.DataFrame) -> dict:
    gaps = []
    for _, group in events.groupby(["recording_id", "class_id"]):
        ordered = group.sort_values(["onset_s", "offset_s"])
        gaps.extend(ordered["onset_s"].to_numpy()[1:] - ordered["offset_s"].to_numpy()[:-1])
    values = np.asarray(gaps)
    return {**summary(gaps), "under_1s": int((values < 1).sum()),
            "overlapping": int((values < 0).sum())}


def missing_gt(recordings: pd.DataFrame, poly: pd.DataFrame, mono: pd.DataFrame) -> dict:
    missing = recordings[~recordings["recording_id"].isin(poly["recording_id"])]
    result = {}
    for split, group in missing.groupby("split"):
        selected = mono[mono["recording_id"].isin(group["recording_id"])]
        result[split] = {"recording_ids": sorted(group["recording_id"].tolist()),
                         "count": len(group), "duration_s": float(group["duration_s"].sum()),
                         "mono_events": len(selected),
                         "mono_by_class": selected["class_id"].value_counts().to_dict()}
    return result


def train_windows(recordings: pd.DataFrame) -> dict:
    train = recordings[recordings["split"] == "train"].copy()
    train["windows"] = np.ceil(train["duration_s"] / 10).astype(int)
    ordered = train.sort_values(["duration_s", "recording_id"], ascending=[False, True])
    total = int(train["windows"].sum())
    return {"window_s": 10, "total": total,
            "per_recording": dict(zip(train["recording_id"], train["windows"], strict=True)),
            "top20_fraction": float(ordered.head(20)["windows"].sum() / total),
            "top5_fraction": float(ordered.head(5)["windows"].sum() / total),
            "longest": ordered.head(20)[["recording_id", "duration_s", "windows"]]
            .to_dict(orient="records")}


def mono_comparison(poly: pd.DataFrame, mono: pd.DataFrame, class_ids: tuple[str, ...]) -> dict:
    keys = ["recording_id", "class_id", "onset_s", "offset_s"]
    eligible = mono[mono["class_id"].isin(class_ids)]
    matched = eligible.merge(poly[keys].drop_duplicates(), on=keys, how="inner")
    return {"poly_events": len(poly), "mono_events": len(mono),
            "mono_21class_events": len(eligible), "mono_exact_matches": len(matched),
            "by_class": [{"class_id": c, "poly": int((poly["class_id"] == c).sum()),
                          "mono": int((mono["class_id"] == c).sum())}
                         for c in sorted(set(poly["class_id"]) | set(mono["class_id"]))]}


def build_profile(root: Path) -> dict:
    tables = {key: pd.read_csv(root / path) for key, path in SOURCES.items()
              if key != "taxonomy"}
    taxonomy = load_taxonomy(root / SOURCES["taxonomy"])
    recordings = tables["recordings"].merge(tables["splits"], on="recording_id",
                                           validate="one_to_one")
    poly, mono = tables["poly"], tables["mono"]
    events = poly.merge(recordings[["recording_id", "split"]], on="recording_id",
                        validate="many_to_one")
    by_class = []
    for split in sorted(recordings["split"].unique()):
        for class_id in taxonomy.polyphonic_class_ids:
            selected = events[(events["split"] == split) & (events["class_id"] == class_id)]
            by_class.append({"split": split, "class_id": class_id, **event_summary(selected)})
    clips = tables["clips"].copy()
    clips["class_id"] = [path_labels(path, taxonomy)[0] for path in clips["relative_path"]]
    split_map = recordings.set_index("recording_id")["split"].to_dict()
    pairs = [{"left": a, "right": b, "left_split": split_map[a], "right_split": split_map[b]}
             for a, b in identical_pairs(recordings)]
    return {
        "sources": {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                    for path in SOURCES.values()},
        "recording_duration_by_split": {s: summary(g["duration_s"])
                                        for s, g in recordings.groupby("split")},
        "poly_by_class_split": by_class, "poly_event_duration": event_summary(poly),
        "coverage_by_split": {s: grid_coverage(g, poly)
                              for s, g in recordings.groupby("split")},
        "same_class_gaps": gap_summary(poly),
        "gaps_by_split": {s: gap_summary(g) for s, g in events.groupby("split")},
        "missing_poly_gt": missing_gt(recordings, poly, mono), "identical_pairs": pairs,
        "train_windows": train_windows(recordings),
        "mono_vs_poly": mono_comparison(poly, mono, taxonomy.polyphonic_class_ids),
        "datasec_duration": summary(clips["duration_s"]),
        "datasec_by_class": [{"class_id": c, **summary(g["duration_s"])}
                             for c, g in clips.groupby("class_id")],
    }


def table(headers: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers))
            + " |", *["| " + " | ".join(str(v) for v in row) + " |" for row in rows]]


def render(result: dict) -> str:
    lines = ["# Hồ sơ dữ liệu giai đoạn O", "", "Sinh bởi `scripts.report_data_profile`.", "",
             "Chỉ đọc manifest/split/annotation đã đóng băng. Không đọc prediction hoặc audio. "
             "Thống kê test là mô tả dữ liệu, không dùng chọn hệ thống hoặc suy prior.", "",
             "Lưới thời gian: t=0,0.1,…<duration, event hoạt động khi onset ≤ t < offset. "
             "Đếm số event, kể cả event cùng lớp. Gap có dấu: onset kế − offset trước; "
             "giữ số âm khi chồng lấn. Cửa sổ train: ceil(duration/10), không bỏ GT thiếu.", ""]
    sections = [
        ("Độ dài recording theo split (giây)", ["Split", "N", "Mean", "Quantile"],
         [[s, v["count"], v["mean"], v["quantiles"]]
          for s, v in result["recording_duration_by_split"].items()]),
        ("Event polyphonic theo lớp × split", ["Split", "Lớp", "N", "Median s", "% <1s"],
         [[v["split"], v["class_id"], v["count"], v["quantiles"]["0.5"],
           v["percent_under_1s"]] for v in result["poly_by_class_split"]]),
        ("Độ phủ trên lưới 0.1 s", ["Split", "Số điểm", "0 / 1 / 2 / ≥3"],
         [[s, v["points"], v["fractions"]] for s, v in result["coverage_by_split"].items()]),
        ("Thiếu GT polyphonic", ["Split", "Recording", "Mono theo lớp"],
         [[s, v["recording_ids"], v["mono_by_class"]]
          for s, v in result["missing_poly_gt"].items()]),
        ("Recording giống byte", ["Trái", "Phải", "Split trái", "Split phải"],
         [[v[k] for k in ("left", "right", "left_split", "right_split")]
          for v in result["identical_pairs"]]),
        ("Mono vs poly theo lớp", ["Lớp", "Poly", "Mono"],
         [[v["class_id"], v["poly"], v["mono"]] for v in result["mono_vs_poly"]["by_class"]]),
        ("DataSEC v3 theo lớp (giây)", ["Lớp", "N", "Median", "Min", "Max"],
         [[v["class_id"], v["count"], v["quantiles"]["0.5"], v["quantiles"]["0"],
           v["quantiles"]["1"]] for v in result["datasec_by_class"]]),
    ]
    for title, headers, rows in sections:
        lines += [f"## {title}", "", *table(headers, rows), ""]
    for key in ("poly_event_duration", "same_class_gaps", "gaps_by_split", "datasec_duration"):
        lines += [f"## {key}", "", "```json", json.dumps(result[key], ensure_ascii=False,
                                                                    indent=2), "```", ""]
    windows = result["train_windows"]
    lines += ["## Cửa sổ train 10 s", "", f"Tổng: {windows['total']}; "
              f"top-20: {windows['top20_fraction']}; top-5: {windows['top5_fraction']}.", "",
              *table(["Recording", "Giây", "Cửa sổ"],
                     [[v["recording_id"], v["duration_s"], v["windows"]]
                      for v in windows["longest"]]), "",
              f"Mono khớp khít poly (21 lớp): {result['mono_vs_poly']['mono_exact_matches']} / "
              f"{result['mono_vs_poly']['mono_21class_events']} event mono.", "",
              "Hash từng bảng nguồn và git provenance nằm trong JSON đi kèm."]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
                        .strftime("%Y%m%d"))
    args = parser.parse_args()
    result = {"git": git_state(ROOT), **build_profile(ROOT)}
    out = ROOT / f"docs/measurements/data_profile_{args.date}"
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    out.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
