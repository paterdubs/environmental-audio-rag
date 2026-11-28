"""Hình tổng quan công nghệ theo tầng, có biểu tượng, cho bản khóa luận tinh gọn.

Tầng và tên công nghệ đọc từ chính bảng `report/final_tables/f15_tech_stack.md`, nên hình và bảng
không thể lệch nhau. Biểu tượng lấy từ `report/assets/tech_icons/` (Simple Icons, CC0; chép bằng
`scripts.vendor_tech_icons`) và vẽ bằng svgpath2mpl, giữ nguyên hình và màu thương hiệu. Theo chính
sách nhãn hiệu đã tra, Python, PostgreSQL và sản phẩm Microsoft (Playwright) chỉ ghi bằng chữ; biểu
tượng có màu sáng được đặt trên ô nền tối thay vì đổi màu.

    .venv/Scripts/python.exe -m scripts.build_tech_overview
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.transforms import Affine2D

from scripts import gon_chart_style as cs

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "report" / "final_tables" / "f15_tech_stack.md"
ICONS = ROOT / "report" / "assets" / "tech_icons"
DEFAULT_OUTPUT = ROOT / "report" / "gon_figures" / "t01_tech_stack.png"

# Tên trong bảng → slug biểu tượng. Tên không có ở đây được vẽ bằng chữ (có chủ đích).
LOGOS = {"Docker Compose": "docker", "PyTorch": "pytorch", "scikit-learn": "scikitlearn",
         "llama.cpp + Qwen3.5-9B": "qwen", "sentence-transformers (BGE-M3)": "huggingface",
         "pytest": "pytest", "ruff": "ruff", "FastAPI": "fastapi", "React": "react",
         "TypeScript": "typescript", "Vite": "vite", "TanStack Query": "reactquery",
         "Vitest": "vitest"}
# Tên hiển thị trong ô (bỏ phần chú thích trong ngoặc của bảng) và ô rộng hơn cho tên dài (cm).
DISPLAY = {"Node.js (build giao diện)": "Node.js (build)"}
WIDE = {"Docker Compose": 2.6, "llama.cpp + Qwen3.5-9B": 3.4,
        "sentence-transformers (BGE-M3)": 4.0, "PostgreSQL 16 + pgvector": 3.6,
        "Node.js (build giao diện)": 2.3}
LAYER_NAMES = {"Mô hình ngôn ngữ": "Mô hình\nngôn ngữ"}
DARK_TILE = "#20232A"

LABEL_W, TILE_W, TILE_H, GAP, BAND_PAD = 2.3, 1.95, 1.12, 0.2, 0.1


@dataclass(frozen=True)
class Layer:
    name: str
    techs: tuple[str, ...]


def read_layers(table: Path = TABLE) -> list[Layer]:
    """Tầng theo thứ tự xuất hiện trong bảng; mỗi ô công nghệ tách theo ';' và ','."""
    layers: dict[str, list[str]] = {}
    for line in table.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("Tầng", "") or set(cells[0]) <= {"-"}:
            continue
        names = [n.strip() for n in re.split(r"[;,]", cells[1]) if n.strip()]
        layers.setdefault(cells[0], []).extend(names)
    if not layers:
        raise ValueError(f"không đọc được tầng nào từ {table}")
    return [Layer(name, tuple(techs)) for name, techs in layers.items()]


def load_icons(folder: Path = ICONS) -> dict[str, dict]:
    from scripts.vendor_tech_icons import path_data

    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    return {slug: {**info, "d": path_data((folder / f"{slug}.svg").read_text(encoding="utf-8"))}
            for slug, info in manifest["icons"].items()}


def _luminance(hex_color: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def needs_dark_tile(hex_color: str) -> bool:
    """Màu thương hiệu có tương phản dưới 3:1 trên nền trắng thì đặt trên ô tối."""
    return 1.05 / (_luminance(hex_color) + 0.05) < 3.0


_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_SEPARATOR = re.compile(r"[\s,]*")


def normalise_path(d: str) -> str:
    """Viết lại đường SVG với dấu cách giữa mọi tham số.

    Simple Icons nén cờ của lệnh cung liền nhau ("a.186.186 0 00.186-.185" là cờ 0, 0 rồi .186);
    svgpath2mpl 1.0.0 không tách được. Cờ cung là đúng một ký tự 0/1 ở vị trí thứ 4 và 5.
    """
    out: list[str] = []
    pos, command, index = 0, "", 0
    while pos < len(d):
        pos = _SEPARATOR.match(d, pos).end()
        if pos >= len(d):
            break
        if d[pos].isalpha():
            command, index = d[pos], 0
            out.append(command)
            pos += 1
            continue
        if command in "aA" and index % 7 in (3, 4):
            if d[pos] not in "01":
                raise ValueError(f"cờ cung không hợp lệ ở vị trí {pos}: {d[pos:pos + 10]!r}")
            out.append(d[pos])
            pos += 1
        else:
            match = _NUMBER.match(d, pos)
            if not match:
                raise ValueError(f"không đọc được số ở vị trí {pos}: {d[pos:pos + 10]!r}")
            out.append(match.group())
            pos = match.end()
        index += 1
    return " ".join(out)


def _logo(ax, d: str, color: str, x: float, y: float, size: float) -> None:
    from svgpath2mpl import parse_path

    path = parse_path(normalise_path(d))
    # Khung SVG 24 × 24, trục y hướng xuống → lật lại và đặt vào ô (x, y) cạnh `size` cm.
    transform = Affine2D().scale(size / 24, -size / 24).translate(x, y + size) + ax.transData
    ax.add_patch(PathPatch(path, facecolor=f"#{color}", edgecolor="none", transform=transform))


def tile_width(name: str) -> float:
    return WIDE.get(name, TILE_W)


def _tile(ax, name: str, x: float, y: float, icons: dict[str, dict]) -> None:
    slug = LOGOS.get(name)
    icon = icons.get(slug) if slug else None
    dark = bool(icon) and needs_dark_tile(icon["hex"])
    width = tile_width(name)
    ax.add_patch(FancyBboxPatch((x, y), width, TILE_H, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor=DARK_TILE if dark else "white", edgecolor="#9A9A9A",
                                linewidth=0.6))
    label = DISPLAY.get(name, name)
    text_color = "white" if dark else cs.INK
    if icon is None:
        ax.text(x + width / 2, y + TILE_H / 2, label, ha="center", va="center", fontsize=8.5,
                color=text_color)
        return
    size = 0.5
    _logo(ax, icon["d"], icon["hex"], x + (width - size) / 2, y + TILE_H - size - 0.1, size)
    ax.text(x + width / 2, y + 0.24, label, ha="center", va="center", fontsize=7.5,
            color=text_color)


def draw(layers: list[Layer], icons: dict[str, dict], path: Path) -> None:
    band_h = TILE_H + 2 * BAND_PAD
    height = len(layers) * (band_h + 0.12) + 0.1
    fig, ax = cs.plt.subplots(figsize=(cs.WIDTH_CM * cs.CM, height * cs.CM))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, cs.WIDTH_CM)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    for i, layer in enumerate(layers):  # tầng đầu bảng (hạ tầng) nằm dưới cùng
        y = 0.05 + i * (band_h + 0.12)
        ax.add_patch(FancyBboxPatch((0.05, y), cs.WIDTH_CM - 0.1, band_h,
                                    boxstyle="round,pad=0,rounding_size=0.15",
                                    facecolor="#F0F0F0", edgecolor="#BDBDBD", linewidth=0.5))
        ax.text(0.2, y + band_h / 2, LAYER_NAMES.get(layer.name, layer.name), ha="left",
                va="center", fontsize=9.5, fontweight="bold", color=cs.INK)
        x = LABEL_W
        for name in layer.techs:
            _tile(ax, name, x, y + BAND_PAD, icons)
            x += tile_width(name) + GAP
        if x - GAP > cs.WIDTH_CM - 0.1:
            raise ValueError(f"tầng {layer.name} quá nhiều ô: cần {x - GAP:.1f} cm")
    cs.save(fig, path)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cs.apply()
    layers = read_layers()
    draw(layers, load_icons(), args.output)
    print(f"Đã vẽ {sum(len(la.techs) for la in layers)} công nghệ, {len(layers)} tầng: "
          f"{args.output}")


if __name__ == "__main__":
    main()
