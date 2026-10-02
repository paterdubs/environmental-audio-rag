"""Sinh hình 300 dpi cho báo cáo từ artifact đã khóa.

Chỉ đọc JSON đánh giá có sẵn và caption dev; không mở prediction test hay chạy lại metric.

    .venv/Scripts/python.exe -m scripts.build_thesis_figures
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yaml
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "docs" / "measurements"
SCREENSHOTS = ROOT / "docs" / "demo_screenshots"
DEFAULT_OUTPUT = ROOT / "docs" / "thesis" / "figures"
F2_RUN = ROOT / "ml" / "runs" / "sed_ensemble_s13_f2_20260929T045053Z"

COLORS = {
    "blue": "#2563EB",
    "cyan": "#0891B2",
    "green": "#16A34A",
    "orange": "#EA580C",
    "purple": "#7C3AED",
    "slate": "#334155",
    "light": "#F8FAFC",
}


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu artifact nguồn: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig: plt.Figure, path: Path, revision: str, sources: list[Path]) -> None:
    metadata = {
        "Title": path.stem,
        "Author": "scripts.build_thesis_figures",
        "GitRevision": revision,
        "Source": "; ".join(source.relative_to(ROOT).as_posix() for source in sources),
    }
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, color: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.5,
        edgecolor=color,
        facecolor="white",
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, color=COLORS["slate"]
    )


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.4, color="#64748B"
        )
    )


def architecture(output: Path, revision: str) -> list[Path]:
    source = ROOT / "docs" / "SYSTEM.md"
    fig, ax = plt.subplots(figsize=(13, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Kiến trúc hệ thống đầu-cuối", fontsize=16, fontweight="bold", pad=18)
    nodes = [
        (0.03, 0.60, 0.13, 0.16, "Audio\nWAV", COLORS["blue"]),
        (0.21, 0.60, 0.16, 0.16, "Inference service\nSED f2 + cSEBB", COLORS["cyan"]),
        (0.42, 0.60, 0.14, 0.16, "Event timeline\n(onset, offset, score)", COLORS["green"]),
        (0.61, 0.72, 0.15, 0.16, "Grounded caption\nEN / VI + evidence", COLORS["orange"]),
        (0.61, 0.44, 0.15, 0.16, "Event store\nPostgreSQL + vector", COLORS["purple"]),
        (0.81, 0.44, 0.16, 0.16, "Parser + hybrid RAG\nanswer + citation", COLORS["blue"]),
        (0.81, 0.72, 0.16, 0.16, "Frontend\ntimeline + playback", COLORS["cyan"]),
    ]
    for node in nodes:
        box(ax, *node)
    arrow(ax, (0.16, 0.68), (0.21, 0.68))
    arrow(ax, (0.37, 0.68), (0.42, 0.68))
    arrow(ax, (0.56, 0.68), (0.61, 0.80))
    arrow(ax, (0.56, 0.65), (0.61, 0.52))
    arrow(ax, (0.76, 0.52), (0.81, 0.52))
    arrow(ax, (0.89, 0.60), (0.89, 0.72))
    arrow(ax, (0.76, 0.80), (0.81, 0.80))
    ax.text(
        0.5,
        0.19,
        "services/api chỉ điều phối contract; checkpoint được nạp trong services/inference",
        ha="center",
        fontsize=10,
        color="#475569",
    )
    save(fig, output / "01_system_architecture.png", revision, [source])
    return [source]


def data_pipeline(output: Path, revision: str) -> list[Path]:
    sources = [
        ROOT / "docs" / "DATA_PLAN.md",
        ROOT / "data" / "manifests" / "duplicate_audit.json",
        ROOT / "data" / "splits" / "datased_polyphonic.frozen.json",
    ]
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Pipeline dữ liệu D0–D4", fontsize=16, fontweight="bold", pad=18)
    labels = [
        ("D0", "Tải archive\nDOI + checksum"),
        ("D1", "Inventory\nfile + duration"),
        ("D2", "Chuẩn hóa\nannotation contract"),
        ("D3", "Deduplicate\nnội bộ + xuyên dataset"),
        ("D4", "Split theo\nleakage_group"),
    ]
    colors = [COLORS["blue"], COLORS["cyan"], COLORS["green"], COLORS["orange"], COLORS["purple"]]
    for index, ((stage, label), color) in enumerate(zip(labels, colors, strict=True)):
        x = 0.03 + index * 0.195
        box(ax, x, 0.42, 0.16, 0.27, f"{stage}\n{label}", color)
        if index < len(labels) - 1:
            arrow(ax, (x + 0.16, 0.555), (x + 0.195, 0.555))
    ax.text(
        0.515,
        0.18,
        "Đầu ra: manifest có provenance + split đóng băng; test không dùng để chọn mô hình",
        ha="center",
        fontsize=10.5,
        color="#475569",
    )
    save(fig, output / "02_data_pipeline_d0_d4.png", revision, sources)
    return sources


def sed_architectures(output: Path, revision: str) -> list[Path]:
    sources = [
        ROOT / "docs" / "SYSTEM.md",
        ROOT / "docs" / "decisions" / "ADR-0032-track2-encoder-pretrain-theo-frame.md",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Kiến trúc SED v2 và hệ T2b/f2", fontsize=16, fontweight="bold")
    for ax, title in zip(axes, ("SED v2", "T2b và hệ f2"), strict=True):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title, fontsize=13, fontweight="bold")
    v2 = [
        (0.05, 0.68, 0.22, 0.16, "Log-mel\n64 bins", COLORS["blue"]),
        (0.38, 0.68, 0.24, 0.16, "CNN14 /8\nAudioSet init", COLORS["cyan"]),
        (0.72, 0.68, 0.23, 0.16, "BiGRU 2×256\n21 sigmoid", COLORS["green"]),
        (0.38, 0.30, 0.24, 0.16, "Global θ +\nduration prior", COLORS["orange"]),
    ]
    for node in v2:
        box(axes[0], *node)
    arrow(axes[0], (0.27, 0.76), (0.38, 0.76))
    arrow(axes[0], (0.62, 0.76), (0.72, 0.76))
    arrow(axes[0], (0.835, 0.68), (0.58, 0.46))
    t2b = [
        (0.05, 0.68, 0.22, 0.16, "Waveform\n16 kHz", COLORS["blue"]),
        (0.36, 0.68, 0.28, 0.16, "Frame-MobileNet×3\nAudioSet Strong", COLORS["cyan"]),
        (0.73, 0.68, 0.22, 0.16, "Mean posterior\n21 lớp", COLORS["green"]),
        (0.36, 0.30, 0.28, 0.16, "cSEBB khóa từ\nCV dev annotated", COLORS["purple"]),
    ]
    for node in t2b:
        box(axes[1], *node)
    arrow(axes[1], (0.27, 0.76), (0.36, 0.76))
    arrow(axes[1], (0.64, 0.76), (0.73, 0.76))
    arrow(axes[1], (0.84, 0.68), (0.59, 0.46))
    axes[1].text(
        0.5,
        0.15,
        "f2 = T2b×3 + cSEBB",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=COLORS["purple"],
    )
    save(fig, output / "03_sed_v2_t2b_architecture.png", revision, sources)
    return sources


def event_f1_progress(output: Path, revision: str) -> list[Path]:
    source = MEASUREMENTS / "s13_test_20261018.json"
    data = load(source)
    by_label = {row["label"]: row for row in data["results"]}
    labels = ["v1\nensemble C", "v2\n3 seed", "f2\nT2b×3+cSEBB"]
    values = [by_label[label]["micro"] for label in ("a", "c", "f2")]
    lower = [by_label[label]["micro_ci_lower"] for label in ("a", "c", "f2")]
    upper = [by_label[label]["micro_ci_upper"] for label in ("a", "c", "f2")]
    errors = [
        [value - low for value, low in zip(values, lower, strict=True)],
        [high - value for value, high in zip(values, upper, strict=True)],
    ]
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    x = range(len(labels))
    ax.errorbar(
        x,
        values,
        yerr=errors,
        fmt="o-",
        capsize=6,
        linewidth=2.2,
        markersize=8,
        color=COLORS["blue"],
    )
    for index, value in enumerate(values):
        ax.text(index, value + 0.012, f"{value:.4f}", ha="center", fontsize=10)
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("Event-F1 micro")
    ax.set_title("Tiến triển SED trên test annotated (95% CI)", fontweight="bold")
    ax.set_ylim(0, max(upper) + 0.055)
    ax.grid(axis="y", alpha=0.25)
    save(fig, output / "04_event_f1_progress.png", revision, [source])
    return [source]


def per_class_f1(output: Path, revision: str) -> list[Path]:
    source = F2_RUN / "evaluation_cv_annotated.json"
    lexicon_path = ROOT / "ml" / "configs" / "caption_lexicon_vi.yaml"
    data = load(source)
    lexicon = yaml.safe_load(lexicon_path.read_text(encoding="utf-8"))["class"]
    pairs = []
    for class_id, metrics in data["event_based_f1_per_class"].items():
        label = lexicon.get(class_id, [class_id.replace("_", " ")])[0]
        label = label.removeprefix("tiếng ").removeprefix("âm thanh ")
        pairs.append((label, metrics["f_measure"]))
    pairs.sort(key=lambda item: item[1])
    labels = [textwrap.fill(label, 27) for label, _ in pairs]
    values = [value for _, value in pairs]
    fig, ax = plt.subplots(figsize=(10, 8.4))
    colors = [COLORS["orange"] if value == 0 else COLORS["blue"] for value in values]
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Event-F1 theo lớp")
    ax.set_title("Hệ f2 trên test annotated", fontweight="bold")
    ax.set_xlim(0, max(values + [0.1]) * 1.16)
    ax.grid(axis="x", alpha=0.2)
    for index, value in enumerate(values):
        ax.text(value + 0.008, index, f"{value:.3f}", va="center", fontsize=8.5)
    save(fig, output / "05_f2_per_class_event_f1.png", revision, [source, lexicon_path])
    return [source, lexicon_path]


def timeline_caption(output: Path, revision: str) -> list[Path]:
    source = F2_RUN / "captions" / "constrained_cover_dev.jsonl"
    selected = None
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["recording_id"] == "S-0009" and row["level"] == "e2e":
                selected = row
                break
    if selected is None:
        raise RuntimeError("Không tìm thấy caption dev e2e cho S-0009")
    events = selected["timeline"]["events"]
    classes = list(dict.fromkeys(event["class_id"] for event in events))
    positions = {class_id: index for index, class_id in enumerate(classes)}
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    palette = [COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["purple"]]
    for event in events:
        y = positions[event["class_id"]]
        ax.barh(
            y,
            event["offset_s"] - event["onset_s"],
            left=event["onset_s"],
            height=0.48,
            color=palette[y % len(palette)],
            alpha=0.85,
        )
        ax.text(
            (event["onset_s"] + event["offset_s"]) / 2,
            y,
            f"{event['score']:.2f}",
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            fontweight="bold",
        )
    ax.set_yticks(range(len(classes)), [class_id.replace("_", " ") for class_id in classes])
    ax.set_xlabel("Thời gian (giây)")
    ax.set_title("Ví dụ timeline và caption dev — S-0009", fontweight="bold")
    ax.grid(axis="x", alpha=0.2)
    caption = textwrap.fill(selected["caption"]["text"], 115)
    fig.text(0.12, 0.02, f"Caption: {caption}", ha="left", va="bottom", fontsize=9.5)
    fig.subplots_adjust(bottom=0.24)
    save(fig, output / "06_dev_timeline_caption.png", revision, [source])
    return [source]


def demo_interface(output: Path, revision: str) -> list[Path]:
    sources = [
        SCREENSHOTS / name
        for name in ("01-start.png", "02-timeline.png", "03-filter-chip.png", "04-rag-evidence.png")
    ]
    titles = ["Khởi động", "Timeline + caption", "Chip bộ lọc", "Câu trả lời + evidence"]
    fig, axes = plt.subplots(2, 2, figsize=(14.4, 9))
    for ax, source, title in zip(axes.flat, sources, titles, strict=True):
        if not source.is_file():
            raise FileNotFoundError(f"Thiếu ảnh demo: {source.relative_to(ROOT)}")
        ax.imshow(plt.imread(source))
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.axis("off")
    fig.suptitle("Giao diện demo local", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save(fig, output / "07_demo_interface.png", revision, sources)
    return sources


BUILDERS = [
    architecture,
    data_pipeline,
    sed_architectures,
    event_f1_progress,
    per_class_f1,
    timeline_caption,
    demo_interface,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    state = git_state(ROOT)
    if state["dirty"]:
        raise SystemExit("Tree đang bẩn; không sinh hình chính thức.")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"git": state, "dpi": 300, "font": "DejaVu Sans", "figures": {}}
    for builder in BUILDERS:
        sources = builder(args.output_dir, state["revision"])
        filename = sorted(args.output_dir.glob(f"{BUILDERS.index(builder) + 1:02d}_*.png"))[-1]
        manifest["figures"][filename.name] = [
            source.relative_to(ROOT).as_posix() for source in sources
        ]
        print(f"Đã sinh {filename.relative_to(ROOT)}")
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Đã sinh {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
