"""Đổi chữ hiển thị trong hình matplotlib ngay trước khi lưu, không đổi dữ liệu vẽ.

Dùng cho bản báo cáo tinh gọn: cùng script vẽ hình, nhưng mã nội bộ (B0, LBR V2, …) được thay
bằng tên có nghĩa. Danh sách thay lấy từ khóa ``figure_names`` của ``display.yaml``; mục có dạng
``["=f2", "Hệ mốc"]`` chỉ thay khi cả chuỗi bằng đúng ``f2`` (tránh đụng chuỗi dài hơn).
"""

from __future__ import annotations

from pathlib import Path

import yaml

Names = tuple[tuple[str, str], ...]


def load(path: Path | None) -> Names:
    if path is None:
        return ()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return tuple((str(a), str(b)) for a, b in raw.get("figure_names", []))


def relabel_text(text: str, names: Names) -> str:
    for old, new in names:
        if old.startswith("="):
            if text == old[1:]:
                text = new
        else:
            text = text.replace(old, new)
    return text


def relabel(fig, names: Names) -> None:  # noqa: ANN001 - matplotlib Figure
    """Thay chữ ở mọi đối tượng Text của hình (tiêu đề, nhãn trục, nhãn vạch, chú giải)."""
    if not names:
        return
    from matplotlib.text import Text

    # Nhãn vạch được bộ định dạng sinh lại mỗi lần vẽ, nên phải chốt chúng thành nhãn cố định.
    fig.canvas.draw()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            labels = [t.get_text() for t in axis.get_ticklabels()]
            renamed = [relabel_text(t, names) for t in labels]
            if renamed != labels:
                axis.set_ticks(axis.get_ticklocs(), renamed)
    for artist in fig.findobj(Text):
        old = artist.get_text()
        new = relabel_text(old, names)
        if new != old:
            artist.set_text(new)
