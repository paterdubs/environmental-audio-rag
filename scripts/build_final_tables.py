"""Sinh bảng cho báo cáo cuối (R5) từ `final_numbers_*.json`.

Chỉ đọc JSON đã sinh bởi `scripts.report_final_numbers` (mỗi ô có nguồn); không tính lại metric,
không đọc `predictions/test.npz`.

    .venv/Scripts/python.exe -m scripts.build_final_tables --final-numbers <final_numbers.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ml.provenance import git_state
from scripts.build_thesis_tables import ROOT, table
from scripts.report_final_numbers_render import ci, v

DEFAULT_OUTPUT = ROOT / "report" / "final_tables"
SED_ROWS = {
    "f2": "f2 (mốc S13)",
    "B0": "B0 (cuối giai đoạn O)",
    "lbrv2_f1": "LBR V2, điểm f1",
    "lbrv3_f1": "LBR V3, điểm f1",
    "lbrv3_recall_first": "LBR V3, recall_first",
}
SYSTEMS = {"f2": "f2", "B0": "B0", "lbrv2": "LBR V2", "lbrv3": "LBR V3"}
MODES = {
    "template": "Template",
    "unconstrained": "Unconstrained",
    "constrained": "Constrained",
    "constrained_cover": "Constrained-cover",
}


def _pair(cell: dict[str, Any] | None) -> str:
    return "—" if cell is None else f"{v(cell['psds_1'])} / {v(cell['psds_2'])}"


def build_sed(data: dict[str, Any], revision: str, source: Path) -> str:
    rows = []
    for key, label in SED_ROWS.items():
        r = data["sed"]["rows"][key]
        micro = v(r["micro"])
        if "micro_ci" in r:
            micro += " " + ci(r["micro_ci"]["lower"], r["micro_ci"]["upper"])
        delta = r.get("delta_micro_vs_b0")
        delta_s = (
            "—"
            if delta is None
            else f"{v(delta['estimate'], '+.4f')} {ci(delta['lower'], delta['upper'], '+.4f')}"
        )
        rows.append(
            [
                label,
                v(r["macro"]),
                micro,
                delta_s,
                f"{v(r['nsys'], 'd')}/{v(r['nref'], 'd')}",
                _pair(r.get("psds_linear")),
                _pair(r.get("psds_log")),
            ]
        )
    return table(
        "SED trên test annotated (n = 139, event-F1 collar 0,2 s)",
        ["Hệ thống", "Macro", "Micro [CI 95%]", "Δ micro so B0", "Nsys/Nref",
         "PSDS-1/2 lưới tuyến tính", "PSDS-1/2 lưới log"],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def build_intersection(data: dict[str, Any], revision: str, source: Path) -> str:
    rows = []
    for key in ("B0", "lbrv2_f1", "lbrv3_f1", "lbrv3_recall_first"):
        r = data["sed"]["rows"][key]
        rows.append(
            [
                SED_ROWS[key],
                v(r["intersection_recall"]),
                v(r["intersection_precision"]),
                v(r["segment_f1_1s"]),
                f"{v(r['nsys'], 'd')}/{v(r['nref'], 'd')}",
            ]
        )
    return table(
        "Thước ứng dụng trên test annotated (n = 139)",
        ["Hệ thống", "Recall giao nhau", "Precision giao nhau", "Segment-F1 1 s", "Nsys/Nref"],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:", "---:"],
    )


def build_rq1(data: dict[str, Any], revision: str, source: Path) -> str:
    rows = []
    for name, r in data["rq1"].items():
        b, c = r["branches"]["B"], r["branches"]["C"]
        boot, p = r["bootstrap_c_minus_b"], r["welch_p"]
        rows.append(
            [
                name,
                f"{v(b['mean'])} ± {v(b['sd'])} ({v(b['n'], 'd')})",
                f"{v(c['mean'])} ± {v(c['sd'])} ({v(c['n'], 'd')})",
                f"{v(boot['estimate'], '+.4f')} {ci(boot['lower'], boot['upper'], '+.4f')}",
                f"{v(p['event_f1'], '.3f')} / {v(p['psds_1'], '.3f')} / {v(p['psds_2'], '.3f')}",
            ]
        )
    return table(
        "RQ1: nhánh C (DataSEC) so với nhánh B (AudioSet), event-F1 micro",
        ["Công thức", "B trung bình ± sd (n)", "C trung bình ± sd (n)", "C − B (bootstrap)",
         "Welch p: event-F1 / PSDS-1 / PSDS-2"],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:", "---:"],
    )


def _est(cell: dict[str, Any], fmt: str = ".3f") -> str:
    inner = cell["value"]
    return f"{format(inner['estimate'], fmt)} {ci_dict(inner, fmt)}"


def ci_dict(inner: dict[str, Any], fmt: str = ".3f") -> str:
    return f"[{format(inner['lower'], fmt)}, {format(inner['upper'], fmt)}]"


def build_rq2(data: dict[str, Any], revision: str, source: Path) -> str:
    """Bỏ sót và ảo giác theo chế độ sinh × hệ thống SED (mức đầu–cuối)."""
    e2e = data["rq2"]["llm_e2e"]
    rows = []
    for mode_key, mode_label in MODES.items():
        for metric, label in (("omission_rate", "bỏ sót"), ("hallucination_rate", "ảo giác")):
            rows.append(
                [f"{mode_label} — {label}"]
                + [_est(e2e[mode_key][s][metric]) for s in SYSTEMS]
            )
    return table(
        "RQ2 (mức đầu–cuối, test annotated, n = 139): bỏ sót và ảo giác theo chế độ sinh",
        ["Chế độ — chỉ số", *SYSTEMS.values()],
        rows,
        [ROOT / data["rq2"]["llm_source"], source],
        revision,
        ["---", "---:", "---:", "---:", "---:"],
    )


def build_rq3(data: dict[str, Any], revision: str, source: Path) -> str:
    rows = []
    for key, label in SYSTEMS.items():
        r = data["rq3"][key]
        n = r["ndcg10_gold"]
        a = r["answers_hybrid_en"]
        rows.append(
            [label]
            + [
                f"{v(n[c]['estimate'], '.3f')} {ci(n[c]['lower'], n[c]['upper'], '.3f')}"
                for c in ("structured_only/en", "vector_only/en", "hybrid/en")
            ]
            + [
                f"{v(a['answered'], 'd')}/{v(a['n'], 'd')}",
                v(a["unsupported_claim_rate"], ".3f"),
                v(a["cited_relevant_share"], ".3f"),
            ]
        )
    return table(
        "RQ3 (test, bộ lọc gold): nDCG@10 và chất lượng câu trả lời",
        ["Corpus", "structured/en", "vector/en", "hybrid/en", "Có trả lời",
         "Khẳng định thiếu bằng chứng", "Trích đúng GT"],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def _signed(cell: dict[str, float]) -> str:
    return (f"{cell['estimate']:+.3f} [{cell['lower']:+.3f}, {cell['upper']:+.3f}]")


def build_rq3_paired(data: dict[str, Any], revision: str, source: Path) -> str:
    """Hiệu ghép cặp giữa ba chế độ truy hồi và độ đúng bộ lọc (từ `report_rq3_modes`)."""
    rows = []
    for key, label in SYSTEMS.items():
        s = data["systems"][key]
        rows.append([
            label,
            _signed(s["paired"]["hybrid−vector_only/en"]),
            _signed(s["paired"]["hybrid−structured_only/en"]),
            f"{s['filter_exactness']['vector_only']:.3f}",
            f"{s['filter_exactness']['hybrid']:.3f}",
        ])
    return table(
        "RQ3 (test, bộ lọc gold): hiệu nDCG@10 ghép cặp giữa các chế độ và độ đúng bộ lọc",
        ["Corpus", "hybrid − vector", "hybrid − structured", "Độ đúng bộ lọc (vector)",
         "Độ đúng bộ lọc (hybrid)"],
        rows, [source], revision, ["---", "---:", "---:", "---:", "---:"],
    )


def build_rq3_groups(data: dict[str, Any], revision: str, source: Path) -> str:
    """nDCG@10 hybrid / vector_only theo nhóm câu hỏi."""
    groups = ("duration", "single_class", "multi_class", "temporal")
    names = {"duration": "Thời lượng", "single_class": "Một lớp",
             "multi_class": "Nhiều lớp", "temporal": "Quan hệ thời gian"}
    rows = []
    for key, label in SYSTEMS.items():
        s = data["systems"][key]
        rows.append([label] + [
            f"{s['by_group']['hybrid'][g]:.3f} / {s['by_group']['vector_only'][g]:.3f}"
            for g in groups])
    return table(
        "RQ3 (test, bộ lọc gold): nDCG@10 hybrid / vector_only theo nhóm câu hỏi",
        ["Corpus"] + [names[g] for g in groups],
        rows, [source], revision, ["---", "---:", "---:", "---:", "---:"],
    )


def build_rq3_backfill(data: dict[str, Any], revision: str, source: Path) -> str:
    """nDCG@10 bốn chế độ và hiệu ghép cặp của backfill (từ `report_rq3_backfill`, ADR-0049)."""
    rows = []
    for key, label in SYSTEMS.items():
        s = data["results"][f"{key}/gold/en"]["summary"]
        nd = {m: s["mean"][m]["ndcg@10"] for m in ("vector_only", "hybrid", "backfill")}
        p = s["paired_ndcg@10"]
        rows.append([label, f"{nd['vector_only']:.3f}", f"{nd['hybrid']:.3f}",
                     f"{nd['backfill']:.3f}", _signed(p["backfill−vector_only"]),
                     _signed(p["backfill−hybrid"]),
                     f"{s['mean']['backfill']['tier1_share']:.3f}"])
    return table(
        f"RQ3 ({data['split']}, bộ lọc gold): chế độ backfill so với vector_only và hybrid",
        ["Corpus", "vector", "hybrid", "backfill", "backfill − vector", "backfill − hybrid",
         "Tỷ lệ thỏa bộ lọc"],
        rows, [source], revision, ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def build_lbr_context(data: dict[str, Any], revision: str, source: Path) -> str:
    """LBR cạnh các mốc đơn giản hơn và trần sửa biên, trên OOF (từ `report_lbr_context`)."""
    r, d, ex = data["rows"], data["deltas"], data["exploratory"]

    def cells(name: str) -> list[str]:
        return [f"{r[name]['micro']:.4f}", f"{r[name]['macro']:.4f}"]

    def delta(key: str) -> str:
        c = d[key]
        return f"{c['estimate']:+.4f} [{c['lower']:+.4f}, {c['upper']:+.4f}]"

    rows = [
        ["B0 (mốc)"] + cells("B0") + ["—"],
        ["Ngưỡng riêng từng lớp (thăm dò)", f"{ex['per_class_lambda']:.4f}", "—", "—"],
        ["Dịch onset toàn cục (thăm dò)", f"{ex['global_onset_shift']:.4f}", "—", "—"],
        ["LBR V1"] + cells("LBR_v1") + [delta("LBR_v1")],
        ["LBR V2 (số chính)"] + cells("LBR_v2") + [delta("LBR_v2")],
        ["P1×3 (ensemble 3 seed, mốc)"] + cells("P1x3") + ["—"],
        ["LBR V2 học trên một mô hình, áp lên P1×3"] + cells("LBR_v2_on_P1x3")
        + [delta("LBR_v2_on_P1x3")],
        ["Trần: sửa biên mọi hộp 1-1 trong ±1 s", f"{data['oracle_ceiling_1s']:.4f}", "—", "—"],
    ]
    return table(
        "LBR trong bối cảnh (dự đoán ngoài mẫu, 564 bản ghi, 21 lớp)",
        ["Cấu hình", "Micro", "Macro", "Δ micro [95% CI] so với mốc cùng nhóm"],
        rows, [source], revision, ["---", "---:", "---:", "---"],
    )


def build_calibration(data: dict[str, Any], revision: str, source: Path) -> str:
    """Event-F1 của B0/LBR cạnh mức đồng thuận quan sát giữa hai lần gán nhãn."""
    rows = []
    for name, r in data["rows"].items():
        inter = ("—" if r["intersection_recall"] is None
                 else f"{r['intersection_recall']:.4f} / {r['intersection_precision']:.4f}")
        rows.append([name, f"{r['micro']:.4f}", f"{r['collar_1s']:.4f}",
                     f"{r['segment_1s']:.4f}", inter])
    h = data["human"]
    rows.append([f"Đồng thuận giữa hai lần gán nhãn ({h['pairs']} cặp)",
                 f"{h['micro_f1']:.4f}", f"{h['event_f1_collar_1s']:.4f}",
                 f"{h['segment_f1_1s']:.4f}", "—"])
    return table(
        f"Event-F1 theo bốn thước đo (test annotated, n = {data['n_recordings']})",
        ["Hệ thống", "Micro, collar 0,2 s", "Micro, collar 1 s", "Segment-F1 1 s",
         "Giao nhau R / P"],
        rows, [source], revision, ["---", "---:", "---:", "---:", "---:"],
    )


def build_workload(data: dict[str, Any], revision: str, source: Path) -> str:
    """Khối lượng thực hiện, đếm từ repo bởi `report_workload`."""
    py, runs = data["python_lines"], data["runs"]
    rows = [
        ["Lịch sử làm việc", f"{data['commits']} commit, {data['first_commit']} đến "
                              f"{data['last_commit']}"],
        ["Mã Python", f"{sum(py.values()):,} dòng (ml {py['ml']:,}; scripts {py['scripts']:,}; "
                      f"tests {py['tests']:,}; services {py['services']:,})".replace(",", ".")],
        ["Giao diện web (TS/TSX)", f"{data['frontend_lines']:,} dòng".replace(",", ".")],
        ["Kiểm thử", f"{data['test_functions']} hàm kiểm thử (pytest) và vitest cho giao diện"],
        ["Quyết định thiết kế", f"{data['adr']} ADR"],
        ["Báo cáo đo sinh tự động", f"{data['measurement_reports']} tệp Markdown"],
        ["Huấn luyện", f"{runs['sed']} run SED và {runs['classifier']} run phân loại"],
        ["Hợp đồng dữ liệu", f"{data['json_schemas']} JSON Schema"],
    ]
    return table(
        "Khối lượng thực hiện (đếm từ repo)", ["Hạng mục", "Số đếm"], rows, [source], revision,
        ["---", "---"],
    )


def build_latency(data: dict[str, Any], revision: str, source: Path) -> str:
    """Độ trễ của demo đang chạy, đo bởi `report_latency` trên bản ghi TRAIN."""
    e, r, q, a = data["elapsed_s"], data["rtf"], data["query_s"], data["audio_duration_s"]
    rows = [
        ["Tải lên + phân tích (giây)", str(e["n"]), f"{e['median']:.2f}", f"{e['p95']:.2f}"],
        ["Hệ số thời gian thực (xử lý / độ dài)", str(r["n"]), f"{r['median']:.3f}",
         f"{r['p95']:.3f}"],
        ["Truy vấn kết hợp (giây)", str(q["n"]), f"{q['median']:.3f}", f"{q['p95']:.3f}"],
        ["Độ dài âm thanh (giây)", str(e["n"]), f"{a['min']:.1f} đến {a['max']:.1f}", "—"],
    ]
    return table(
        "Độ trễ của demo trên CPU (LBR V3, bản ghi TRAIN)",
        ["Đại lượng", "n", "Trung vị", "p95"],
        rows,
        [source],
        revision,
        ["---", "---:", "---:", "---:"],
    )


def build_run_registry(data: dict[str, Any], revision: str, source: Path) -> str:
    """Sổ đăng ký run theo loại, từ `report_run_registry`."""
    from scripts.report_run_registry import TASK_NAMES

    def day(stamp: str) -> str:
        return f"{stamp[6:]}/{stamp[4:6]}"

    rows = [[TASK_NAMES.get(task, task), str(s["n"]), str(s["complete"]), str(s["dirty"]),
             str(s["split_hashes"]), f"{day(s['first'])} – {day(s['last'])}"]
            for task, s in data["by_task"].items()]
    rows.append(["Tổng", str(data["n_runs"]),
                 str(sum(s["complete"] for s in data["by_task"].values())),
                 str(sum(s["dirty"] for s in data["by_task"].values())), "—", "—"])
    return table(
        f"Sổ đăng ký {data['n_runs']} lần chạy trong ml/runs",
        ["Loại lần chạy", "n", "Hoàn tất", "Cây bẩn", "Mã băm split", "Khoảng ngày"],
        rows, [source], revision, ["---", "---:", "---:", "---:", "---:", "---"],
    )


def build_psds(data: dict[str, Any], revision: str, source: Path) -> str:
    d = data["psds_diagnosis"]
    rows = [
        ["Δ event-F1 micro (v2 − v1)", format(d["delta_event_f1_micro"], "+.4f")],
        ["Δ PSDS-1 (lưới tuyến tính)", format(d["delta_psds_linear"]["psds_1"], "+.4f")],
        ["Δ PSDS-2 (lưới tuyến tính)", format(d["delta_psds_linear"]["psds_2"], "+.4f")],
    ]
    for name, label in (("H1", "H1 — lưới ngưỡng"), ("H2", "H2 — lợi ích quanh điểm vận hành"),
                        ("H3", "H3 — alpha_st = 0")):
        ok = d["supported"][name]["psds_2"]
        rows.append([label + " (PSDS-2)", "đủ điều kiện" if ok else "không"])
    return table(
        "Chẩn đoán PSDS v1 → v2 trên dev annotated (n = 134)",
        ["Đại lượng", "Giá trị"],
        rows,
        [ROOT / d["source"], source],
        revision,
        ["---", "---:"],
    )


def build_ledger(ledger: dict[str, Any], revision: str, source: Path) -> str:
    rows = [["Đánh giá SED trên test", len(ledger["sed"])]]
    rows += [[name, len(items)] for name, items in ledger["other"].items()]
    rows.append(["Đánh giá SED ghi git dirty", sum(1 for r in ledger["sed"] if r["git_dirty"])])
    return table(
        "Sổ ghi các lần chạm tập test", ["Nhóm", "Số mục"], rows, [source], revision,
        ["---", "---:"],
    )


def build_freeze(freeze: dict[str, Any], revision: str, source: Path) -> str:
    """Hệ chính liệt kê riêng; các run phụ của giai đoạn O gộp thành một dòng."""
    rows = []
    phase_o = [r for r in freeze["runs"] if r["label"].startswith("phase O:")]
    for item in freeze["runs"]:
        if item in phase_o:
            continue
        ok = item["exists"] and all(a["exists"] for a in item["artifacts"])
        rows.append([item["label"], f"`{item['run_id']}`", len(item["artifacts"]),
                     "có" if ok else "thiếu"])
    n_files = sum(len(r["artifacts"]) for r in phase_o)
    ok_o = all(r["exists"] and all(a["exists"] for a in r["artifacts"]) for r in phase_o)
    rows.append([f"Giai đoạn O: {len(phase_o)} run phụ (fold, ứng viên, OOF)", "—", n_files,
                 "có" if ok_o else "thiếu"])
    rows += [
        [item["kind"], f"`{Path(item['path']).name}`", 1, "có" if item["exists"] else "thiếu"]
        for item in freeze["external"]
    ]
    return table(
        "Artifact đã đóng băng và kiểm SHA-256",
        ["Thành phần", "Run / tệp", "Số tệp", "Tồn tại"],
        rows, [source], revision, ["---", "---", "---:", "---"],
    )


def build_per_class(run_dir: Path, revision: str) -> str:
    """Event-F1 theo lớp của B0 và LBR V2 trên test annotated; lớp n < 10 chỉ báo số tuyệt đối."""
    from scripts.build_midterm_tables import (
        ANNOTATIONS,
        DATASED_SPLIT,
        SMALL_N,
        UNANNOTATED,
        annotated_test_counts,
    )

    b0_path = run_dir / "evaluation_phase_o_annotated.json"
    v2_path = run_dir / "evaluation_phase_lbr_annotated.json"
    b0 = json.loads(b0_path.read_text(encoding="utf-8"))
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    counts = annotated_test_counts()
    if sum(counts.values()) != v2["n_events_reference"]:
        raise ValueError("Số sự kiện tham chiếu đếm từ nhãn gốc không khớp evaluation đã lưu")
    rows = []
    for class_id, v2_scores in v2["event_based_f1_per_class"].items():
        n = counts[class_id]
        b0_scores = b0["event_based_f1_per_class"][class_id]
        if n >= SMALL_N:
            rows.append([f"`{class_id}`", n, format(b0_scores["f_measure"], ".4f"),
                         format(v2_scores["f_measure"], ".4f"),
                         format(v2_scores["precision"], ".4f"),
                         format(v2_scores["recall"], ".4f")])
        else:
            rows.append([f"`{class_id}`", n, f"khớp {round(b0_scores['recall'] * n)}/{n}",
                         f"khớp {round(v2_scores['recall'] * n)}/{n}", "—", "—"])
    return table(
        "Event-F1 theo lớp của B0 và LBR V2 trên test annotated (n = 139 bản ghi)",
        ["Lớp", "Sự kiện tham chiếu", "B0 F1", "LBR V2 F1", "LBR V2 precision", "LBR V2 recall"],
        rows,
        [b0_path, v2_path, ANNOTATIONS, DATASED_SPLIT, UNANNOTATED],
        revision,
        ["---", "---:", "---:", "---:", "---:", "---:"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-numbers", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, help="test_ledger_*.json")
    parser.add_argument("--freeze", type=Path, help="artifact_freeze_*.json")
    parser.add_argument("--rq3-modes", type=Path, help="rq3_modes_*.json")
    parser.add_argument("--rq3-backfill", type=Path, help="retrieval_backfill_test_*.json")
    parser.add_argument("--lbr-context", type=Path, help="lbr_context_*.json")
    parser.add_argument("--calibration", type=Path, help="calibration_*.json")
    parser.add_argument("--workload", type=Path, help="workload_*.json")
    parser.add_argument("--latency", type=Path, help="latency_*.json")
    parser.add_argument("--run-registry", type=Path, help="run_registry_*.json")
    parser.add_argument("--run-dir", type=Path, help="run B0 final test (bảng theo lớp)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.final_numbers.resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    revision = git_state(ROOT)["revision"]
    builders = {
        "f01_sed.md": build_sed,
        "f02_intersection.md": build_intersection,
        "f03_rq1.md": build_rq1,
        "f04_rq2.md": build_rq2,
        "f05_rq3.md": build_rq3,
        "f06_psds.md": build_psds,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, builder in builders.items():
        text = builder(data, revision, source).replace(
            "scripts.build_thesis_tables", "scripts.build_final_tables"
        )
        (args.output / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"Đã ghi {args.output / name}")
    if args.run_dir is not None:
        text = build_per_class(args.run_dir.resolve(), revision).replace(
            "scripts.build_thesis_tables", "scripts.build_final_tables"
        )
        (args.output / "f09_per_class.md").write_text(text, encoding="utf-8", newline="\n")
        print(f"Đã ghi {args.output / 'f09_per_class.md'}")
    extra = (
        ("f07_ledger.md", build_ledger, args.ledger),
        ("f08_freeze.md", build_freeze, args.freeze),
        ("f05b_rq3_paired.md", build_rq3_paired, args.rq3_modes),
        ("f05c_rq3_groups.md", build_rq3_groups, args.rq3_modes),
        ("f05d_rq3_backfill.md", build_rq3_backfill, args.rq3_backfill),
        ("f10_lbr_context.md", build_lbr_context, args.lbr_context),
        ("f11_calibration.md", build_calibration, args.calibration),
        ("f12_workload.md", build_workload, args.workload),
        ("f13_latency.md", build_latency, args.latency),
        ("f14_run_registry.md", build_run_registry, args.run_registry),
    )
    for name, builder, path in extra:
        if path is None:
            continue
        source = path.resolve()
        text = builder(json.loads(source.read_text(encoding="utf-8")), revision, source).replace(
            "scripts.build_thesis_tables", "scripts.build_final_tables"
        )
        (args.output / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"Đã ghi {args.output / name}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
