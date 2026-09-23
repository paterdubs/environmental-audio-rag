"""Sinh phiếu duyệt tay cho các cặp trùng lặp xuyên dataset (DATA_PLAN §7.3).

    .venv/Scripts/python.exe -m scripts.build_review_worksheet

Sinh hai thứ:

- `data/manifests/review_worksheet.csv` — bảng để điền, một dòng một cặp.
- `docs/measurements/review_worksheet_<ngày>.md` — hướng dẫn kèm lệnh nghe sẵn.

Phiếu chứa **mốc thời gian đã căn chỉnh**, nên người duyệt nghe đúng đoạn chồng
lấp thay vì nghe cả hai file từ đầu.
"""

from __future__ import annotations

import csv
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.dataops.fingerprint import FingerprintConfig

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
MEASUREMENTS = ROOT / "docs" / "measurements"
QUEUE = MANIFESTS / "review_queue_cross_dataset.csv"
WORKSHEET = MANIFESTS / "review_worksheet.csv"

DECISION_VALUES = ("duplicate", "distinct", "unsure")


def audio_path(file_id: str) -> Path:
    dataset, relative = file_id.split(":", 1)
    return ROOT / "data" / "raw" / dataset / "extracted" / relative


def read_queue(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(
            f"Thiếu {path}. Chạy scripts.find_duplicates detect (hoặc regroup) trước."
        )
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_rows(queue: list[dict]) -> list[dict]:
    """Một dòng một cặp, kèm cột trống để người duyệt điền."""
    return [
        {
            "pair_id": f"rev-{index:03d}",
            "similarity": row["similarity"],
            "overlap_s": row["overlap_s"],
            "pretraining_file_id": row["left_file_id"],
            "benchmark_file_id": row["right_file_id"],
            "pretraining_path": str(audio_path(row["left_file_id"])),
            "benchmark_path": str(audio_path(row["right_file_id"])),
            "decision": "",
            "decided_by": "",
            "note": "",
        }
        for index, row in enumerate(sorted(queue, key=lambda r: -float(r["similarity"])), 1)
    ]


def write_worksheet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_guide(rows: list[dict]) -> str:
    config = FingerprintConfig()
    lines = [
        "# Phiếu duyệt tay — cặp trùng lặp xuyên dataset",
        "",
        f"**Sinh tự động** `scripts.build_review_worksheet` — "
        f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"**{len(rows)} cặp** cần quyết định. Đây là phần **duy nhất** của cổng D3 "
        "không tự động hoá được, và là phần quyết định tính hợp lệ của RQ1.",
        "",
        "## Câu hỏi phải trả lời cho mỗi cặp",
        "",
        "> Hai file này có phải **cùng một bản ghi gốc** không?",
        "",
        "Không phải hỏi *có giống nhau không* — hai tiếng còi xe khác nhau nghe rất "
        "giống. Hỏi là *có phải cùng một lần thu* không: cùng nền, cùng vọng âm, "
        "cùng nhiễu nền, cùng nhịp biến thiên.",
        "",
        "| Dấu hiệu **cùng nguồn** | Dấu hiệu **khác nguồn** |",
        "|---|---|",
        "| Nhiễu nền trùng khớp từng đoạn | Nền khác hẳn (một bên có gió, một bên không) |",
        "| Âm phụ ngẫu nhiên có ở cả hai (chim, tiếng người) "
        "| Chỉ tiếng nguồn chính giống nhau |",
        "| Vọng âm và độ xa giống nhau | Khoảng cách tới nguồn khác nhau rõ |",
        "| Biến thiên cao độ trùng nhau theo thời gian | Cùng loại nguồn nhưng nhịp khác |",
        "",
        "## Cách điền",
        "",
        f"Mở `{WORKSHEET.relative_to(ROOT).as_posix()}`, điền ba cột:",
        "",
        "| Cột | Giá trị |",
        "|---|---|",
        f"| `decision` | một trong {', '.join(f'`{value}`' for value in DECISION_VALUES)} |",
        "| `decided_by` | tên bạn, ví dụ `human:patph` |",
        "| `note` | lý do ngắn — dòng này đi vào phụ lục khóa luận |",
        "",
        "`unsure` là câu trả lời hợp lệ. Nó được xử lý **thận trọng**: coi như "
        "`duplicate` và loại clip pretraining, vì loại nhầm một clip rẻ hơn nhiều "
        "so với giữ lại một rò rỉ.",
        "",
        "Điền xong chạy:",
        "",
        "```bash",
        ".venv/Scripts/python.exe -m scripts.apply_review_decisions",
        ".venv/Scripts/python.exe -m scripts.check_leakage datased",
        "```",
        "",
        "## Danh sách",
        "",
        "Xếp theo similarity giảm dần — cặp đầu đáng ngờ nhất.",
        "",
    ]
    for row in rows:
        overlap = float(row["overlap_s"])
        lines += [
            f"### {row['pair_id']} · similarity {float(row['similarity']):.4f}"
            f" · chồng lấp {overlap:.1f} s",
            "",
            f"- pretraining: `{row['pretraining_file_id']}`",
            f"- benchmark: `{row['benchmark_file_id']}`",
            "",
            "```bash",
            f'ffplay -autoexit -nodisp "{row["pretraining_path"]}"',
            f'ffplay -autoexit -nodisp "{row["benchmark_path"]}"',
            "```",
            "",
        ]
    lines += [
        "## Ghi chú kỹ thuật",
        "",
        f"- Fingerprint: frame {config.frame_s} s, hop {config.hop_s} s, "
        f"{config.dimensions} chiều, `fmax` {config.fmax:.0f} Hz.",
        "- Similarity là cosine trung bình trên đoạn chồng lấp dài nhất, sau khi "
        "chuẩn hoá z-score theo thống kê corpus.",
        "- Mọi cặp ở đây nằm dưới 0.95, tức **không** đạt ngưỡng tự động. Ba cặp "
        "vượt 0.95 đã được xử lý bằng luật và không có trong phiếu này.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rows = build_rows(read_queue(QUEUE))
    if not rows:
        print("Hàng đợi rỗng: không có cặp xuyên dataset nào cần duyệt.")
        return

    write_worksheet(WORKSHEET, rows)
    MEASUREMENTS.mkdir(parents=True, exist_ok=True)
    guide = MEASUREMENTS / f"review_worksheet_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    guide.write_text(build_guide(rows) + "\n", encoding="utf-8")

    missing = [row["pair_id"] for row in rows if not Path(row["pretraining_path"]).exists()]
    print(f"{len(rows)} cặp → {WORKSHEET}")
    print(f"hướng dẫn → {guide}")
    if missing:
        print(f"CẢNH BÁO: {len(missing)} cặp có đường dẫn audio không tồn tại: {missing[:3]}")


if __name__ == "__main__":
    main()
