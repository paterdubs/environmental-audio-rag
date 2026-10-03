"""Sinh hình cho báo cáo giữa kỳ (task L3).

Các sơ đồ vẽ theo mã nguồn và cấu hình hiện hành; số trên hình đọc từ manifest, split đóng băng và
measurement đã khóa. Hình dòng thời gian chỉ dùng tập **dev**. Không chạy suy luận hay đánh giá.
Mọi hình vẽ ở khổ ≈ 6,6 inch để khi đặt rộng 15,5 cm chữ vẫn ≥ 7 pt.

    .venv/Scripts/python.exe -m scripts.build_midterm_figures
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from ml.provenance import git_state  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "docs" / "measurements"
CAPTIONS_DEV = (
    ROOT
    / "ml"
    / "runs"
    / "sed_ensemble_s13_f2_20260929T045053Z"
    / "captions"
    / "constrained_cover_dev.jsonl"
)
DEFAULT_OUTPUT = ROOT / "report" / "figures"
DPI = 300
WIDTH_IN = 6.6
INK, MUTED, GRID = "#1f2328", "#57606a", "#d0d7de"
SERIES_TEST, SERIES_DEV = "#2a78d6", "#eb6834"  # dataviz palette, slot 1 và 2
FILLS = {"store": "#eef4fc", "service": "#f6f8fa", "model": "#fdf1ec", "offline": "#eefaf4"}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
    }
)


def canvas(height: float) -> tuple[plt.Figure, plt.Axes]:
    """Trục tính bằng inch: 1 đơn vị = 1 inch, để cỡ chữ (pt) và kích thước hộp so được."""
    fig, ax = plt.subplots(figsize=(WIDTH_IN, height))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, WIDTH_IN)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def box(
    ax, x: float, y: float, w: float, h: float, title: str, body: str = "", kind: str = "service"
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.06",
            linewidth=0.9,
            edgecolor=MUTED,
            facecolor=FILLS[kind],
        )
    )
    ax.text(
        x + w / 2,
        y + h - 0.1,
        title,
        ha="center",
        va="top",
        fontsize=8.8,
        fontweight="bold",
        color=INK,
    )
    if body:
        ax.text(
            x + w / 2,
            y + h - 0.32,
            body,
            ha="center",
            va="top",
            fontsize=7.8,
            color=MUTED,
            linespacing=1.3,
        )


def arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str = "",
    dashed: bool = False,
    offset: tuple[float, float] = (0.0, 0.05),
    ha: str = "center",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=0.9,
            color=MUTED,
            linestyle="--" if dashed else "-",
            shrinkA=0,
            shrinkB=0,
        )
    )
    if label:
        ax.text(
            (start[0] + end[0]) / 2 + offset[0],
            (start[1] + end[1]) / 2 + offset[1],
            label,
            ha=ha,
            va="bottom",
            fontsize=7.3,
            color=MUTED,
        )


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)


def figure_architecture(path: Path) -> list[str]:
    fig, ax = canvas(5.3)
    w, h = 1.85, 0.95
    cols = (0.05, 2.375, 4.7)
    box(ax, cols[0], 4.25, w, h, "Người dùng", "trình duyệt: tải WAV,\nđặt câu hỏi, nghe lại")
    box(ax, cols[1], 4.25, w, h, "Giao diện web", "React + Vite\ndòng thời gian, thẻ lọc")
    box(
        ax,
        cols[0],
        2.75,
        w,
        h,
        "llama.cpp",
        "Qwen3.5-9B (GPU máy chủ)\ncâu hỏi → bộ lọc JSON",
        "model",
    )
    box(ax, cols[1], 2.75, w, h, "Dịch vụ API", "FastAPI, không nạp torch\nđiều phối, bằng chứng")
    box(
        ax,
        cols[2],
        2.75,
        w,
        h,
        "Dịch vụ suy luận",
        "SED f2 + cSEBB, mô tả\nBGE-M3 (CPU container)",
        "model",
    )
    box(
        ax,
        cols[1],
        1.3,
        w,
        h,
        "Kho sự kiện",
        "PostgreSQL 16 + pgvector\nsự kiện, mô tả, tài liệu",
        "store",
    )
    box(
        ax,
        cols[0],
        0.08,
        4.2,
        0.85,
        "Quy trình nghiên cứu (ngoại tuyến)",
        "D0–D4 → huấn luyện → chọn trên dev → test một lần\n"
        "→ artifact đóng băng (manifest, SHA-256)",
        "offline",
    )
    arrow(ax, (cols[0] + w, 4.72), (cols[1], 4.72))
    arrow(
        ax, (cols[1] + w / 2, 4.25), (cols[1] + w / 2, 3.7), "HTTP", offset=(0.06, -0.05), ha="left"
    )
    arrow(ax, (cols[1], 3.22), (cols[0] + w, 3.22), "parse", offset=(0.0, 0.06))
    arrow(
        ax, (cols[1] + w, 3.22), (cols[2], 3.22), "analyze" + chr(10) + "embed", offset=(0.0, 0.06)
    )
    arrow(
        ax,
        (cols[1] + w / 2, 2.75),
        (cols[1] + w / 2, 2.25),
        "SQL: lọc cứng + vector",
        offset=(0.06, -0.05),
        ha="left",
    )
    arrow(
        ax,
        (4.25, 0.5),
        (cols[2] + w / 2, 2.75),
        "gắn chỉ đọc",
        dashed=True,
        offset=(0.12, -0.1),
        ha="left",
    )
    ax.text(
        5.53,
        4.75,
        "Docker Compose:\ndb, api, inference",
        ha="center",
        va="center",
        fontsize=7.5,
        color=MUTED,
        style="italic",
    )
    save(fig, path)
    return [
        "services/",
        "ml/inference/engine.py",
        "docker-compose.yml",
        "ml/configs/caption_llm.yaml",
    ]


def _column(ax, x: float, title: str, steps: list[tuple[str, str]]) -> None:
    ax.text(
        x + 1.0, 5.45, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color=INK
    )
    for index, (head, detail) in enumerate(steps):
        y = 4.42 - index * 1.0
        box(ax, x, y, 2.0, 0.72, head, detail, "model" if index in (1, 2) else "service")
        if index:
            arrow(ax, (x + 1.0, y + 1.0), (x + 1.0, y + 0.72))


def figure_sed(path: Path) -> list[str]:
    fig, ax = canvas(5.65)
    _column(
        ax,
        0.1,
        "v1 (nhánh B/C)",
        [
            ("Log-mel 64 × 1000", "100 khung/s, cửa sổ 10 s"),
            ("CNN14, 6 khối", "gộp thời gian /64"),
            ("Lặp + tuyến tính", "21 sigmoid, 8 epoch"),
            ("Hậu xử lý", "θ chung + thời lượng"),
            ("Hệ a (ensemble C)", "trần event-F1 ≈ 0,63"),
        ],
    )
    _column(
        ax,
        2.3,
        "v2",
        [
            ("Log-mel 64 × 1000", "+ tăng cường dữ liệu"),
            ("CNN14, gộp /8", "80 ms mỗi khung"),
            ("BiGRU 2 × 256", "21 sigmoid, 100 khung/s"),
            ("Hậu xử lý", "θ chung hoặc cSEBB"),
            ("Ensemble 3 seed", "30 epoch, w_max = 10"),
        ],
    )
    _column(
        ax,
        4.5,
        "f2 (T2b × 3)",
        [
            ("Dạng sóng 16 kHz", "mel 128, bước 10 ms"),
            ("Frame-MobileNet", "tinh chỉnh, 40 ms/bước"),
            ("Tuyến tính 21 lớp", "không mô hình chuỗi"),
            ("Trung bình xác suất", "3 seed"),
            ("cSEBB", "τ = 0,64 s, gộp tương đối 2"),
        ],
    )
    save(fig, path)
    return [
        "ml/models/panns.py",
        "ml/models/frame_mn_finetune.py",
        "scripts/train_sed.py",
        "docs/decisions/ADR-0030-cai-thien-sed-v2.md",
        "docs/measurements/s13_selection_20261018.json",
    ]


def figure_pipeline(path: Path) -> list[str]:
    paths = {
        name: ROOT / rel
        for name, rel in {
            "sec": "data/manifests/datasec_inventory_summary.json",
            "sed": "data/manifests/datased_inventory_summary.json",
            "prep": "data/manifests/datased_preparation_audit.json",
            "dup": "data/manifests/duplicate_audit.json",
            "sed_split": "data/splits/datased_polyphonic.frozen.json",
            "sec_split": "data/splits/datasec_classification.frozen.json",
        }.items()
    }
    data = {name: json.loads(p.read_text(encoding="utf-8")) for name, p in paths.items()}
    sec, sed, prep, dup = data["sec"], data["sed"], data["prep"], data["dup"]
    s_sed, s_sec = data["sed_split"]["items"], data["sec_split"]["items"]
    poly = prep["annotations"]["polyphonic"]
    excluded = sec["files"] - sum(s_sec.values())

    def fmt(number: int) -> str:
        return f"{number:,}".replace(",", ".")

    fig, ax = canvas(3.25)
    w, h = 1.95, 1.12
    box(
        ax, 0.1, 2.0, w, h, "D0 · Tệp nén", "kích thước + MD5\nnhãn khớp hệ lớp\ntrước khi giải nén"
    )
    box(
        ax,
        2.33,
        2.0,
        w,
        h,
        "D1 · Kiểm kê",
        f"DataSEC {fmt(sec['files'])} tệp\nDataSED {fmt(sed['files'])} tệp\n"
        "log-mel 50 / 100 khung/s",
    )
    box(
        ax,
        4.56,
        2.0,
        w,
        h,
        "D2 · Chú giải",
        f"{fmt(poly['events'])} sự kiện đa âm\n{poly['classes']} lớp, phủ "
        f"{poly['recordings_with_events']}/{sed['files']}\nnhãn gốc không sửa",
    )
    box(
        ax,
        1.2,
        0.42,
        w,
        h,
        "D3 · Khử trùng lặp",
        f"T1/T2/T3: {dup['groups']} nhóm\n{dup['cross_dataset_groups']} nhóm xuyên dataset\n"
        f"{dup['review_queue_cross_dataset']} cặp duyệt tay",
    )
    box(
        ax,
        3.45,
        0.42,
        w,
        h,
        "D4 · Chia tập",
        f"DataSED {s_sed['train']}/{s_sed['validation']}/{s_sed['test']}\n"
        f"DataSEC {fmt(s_sec['train'])}/{s_sec['validation']}/{s_sec['test']}\n"
        f"loại {excluded} đoạn DataSEC",
        "offline",
    )
    arrow(ax, (2.05, 2.56), (2.33, 2.56))
    arrow(ax, (4.28, 2.56), (4.56, 2.56))
    arrow(ax, (5.2, 2.0), (2.6, 1.54))
    arrow(ax, (3.15, 0.98), (3.45, 0.98))
    ax.text(
        WIDTH_IN / 2,
        0.15,
        "Cổng sau chỉ chạy khi cổng trước đạt; tập chia đóng băng bằng SHA-256",
        ha="center",
        va="center",
        fontsize=7.5,
        color=MUTED,
        style="italic",
    )
    save(fig, path)
    return [p.relative_to(ROOT).as_posix() for p in paths.values()]


def _timeline_rows(path: Path, recording: str) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["recording_id"] == recording:
            rows[row["level"]] = row
    if set(rows) != {"oracle", "e2e"}:
        raise RuntimeError(f"Thiếu oracle/e2e cho {recording} trong {path.name}")
    return rows


def figure_timeline(path: Path) -> list[str]:
    rows = _timeline_rows(CAPTIONS_DEV, "S-0009")
    classes = sorted({e["class_id"] for r in rows.values() for e in r["timeline"]["events"]})
    duration = rows["oracle"]["timeline"]["duration_s"]
    fig, axes = plt.subplots(2, 1, figsize=(WIDTH_IN, 3.6), sharex=True)
    panels = (
        ("oracle", "Nhãn gốc (oracle)", "#8c959f"),
        ("e2e", "Dự đoán hệ f2 (đầu–cuối)", SERIES_TEST),
    )
    for ax, (level, title, color) in zip(axes, panels, strict=True):
        for event in rows[level]["timeline"]["events"]:
            ax.broken_barh(
                [(event["onset_s"], event["offset_s"] - event["onset_s"])],
                (classes.index(event["class_id"]) - 0.32, 0.64),
                color=color,
            )
        ax.set_yticks(range(len(classes)), [f"`{c}`".strip("`") for c in classes], fontsize=7.5)
        ax.set_ylim(-0.7, len(classes) - 0.3)
        ax.invert_yaxis()
        ax.set_title(title, loc="left", fontsize=8.8, fontweight="bold", color=INK)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[-1].set_xlim(0, duration)
    axes[-1].set_xlabel("Thời gian (s)")
    fig.tight_layout()
    save(fig, path)
    return [CAPTIONS_DEV.relative_to(ROOT).as_posix()]


def figure_s13(path: Path) -> list[str]:
    selection_path = MEASUREMENTS / "s13_selection_20261018.json"
    test_path = MEASUREMENTS / "s13_test_20261018.json"
    ranking = json.loads(selection_path.read_text(encoding="utf-8"))["ranking"]
    results = {
        row["label"]: row for row in json.loads(test_path.read_text(encoding="utf-8"))["results"]
    }
    rows = sorted(ranking, key=lambda r: r["rank"])
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 4.5))
    for index, row in enumerate(rows):
        y = len(rows) - 1 - index
        score = row["annotated"]["score"]
        test = results[row["label"]]
        ax.errorbar(
            score["mean"],
            y + 0.16,
            xerr=score["sd"],
            fmt="s",
            ms=5,
            color=SERIES_DEV,
            elinewidth=1.2,
            capsize=2.5,
            label="CV dev annotated (trung bình ± sd fold)" if index == 0 else None,
        )
        ax.errorbar(
            test["micro"],
            y - 0.16,
            xerr=[
                [test["micro"] - test["micro_ci_lower"]],
                [test["micro_ci_upper"] - test["micro"]],
            ],
            fmt="o",
            ms=5,
            color=SERIES_TEST,
            elinewidth=1.2,
            capsize=2.5,
            label="Test annotated (95% CI)" if index == 0 else None,
        )
    labels = [
        f"{r['rank']}. {r['label']}" + (" (khóa)" if r["label"] == "f2" else "") for r in rows
    ]
    ax.set_yticks(range(len(rows) - 1, -1, -1), labels)
    ax.set_xlabel("Event-F1 micro (collar 0,2 s)")
    ax.set_xlim(0.0, 0.32)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, frameon=False, fontsize=8)
    save(fig, path)
    return [selection_path.relative_to(ROOT).as_posix(), test_path.relative_to(ROOT).as_posix()]


FIGURES = {
    "m01_architecture.png": figure_architecture,
    "m02_sed_architectures.png": figure_sed,
    "m03_s13_dev_vs_test.png": figure_s13,
    "m04_data_pipeline.png": figure_pipeline,
    "m05_dev_timeline.png": figure_timeline,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"git": git_state(ROOT), "dpi": DPI, "figures": {}}
    for name, builder in FIGURES.items():
        manifest["figures"][name] = builder(args.output / name)
        print(f"Đã ghi {(args.output / name).relative_to(ROOT)}")
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
