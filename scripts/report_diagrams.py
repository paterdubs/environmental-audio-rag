"""Bảy sơ đồ khối của bản báo cáo tinh gọn, vẽ bằng shape Word (sửa được trong Word).

Nội dung giống các hình PNG của `build_system_figures` và `build_midterm_figures`, và đọc cùng
nguồn: manifest của hệ đang phục vụ, giới hạn tải lên trong `services/common/audio.py`, tệp kiểm
kê và tập chia đã khóa, migration SQL. Mã đổi mà sơ đồ không đổi theo thì test báo lỗi.

    @@DIAGRAM:pipeline@@   (dùng trong report/gon_src, ngay trước @@CAP:fig:…@@)
"""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import cache
from pathlib import Path

from scripts.build_system_figures import (
    ERD_LAYOUT,
    MIGRATION,
    _fmt,
    parse_schema,
    served_facts,
)
from scripts.report_docx.diagram import Box, Diagram, Line
from services.common.audio import ALLOWED_SUFFIXES, MAX_BYTES, MAX_DURATION_S

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 15.5


def _grid(columns: int, box_w: float) -> list[float]:
    gap = (WIDTH - columns * box_w) / (columns - 1)
    return [round(i * (box_w + gap), 3) for i in range(columns)]


def _label(x: float, y: float, w: float, text: str, size: float = 8.0, h: float = 0.5,
           align: str = "center", italic: bool = False) -> Box:
    return Box(x, y, w, h, (text,), fill="none", title=False, size=size, border=False,
               align=align, italic=italic)


def _fmt_int(number: int) -> str:
    return f"{number:,}".replace(",", ".")


# ---------------------------------------------------------------- D0–D4
def pipeline() -> Diagram:
    load = lambda rel: json.loads((ROOT / rel).read_text(encoding="utf-8"))  # noqa: E731
    sec = load("data/manifests/datasec_inventory_summary.json")
    sed = load("data/manifests/datased_inventory_summary.json")
    poly = load("data/manifests/datased_preparation_audit.json")["annotations"]["polyphonic"]
    dup = load("data/manifests/duplicate_audit.json")
    s_sed = load("data/splits/datased_polyphonic.frozen.json")["items"]
    s_sec = load("data/splits/datasec_classification.frozen.json")["items"]
    excluded = sec["files"] - sum(s_sec.values())
    w, h = 4.6, 2.0
    x0, x1, x2 = _grid(3, w)
    y1 = 2.7
    items = (
        Box(x0, 0, w, h, ("D0. Kiểm tệp nén", "kích thước và MD5,", "nhãn khớp hệ lớp,",
                          "trước khi giải nén")),
        Box(x1, 0, w, h, ("D1. Kiểm kê", f"DataSEC {_fmt_int(sec['files'])} tệp",
                          f"DataSED {_fmt_int(sed['files'])} tệp", "trích sẵn phổ log-mel")),
        Box(x2, 0, w, h, ("D2. Chuẩn hóa nhãn", f"{_fmt_int(poly['events'])} sự kiện đa âm",
                          f"{poly['classes']} lớp, phủ {poly['recordings_with_events']}"
                          f"/{sed['files']} bản ghi", "nhãn gốc không sửa")),
        Box(x2, y1, w, h, ("D3. Tìm bản trùng", f"ba tầng: {dup['groups']} nhóm trùng",
                           f"{dup['cross_dataset_groups']} nhóm giữa hai bộ",
                           f"{dup['review_queue_cross_dataset']} cặp nghe duyệt tay")),
        Box(x1, y1, w, h, ("D4. Chia tập và khóa",
                           f"DataSED {s_sed['train']}/{s_sed['validation']}/{s_sed['test']}",
                           f"DataSEC {_fmt_int(s_sec['train'])}/{s_sec['validation']}"
                           f"/{s_sec['test']}", f"loại {excluded} đoạn DataSEC"),
            fill="offline"),
        Box(x0, y1, w, h, ("Cổng sau chỉ chạy khi cổng trước đạt.",
                           "Tập chia được khóa bằng mã băm SHA-256."),
            fill="none", title=False, border=False, italic=True, size=9),
        Line(((x0 + w, 1.0), (x1, 1.0))),
        Line(((x1 + w, 1.0), (x2, 1.0))),
        Line(((x2 + w / 2, h), (x2 + w / 2, y1))),
        Line(((x2, y1 + 1.0), (x1 + w, y1 + 1.0))),
    )
    return Diagram("pipeline", WIDTH, y1 + h, items,
                   "Quy trình chuẩn bị dữ liệu D0 đến D4")


# ---------------------------------------------------------------- luồng dữ liệu
def dataflow() -> Diagram:
    facts = served_facts()
    if facts.recipe != "t2b":
        raise ValueError(
            f"sơ đồ giả định công thức Frame-MobileNet (t2b), manifest ghi {facts.recipe}"
        )
    formats = "/".join(s[1:].upper() for s in ALLOWED_SUFFIXES)
    steps = [
        ("1. Tệp âm thanh", formats, f"≤ {MAX_BYTES // 2**20} MB, ≤ {MAX_DURATION_S:g} s"),
        ("2. Tiền xử lý", "đơn kênh 16 kHz;", "log-mel 128 dải, 100 khung/s"),
        ("3. Cửa sổ trượt", f"dài {_fmt(facts.window_s)} s, bước {_fmt(facts.hop_s)} s,",
         "gộp theo trọng số tam giác"),
        ("4. Mô hình SED", f"Frame-MobileNet × {facts.folds} fold,", "trung bình xác suất"),
        ("5. Xác suất theo khung", "21 lớp × khung 10 ms"),
        ("6. cSEBB", "tách thành hộp sự kiện;", "ngưỡng chỉ giữ hoặc bỏ hộp"),
        ("7. LBR", "dời biên và chấm lại", "từng hộp"),
        ("8. Dòng thời gian", "lớp, bắt đầu, kết thúc,", "điểm tin cậy"),
        ("9. Mô tả Anh, Việt", "gộp theo lớp, rào đón", "khi điểm thấp"),
        ("10. Tài liệu truy hồi", "mô tả và tóm tắt", "sự kiện"),
        ("11. Nhúng BGE-M3", "vector 1024 chiều"),
        ("12. Kho sự kiện", "PostgreSQL 16", "và pgvector"),
    ]
    fills = {3: "model", 4: "store", 6: "model", 7: "store", 10: "model", 11: "store"}
    w, h, row_gap = 4.6, 1.55, 0.6
    xs = _grid(3, w)
    items: list[Box | Line] = []
    corners = []
    for index, lines in enumerate(steps):
        row, col = divmod(index, 3)
        col = col if row % 2 == 0 else 2 - col
        x, y = xs[col], row * (h + row_gap)
        items.append(Box(x, y, w, h, lines, fill=fills.get(index, "plain")))
        corners.append((x, y))
    for index in range(len(steps) - 1):
        (xa, ya), (xb, yb) = corners[index], corners[index + 1]
        if ya == yb:
            start = (xa + w, ya + h / 2) if xb > xa else (xa, ya + h / 2)
            end = (xb, yb + h / 2) if xb > xa else (xb + w, yb + h / 2)
        else:
            start, end = (xa + w / 2, ya + h), (xb + w / 2, yb)
        items.append(Line((start, end)))
    y_off = 4 * (h + row_gap)
    items.append(Box(0, y_off, WIDTH, 1.7, (
        "Ngoại tuyến (không chạy khi phục vụ)",
        "Ngưỡng, cSEBB và LBR được chọn trên dữ liệu phát triển rồi khóa cạnh checkpoint;",
        "dịch vụ suy luận chỉ nạp tham số đã khóa."), fill="offline"))
    return Diagram("dataflow", WIDTH, y_off + 1.7, tuple(items),
                   "Luồng xử lý dữ liệu của hệ thống cuối, từ tệp âm thanh tới kho sự kiện")


# ---------------------------------------------------------------- LBR
def lbr() -> Diagram:
    w, h = 4.6, 1.9
    x0, x1, x2 = _grid(3, w)
    y1, y2 = 2.6, 5.2
    items = (
        Box(x0, 0, w, h, ("Đầu vào", "hộp cSEBB của hệ cơ sở", "và xác suất ngoài mẫu"),
            fill="store"),
        Box(x1, 0, w, h, ("Đặc trưng mỗi hộp", "điểm, độ dài, vị trí, lớp;",
                          "xác suất quanh hai biên")),
        Box(x2, 0, w, h, ("Bộ tinh chỉnh", "cây tăng cường gradient,", "dự đoán độ dời biên"),
            fill="model"),
        Box(x2, y1, w, h, ("Bộ chấm lại", "cây tăng cường gradient,", "xác suất hộp đúng"),
            fill="model"),
        Box(x1, y1, w, h, ("Điểm vận hành", "LBR chính: tối đa event-F1",
                           "LBR ứng dụng: ưu tiên", "phát hiện")),
        Box(x0, y1, w, h, ("Dòng thời gian mới", "hộp đã dời biên, giữ", "nếu điểm ≥ ngưỡng"),
            fill="store"),
        Box(0, y2, WIDTH, 1.7, (
            "Học chéo lồng nhau (cross-fit, 5 fold theo bản ghi)",
            "Mô hình áp cho fold k chỉ học trên 4 fold còn lại;",
            "nhãn để chọn ngưỡng lấy từ một vòng chia bên trong."), fill="offline"),
        Line(((x0 + w, h / 2), (x1, h / 2))),
        Line(((x1 + w, h / 2), (x2, h / 2))),
        Line(((x2 + w / 2, h), (x2 + w / 2, y1))),
        _label(x2 + w / 2 + 0.1, h + 0.05, 2.0, "độ dời biên", align="left"),
        Line(((x2, y1 + h / 2), (x1 + w, y1 + h / 2))),
        Line(((x1, y1 + h / 2), (x0 + w, y1 + h / 2))),
    )
    return Diagram("lbr", WIDTH, y2 + 1.7, items,
                   "Hai bộ học của LBR và cách học chéo lồng nhau")


# ---------------------------------------------------------------- kiến trúc
def architecture() -> Diagram:
    facts = served_facts()
    w, h = 4.3, 1.8
    x0, x1, x2 = _grid(3, w)
    y1, y2, y3 = 2.8, 5.6, 7.9
    mid1, mid2 = x1 + w / 2, x2 + w / 2
    items = (
        Box(x0, 0, w, h, ("Người dùng", "trình duyệt: tải tệp,", "hỏi, nghe lại")),
        Box(x1, 0, w, h, ("Giao diện web", "React và Vite;", "dòng thời gian, thẻ lọc")),
        _label(x2, 0.4, w, "Docker Compose chạy ba dịch vụ: db, api, inference", size=8.5,
               h=1.0, italic=True),
        Box(x0, y1, w, h, ("llama.cpp (GPU máy chủ)", facts.llm, "câu hỏi → bộ lọc JSON"),
            fill="model"),
        Box(x1, y1, w, h, ("Dịch vụ API", "FastAPI, không nạp PyTorch;",
                           "điều phối, bằng chứng")),
        Box(x2, y1, w, h, ("Dịch vụ suy luận", f"SED × {facts.folds} fold và LBR;",
                           "mô tả, BGE-M3"), fill="model"),
        Box(x1, y2, w, h, ("Kho sự kiện", "PostgreSQL 16 + pgvector;",
                           "sự kiện, mô tả, tài liệu"), fill="store"),
        Box(x0, y3, x2 - x0 - 0.5, 1.7, (
            "Quy trình nghiên cứu (ngoại tuyến)",
            "chuẩn bị dữ liệu → huấn luyện → chọn trên tập phát triển",
            "→ đo tập kiểm tra một lần → khóa checkpoint và tham số"), fill="offline"),
        Line(((x0 + w, h / 2), (x1, h / 2))),
        Line(((mid1, h), (mid1, y1))),
        _label(mid1 + 0.1, h + 0.15, 1.6, "HTTP", align="left"),
        Line(((x1, y1 + h / 2), (x0 + w, y1 + h / 2))),
        _label(x0 + w, y1 + h / 2 - 0.55, x1 - x0 - w, "câu hỏi"),
        Line(((x1 + w, y1 + h / 2), (x2, y1 + h / 2))),
        _label(x1 + w, y1 + h / 2 - 0.55, x2 - x1 - w, "phân tích"),
        Line(((mid1, y1 + h), (mid1, y2))),
        _label(mid1 + 0.1, y1 + h + 0.15, 3.0, "SQL: lọc cứng + vector", align="left"),
        Line(((x2 - 0.5, y3 + 0.85), (mid2, y3 + 0.85), (mid2, y1 + h)), dashed=True),
        _label(mid2 + 0.1, y2 + 0.3, 2.0, "gắn chỉ đọc", align="left"),
    )
    return Diagram("architecture", WIDTH, y3 + 1.7, items, "Kiến trúc triển khai của hệ thống")


# ---------------------------------------------------------------- tuần tự
def _sequence(name: str, descr: str, actors: list[str], messages: list[tuple[int, int, str]],
              notes: dict[int, str]) -> Diagram:
    col = WIDTH / len(actors)
    xs = [col * (i + 0.5) for i in range(len(actors))]
    box_w, box_h, step, note_step, top = min(col - 0.3, 3.2), 0.8, 0.8, 0.5, 1.3
    height = top + step * len(messages) + note_step * len(notes) + 0.3
    items: list[Box | Line] = []
    for x, actor in zip(xs, actors, strict=True):
        items.append(Box(x - box_w / 2, 0, box_w, box_h, (actor,), title=False, size=9))
        items.append(Line(((x, box_h), (x, height)), arrow=False, dashed=True, width_pt=0.75))
    y = top - step + 0.45
    for index, (src, dst, text) in enumerate(messages, start=1):
        y += step
        label = f"{index}. {text}"
        if src == dst:
            items.append(Box(xs[src] - 0.1, y - 0.25, 0.2, 0.5, ("",), fill="model", title=False))
            width = min(6.5, WIDTH - xs[src] - 0.2)
            items.append(_label(xs[src] + 0.15, y - 0.25, width, label, align="left"))
        else:
            items.append(Line(((xs[src], y), (xs[dst], y))))
            mid, span = (xs[src] + xs[dst]) / 2, max(abs(xs[dst] - xs[src]), 6.0)
            left = min(max(mid - span / 2, 0.0), WIDTH - span)
            items.append(_label(left, y - 0.5, span, label))
        if index in notes:
            y += note_step
            items.append(_label(xs[1] + 0.15, y - 0.3, WIDTH - xs[1] - 0.2, f"({notes[index]})",
                                size=8, h=0.45, align="left", italic=True))
    return Diagram(name, WIDTH, height, tuple(items), descr)


def uploadflow() -> Diagram:
    folds = served_facts().folds
    messages = [
        (0, 1, "tải tệp âm thanh lên"),
        (1, 1, "kiểm định dạng, dung lượng, độ dài; SHA-256"),
        (1, 3, "tìm bản ghi có cùng mã băm"),
        (3, 1, "đã có: trả mã bản ghi cũ, dừng"),
        (1, 2, "gửi tệp để phân tích"),
        (2, 2, f"SED × {folds} fold → cSEBB → LBR"),
        (2, 2, "mô tả Anh, Việt; tài liệu; vector"),
        (2, 1, "dòng thời gian, mô tả, tài liệu, vector"),
        (1, 3, "ghi 5 bảng trong một giao dịch"),
        (1, 0, "mã bản ghi, dòng thời gian, mô tả"),
    ]
    notes = {5: "suy luận lỗi → mã 503, xóa tệp vừa lưu", 9: "ghi lỗi → hoàn tác, xóa tệp"}
    return _sequence("uploadflow", "Luồng tải lên và phân tích một bản ghi",
                     ["Giao diện", "Dịch vụ API", "Dịch vụ suy luận", "PostgreSQL"],
                     messages, notes)


def queryflow() -> Diagram:
    llm = served_facts().llm
    messages = [
        (0, 1, "gửi câu hỏi tự nhiên"),
        (1, 2, "sinh JSON theo lược đồ: 21 lớp, 4 điều kiện"),
        (2, 1, "bộ lọc: lớp, thời lượng, trước/sau"),
        (1, 0, "hiện bộ lọc thành thẻ để sửa"),
        (0, 1, "chạy truy vấn (bộ lọc, chế độ)"),
        (1, 3, "nhúng câu hỏi"),
        (3, 1, "vector BGE-M3"),
        (1, 4, "SQL: lọc cứng + xếp hạng cosine"),
        (1, 4, "chế độ bổ sung: thêm kết quả gần nghĩa"),
        (4, 1, "bản ghi và sự kiện bằng chứng"),
        (1, 0, "câu trả lời kèm (bản ghi, khoảng thời gian)"),
    ]
    notes = {2: f"{llm} trên llama.cpp; tắt → 503, vẫn lọc tay được",
             10: "kết quả gần nghĩa chỉ được nêu tên, không làm bằng chứng"}
    return _sequence("queryflow", "Luồng hỏi đáp: phân tích câu hỏi, truy hồi, trả lời",
                     ["Giao diện", "Dịch vụ API", "llama.cpp", "Dịch vụ suy luận", "PostgreSQL"],
                     messages, notes)


# ---------------------------------------------------------------- ERD
ERD_COLUMNS = {  # cột x (0, 1, 2) và thứ tự từ trên xuống; bảng mới mà thiếu ở đây sẽ báo lỗi
    "captions": (0, 0),
    "retrieval_documents": (0, 1),
    "caption_evidence": (1, 0),
    "recordings": (1, 1),
    "events": (2, 0),
    "event_subclass_predictions": (2, 1),
    "runs": (1, 2),
}


def erd(max_columns: int = 9) -> Diagram:
    tables = parse_schema(MIGRATION.read_text(encoding="utf-8"))
    names = {t.name for t in tables}
    if names != set(ERD_COLUMNS) or names != set(ERD_LAYOUT):
        raise KeyError(f"bảng trong migration khác bố cục ERD: {sorted(names ^ set(ERD_COLUMNS))}")
    w, row, gap = 4.9, 0.36, 0.8
    xs = _grid(3, w)
    rects: dict[str, tuple[float, float, float, float]] = {}
    tops = [0.0, 0.0, 0.0]
    items: list[Box | Line] = []
    for table in sorted(tables, key=lambda t: ERD_COLUMNS[t.name][::-1]):
        col = ERD_COLUMNS[table.name][0]
        shown = table.columns[:max_columns]
        hidden = len(table.columns) - len(shown)
        fk = {c for c, _ in table.references}
        lines = [table.name]
        for column, kind, primary in shown:
            mark = "PK " if primary else ("FK " if column in fk else "")
            lines.append(f"{mark}{column}: {kind.lower()}")
        if hidden:
            lines.append(f"… {hidden} cột khác")
        h = 0.3 + row * len(lines)
        x, y = xs[col], tops[col]
        items.append(Box(x, y, w, h, tuple(lines), fill="store", size=8, align="left"))
        rects[table.name] = (x, y, w, h)
        tops[col] = y + h + gap
    for table in tables:
        for _, target in table.references:
            items.append(Line(_fk_route(rects[table.name], rects[target])))
    height = max(tops) - gap + 0.7
    items.append(_label(0, height - 0.5, WIDTH, "Mũi tên: khóa ngoại trỏ tới bảng cha "
                        "(xóa bảng cha thì xóa theo)", size=8, italic=True, align="left"))
    return Diagram("erd", WIDTH, height, tuple(items),
                   "Sơ đồ bảng của kho sự kiện (PostgreSQL 16 và pgvector)")


def _fk_route(child: tuple[float, float, float, float],
              parent: tuple[float, float, float, float]) -> tuple[tuple[float, float], ...]:
    cx, cy, cw, ch = child
    px, py, pw, ph = parent
    low, high = max(cy, py), min(cy + ch, py + ph)
    if high - low > 0.4:  # chồng theo chiều dọc: nối ngang
        y = (low + high) / 2
        return ((cx, y), (px + pw, y)) if cx > px else ((cx + cw, y), (px, y))
    if abs(cx - px) < 0.01:  # cùng cột: nối dọc
        x = cx + cw / 2
        return ((x, cy), (x, py + ph)) if cy > py else ((x, cy + ch), (x, py))
    # khác cột, không chồng: đi ngang từ cạnh bên rồi đi dọc vào cạnh trên/dưới của bảng cha
    start_x = cx + cw if cx < px else cx
    y0 = cy + min(0.6, ch / 2)
    x1 = px + pw / 2 + (0.6 if cx > px else -0.6)
    end_y = py if cy < py else py + ph
    return ((start_x, y0), (x1, y0), (x1, end_y))


BUILDERS: dict[str, Callable[[], Diagram]] = {
    "pipeline": pipeline,
    "dataflow": dataflow,
    "lbr": lbr,
    "architecture": architecture,
    "uploadflow": uploadflow,
    "queryflow": queryflow,
    "erd": erd,
}


@cache
def build(name: str) -> Diagram:
    if name not in BUILDERS:
        raise KeyError(f"không có sơ đồ '{name}'; có: {sorted(BUILDERS)}")
    return BUILDERS[name]()
