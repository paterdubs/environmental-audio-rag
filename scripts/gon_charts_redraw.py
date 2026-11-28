"""Vẽ lại bốn hình phân tích của bản chính (r06, r09, r10, r11) theo kiểu in của bản gọn.

Số đọc từ cùng artifact như `scripts.build_research_figures`; chỉ đổi kiểu (khổ in, Times New Roman,
dấu phẩy thập phân, màu theo thực thể) và nhãn tiếng Việt. Bản chính vẫn dùng hình cũ.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts import gon_chart_style as cs

SYSTEMS = ("f2", "B0", "lbrv2", "lbrv3")
NAMES = {s: cs.ENTITY_NAMES[cs.SYSTEM_ENTITY[s]] for s in SYSTEMS}
METHODS = {"template": "Theo mẫu", "unconstrained": "Tự do", "constrained": "Ràng buộc",
           "constrained_cover": "Ràng buộc + phủ"}
RQ2_METRICS = (("omission_rate", "Bỏ sót"), ("hallucination_rate", "Ảo giác nguồn âm"),
               ("context_term_rate", "Suy diễn bối cảnh"))


# ---------- dữ liệu thuần (có test) ----------

def onset_bias(diag: dict) -> list[tuple[str, float]]:
    errors = diag["breakdown"]["onset_error_median_per_class"]
    return sorted(errors.items(), key=lambda kv: kv[1], reverse=True)


def rq1_branches(data: dict) -> dict[str, Any]:
    return {"branches": {b: data["branches"][b]["event_f1"] for b in ("B", "C")},
            "p": data["welch"]["event_f1"]["p"]}


def rq2_rates(rq2: dict) -> dict[str, dict[str, dict[str, float]]]:
    """metric → cách sinh → hệ SED → tỷ lệ (tập kiểm tra, so với danh sách dự đoán)."""
    return {metric: {method: {s: rq2["e2e"][method][s]["summary"][metric] for s in SYSTEMS}
                     for method in METHODS} for metric, _ in RQ2_METRICS}


def query_diffs(per_query: list[dict], language: str = "en") -> list[float]:
    """Hiệu nDCG@10 (kết hợp − chỉ ngữ nghĩa) theo từng câu truy vấn có bản ghi liên quan."""
    scores: dict[str, dict[str, float]] = {}
    for row in per_query:
        if row["language"] == language and row["n_relevant"] > 0:
            scores.setdefault(row["query_id"], {})[row["mode"]] = row["ndcg@10"]
    return [s["hybrid"] - s["vector_only"] for s in scores.values()
            if "hybrid" in s and "vector_only" in s]


def rq3_stores(rq3: dict, per_query: dict[str, list[dict]]) -> list[dict]:
    stores = []
    for key in SYSTEMS:
        diffs = query_diffs(per_query[key])
        est = rq3["systems"][key]["paired"]["hybrid−vector_only/en"]
        stores.append({"key": key, "diffs": diffs, "neg": sum(d < -1e-9 for d in diffs),
                       "zero": sum(abs(d) <= 1e-9 for d in diffs),
                       "pos": sum(d > 1e-9 for d in diffs), "estimate": est["estimate"],
                       "lower": est["lower"], "upper": est["upper"]})
    return stores


# ---------- hình ----------

def fig_onset_bias(rows: list[tuple[str, float]], path: Path) -> None:
    fig, ax = cs.figure(10.5)
    values = [v for _, v in rows]
    ax.axvspan(-0.2, 0.2, color=cs.GRID, alpha=0.6, zorder=0, label="trong dung sai ±0,2 s")
    ax.barh(range(len(rows)), values,
            color=["#CC3311" if v < -0.2 else cs.ACCENT for v in values], zorder=2)
    ax.axvline(0, color=cs.INK, linewidth=0.8, zorder=3)
    ax.set_yticks(range(len(rows)), [c for c, _ in rows], fontsize=8.5)
    ax.set_ylim(len(rows) - 0.4, -0.6)
    cs.comma_axis(ax, "x", 2)
    ax.set_xlabel("Trung vị độ lệch thời điểm bắt đầu (dự đoán − tham chiếu), giây;\n"
                  "giá trị âm là đoán sớm")
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    cs.style(ax, "x")
    cs.save(fig, path)


def fig_rq1_seeds(v1: dict, v2: dict, path: Path) -> None:
    fig, axes = cs.figure(6.6, ncols=2)
    colors = {"B": (cs.NEUTRAL, "s"), "C": (cs.ACCENT, "o")}
    panels = ((axes[0], v1, "SED v1 (142 bản ghi)", 3), (axes[1], v2, "SED v2 (139 bản ghi)", 3))
    for ax, data, title, decimals in panels:
        for i, branch in enumerate(("B", "C")):
            s = data["branches"][branch]
            color, marker = colors[branch]
            ax.plot([i, i], [s["min"], s["max"]], color=cs.GRID, linewidth=4,
                    solid_capstyle="butt", zorder=1)
            ax.errorbar(i, s["mean"], yerr=s["sd"], fmt=marker, color=color, capsize=4,
                        markersize=6, zorder=2)
            ax.text(i + 0.1, s["mean"], f"{s['n']} lần", va="center", fontsize=8.5)
        ax.set_xticks([0, 1], ["Nhánh B:\nAudioSet", "Nhánh C:\nAudioSet → DataSEC"])
        ax.set_xlim(-0.5, 1.6)
        ax.set_title(f"{title}; p (Welch) = {cs.vn(data['p'], 2)}")
        cs.comma_axis(ax, "y", decimals)
        cs.style(ax)
    axes[0].set_ylabel("F1 theo sự kiện micro (tập kiểm tra)")
    cs.save(fig, path)


def fig_rq2_errors(rates: dict, path: Path) -> None:
    fig, axes = cs.figure(7.4, ncols=3)
    width = 0.2
    for ax, (metric, title) in zip(axes, RQ2_METRICS, strict=True):
        top = max(max(v.values()) for v in rates[metric].values())
        for j, (method, label) in enumerate(METHODS.items()):
            xs = [i + (j - 1.5) * width for i in range(len(SYSTEMS))]
            values = [rates[metric][method][s] for s in SYSTEMS]
            color = cs.SEQUENTIAL[j]
            ax.bar(xs, values, width, color=color, label=label, edgecolor=cs.MUTED,
                   linewidth=0.3)
            zeros = [x for x, v in zip(xs, values, strict=True) if v == 0]
            ax.plot(zeros, [top * 0.015] * len(zeros), "^", color=color, mec=cs.MUTED,
                    mew=0.4, markersize=4)
        ax.set_xticks(range(len(SYSTEMS)), [NAMES[s] for s in SYSTEMS], fontsize=8.5,
                      rotation=30, ha="right", rotation_mode="anchor")
        ax.set_title(title)
        cs.comma_axis(ax, "y", 2 if top > 0.05 else 3)
        cs.style(ax)
    fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, ncol=4,
               loc="outside upper center", fontsize=8.5)
    axes[0].set_ylabel("Tỷ lệ (tập kiểm tra)")
    cs.save(fig, path)


def fig_rq3_queries(stores: list[dict], path: Path) -> None:
    fig, ax = cs.figure(7.0)
    for i, s in enumerate(stores):
        jitter = [(k % 9 - 4) * 0.035 for k in range(len(s["diffs"]))]
        ax.scatter([i + j for j in jitter], s["diffs"], s=6, color=cs.NEUTRAL, alpha=0.6,
                   zorder=2, linewidths=0)
        color, marker = cs.ENTITY[cs.SYSTEM_ENTITY[s["key"]]]
        yerr = [[s["estimate"] - s["lower"]], [s["upper"] - s["estimate"]]]
        ax.errorbar(i + 0.3, s["estimate"], yerr=yerr, fmt=marker, color=color, capsize=4,
                    markersize=6, zorder=3)
        ax.text(i, 1.1, f"−{s['neg']} / ={s['zero']} / +{s['pos']}", ha="center", fontsize=8.5)
    ax.axhline(0, color=cs.INK, linewidth=0.8)
    ax.set_xticks(range(len(stores)),
                  [cs.ENTITY_NAMES[cs.SYSTEM_ENTITY[s["key"]]] for s in stores])
    ax.set_ylim(-1.05, 1.22)
    cs.comma_axis(ax, "y", 1)
    ax.set_ylabel("nDCG@10: kết hợp − chỉ ngữ nghĩa")
    cs.style(ax)
    cs.save(fig, path)
