"""Sinh các bảng bổ sung cho báo cáo giữa kỳ (task L3) từ artifact đã khóa.

Chỉ đọc measurement, run manifest/metrics/evaluation đã lưu, nhãn gốc và split đóng băng; không chạy
suy luận, không đánh giá lại và không đọc `predictions/test.npz`. Số theo lớp trên test lấy từ
`evaluation_cv_annotated.json` đã có; số sự kiện tham chiếu đếm từ nhãn gốc (không phải dự đoán).

    .venv/Scripts/python.exe -m scripts.build_midterm_tables
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from ml.provenance import git_state
from scripts.build_thesis_tables import MEASUREMENTS, ROOT, f4, load, table

RUNS = ROOT / "ml" / "runs"
CLASSIFIER = RUNS / "classifier_datasec_20260923T121808Z"
F2 = RUNS / "sed_ensemble_s13_f2_20260929T045053Z"
ANNOTATIONS = ROOT / "data" / "annotations" / "datased_polyphonic_events.csv"
DATASED_SPLIT = ROOT / "data" / "splits" / "datased_polyphonic.csv"
UNANNOTATED = ROOT / "data" / "manifests" / "datased_polyphonic_unannotated.csv"
TAXONOMY = ROOT / "ml" / "configs" / "taxonomy.yaml"
DEFAULT_OUTPUT = ROOT / "report" / "tables"
SMALL_N = 10  # evaluation_protocol §4.2: n_test < 10 → chỉ báo số tuyệt đối


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu artifact nguồn: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def build_classifier(revision: str) -> str:
    metrics_path = CLASSIFIER / "metrics.json"
    ece_path = MEASUREMENTS / "ece_datasec_20260923.md"
    test = load(metrics_path)["test"]
    ece = read_text(ece_path)
    temperature = re.search(r"Temperature \(locked from dev\): `([\d.]+)`", ece).group(1)
    before = re.search(r"Test ECE before scaling \(T=1\): `([\d.]+)`", ece).group(1)
    after = re.search(r"Test ECE after scaling: `([\d.]+)`", ece).group(1)
    rows = [
        ["Macro-F1 lớp gộp (22 lớp)", f4(test["coarse_macro_f1"]), f"{test['items']} đoạn test"],
        [
            "Macro-F1 lớp con, mọi nút (28)",
            f4(test["subclass_macro_f1_all"]),
            "Gồm cả nút có n_test < 10",
        ],
        [
            "Macro-F1 lớp con, nút có n_test ≥ 10 (5)",
            f4(test["subclass_macro_f1_supported"]),
            "Con số diễn giải được",
        ],
        [
            "Tỷ lệ nhất quán cha–con",
            f4(test["parent_consistency_rate"]),
            f"{test['items_with_subclass']} đoạn có lớp con",
        ],
        ["ECE trước hiệu chuẩn (T = 1)", before, "Đầu lớp gộp"],
        [
            f"ECE sau temperature scaling (T = {float(temperature):.4f}, chọn trên dev)",
            after,
            "Tăng, không giảm",
        ],
    ]
    return table(
        "Kết quả mô hình phân loại DataSEC trên tập test",
        ["Chỉ số", "Giá trị", "Ghi chú"],
        rows,
        [metrics_path, ece_path],
        revision,
        ["---", "---:", "---"],
    )


def build_classifier_per_class(revision: str) -> str:
    path = MEASUREMENTS / "per_class_metrics_datasec_20260923.md"
    text = read_text(path)
    block = text.split("## Coarse classes", 1)[1].split("##", 1)[0]
    rows = []
    for class_id, correct, total, f1 in re.findall(
        r"\| `(\w+)` \| (\d+) \| (\d+) \| ([\d.]+) \|", block
    ):
        n = int(total)
        rows.append(
            [
                f"`{class_id}`",
                f"{correct}/{total}",
                f"{float(f1):.4f}" if n >= SMALL_N else "— (n < 10)",
            ]
        )
    return table(
        "Kết quả theo lớp gộp của mô hình phân loại DataSEC (test)",
        ["Lớp", "Đúng / tổng", "F1"],
        rows,
        [path],
        revision,
        ["---", "---:", "---:"],
    )


def build_ceilings(revision: str) -> str:
    v1_path = MEASUREMENTS / "sed_ceilings_20260926.json"
    v2_path = MEASUREMENTS / "sed_ceilings_v2_20260926.json"
    v1, v2 = load(v1_path), load(v2_path)
    rows = []
    for item in v1["resolution_ceiling"]:
        if item["block_s"] in (0.32, 0.64, 1.28):
            rows.append(
                [
                    f"Trần độ phân giải: mô hình hoàn hảo, khối {item['block_s']:.2f} s",
                    f4(item["event_f1"]),
                    "—",
                    "—",
                    "—",
                ]
            )
    rows.append(
        [
            "Trần người: 8 cặp bản ghi trùng chú giải hai lần",
            f4(v1["human_agreement"]["event_f1_collar_0.2s"]),
            "—",
            "—",
            "—",
        ]
    )
    for label, data in (
        ("Hệ v1 (ensemble C)", v1["system"]),
        ("Hệ v2 (ensemble 3 seed)", v2["system"]),
    ):
        rows.append(
            [
                label,
                f4(data["event_f1"]),
                f4(data["event_f1_onset_only"]),
                f4(data["event_f1_offset_only"]),
                f4(data["segment_f1_1s"]),
            ]
        )
    rows.append(
        [
            "Phân rã v1: khớp / lệch biên / bỏ sót (trên 886 sự kiện)",
            f"{v1['system']['n_collar_match']} / {v1['system']['n_overlap_but_boundary_miss']}"
            f" / {v1['system']['n_deleted']}",
            "—",
            "—",
            "—",
        ]
    )
    rows.append(
        [
            "Phân rã v2: khớp / lệch biên / bỏ sót (trên 886 sự kiện)",
            f"{v2['system']['n_collar_match']} / {v2['system']['n_overlap_but_boundary_miss']}"
            f" / {v2['system']['n_deleted']}",
            "—",
            "—",
            "—",
        ]
    )
    return table(
        "Chẩn đoán trần và phân rã lỗi SED trên tập dev",
        ["Đại lượng", "Event-F1 (micro)", "Chỉ onset", "Chỉ offset", "Segment-F1 1 s"],
        rows,
        [v1_path, v2_path],
        revision,
        ["---", "---:", "---:", "---:", "---:"],
    )


def build_rq2_levels(revision: str) -> str:
    path = MEASUREMENTS / "caption_grounding_sed_ensemble_s13_f2_20260929T045053Z_test.json"
    summary = load(path)["summary"]
    names = {
        "template": "Template",
        "constrained": "Constrained",
        "constrained_cover": "Constrained-cover",
        "unconstrained": "Unconstrained",
    }
    rows = []
    for mode in ("template", "constrained", "constrained_cover", "unconstrained"):
        for level, label in (("oracle", "oracle"), ("e2e", "đầu–cuối")):
            s = summary[f"{mode}/{level}"]
            rows.append(
                [
                    names[mode],
                    label,
                    f4(s["hallucination_rate"]),
                    f4(s["omission_rate"]),
                    f"{s['temporal_order_eligible']:.4f} ({s['n_temporal_eligible']})",
                    f4(s["over_specific_rate"]),
                    f4(s["context_term_rate"]),
                    f4(s["forbidden_term_rate"]),
                    f"{s['n_mentions']:.2f}",
                ]
            )
    return table(
        "Mức căn cứ của mô tả trên test theo chế độ sinh và mức đánh giá (hệ f2, n = 142)",
        [
            "Chế độ",
            "Mức",
            "Ảo giác",
            "Bỏ sót",
            "Thứ tự (n ≥ 2 nhắc)",
            "Quá cụ thể",
            "Bối cảnh",
            "Từ cấm",
            "Số nhắc",
        ],
        rows,
        [path],
        revision,
        ["---", "---"] + ["---:"] * 7,
    )


def annotated_test_counts() -> Counter:
    unannotated = (
        {row["recording_id"] for row in csv.DictReader(read_text(UNANNOTATED).splitlines())}
        if UNANNOTATED.is_file()
        else set()
    )
    test = {
        row["recording_id"]
        for row in csv.DictReader(read_text(DATASED_SPLIT).splitlines())
        if row["split"] == "test"
    } - unannotated
    return Counter(
        row["class_id"]
        for row in csv.DictReader(read_text(ANNOTATIONS).splitlines())
        if row["recording_id"] in test
    )


def build_f2_per_class(revision: str) -> str:
    path = F2 / "evaluation_cv_annotated.json"
    evaluation = load(path)
    counts = annotated_test_counts()
    if sum(counts.values()) != evaluation["n_events_reference"]:
        raise ValueError("Số sự kiện tham chiếu đếm từ nhãn gốc không khớp evaluation đã lưu")
    rows = []
    for class_id, scores in evaluation["event_based_f1_per_class"].items():
        n = counts[class_id]
        hits = round(scores["recall"] * n) if n else 0
        if n >= SMALL_N:
            rows.append(
                [
                    f"`{class_id}`",
                    n,
                    f4(scores["f_measure"]),
                    f4(scores["precision"]),
                    f4(scores["recall"]),
                ]
            )
        else:
            rows.append([f"`{class_id}`", n, f"khớp {hits}/{n}", "—", "—"])
    return table(
        "Event-F1 theo lớp của hệ f2 trên test annotated (n = 139 bản ghi)",
        ["Lớp", "Sự kiện tham chiếu", "F1", "Precision", "Recall"],
        rows,
        [path, ANNOTATIONS, DATASED_SPLIT, UNANNOTATED],
        revision,
        ["---", "---:", "---:", "---:", "---:"],
    )


def build_ledger(revision: str) -> str:
    path = MEASUREMENTS / "test_ledger_20261002.json"
    ledger = load(path)
    rows = [["Đánh giá SED trên test", len(ledger["sed"])]]
    rows += [[name, len(items)] for name, items in ledger["other"].items()]
    rows.append(["Đánh giá SED ghi git dirty", sum(1 for r in ledger["sed"] if r["git_dirty"])])
    return table(
        "Sổ ghi các lần chạm tập test", ["Nhóm", "Số mục"], rows, [path], revision, ["---", "---:"]
    )


def build_freeze(revision: str) -> str:
    path = MEASUREMENTS / "artifact_freeze_20261002.json"
    freeze = load(path)
    rows = [
        [
            item["label"],
            f"`{item['run_id']}`",
            len(item["artifacts"]),
            "có" if item["exists"] and all(a["exists"] for a in item["artifacts"]) else "thiếu",
        ]
        for item in freeze["runs"]
    ]
    rows += [
        [item["kind"], f"`{Path(item['path']).name}`", 1, "có" if item["exists"] else "thiếu"]
        for item in freeze["external"]
    ]
    return table(
        "Artifact đã đóng băng và kiểm SHA-256",
        ["Thành phần", "Run / tệp", "Số tệp", "Tồn tại"],
        rows,
        [path],
        revision,
        ["---", "---", "---:", "---"],
    )


def build_taxonomy(revision: str) -> str:
    raw = yaml.safe_load(read_text(TAXONOMY))
    events = Counter(row["class_id"] for row in csv.DictReader(read_text(ANNOTATIONS).splitlines()))
    rows = []
    for item in raw["classes"]:
        polyphonic = item.get("polyphonic", True)
        rows.append(
            [
                f"`{item['id']}`",
                item["source_label"],
                ", ".join(item.get("subclasses", [])) or "—",
                "có" if polyphonic else "không",
                events.get(item["id"], 0),
            ]
        )
    return table(
        f"Hệ lớp phiên bản {raw['version']}",
        ["class_id", "Nhãn gốc", "Lớp con (DataSEC)", "Thuộc SED 21 lớp", "Sự kiện đa âm DataSED"],
        rows,
        [TAXONOMY, ANNOTATIONS],
        revision,
        ["---", "---", "---", "---", "---:"],
    )


BUILDERS = {
    "m01_classifier.md": build_classifier,
    "m02_classifier_per_class.md": build_classifier_per_class,
    "m03_sed_ceilings.md": build_ceilings,
    "m04_rq2_levels.md": build_rq2_levels,
    "m05_f2_per_class.md": build_f2_per_class,
    "m06_test_ledger.md": build_ledger,
    "m07_artifact_freeze.md": build_freeze,
    "m08_taxonomy.md": build_taxonomy,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    revision = git_state(ROOT)["revision"]
    args.output.mkdir(parents=True, exist_ok=True)
    for name, builder in BUILDERS.items():
        text = builder(revision).replace(
            "scripts.build_thesis_tables", "scripts.build_midterm_tables"
        )
        (args.output / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"Đã ghi {(args.output / name).relative_to(ROOT)}")
    print(json.dumps({"git": git_state(ROOT)}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
