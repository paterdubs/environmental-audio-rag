"""Bảng "Kết quả chính" mở đầu Chương 6: mỗi câu hỏi một dòng, số đọc từ các tệp đo đã khóa.

Không tính lại chỉ số nào; chỉ đọc `final_numbers`, `rq3_modes`, `retrieval_backfill_test`,
`caption_vs_gt_dev` và `latency`. Đổi tệp đo thì bảng đổi theo.

    .venv/Scripts/python.exe -m scripts.report_key_results
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ml.provenance import git_state
from scripts.report_final_numbers_render import v
from scripts.report_system_tables import render

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "docs" / "measurements"
DEFAULTS = {
    "final_numbers": MEASUREMENTS / "final_numbers_20261110.json",
    "rq3_modes": MEASUREMENTS / "rq3_modes_20261123.json",
    "backfill": MEASUREMENTS / "retrieval_backfill_test_20261124.json",
    "caption_tiers": MEASUREMENTS / "caption_vs_gt_dev_20261124.json",
    "latency": MEASUREMENTS / "latency_lbrv3_20261123.json",
}
LOW_COVERAGE = ("f2", "B0", "lbrv2")
SYSTEMS = ("f2", "B0", "lbrv2", "lbrv3")


def _num(value: float, fmt: str = ".3f") -> str:
    return format(value, fmt).replace(".", ",")


def _ci(cell: dict[str, Any], fmt: str = "+.3f") -> str:
    est, low, high = (v(cell[k], fmt) for k in ("estimate", "lower", "upper"))
    return f"{est} [{low}; {high}]".replace(".", ",").replace("-", "−")


def _span(values: list[float], fmt: str = ".3f") -> str:
    if min(values) == max(values):
        return "0" if max(values) == 0 else _num(max(values), fmt)
    return f"{_num(min(values), fmt)} đến {_num(max(values), fmt)}"


def _signed_span(values: list[float]) -> str:
    if min(values) == max(values):
        return format(values[0], "+.3f").replace(".", ",").replace("-", "−")
    text = f"{format(min(values), '+.3f')} đến {format(max(values), '+.3f')}"
    return text.replace(".", ",").replace("-", "−")


def _sed_cell(b0: dict[str, Any], v2: dict[str, Any]) -> str:
    micro = f"Micro {v(b0['micro'])} → {v(v2['micro'])}".replace(".", ",")
    seg = f"F1 theo đoạn {v(b0['segment_f1_1s'])} → {v(v2['segment_f1_1s'])}"
    psds = f"PSDS-2 (lưới log) {v(b0['psds_log']['psds_2'])} → {v(v2['psds_log']['psds_2'])}"
    delta = _ci(v2["delta_micro_vs_b0"], "+.4f")
    return f"{micro}, hiệu {delta}; " + f"{seg}; {psds}".replace(".", ",")


def rows_from(data: dict[str, dict[str, Any]]) -> list[list[str]]:
    final, modes = data["final_numbers"], data["rq3_modes"]
    backfill, tiers, latency = data["backfill"], data["caption_tiers"], data["latency"]
    rq1 = final["rq1"]["v2"]["bootstrap_c_minus_b"]
    sed = final["sed"]["rows"]
    b0, v2 = sed["B0"], sed["lbrv2_f1"]
    e2e = final["rq2"]["llm_e2e"]

    def rq2(mode: str, metric: str) -> list[float]:
        return [e2e[mode][s][metric]["value"]["estimate"] for s in SYSTEMS]

    vs_gt = [
        tiers["results"][f"{s}/template"]["e2e_vs_gt"]["omission_rate"]["estimate"]
        for s in LOW_COVERAGE
    ]
    hybrid_vs_vector = [modes["systems"][s]["paired"]["hybrid−vector_only/en"] for s in SYSTEMS]
    exact = [modes["systems"][s]["filter_exactness"]["vector_only"] for s in SYSTEMS]
    gain = [
        backfill["results"][f"{s}/gold/en"]["summary"]["paired_ndcg@10"]["backfill−vector_only"]
        for s in SYSTEMS
    ]
    return [
        [
            "RQ1: thêm DataSEC",
            "Test, công thức v2, 3 + 3 seed",
            f"C − B micro {_ci(rq1, '+.4f')}",
            "Không có khác biệt đo được (KTC chứa 0)",
        ],
        [
            "SED: B0 → LBR V2",
            "Test annotated, n = 139",
            _sed_cell(b0, v2),
            "LBR tăng event-F1 rõ; đổi lại F1 theo đoạn và PSDS-2 thấp hơn",
        ],
        [
            "RQ2: so với dự đoán",
            "Test annotated, bốn hệ SED",
            f"Viết tự do: ảo giác {_span(rq2('unconstrained', 'hallucination_rate'))}, suy diễn "
            f"bối cảnh {_span(rq2('unconstrained', 'context_term_rate'))}; có ràng buộc: "
            f"{_span(rq2('constrained', 'hallucination_rate'))} và "
            f"{_span(rq2('constrained', 'context_term_rate'))}",
            "Ràng buộc loại lỗi của bộ sinh (theo cấu tạo); cái giá là bỏ sót",
        ],
        [
            "RQ2: so với nhãn gốc",
            "Dev annotated, f2 / B0 / LBR V2",
            f"Template bỏ sót {_span(vs_gt)} số lớp có thật",
            "Lỗi còn lại do SED, không do bộ sinh",
        ],
        [
            "RQ3: hybrid so với vector_only",
            "Test, bộ lọc gold, bốn kho",
            f"Hiệu nDCG@10 {_signed_span([h['estimate'] for h in hybrid_vs_vector[:3]])} ở ba kho "
            f"độ phủ thấp, {_signed_span([hybrid_vs_vector[3]['estimate']])} ở V3; "
            f"độ đúng bộ lọc 1,000 so với {_span(exact)}",
            "Lọc cứng luôn đúng điều kiện nhưng xếp hạng bị chặn bởi độ phủ của SED",
        ],
        [
            "RQ3: chế độ backfill",
            "Test, bộ lọc gold, bốn kho",
            f"Hơn vector_only {_signed_span([g['estimate'] for g in gain])}, mọi KTC > 0",
            "Cải tiến có tác dụng nằm ở độ phủ khi truy hồi",
        ],
        [
            "Ứng dụng",
            "CPU, 10 bản ghi TRAIN",
            f"Tải lên và phân tích trung vị {_num(latency['elapsed_s']['median'], '.2f')} s; "
            f"truy vấn {_num(latency['query_s']['median'], '.2f')} s",
            "Phân tích âm thanh chạy cục bộ trên CPU; bộ phân tích câu hỏi cần máy chủ llama.cpp",
        ],
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for key, path in DEFAULTS.items():
        parser.add_argument(f"--{key.replace('_', '-')}", type=Path, default=path)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "report" / "final_tables" / "f00_key_results.md"
    )
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in DEFAULTS}
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in paths.items()}
    text = render(
        "Kết quả chính theo câu hỏi nghiên cứu",
        ["Câu hỏi", "Tập đo", "Kết quả (KTC 95%)", "Kết luận"],
        rows_from(data),
        [path.relative_to(ROOT).as_posix() for path in paths.values()],
        git_state(ROOT)["revision"],
    ).replace("scripts.report_system_tables", "scripts.report_key_results")
    args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
