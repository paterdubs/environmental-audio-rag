"""Sinh hình cho báo cáo cuối (R5) từ `final_numbers_*.json`.

Số trên hình đọc thẳng từ JSON đã sinh bởi `scripts.report_final_numbers`; không tính lại metric,
không đọc `predictions/test.npz`. Khổ ≈ 6,6 inch để khi đặt rộng 15,5 cm chữ vẫn ≥ 7 pt.

    .venv/Scripts/python.exe -m scripts.build_final_figures --final-numbers <final_numbers.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ml.provenance import git_state  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "report" / "final_figures"
DPI = 300
WIDTH_IN = 6.6
INK, MUTED, GRID = "#1f2328", "#57606a", "#d0d7de"
BLUE, ORANGE = "#2a78d6", "#eb6834"
LABELS = {
    "f2": "f2",
    "B0": "B0",
    "lbrv2_f1": "LBR V2",
    "lbrv3_f1": "LBR V3 (f1)",
    "lbrv3_recall_first": "LBR V3 (recall_first)",
}

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


def _v(cell: dict[str, Any]) -> float:
    return float(cell["value"])


def figure_sed_final(data: dict[str, Any], path: Path) -> None:
    """Trái: event-F1 micro (có CI khi có). Phải: recall và precision giao nhau."""
    rows = data["sed"]["rows"]
    keys = list(LABELS)
    fig, (left, right) = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.0), gridspec_kw={"wspace": 0.7})

    micro = [_v(rows[k]["micro"]) for k in keys]
    ypos = list(range(len(keys)))
    left.barh(ypos, micro, color=BLUE, height=0.6)
    for y, k, m in zip(ypos, keys, micro, strict=True):
        ci = rows[k].get("micro_ci")
        label = f"{m:.3f}".replace(".", ",")
        if ci:
            lo, hi = _v(ci["lower"]), _v(ci["upper"])
            left.plot([lo, hi], [y, y], color=INK, linewidth=1.2)
            left.plot([lo, lo], [y - 0.12, y + 0.12], color=INK, linewidth=1.2)
            left.plot([hi, hi], [y - 0.12, y + 0.12], color=INK, linewidth=1.2)
        else:
            label += " (không có CI)"
        left.text(m + 0.012, y - 0.32, label, color=INK, fontsize=7.5)
    left.set_yticks(ypos, [LABELS[k] for k in keys])
    left.invert_yaxis()
    left.set_xlim(0, 0.5)
    left.set_xlabel("Event-F1 micro (collar 0,2 s)")
    left.set_title("Event-F1 micro (đoạn: CI 95% nếu có)", loc="left", fontsize=8.5, color=INK)

    sel = [k for k in keys if k != "f2"]
    recall = [_v(rows[k]["intersection_recall"]) for k in sel]
    prec = [_v(rows[k]["intersection_precision"]) for k in sel]
    ypos2 = list(range(len(sel)))
    h = 0.36
    right.barh([y - h / 2 for y in ypos2], recall, height=h, color=BLUE, label="Recall giao nhau")
    right.barh(
        [y + h / 2 for y in ypos2], prec, height=h, color=ORANGE, label="Precision giao nhau"
    )
    right.set_yticks(ypos2, [LABELS[k] for k in sel])
    right.invert_yaxis()
    right.set_xlim(0, 1.0)
    right.set_xlabel("Thước ứng dụng (tiêu chí giao nhau)")
    right.set_title("Độ phủ và độ chính xác", loc="left", fontsize=8.5, color=INK)
    right.legend(
        frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2
    )
    for ax in (left, right):
        ax.grid(axis="x", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-numbers", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.final_numbers.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "f01_sed_final.png"
    figure_sed_final(data, out)
    manifest = {
        "git": git_state(ROOT),
        "dpi": DPI,
        "source": args.final_numbers.resolve().relative_to(ROOT).as_posix(),
        "figures": ["f01_sed_final.png"],
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Đã ghi {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
