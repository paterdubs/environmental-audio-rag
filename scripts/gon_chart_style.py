"""Kiểu in cho biểu đồ của bản khóa luận tinh gọn.

Hình vẽ đúng khổ in (rộng 15,5 cm) nên cỡ chữ trong mã bằng cỡ chữ trên giấy: số trên trục 9 pt,
nhãn và chú giải 10 pt. Màu gán theo **thực thể** (mỗi hệ SED một màu dùng chung cho mọi hình), chọn
từ bảng của Paul Tol để phân biệt được với người mù màu đỏ–lục và khi in xám, kèm mã hóa kép bằng
hình điểm. Kiểu chỉ áp khi gọi `apply()`, nên các script vẽ hình của bản chính không bị ảnh hưởng.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

CM = 1 / 2.54
WIDTH_CM = 15.5
DPI = 300
INK, MUTED, GRID = "#1f2328", "#555555", "#D9D9D9"

# Thực thể → (màu, hình điểm). Thứ tự L* giảm dần để in xám vẫn tách được.
ENTITY = {
    "lbr_main": ("#004488", "o"),
    "lbr_app": ("#CC3311", "^"),
    "base": ("#888888", "s"),
    "anchor": ("#BBBBBB", "o"),
}
ENTITY_NAMES = {"anchor": "Hệ mốc", "base": "Hệ cơ sở", "lbr_main": "LBR chính",
                "lbr_app": "LBR ứng dụng"}
SYSTEM_ENTITY = {"f2": "anchor", "B0": "base", "lbrv2": "lbr_main", "lbrv3": "lbr_app"}
# Thang có thứ tự (ví dụ mức ràng buộc của cách sinh mô tả): một sắc độ xanh đậm dần.
SEQUENTIAL = ("#C6DBEF", "#6BAED6", "#2171B5", "#08306B")
ACCENT = "#004488"
NEUTRAL = "#888888"

RC = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 10,
    "axes.titlesize": 10.5,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.linewidth": 0.6,
    "axes.unicode_minus": True,
    "savefig.facecolor": "white",
}


def apply() -> None:
    plt.rcParams.update(RC)


def vn(value: float, decimals: int = 3, sign: bool = False) -> str:
    """Số kiểu Việt: dấu phẩy thập phân, dấu trừ thật (U+2212), tùy chọn dấu cộng."""
    text = f"{abs(value):.{decimals}f}".replace(".", ",")
    if value < 0 and float(text.replace(",", ".")) != 0:
        return "−" + text
    return ("+" + text) if sign else text


def comma_axis(ax: plt.Axes, axis: str = "y", decimals: int = 2) -> None:
    formatter = FuncFormatter(lambda v, _pos: vn(v, decimals))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)


def figure(height_cm: float, ncols: int = 1, nrows: int = 1, **kwargs):
    return plt.subplots(nrows, ncols, figsize=(WIDTH_CM * CM, height_cm * CM),
                        layout="constrained", **kwargs)


def style(ax: plt.Axes, axis: str = "y") -> None:
    ax.grid(axis=axis, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def entity_marker(ax: plt.Axes, x, y, entity: str, size: float = 6, **kwargs) -> None:
    color, marker = ENTITY[entity]
    face = "white" if entity == "anchor" else color
    edge = "#555555" if entity == "anchor" else color
    ax.plot(x, y, marker, color=color, mfc=face, mec=edge, markersize=size, linestyle="none",
            **kwargs)


def save(fig: plt.Figure, path: Path) -> None:
    # Không dùng bbox_inches="tight": giữ đúng khổ 15,5 cm để chữ trên giấy bằng chữ trong mã.
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
