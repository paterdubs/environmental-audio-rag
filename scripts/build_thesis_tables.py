"""Sinh các bảng số cho báo cáo từ artifact JSON đã khóa.

Chỉ đọc measurement, manifest và split đã tồn tại; không chạy lại suy luận hay đánh giá test.

    .venv/Scripts/python.exe -m scripts.build_thesis_tables
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "docs" / "measurements"
MANIFESTS = ROOT / "data" / "manifests"
SPLITS = ROOT / "data" / "splits"
DEFAULT_OUTPUT = ROOT / "docs" / "thesis" / "tables"


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu artifact nguồn: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f4(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:.4f}"


def pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{100 * value:.2f}%"


def table(
    title: str,
    headers: list[str],
    rows: list[list[object]],
    sources: list[Path],
    revision: str,
    align: list[str] | None = None,
) -> str:
    if align is None:
        align = ["---"] * len(headers)
    lines = [
        f"# {title}",
        "",
        f"> Sinh tự động bởi `scripts.build_thesis_tables` tại git `{revision[:7]}`.",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(align) + "|",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    lines.extend(
        [
            "",
            "**Nguồn:** " + "; ".join(f"`{rel(source)}`" for source in sources) + ".",
            "",
        ]
    )
    return "\n".join(lines)


def build_data_split(revision: str) -> str:
    sec_inv_path = MANIFESTS / "datasec_inventory_summary.json"
    sed_inv_path = MANIFESTS / "datased_inventory_summary.json"
    sec_split_path = SPLITS / "datasec_classification.frozen.json"
    sed_split_path = SPLITS / "datased_polyphonic.frozen.json"
    sec_inv, sed_inv = load(sec_inv_path), load(sed_inv_path)
    sec_split, sed_split = load(sec_split_path), load(sed_split_path)
    rows = []
    for name, task, inv, split in (
        ("DataSEC", "Phân loại", sec_inv, sec_split),
        ("DataSED", "SED đa âm", sed_inv, sed_split),
    ):
        items = split["items"]
        rows.append(
            [
                name,
                task,
                inv["files"],
                f"{inv['hours']:.2f}",
                items["train"],
                items["validation"],
                items["test"],
                split["leakage_groups"]["groups"],
                f"`{split['split_sha256'][:12]}…`",
            ]
        )
    return table(
        "Bảng dữ liệu và split đóng băng",
        [
            "Dataset",
            "Bài toán",
            "File",
            "Giờ",
            "Train",
            "Validation",
            "Test",
            "Nhóm leakage",
            "SHA split",
        ],
        rows,
        [sec_inv_path, sed_inv_path, sec_split_path, sed_split_path],
        revision,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---"],
    )


def build_leakage(revision: str) -> str:
    dup_path = MANIFESTS / "duplicate_audit.json"
    sec_gate_path = MANIFESTS / "datasec_leakage_report.json"
    sed_gate_path = MANIFESTS / "datased_leakage_report.json"
    sec_split_path = SPLITS / "datasec_classification.frozen.json"
    dup, sec_gate, sed_gate = load(dup_path), load(sec_gate_path), load(sed_gate_path)
    sec_split = load(sec_split_path)
    rows = [
        [
            "D3",
            "Cặp ứng viên T1/T2/T3",
            "/".join(str(dup["pairs_by_tier"][k]) for k in ("T1", "T2", "T3")),
            "Audit 3 tầng",
        ],
        ["D3", "Nhóm duplicate", dup["groups"], "Nội bộ và xuyên dataset"],
        [
            "D3",
            "Nhóm xuyên DataSEC–DataSED",
            dup["cross_dataset_groups"],
            "Đã gom theo leakage group",
        ],
        [
            "D3",
            "Clip pretraining bị loại",
            sec_split["gates"]["leaked_pretraining_clips"],
            "Trùng DataSED dev/test",
        ],
        [
            "D4",
            "Cổng DataSEC",
            "PASS" if sec_gate["passed"] else "FAIL",
            f"{len(sec_gate['checks'])}/5 kiểm tra đạt",
        ],
        [
            "D4",
            "Cổng DataSED",
            "PASS" if sed_gate["passed"] else "FAIL",
            f"{len(sed_gate['checks'])}/5 kiểm tra đạt",
        ],
    ]
    return table(
        "Bảng kiểm soát leakage D3/D4",
        ["Cổng", "Chỉ báo", "Kết quả", "Diễn giải"],
        rows,
        [dup_path, sec_gate_path, sed_gate_path, sec_split_path],
        revision,
        ["---", "---", "---:", "---"],
    )


def build_rq1(revision: str) -> str:
    v1_path = MEASUREMENTS / "rq1_multiseed_clean_20260924.json"
    v1_ci_path = MEASUREMENTS / "rq1_multirun_bootstrap_clean_20260925.json"
    v2_path = MEASUREMENTS / "rq1_v2_multiseed_20260929.json"
    v2_ci_path = MEASUREMENTS / "rq1_multirun_bootstrap_rq1_v2_annotated_20260929.json"
    v1, v1_ci, v2, v2_ci = load(v1_path), load(v1_ci_path), load(v2_path), load(v2_ci_path)
    rows: list[list[object]] = []
    for branch in ("B", "C"):
        metric = v1["branches"][branch]["event_f1"]
        ci = v1_ci["branches"][branch]
        rows.append(
            [
                "RQ1-v1",
                branch,
                metric["n"],
                "—",
                f4(metric["mean"]),
                f"[{f4(ci['lower'])}, {f4(ci['upper'])}]",
                "—",
            ]
        )
    delta = v1_ci["differences"]["C-B"]
    rows.append(
        [
            "RQ1-v1",
            "C−B",
            "—",
            "—",
            f4(delta["estimate"]),
            f"[{f4(delta['lower'])}, {f4(delta['upper'])}]",
            f4(v1["welch"]["event_f1"]["p"]),
        ]
    )
    for branch in ("B", "C"):
        macro = v2["branches"][branch]["event_f1_macro"]
        micro = v2["branches"][branch]["event_f1"]
        ci = v2_ci["branches"][branch]
        rows.append(
            [
                "RQ1-v2",
                branch,
                micro["n"],
                f4(macro["mean"]),
                f4(micro["mean"]),
                f"[{f4(ci['lower'])}, {f4(ci['upper'])}]",
                "—",
            ]
        )
    delta = v2_ci["differences"]["C-B"]
    rows.append(
        [
            "RQ1-v2",
            "C−B",
            "—",
            f4(v2["delta_mean_c_minus_b"]["event_f1_macro"]),
            f4(delta["estimate"]),
            f"[{f4(delta['lower'])}, {f4(delta['upper'])}]",
            f4(v2["welch"]["event_f1"]["p"]),
        ]
    )
    return table(
        "Bảng kết quả RQ1 và RQ1-v2",
        ["Thí nghiệm", "Nhánh", "n run", "Macro-F1", "Micro-F1", "95% CI micro", "p Welch"],
        rows,
        [v1_path, v1_ci_path, v2_path, v2_ci_path],
        revision,
        ["---", "---", "---:", "---:", "---:", "---", "---:"],
    )


def build_sed_progress(revision: str) -> str:
    s13_path = MEASUREMENTS / "s13_test_20261018.json"
    s13 = load(s13_path)
    by_label = {row["label"]: row for row in s13["results"]}
    rows = []
    for label, name in (
        ("a", "v1 — ensemble C"),
        ("c", "v2 — ensemble 3 seed"),
        ("f2", "S13 — T2b×3 + cSEBB (khóa)"),
    ):
        row = by_label[label]
        rows.append(
            [
                name,
                row["postproc_family"],
                f4(row["macro"]),
                f4(row["micro"]),
                f"[{f4(row['micro_ci_lower'])}, {f4(row['micro_ci_upper'])}]",
                f4(row["psds_1"]),
                f4(row["psds_2"]),
                row["n_recordings"],
            ]
        )
    return table(
        "Bảng tiến triển SED v1 → v2 → S13 trên test annotated",
        ["Hệ thống", "Hậu xử lý", "Macro-F1", "Micro-F1", "95% CI micro", "PSDS-1", "PSDS-2", "n"],
        rows,
        [s13_path],
        revision,
        ["---", "---", "---:", "---:", "---", "---:", "---:", "---:"],
    )


def build_ablation(revision: str) -> str:
    source = MEASUREMENTS / "sed_v2_ablation_20260926.json"
    data = load(source)
    baseline = data["full"][0]["cv_mean"]
    rows = []
    for group, values in (
        ("Đầy đủ", data["full"]),
        ("Ablation", data["ablations"]),
        ("Tham chiếu", data["references"]),
    ):
        for row in values:
            rows.append(
                [
                    group,
                    row["label"],
                    f4(row["cv_mean"]),
                    f4(row["cv_sd"]),
                    f4(row["cv_mean"] - baseline),
                    row["run"],
                ]
            )
    return table(
        "Bảng ablation SED v2 trên CV dev",
        ["Nhóm", "Cấu hình", "Micro-F1 CV", "SD fold", "Δ so với v2 seed 1", "Run"],
        rows,
        [source],
        revision,
        ["---", "---", "---:", "---:", "---:", "---"],
    )


def build_s13(revision: str) -> str:
    rank_path = MEASUREMENTS / "s13_selection_20261018.json"
    test_path = MEASUREMENTS / "s13_test_20261018.json"
    rank, test = load(rank_path), load(test_path)
    test_by_label = {row["label"]: row for row in test["results"]}
    rows = []
    for candidate in rank["ranking"]:
        result = test_by_label[candidate["label"]]
        score = candidate["annotated"]["score"]
        rows.append(
            [
                candidate["rank"],
                candidate["label"],
                candidate["models"],
                score["family"],
                f4(score["mean"]),
                f4(score["sd"]),
                f4(result["macro"]),
                f4(result["micro"]),
                f"[{f4(result['micro_ci_lower'])}, {f4(result['micro_ci_upper'])}]",
            ]
        )
    return table(
        "Bảng xếp hạng S13 trên dev và kết quả test một lần",
        [
            "Hạng CV",
            "Mã",
            "Model",
            "Hậu xử lý",
            "Dev micro",
            "SD fold",
            "Test macro",
            "Test micro",
            "95% CI test micro",
        ],
        rows,
        [rank_path, test_path],
        revision,
        ["---:", "---", "---:", "---", "---:", "---:", "---:", "---:", "---"],
    )


def build_csebb(revision: str) -> str:
    selection_path = MEASUREMENTS / "s13_selection_20261018.json"
    test_path = MEASUREMENTS / "s13_test_20261018.json"
    selection, test = load(selection_path), load(test_path)
    f2 = next(row for row in selection["ranking"] if row["label"] == "f2")
    test_f2 = next(row for row in test["results"] if row["label"] == "f2")
    rows = []
    for family in f2["annotated"]["families"]:
        rows.append(
            [
                "CV dev annotated",
                family["family"],
                family["config"],
                f4(family["mean"]),
                f4(family["sd"]),
                "—",
            ]
        )
    rows.append(
        ["Test annotated", "csebb", "khóa từ dev", f4(test_f2["micro"]), "—", f4(test_f2["macro"])]
    )
    return table(
        "Bảng hậu xử lý cSEBB của hệ f2",
        ["Tập", "Họ", "Cấu hình", "Micro-F1", "SD fold", "Macro-F1"],
        rows,
        [selection_path, test_path],
        revision,
        ["---", "---", "---", "---:", "---:", "---:"],
    )


def build_rq2(revision: str) -> str:
    source = MEASUREMENTS / "s8_summary_20261002.json"
    data = load(source)["rq2"]
    rows = []
    for corpus, name in (
        ("baseline_v1_all", "v1 — all"),
        ("f2_all", "f2 — all"),
        ("f2_annotated", "f2 — annotated"),
    ):
        for mode, metrics in data[corpus].items():
            hall = metrics["hallucination_rate"]
            omit = metrics["omission_rate"]
            rows.append(
                [
                    name,
                    mode.removesuffix("/e2e"),
                    metrics["n"],
                    f4(hall["estimate"]),
                    f"[{f4(hall['lower'])}, {f4(hall['upper'])}]",
                    f4(omit["estimate"]),
                    f"[{f4(omit['lower'])}, {f4(omit['upper'])}]",
                    f4(metrics["forbidden_term_rate"]["estimate"]),
                ]
            )
    return table(
        "Bảng RQ2 — grounding caption trên test",
        ["Hệ", "Chế độ", "n", "Hallucination", "95% CI", "Omission", "95% CI", "G3"],
        rows,
        [source],
        revision,
        ["---", "---", "---:", "---:", "---", "---:", "---", "---:"],
    )


def build_rq3(revision: str) -> str:
    source = MEASUREMENTS / "s8_summary_20261002.json"
    data = load(source)["rq3"]
    rows = []
    for block, name in (
        ("baseline_run_b_gold", "Run B — gold"),
        ("f2_gold", "f2 — gold"),
        ("f2_parsed", "f2 — parsed"),
    ):
        for mode_lang, metrics in data[block].items():
            ci = metrics["ndcg@10_ci"]
            rows.append(
                [
                    name,
                    mode_lang,
                    metrics["n"],
                    f4(metrics["ndcg@10"]),
                    f"[{f4(ci['lower'])}, {f4(ci['upper'])}]",
                    f4(metrics["recall@1"]),
                    f4(metrics["recall@5"]),
                    f4(metrics["recall@10"]),
                    f4(metrics["filter_exactness"]),
                ]
            )
    return table(
        "Bảng RQ3 — retrieval với bộ lọc gold và parsed",
        [
            "Corpus/bộ lọc",
            "Mode/ngôn ngữ",
            "n",
            "nDCG@10",
            "95% CI",
            "R@1",
            "R@5",
            "R@10",
            "Filter exactness",
        ],
        rows,
        [source],
        revision,
        ["---", "---", "---:", "---:", "---", "---:", "---:", "---:", "---:"],
    )


def build_parser(revision: str) -> str:
    source = MEASUREMENTS / "query_parser_20260928.json"
    summary = load(source)["summary"]
    rows = []
    for name in ("template", "paraphrase"):
        row = summary[name]
        rows.append(
            [
                name,
                row["n"],
                f4(row["parse_success"]),
                f4(row["exact_match"]),
                f4(row["class_precision"]),
                f4(row["class_recall"]),
                f4(row["predicate_accuracy"]),
                row["n_temporal"],
            ]
        )
    return table(
        "Bảng đánh giá parser L2",
        [
            "Tập",
            "n",
            "Parse success",
            "Exact match",
            "Class precision",
            "Class recall",
            "Predicate accuracy",
            "n temporal",
        ],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def build_parity(revision: str) -> str:
    cuda_path = MEASUREMENTS / "inference_parity_20260929.json"
    cpu_path = MEASUREMENTS / "inference_parity_cpu_20261002.json"
    cuda, cpu = load(cuda_path), load(cpu_path)
    rows = []
    for name, payload in (("Host CUDA", cuda), ("Container CPU", cpu)):
        summary = payload["summary"]
        rows.append(
            [
                name,
                payload["torch"],
                summary["events_equal"],
                142,
                summary["n_events"],
                summary["n_served_events"],
                summary["n_shared_events"],
                summary["n_within_collar"],
                f"{summary['prob_max_abs']:.6f}",
            ]
        )
    return table(
        "Bảng parity giữa pipeline nghiên cứu và phục vụ",
        [
            "Thiết bị",
            "Torch",
            "Recording trùng event",
            "Tổng recording",
            "Event chuẩn",
            "Event phục vụ",
            "Event trùng",
            "Trong collar",
            "Δp lớn nhất",
        ],
        rows,
        [cuda_path, cpu_path],
        revision,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def build_runtime(revision: str) -> str:
    frame_path = MEASUREMENTS / "track2_t0_frame_mn_20260927.json"
    beats_path = MEASUREMENTS / "track2_t0_beats_20260927.json"
    demo_path = MEASUREMENTS / "demo_f2_e2e_20261002.json"
    frame, beats, demo = load(frame_path), load(beats_path), load(demo_path)
    rows = [
        [
            "Frame-MobileNet T0",
            "GPU train+dev",
            "Giây/epoch ước tính",
            f"{frame['epoch_time']['estimated_seconds_per_epoch']:.2f}",
            f"batch={frame['epoch_time']['batch_size']}",
        ],
        [
            "BEATs T0",
            "GPU train+dev",
            "Giây/epoch ước tính",
            f"{beats['estimated_seconds_per_epoch']:.2f}",
            "batch=24",
        ],
        [
            "Demo f2",
            "CPU container",
            "Upload + phân tích recording",
            f"{demo['upload_elapsed_s']:.3f}",
            demo["source_recording_id"],
        ],
        [
            "Demo RAG",
            "CPU container + BGE-M3",
            "Hybrid query",
            f"{demo['rag_elapsed_s']:.3f}",
            f"{demo['rag_evidence']} evidence",
        ],
    ]
    return table(
        "Bảng thời gian xử lý đã đo",
        ["Thành phần", "Môi trường", "Phép đo", "Thời gian (s)", "Ghi chú"],
        rows,
        [frame_path, beats_path, demo_path],
        revision,
        ["---", "---", "---", "---:", "---"],
    )


BUILDERS = {
    "01_data_split.md": build_data_split,
    "02_leakage_d3_d4.md": build_leakage,
    "03_rq1.md": build_rq1,
    "04_sed_progress.md": build_sed_progress,
    "05_sed_v2_ablation.md": build_ablation,
    "06_s13_ranking_test.md": build_s13,
    "07_csebb.md": build_csebb,
    "08_rq2_caption.md": build_rq2,
    "09_rq3_retrieval.md": build_rq3,
    "10_parser_l2.md": build_parser,
    "11_serving_parity.md": build_parity,
    "12_runtime.md": build_runtime,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    state = git_state(ROOT)
    if state["dirty"]:
        raise SystemExit("Tree đang bẩn; không sinh bảng số chính thức.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, builder in BUILDERS.items():
        destination = args.output_dir / filename
        destination.write_text(builder(state["revision"]), encoding="utf-8")
        print(f"Đã sinh {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
