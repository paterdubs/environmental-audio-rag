"""Sinh các sơ đồ hệ thống cho báo cáo chính thức (giai đoạn F).

Năm hình, đều vẽ theo mã nguồn và cấu hình hiện hành, không chạy suy luận:

- `s01_data_flow.png`: luồng xử lý dữ liệu từ tệp âm thanh tới kho sự kiện (Chương 4);
- `s02_lbr.png`: hai bộ học của LBR và cross-fit (Chương 4);
- `s03_deployment.png`: kiến trúc triển khai Docker Compose (Chương 5);
- `s04_upload_flow.png`, `s05_query_flow.png`: hai luồng hệ thống dạng tuần tự (Chương 5);
- `s06_erd.png`: sơ đồ bảng của kho sự kiện, đọc trực tiếp từ migration SQL (Chương 5).

Tham số trên hình (tần số lấy mẫu, cửa sổ, bước trượt, số fold, mô hình) đọc từ manifest và
cấu hình; nếu mã đổi mà hình không đổi theo, hàm `served_facts` báo lỗi.

    .venv/Scripts/python.exe -m scripts.build_system_figures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from scripts.build_midterm_figures import (
    FILLS,
    INK,
    MUTED,
    WIDTH_IN,
    arrow,
    box,
    canvas,
    figure_architecture,
    save,
)
from services.common.audio import ALLOWED_SUFFIXES, MAX_BYTES, MAX_DURATION_S

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "report" / "final_figures"
SERVED_RUN = ROOT / "ml" / "runs" / "sed_served_B0_20261107T175659Z" / "manifest.json"
LLM_CONFIG = ROOT / "ml" / "configs" / "caption_llm.yaml"
MIGRATION = ROOT / "db" / "migrations" / "001_event_store.sql"


@dataclass(frozen=True)
class ServedFacts:
    folds: int
    window_s: float
    hop_s: float
    weighting: str
    recipe: str
    llm: str
    llm_runtime: str


def served_facts() -> ServedFacts:
    """Thông số của hệ phục vụ, đọc từ manifest B0 và manifest thành viên đầu tiên."""
    served = json.loads(SERVED_RUN.read_text(encoding="utf-8"))["config"]
    first = ROOT / "ml" / "runs" / served["members"][0] / "manifest.json"
    member = json.loads(first.read_text(encoding="utf-8"))["config"]
    llm = yaml.safe_load(LLM_CONFIG.read_text(encoding="utf-8"))
    window_s = member["window_frames"] / member["frame_rate"]
    return ServedFacts(
        folds=len(served["members"]),
        window_s=window_s,
        hop_s=float(served["serving"]["hop_seconds"]),
        weighting=served["serving"]["window_weighting"],
        recipe=member["recipe"],
        llm=llm["model"]["name"],
        llm_runtime=f"{llm['runtime']['name']} {llm['runtime']['build']}",
    )


def _fmt(value: float) -> str:
    return f"{value:g}".replace(".", ",")


# ---------------------------------------------------------------- luồng dữ liệu
def figure_data_flow(path: Path, facts: ServedFacts) -> list[str]:
    if facts.recipe != "t2b":
        raise ValueError(
            f"hình giả định công thức T2b (Frame-MobileNet), manifest ghi {facts.recipe}"
        )
    fig, ax = canvas(6.2)
    w, h, x0, gap = 1.95, 0.78, 0.1, 0.25
    xs = [x0 + i * (w + gap) for i in range(3)]
    rows = [5.25, 4.12, 2.99]
    steps = [
        (
            "1. Tệp âm thanh",
            f"{'/'.join(s[1:].upper() for s in ALLOWED_SUFFIXES)}\n"
            f"≤ {MAX_BYTES // 2**20} MB, ≤ {MAX_DURATION_S:g} s; SHA-256",
            "service",
        ),
        ("2. Tiền xử lý", "đơn kênh, 16 kHz, PCM16\nlog-mel 128 dải, 100 khung/s", "service"),
        (
            "3. Cửa sổ trượt",
            f"cửa sổ {_fmt(facts.window_s)} s, bước {_fmt(facts.hop_s)} s\ngộp trọng số tam giác",
            "service",
        ),
        (
            "4. Mô hình SED (B0)",
            f"Frame-MobileNet × {facts.folds} fold\ntrung bình xác suất",
            "model",
        ),
        ("5. Xác suất theo khung", "21 lớp × khung 10 ms\n(ma trận p[t, c])", "store"),
        ("6. cSEBB", "điểm đổi hướng → hộp sự kiện\nngưỡng chỉ giữ / bỏ hộp", "service"),
        ("7. LBR", "dời biên + chấm lại hộp\n(V2: số chính, V3: demo)", "model"),
        ("8. Dòng thời gian", "(lớp, onset, offset, điểm)\nkẹp trong độ dài bản ghi", "store"),
        ("9. Mô tả EN / VI", "template gộp theo lớp\nrào đón khi điểm thấp", "service"),
    ]
    centers = {}
    for index, (title, body, kind) in enumerate(steps):
        row, col = divmod(index, 3)
        col = col if row != 1 else 2 - col  # hàng giữa chạy ngược để mũi tên nối kiểu rắn
        x, y = xs[col], rows[row]
        box(ax, x, y, w, h, title, body, kind)
        centers[index] = (x, y)
    for index in range(len(steps) - 1):
        (xa, ya), (xb, yb) = centers[index], centers[index + 1]
        if ya == yb:
            if xb > xa:
                arrow(ax, (xa + w, ya + h / 2), (xb, yb + h / 2))
            else:
                arrow(ax, (xa, ya + h / 2), (xb + w, yb + h / 2))
        else:
            arrow(ax, (xa + w / 2, ya), (xb + w / 2, yb + h))
    # nhánh lưu trữ
    yb = 1.55
    box(
        ax,
        xs[0],
        yb,
        w,
        h,
        "10. Tài liệu truy hồi",
        "mô tả EN + VI + tóm tắt\nsự kiện chuẩn hóa",
        "service",
    )
    box(ax, xs[1], yb, w, h, "11. Nhúng BGE-M3", "vector 1024 chiều\nchuẩn hóa cosine", "model")
    box(
        ax,
        xs[2],
        yb,
        w,
        h,
        "12. Kho sự kiện",
        "PostgreSQL 16 + pgvector\nB-tree, GIN, HNSW",
        "store",
    )
    x9, y9 = centers[8]
    arrow(
        ax,
        (x9 + w / 2, y9),
        (xs[2] + w / 2, yb + h),
        "sự kiện, mô tả",
        offset=(0.06, 0.0),
        ha="left",
    )
    x8, y8 = centers[7]
    arrow(ax, (x8 + w / 2, y8), (xs[0] + w / 2, yb + h))
    arrow(ax, (xs[0] + w, yb + h / 2), (xs[1], yb + h / 2))
    arrow(ax, (xs[1] + w, yb + h / 2), (xs[2], yb + h / 2))
    box(
        ax,
        x0,
        0.25,
        3 * w + 2 * gap,
        0.78,
        "Ngoại tuyến (chỉ khi nghiên cứu, không chạy khi phục vụ)",
        "chọn ngưỡng, cSEBB, LBR trên dev / dự đoán ngoài mẫu → khóa tham số cạnh checkpoint\n"
        "test chạy một lần trên cấu hình đã khóa; dịch vụ suy luận chỉ nạp tham số đã khóa",
        "offline",
    )
    save(fig, path)
    return [
        "ml/inference/pipeline.py",
        "ml/inference/sed.py",
        "ml/models/frame_mn_finetune.py",
        "ml/retrieval/document_builder.py",
        SERVED_RUN.relative_to(ROOT).as_posix(),
    ]


# ---------------------------------------------------------------- LBR
def figure_lbr(path: Path) -> list[str]:
    fig, ax = canvas(3.9)
    w, h = 1.95, 0.95
    box(ax, 0.1, 2.75, w, h, "Đầu vào", "hộp cSEBB của B0\n+ xác suất khung ngoài mẫu", "store")
    box(
        ax,
        2.35,
        2.75,
        w,
        h,
        "Đặc trưng mỗi hộp",
        "điểm, độ dài, vị trí, lớp;\nđường xác suất quanh\nonset / offset",
        "service",
    )
    box(
        ax,
        4.6,
        2.75,
        1.9,
        h,
        "Bộ tinh chỉnh",
        "GBM hồi quy (mất mát\ntuyệt đối): Δonset, Δoffset",
        "model",
    )
    box(
        ax,
        4.6,
        1.45,
        1.9,
        h,
        "Bộ chấm lại",
        "GBM phân loại trên\nđặc trưng + Δ: hộp đúng?",
        "model",
    )
    box(ax, 2.35, 1.45, w, h, "Điểm vận hành", "V2: tối đa event-F1\nV3: ưu tiên phát hiện")
    box(ax, 0.1, 1.45, w, h, "Dòng thời gian", "hộp đã dời biên,\ngiữ nếu điểm ≥ ngưỡng", "store")
    box(
        ax,
        0.1,
        0.1,
        6.4,
        0.95,
        "Cross-fit lồng nhau (5 fold theo bản ghi)",
        "mô hình áp cho fold k chỉ học trên 4 fold còn lại;\n"
        "nhãn chọn ngưỡng và nhãn cho bộ chấm lại đến từ vòng chia bên trong",
        "offline",
    )
    arrow(ax, (2.05, 3.22), (2.35, 3.22))
    arrow(ax, (4.3, 3.22), (4.6, 3.22))
    arrow(ax, (5.55, 2.75), (5.55, 2.4), "Δ", offset=(0.08, -0.08), ha="left")
    arrow(ax, (4.6, 1.92), (4.3, 1.92))
    arrow(ax, (2.35, 1.92), (2.05, 1.92))
    save(fig, path)
    return [
        "ml/postprocessing/boundary_refine.py",
        "ml/postprocessing/lbr_crossfit.py",
        "ml/postprocessing/lbr_apply.py",
    ]


# ---------------------------------------------------------------- tuần tự
def sequence(
    path: Path, actors: list[str], messages: list[tuple[int, int, str]], notes: dict[int, str]
) -> None:
    """Sơ đồ tuần tự: mỗi thông điệp (từ, tới, nhãn); từ == tới là bước xử lý nội bộ."""
    from matplotlib.patches import FancyBboxPatch, Rectangle

    step = 0.46
    height = 1.0 + step * (len(messages) + 0.6)
    fig, ax = canvas(height)
    span = WIDTH_IN - 0.4
    xs = [0.2 + span * (i + 0.5) / len(actors) for i in range(len(actors))]
    top = height - 0.15
    for x, name in zip(xs, actors, strict=True):
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.6, top - 0.42),
                1.2,
                0.4,
                boxstyle="round,pad=0,rounding_size=0.05",
                linewidth=0.9,
                edgecolor=MUTED,
                facecolor=FILLS["service"],
            )
        )
        ax.text(
            x, top - 0.22, name, ha="center", va="center", fontsize=8, fontweight="bold", color=INK
        )
        ax.plot([x, x], [top - 0.42, 0.1], color=MUTED, linewidth=0.7, linestyle=(0, (3, 3)))
    y = top - 0.75
    for index, (src, dst, label) in enumerate(messages, start=1):
        text = f"{index}. {label}"
        if src == dst:
            ax.add_patch(
                Rectangle(
                    (xs[src] - 0.05, y - 0.14),
                    0.1,
                    0.28,
                    facecolor=FILLS["model"],
                    edgecolor=MUTED,
                    linewidth=0.7,
                )
            )
            ax.text(xs[src] + 0.12, y, text, ha="left", va="center", fontsize=7.3, color=INK)
        else:
            arrow(ax, (xs[src], y), (xs[dst], y))
            ax.text(
                (xs[src] + xs[dst]) / 2,
                y + 0.04,
                text,
                ha="center",
                va="bottom",
                fontsize=7.3,
                color=INK,
            )
        if index in notes:
            ax.text(
                WIDTH_IN - 0.1,
                y - 0.17,
                notes[index],
                ha="right",
                va="top",
                fontsize=6.8,
                color=MUTED,
                style="italic",
            )
        y -= step
    save(fig, path)


def figure_upload_flow(path: Path, facts: ServedFacts) -> list[str]:
    actors = ["Giao diện", "Dịch vụ API", "Dịch vụ suy luận", "PostgreSQL"]
    messages = [
        (0, 1, "POST /api/v1/audio/upload (tệp âm thanh)"),
        (1, 1, "kiểm định dạng, dung lượng, độ dài; SHA-256"),
        (1, 3, "tìm bản ghi trùng mã băm"),
        (3, 1, "đã có → trả mã bản ghi cũ, dừng"),
        (1, 2, "POST /v1/analyze (tệp, recording_id)"),
        (2, 2, f"SED B0 × {facts.folds} fold → cSEBB → LBR V3"),
        (2, 2, "mô tả gộp EN/VI, tài liệu, nhúng BGE-M3"),
        (2, 1, "dòng thời gian, mô tả, tài liệu, vector"),
        (1, 1, "đối chiếu SHA-256 tệp nhận và tệp lưu"),
        (1, 3, "ghi 5 bảng trong một giao dịch"),
        (1, 0, "201: recording_id, dòng thời gian, mô tả"),
    ]
    notes = {5: "lỗi suy luận → 503, xóa tệp đã lưu", 10: "lỗi ghi → rollback, xóa tệp"}
    sequence(path, actors, messages, notes)
    return [
        "services/api/app/recordings.py",
        "services/inference/app/main.py",
        "ml/inference/engine.py",
        "ml/inference/pipeline.py",
    ]


def figure_query_flow(path: Path, facts: ServedFacts) -> list[str]:
    actors = ["Giao diện", "Dịch vụ API", "llama.cpp", "Dịch vụ suy luận", "PostgreSQL"]
    messages = [
        (0, 1, "POST /api/v1/retrieval/parse (câu hỏi)"),
        (1, 2, "sinh JSON theo lược đồ 21 lớp, 4 điều kiện"),
        (2, 1, "bộ lọc: lớp, thời lượng, trước / sau ..."),
        (1, 0, "thẻ bộ lọc để người dùng sửa"),
        (0, 1, "POST /api/v1/retrieval/query (bộ lọc, chế độ)"),
        (1, 3, "POST /v1/embed (câu hỏi)"),
        (3, 1, "vector BGE-M3"),
        (1, 4, "SQL: lọc cứng + xếp hạng cosine (HNSW)"),
        (1, 4, "backfill: lấp chỗ trống bằng kết quả ngữ nghĩa"),
        (4, 1, "bản ghi, sự kiện bằng chứng"),
        (1, 1, "câu trả lời tất định, kiểm bằng chứng"),
        (1, 0, "câu trả lời + (bản ghi, khoảng thời gian)"),
    ]
    notes = {
        2: f"{facts.llm} trên {facts.llm_runtime}; tắt → 503, vẫn lọc tay được",
        9: "kết quả gần nghĩa chỉ được nêu tên, không làm bằng chứng",
    }
    sequence(path, actors, messages, notes)
    return [
        "services/api/app/retrieval.py",
        "ml/retrieval/query_parser.py",
        "ml/retrieval/store.py",
        "ml/configs/caption_llm.yaml",
    ]


# ---------------------------------------------------------------- ERD
_TABLE = re.compile(r"CREATE TABLE (\w+) \((.*?)\n\);", re.S)
_FK = re.compile(r"REFERENCES (\w+)\((\w+)\)")


@dataclass(frozen=True)
class Table:
    name: str
    columns: tuple[tuple[str, str, bool], ...]  # (tên, kiểu, là khóa chính)
    references: tuple[tuple[str, str], ...]  # (cột, bảng đích)


def parse_schema(sql: str) -> list[Table]:
    tables = []
    for name, body in _TABLE.findall(sql):
        columns, refs, composite = [], [], set()
        for raw in body.split("\n"):
            line = raw.strip().rstrip(",")
            if not line or line.startswith("--"):
                continue
            if line.startswith("PRIMARY KEY"):
                composite = {
                    c.strip() for c in line[line.index("(") + 1 : line.index(")")].split(",")
                }
                continue
            if line.startswith(("UNIQUE", "CHECK", "CONSTRAINT", "FOREIGN")):
                continue
            parts = line.split()
            column, kind = parts[0], parts[1].split("(")[0]
            if parts[1].upper().startswith("VECTOR("):
                kind = parts[1].lower()
            columns.append([column, kind, "PRIMARY KEY" in line])
            fk = _FK.search(line)
            if fk:
                refs.append((column, fk.group(1)))
        for column in columns:
            column[2] = column[2] or column[0] in composite
        tables.append(Table(name, tuple(tuple(c) for c in columns), tuple(refs)))
    return tables


ERD_LAYOUT = {  # (x, y đỉnh) theo inch; bảng mới trong migration mà thiếu ở đây sẽ báo lỗi
    "captions": (0.1, 7.1),
    "caption_evidence": (2.3, 6.6),
    "events": (4.5, 7.1),
    "recordings": (2.3, 4.9),
    "retrieval_documents": (0.1, 3.6),
    "event_subclass_predictions": (4.5, 4.6),
    "runs": (4.5, 3.1),
}
ERD_HEIGHT_IN = 7.2


def _fk_arrow(
    child: tuple[float, float, float, float], parent: tuple[float, float, float, float]
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Mũi tên từ bảng con tới bảng cha: ngang nếu hai bảng chồng nhau theo chiều dọc, dọc nếu
    chồng theo chiều ngang, còn lại nối hai góc gần nhau."""
    cx, ctop, cw, ch = child
    px, ptop, pw, ph = parent
    low, high = max(ctop - ch, ptop - ph), min(ctop, ptop)
    if high - low > 0.2:
        y = (low + high) / 2
        return ((cx, y), (px + pw, y)) if cx > px else ((cx + cw, y), (px, y))
    left, right = max(cx, px), min(cx + cw, px + pw)
    if right - left > 0.2:
        x = (left + right) / 2
        return ((x, ctop), (x, ptop - ph)) if ctop < ptop else ((x, ctop - ch), (x, ptop))
    start_x = cx + cw if cx < px else cx
    end_x = px if cx < px else px + pw
    start_y = ctop - ch if ctop > ptop else ctop
    end_y = ptop if ctop > ptop else ptop - ph
    return (start_x, start_y), (end_x, end_y)


def figure_erd(path: Path, sql_path: Path = MIGRATION, max_columns: int = 9) -> list[str]:
    tables = parse_schema(sql_path.read_text(encoding="utf-8"))
    missing = {t.name for t in tables} - set(ERD_LAYOUT)
    if missing:
        raise KeyError(f"bảng chưa có vị trí trên ERD: {sorted(missing)}")
    fig, ax = canvas(ERD_HEIGHT_IN)
    width, row = 2.0, 0.19
    anchors = {}
    for table in tables:
        x, top = ERD_LAYOUT[table.name]
        shown = list(table.columns[:max_columns])
        hidden = len(table.columns) - len(shown)
        height = row * (len(shown) + 1 + (1 if hidden else 0)) + 0.08
        from matplotlib.patches import Rectangle

        ax.add_patch(
            Rectangle(
                (x, top - height), width, height, facecolor="white", edgecolor=MUTED, linewidth=0.9
            )
        )
        ax.add_patch(
            Rectangle(
                (x, top - row - 0.04),
                width,
                row + 0.04,
                facecolor=FILLS["store"],
                edgecolor=MUTED,
                linewidth=0.9,
            )
        )
        ax.text(
            x + width / 2,
            top - row / 2 - 0.02,
            table.name,
            ha="center",
            va="center",
            fontsize=7.6,
            fontweight="bold",
            color=INK,
        )
        fk_columns = {c for c, _ in table.references}
        for index, (column, kind, primary) in enumerate(shown):
            y = top - row * (index + 1.5) - 0.05
            mark = "PK " if primary else ("FK " if column in fk_columns else "")
            ax.text(
                x + 0.06,
                y,
                f"{mark}{column}",
                ha="left",
                va="center",
                fontsize=6.6,
                color=INK,
                fontweight="bold" if primary else "normal",
            )
            ax.text(
                x + width - 0.06,
                y,
                kind.lower(),
                ha="right",
                va="center",
                fontsize=6.2,
                color=MUTED,
            )
        if hidden:
            ax.text(
                x + 0.06,
                top - row * (len(shown) + 1.5) - 0.05,
                f"… {hidden} cột khác",
                ha="left",
                va="center",
                fontsize=6.4,
                color=MUTED,
                style="italic",
            )
        anchors[table.name] = (x, top, width, height)
    for table in tables:
        for _, target in table.references:
            start, end = _fk_arrow(anchors[table.name], anchors[target])
            arrow(ax, start, end)
    ax.text(
        0.1,
        0.15,
        "mũi tên: khóa ngoại (ON DELETE CASCADE) trỏ tới bảng cha",
        ha="left",
        va="bottom",
        fontsize=6.8,
        color=MUTED,
        style="italic",
    )
    save(fig, path)
    return [sql_path.relative_to(ROOT).as_posix()]


# ---------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    facts = served_facts()
    sources = {
        "s01_data_flow.png": figure_data_flow(args.output / "s01_data_flow.png", facts),
        "s02_lbr.png": figure_lbr(args.output / "s02_lbr.png"),
        "s03_deployment.png": figure_architecture(
            args.output / "s03_deployment.png",
            served=f"SED B0 × {facts.folds} fold + LBR V3\nmô tả gộp EN/VI,",
        ),
        "s04_upload_flow.png": figure_upload_flow(args.output / "s04_upload_flow.png", facts),
        "s05_query_flow.png": figure_query_flow(args.output / "s05_query_flow.png", facts),
        "s06_erd.png": figure_erd(args.output / "s06_erd.png"),
    }
    for name, used in sources.items():
        print(f"{name}: {', '.join(used)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
