"""Biểu đồ phân tích bổ sung cho bản khóa luận tinh gọn (report/gon_src).

Mọi số đọc lại từ artifact đã đóng băng (measurement JSON và tệp đánh giá đã lưu); không tính lại
metric, không đọc `predictions/test.npz`. Hình vẽ theo kiểu in của `scripts.gon_chart_style` (đúng
khổ 15,5 cm, Times New Roman, dấu phẩy thập phân, màu theo thực thể) và chỉ ghi vào thư mục của bản
gọn; bản chính dùng `build_research_figures`/`build_final_figures` nên không đổi.

    .venv/Scripts/python.exe -m scripts.build_gon_charts
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.patches
import numpy as np

from ml.provenance import git_state
from scripts import gon_chart_style as cs
from scripts import gon_charts_redraw as redraw

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
DEFAULT_OUTPUT = ROOT / "report" / "gon_figures"
SOURCES = {
    "final": M / "final_numbers_20261110.json",
    "v2_vs_v1": M / "rq1_multirun_bootstrap_sedv2_vs_v1_20260926.json",
    "lbr_context": M / "lbr_context_20261123.json",
    "oof_o1": M / "oof_selection_20261009.json",
    "oof_o2": M / "oof_selection_20261014.json",
    "oof_p1": M / "oof_selection_20261108.json",
    "oof_p4": M / "oof_selection_20261108_P4.json",
    "lbr_selection": ROOT / "ml/runs/sed_lbr_B0_20261109T172809Z/lbr_selection_annotated.json",
    "lbr_application": ROOT / "ml/runs/sed_lbr_B0v3_20261110T042337Z/"
                              "lbr_application_annotated.json",
    "calibration": M / "calibration_20261123.json",
    "ceiling_v1": M / "sed_ceilings_20260926.json",
    "ceiling_v2": M / "sed_ceilings_v2_20260926.json",
    "ablation": M / "sed_v2_ablation_20260926.json",
    "psds_grid": M / "lbr_psds_grid_20261110_annotated.json",
    "caption_gt": M / "caption_vs_gt_dev_20261124.json",
    "checker": M / "checker_sensitivity_dev_20261124.json",
    "failures": M / "retrieval_failures_test_20261124.json",
    "backfill": M / "retrieval_backfill_test_20261124.json",
    "lbr_diag": M / "lbr_diagnosis_20261109.json",
    "rq1_v1": M / "rq1_multiseed_clean_20260924.json",
    "rq1_v2": M / "rq1_v2_multiseed_20260929.json",
    "rq2": M / "rq2_llm_systems_20261110_test_annotated.json",
    "rq3": M / "rq3_modes_20261123.json",
}
SYSTEMS = ("f2", "B0", "lbrv2", "lbrv3")
METHODS = {"template": "theo mẫu", "unconstrained": "tự do", "constrained": "ràng buộc",
           "constrained_cover": "ràng buộc + phủ"}
OOF_CANDIDATES = (
    ("oof_o1", "TF", "Frame-MobileNet + transformer"),
    ("oof_o1", "TFKD", "Frame-MobileNet + transformer, chưng cất"),
    ("oof_o1", "ENS_B0_TFKD", "Tổ hợp hệ cơ sở + transformer"),
    ("oof_o2", "OD", "BEATs huấn luyện tiếp"),
    ("oof_o2", "ENS_B0_OD", "Tổ hợp hệ cơ sở + BEATs"),
    ("oof_p1", "P1", "Tổ hợp 3 lần huấn luyện hệ cơ sở"),
    ("oof_p4", "P4", "Tăng cường âm lượng và dải tần"),
)
CHECKER_KINDS = {
    "swap_canonical": "Thay bằng tên chuẩn của lớp vắng mặt",
    "swap_synonym": "Thay bằng từ đồng nghĩa của lớp vắng mặt",
    "insert_class": "Chèn câu về một lớp vắng mặt",
    "insert_oov": "Chèn câu về nguồn âm ngoài hệ lớp",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _value(cell: Any) -> float:
    return float(cell["value"]) if isinstance(cell, dict) and "value" in cell else float(cell)


def _ci(cell: dict) -> dict[str, float]:
    return {k: _value(cell[k]) for k in ("estimate", "lower", "upper")}


# ---------- dữ liệu thuần (có test) ----------

def main_differences(final: dict, v2_vs_v1: dict, lbr_context: dict) -> list[dict]:
    """Các hiệu F1 theo sự kiện micro chính, mỗi dòng kèm tập đo và cỡ mẫu."""
    rq1, sed = final["rq1"], final["sed"]
    flipped = v2_vs_v1["differences"]["v1-v2"]
    rows = [
        ("Câu hỏi 1, SED v1: nhánh C − nhánh B", "kiểm tra", 142,
         _ci(rq1["v1"]["bootstrap_c_minus_b"])),
        ("Câu hỏi 1, SED v2: nhánh C − nhánh B", "kiểm tra", 139,
         _ci(rq1["v2"]["bootstrap_c_minus_b"])),
        ("SED v2 − SED v1", "kiểm tra", v2_vs_v1["n_recordings"],
         {"estimate": -flipped["estimate"], "lower": -flipped["upper"],
          "upper": -flipped["lower"]}),
        ("Hệ cơ sở − hệ mốc", "kiểm tra", 139, _ci(sed["b0_minus_f2"])),
        ("LBR chính − hệ cơ sở", "ngoài mẫu", 564, _ci(lbr_context["deltas"]["LBR_v2"])),
        ("LBR chính − hệ cơ sở", "kiểm tra", 139,
         _ci(sed["rows"]["lbrv2_f1"]["delta_micro_vs_b0"])),
    ]
    return [{"label": label, "set": kind, "n": n, **ci} for label, kind, n, ci in rows]


def oof_deltas(data: dict[str, dict]) -> list[dict]:
    """Hiệu micro ngoài mẫu so với hệ cơ sở (564 bản ghi) của mọi ứng viên đã qua tầng C."""
    rows = [{"label": label, "group": "other", **_ci(data[key]["differences"][code])}
            for key, code, label in OOF_CANDIDATES]
    sel, app = data["lbr_selection"]["deltas"], data["lbr_application"]["deltas"]
    rows += [
        {"label": "LBR bản 1 (chỉ tinh chỉnh biên)", "group": "lbr", **_ci(sel["LBR_v1"])},
        {"label": "LBR ứng dụng", "group": "lbr", **_ci(app["LBR_v3"])},
        {"label": "LBR chính", "group": "lbr", **_ci(sel["LBR_v2"])},
    ]
    return rows


def calibration_bars(calibration: dict) -> dict[str, Any]:
    """F1 theo ba cách đo cho ba hệ, cạnh mức đồng thuận giữa hai lần gán nhãn."""
    rows = calibration["rows"]
    systems = (("base", rows["B0"]), ("lbr_main", rows["LBR V2, điểm f1"]),
               ("lbr_app", rows["LBR V3, recall_first"]))
    metrics = (("micro", "micro_f1"), ("collar_1s", "event_f1_collar_1s"),
               ("segment_1s", "segment_f1_1s"))
    human = calibration["human"]
    return {"systems": [(entity, [row[m] for m, _ in metrics]) for entity, row in systems],
            "human": [human[h] for _, h in metrics], "pairs": human["pairs"]}


def ceiling_curve(ceiling: dict) -> list[tuple[float, float, float]]:
    return [(r["block_s"], r["event_f1"], r["event_f1_collar_1s"])
            for r in ceiling["resolution_ceiling"]]


def error_split(ceiling: dict) -> tuple[int, int, int]:
    s = ceiling["system"]
    split = (s["n_collar_match"], s["n_overlap_but_boundary_miss"], s["n_deleted"])
    if sum(split) != s["n_reference"]:
        raise ValueError(f"phân rã lỗi không cộng đủ {s['n_reference']}: {split}")
    return split


def ablation_rows(ablation: dict) -> list[dict]:
    names = {"không độ phân giải (pool /64)": "Quay về nén thời gian 64 lần",
             "trần pos_weight 50": "Trần trọng số mẫu dương 50 (thay vì 10)",
             "không augmentation": "Bỏ tăng cường dữ liệu",
             "ensemble C v1": "SED v1 (tổ hợp nhánh C, tham chiếu)"}
    rows = [{"label": f"SED v2 đủ, lần huấn luyện {i}", "group": "full", "mean": r["cv_mean"],
             "sd": r["cv_sd"]} for i, r in enumerate(ablation["full"], start=1)]
    rows += [{"label": names[r["label"]], "group": "ablation", "mean": r["cv_mean"],
              "sd": r["cv_sd"]} for r in ablation["ablations"]]
    rows += [{"label": names[r["label"]], "group": "reference", "mean": r["cv_mean"],
              "sd": r["cv_sd"]} for r in ablation["references"]]
    return rows


def psds_bars(final: dict, grid: dict) -> dict[str, Any]:
    rows = final["sed"]["rows"]
    pairs = {"base": (rows["B0"]["psds_linear"], rows["B0"]["psds_log"]),
             "lbr_main": (rows["lbrv2_f1"]["psds_old_grid"], rows["lbrv2_f1"]["psds_log"]),
             "lbr_app": (rows["lbrv3_f1"]["psds_old_grid"], rows["lbrv3_f1"]["psds_log"])}
    values = {entity: {"old": {k: _value(v) for k, v in old.items()},
                       "log": {k: _value(v) for k, v in log.items()}}
              for entity, (old, log) in pairs.items()}
    never = {r["lbr_run"]: r["curves"]["T_GRID (cũ)"]["boxes_never_included"]
             for r in grid["results"]}
    return {"values": values, "never_included": never}


def caption_rows(caption_gt: dict) -> list[dict]:
    rows = []
    for system in SYSTEMS:
        for method, name in METHODS.items():
            r = caption_gt["results"][f"{system}/{method}"]
            rows.append({"system": system, "method": name,
                         **{f"{tier}_{metric}": r[f"e2e_vs_{tier}"][f"{metric}_rate"]["estimate"]
                            for tier in ("pred", "gt")
                            for metric in ("hallucination", "omission")}})
    return rows


def checker_rates(checker: dict) -> tuple[list[tuple], list[tuple]]:
    pooled = checker["pooled"]
    kinds = [(CHECKER_KINDS[k], v["caught"], v["n"], v["rate"])
             for k, v in pooled["by_kind"].items()]
    sources = sorted(((f"“{k}”", v["caught"], v["n"], v["rate"])
                      for k, v in pooled["by_oov_source"].items()), key=lambda r: r[3])
    return kinds, sources


def failure_split(failures: dict) -> list[dict]:
    rows = []
    for system in SYSTEMS:
        c = failures["results"][system]["by_group"]["all"]
        rows.append({"system": system, "hit": c["hit"], "beyond": c["beyond_top10_or_miss"],
                     "sed_miss": c["sed_miss"], "false_match": c["sed_false_match"],
                     "retrieved": c["retrieved"],
                     "total": c["hit"] + c["beyond_top10_or_miss"] + c["sed_miss"]})
    if len({r["total"] for r in rows}) != 1:
        raise ValueError("số cặp liên quan khác nhau giữa các kho")
    return rows


def backfill_rows(backfill: dict, filters: str = "gold", language: str = "en") -> list[dict]:
    rows = []
    for system in SYSTEMS:
        paired = backfill["results"][f"{system}/{filters}/{language}"]["summary"]["paired_ndcg@10"]
        for key, name in (("backfill−vector_only", "Bổ sung − chỉ ngữ nghĩa"),
                          ("backfill−hybrid", "Bổ sung − kết hợp")):
            p = paired[key]
            rows.append({"system": system, "comparison": name, "estimate": p["estimate"],
                         "lower": p["lower"], "upper": p["upper"], "win": p["win"],
                         "tie": p["tie"], "loss": p["loss"]})
    return rows


# ---------- hình ----------

def _forest(ax, rows: list[dict], colors: list[str], markers: list[str],
            faces: list[str]) -> None:
    for i, (r, color, marker, face) in enumerate(zip(rows, colors, markers, faces, strict=True)):
        ax.plot([r["lower"], r["upper"]], [i, i], color=color, linewidth=1.4,
                solid_capstyle="butt")
        ax.plot(r["estimate"], i, marker, color=color, mfc=face, mec=color, markersize=6)
    ax.axvline(0, color=cs.INK, linewidth=0.8)
    ax.set_ylim(len(rows) - 0.5, -0.5)


def _right_note(ax, y: float, text: str) -> None:
    """Chữ ở lề phải của trục (x theo tỷ lệ trục, y theo dữ liệu); bố cục tự chừa chỗ."""
    ax.annotate(text, xy=(1.02, y), xycoords=ax.get_yaxis_transform(), va="center",
                fontsize=8.5, annotation_clip=False)


def _ci_text(r: dict) -> str:
    return (f"{cs.vn(r['estimate'], 4, True)} [{cs.vn(r['lower'], 4, True)}; "
            f"{cs.vn(r['upper'], 4, True)}]")


def _lower_first(text: str) -> str:
    """Viết thường chữ đầu của tên thường ("Hệ cơ sở"), giữ nguyên viết tắt ("LBR")."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def fig_main_differences(rows: list[dict], path: Path) -> None:
    fig, ax = cs.figure(7.6)
    colors = [cs.ACCENT if r["label"].startswith("LBR") else cs.NEUTRAL for r in rows]
    faces = ["white" if r["set"] == "ngoài mẫu" else c for r, c in zip(rows, colors, strict=True)]
    _forest(ax, rows, colors, ["o"] * len(rows), faces)
    labels = [f"{r['label']}\n({r['set']}, {r['n']} bản ghi)" for r in rows]
    ax.set_yticks(range(len(rows)), labels, fontsize=9)
    for i, r in enumerate(rows):
        _right_note(ax, i, _ci_text(r))
    ax.set_xlim(-0.04, 0.17)
    ax.set_xticks([0, 0.05, 0.1, 0.15])
    cs.comma_axis(ax, "x", 2)
    ax.set_xlabel("Hiệu F1 theo sự kiện micro, KTC 95%")
    cs.style(ax, "x")
    cs.save(fig, path)


def fig_oof_deltas(rows: list[dict], path: Path) -> None:
    fig, ax = cs.figure(7.6)
    colors = [cs.ACCENT if r["group"] == "lbr" else cs.NEUTRAL for r in rows]
    _forest(ax, rows, colors, ["o" if r["group"] == "lbr" else "s" for r in rows], colors)
    ax.set_yticks(range(len(rows)), [r["label"] for r in rows], fontsize=9)
    for i, r in enumerate(rows):
        _right_note(ax, i, cs.vn(r["estimate"], 4, True))
    ax.axhline(len(OOF_CANDIDATES) - 0.5, color=cs.GRID, linewidth=0.8)
    ax.set_xlim(-0.06, 0.13)
    ax.set_xticks([-0.05, 0, 0.05, 0.1])
    cs.comma_axis(ax, "x", 2)
    ax.set_xlabel("Hiệu F1 theo sự kiện micro so với hệ cơ sở\n"
                  "(ngoài mẫu, 564 bản ghi; KTC 95%)")
    cs.style(ax, "x")
    cs.save(fig, path)


def fig_calibration(bars: dict, path: Path) -> None:
    fig, ax = cs.figure(7.0)
    labels = ("F1 theo sự kiện,\ndung sai 0,2 s", "F1 theo sự kiện,\ndung sai 1 s",
              "F1 theo đoạn 1 s")
    width = 0.25
    for j, (entity, values) in enumerate(bars["systems"]):
        color, _ = cs.ENTITY[entity]
        xs = [i + (j - 1) * width for i in range(len(labels))]
        ax.bar(xs, values, width, color=color, label=cs.ENTITY_NAMES[entity])
        for x, v in zip(xs, values, strict=True):
            ax.text(x, v + 0.012, cs.vn(v, 2), ha="center", fontsize=8, zorder=4,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.6})
    for i, h in enumerate(bars["human"]):
        ax.plot([i - 1.6 * width, i + 1.6 * width], [h, h], color=cs.INK, linestyle="--",
                linewidth=1.0, zorder=3,
                label=f"Hai lần gán nhãn ({bars['pairs']} cặp)" if i == 0 else None)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(0, 1.0)
    cs.comma_axis(ax, "y", 1)
    ax.set_ylabel("F1 trên tập kiểm tra")
    ax.legend(frameon=False, ncol=4, loc="upper left", fontsize=8.5)
    cs.style(ax)
    cs.save(fig, path)


def fig_ceiling(curve: list[tuple], splits: dict[str, tuple[int, int, int]], path: Path) -> None:
    fig, (a, b) = cs.figure(6.6, ncols=2, gridspec_kw={"width_ratios": [1.1, 1]})
    blocks = [c[0] for c in curve]
    a.plot(blocks, [c[1] for c in curve], "o-", color=cs.ACCENT, markersize=4,
           label="dung sai 0,2 s")
    a.plot(blocks, [c[2] for c in curve], "s--", color=cs.NEUTRAL, markersize=4,
           label="dung sai 1 s")
    for x, name in ((0.08, "SED v2"), (0.64, "CNN14 (v1)")):
        a.axvline(x, color=cs.GRID, linewidth=1.0, zorder=0)
        a.text(x * 1.06, 0.06, name, rotation=90, ha="left", va="bottom", fontsize=8.5)
    a.set_xscale("log")
    a.set_xticks(blocks, [cs.vn(b, 2) for b in blocks], fontsize=8)
    a.minorticks_off()
    a.set_ylim(0, 1.05)
    cs.comma_axis(a, "y", 1)
    a.set_xlabel("Độ dài khối quyết định (giây)")
    a.set_ylabel("F1 tối đa khi nhận dạng đúng")
    a.legend(frameon=False, loc="center left", bbox_to_anchor=(0, 0.62), fontsize=8.5)
    cs.style(a)
    names = ("Khớp dung sai", "Đúng lớp, lệch biên", "Bỏ sót")
    colors = (cs.ACCENT, "#6BAED6", cs.NEUTRAL)
    for i, split in enumerate(splits.values()):
        left = 0
        for value, name, color in zip(split, names, colors, strict=True):
            b.barh(i, value, left=left, color=color, label=name if i == 0 else None)
            b.text(left + value / 2, i, str(value), ha="center", va="center", fontsize=8.5,
                   color="white" if color != "#6BAED6" else cs.INK)
            left += value
    b.set_yticks(range(len(splits)), list(splits), fontsize=9)
    b.set_ylim(1.6, -0.6)
    b.set_xlabel(f"Sự kiện tham chiếu (tập phát triển, {sum(next(iter(splits.values())))})")
    b.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5)
    cs.style(b, "x")
    cs.save(fig, path)


def fig_ablation(rows: list[dict], path: Path) -> None:
    fig, ax = cs.figure(6.4)
    full = [r["mean"] for r in rows if r["group"] == "full"]
    # Dải nền: khoảng giữa 3 lần huấn luyện SED v2 đủ (giải thích trong chú thích hình).
    ax.axvspan(min(full), max(full), color=cs.SEQUENTIAL[0], alpha=0.7, zorder=0)
    for i, r in enumerate(rows):
        color = {"full": cs.ACCENT, "ablation": "#CC3311", "reference": cs.NEUTRAL}[r["group"]]
        ax.errorbar(r["mean"], i, xerr=r["sd"], fmt="o", color=color, capsize=3, markersize=5)
        ax.text(r["mean"], i - 0.28, cs.vn(r["mean"], 4), ha="center", fontsize=8)
    ax.set_yticks(range(len(rows)), [r["label"] for r in rows], fontsize=9)
    ax.set_ylim(len(rows) - 0.5, -0.7)
    ax.set_xlim(0, 0.3)
    cs.comma_axis(ax, "x", 2)
    ax.set_xlabel("F1 theo sự kiện micro, kiểm chứng chéo 5 phần trên tập phát triển\n"
                  "(thanh: ±1 độ lệch chuẩn giữa các phần)")
    cs.style(ax, "x")
    cs.save(fig, path)


def fig_psds(bars: dict, path: Path) -> None:
    fig, axes = cs.figure(6.4, ncols=2, sharey=True)
    entities = list(bars["values"])
    for ax, key, title in ((axes[0], "psds_1", "PSDS-1 (biên khớp chặt)"),
                           (axes[1], "psds_2", "PSDS-2 (chỉ cần chồng lấp)")):
        for i, entity in enumerate(entities):
            color, _ = cs.ENTITY[entity]
            for j, grid in enumerate(("old", "log")):
                value = bars["values"][entity][grid][key]
                x = i + (j - 0.5) * 0.36
                ax.bar(x, value, 0.34, color=color if grid == "log" else "white",
                       edgecolor=color, hatch=None if grid == "log" else "///", linewidth=1.0)
                ax.text(x, value + 0.015, cs.vn(value, 2), ha="center", fontsize=8)
        ax.set_xticks(range(len(entities)), [cs.ENTITY_NAMES[e] for e in entities], fontsize=9)
        ax.set_title(title)
        ax.set_ylim(0, 0.9)
        cs.comma_axis(ax, "y", 1)
        cs.style(ax)
    handles = [matplotlib.patches.Patch(facecolor="white", edgecolor=cs.MUTED, hatch="///",
                                        label="Lưới ngưỡng ban đầu"),
               matplotlib.patches.Patch(facecolor=cs.MUTED, label="Lưới log, dùng chung")]
    axes[0].legend(handles=handles, frameon=False, loc="upper left", fontsize=8.5)
    cs.save(fig, path)


def fig_caption_gt(rows: list[dict], path: Path) -> None:
    fig, axes = cs.figure(10.5, ncols=2, sharey=True)
    for ax, metric, title in ((axes[0], "hallucination", "Ảo giác"),
                              (axes[1], "omission", "Bỏ sót")):
        for i, r in enumerate(rows):
            color, marker = cs.ENTITY[cs.SYSTEM_ENTITY[r["system"]]]
            pred, gt = r[f"pred_{metric}"], r[f"gt_{metric}"]
            ax.plot([pred, gt], [i, i], color=cs.GRID, linewidth=2, zorder=1)
            ax.plot(pred, i, marker, color=color, mfc="white", mec=color, markersize=5, zorder=2)
            ax.plot(gt, i, marker, color=color, markersize=5, zorder=3)
        for k in range(1, len(SYSTEMS)):
            ax.axhline(k * len(METHODS) - 0.5, color=cs.GRID, linewidth=0.6)
        ax.set_title(title)
        ax.set_xlim(-0.02, 0.62)
        cs.comma_axis(ax, "x", 1)
        cs.style(ax, "x")
    labels = [f"{cs.ENTITY_NAMES[cs.SYSTEM_ENTITY[r['system']]]}, {r['method']}" for r in rows]
    axes[0].set_yticks(range(len(rows)), labels, fontsize=8.5)
    axes[0].set_ylim(len(rows) - 0.5, -0.5)
    axes[0].plot([], [], "o", color=cs.MUTED, mfc="white", label="so với danh sách dự đoán")
    axes[0].plot([], [], "o", color=cs.MUTED, label="so với nhãn gốc")
    fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, loc="outside upper center",
               ncol=2, fontsize=8.5)
    fig.supxlabel("Tỷ lệ (tập phát triển, 134 bản ghi)", fontsize=9.5)
    cs.save(fig, path)


def fig_checker(kinds: list[tuple], sources: list[tuple], path: Path) -> None:
    fig, (a, b) = cs.figure(6.6, ncols=2, gridspec_kw={"width_ratios": [1, 1]})
    for ax, rows, title in ((a, kinds, "Theo kiểu lỗi chèn vào"),
                            (b, sources, "Nguồn âm ngoài hệ lớp")):
        rates = [r[3] for r in rows]
        ax.barh(range(len(rows)), rates,
                color=[cs.ACCENT if r >= 0.95 else "#CC3311" for r in rates])
        for i, (_, caught, n, rate) in enumerate(rows):
            inside = rate > 0.4
            ax.text(rate - 0.02 if inside else rate + 0.02, i, f"{caught}/{n}", va="center",
                    ha="right" if inside else "left", fontsize=8,
                    color="white" if inside else cs.INK)
        ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8.5)
        ax.set_xlim(0, 1.0)
        ax.set_title(title)
        cs.comma_axis(ax, "x", 1)
        cs.style(ax, "x")
    fig.supxlabel("Tỷ lệ lỗi chèn vào bị bộ đo bắt được (tập phát triển)", fontsize=9.5)
    cs.save(fig, path)


def fig_failures(rows: list[dict], path: Path) -> None:
    fig, ax = cs.figure(6.4)
    parts = (("hit", "Vào top-10", cs.ACCENT),
             ("beyond", "Không vào top-10 (bị cắt hoặc SED bỏ sót)", "#6BAED6"),
             ("sed_miss", "Bị bộ lọc loại vì sự kiện dự đoán không thỏa", cs.NEUTRAL))
    for i, r in enumerate(rows):
        left = 0
        for key, name, color in parts:
            ax.barh(i, r[key], left=left, color=color, label=name if i == 0 else None)
            ax.text(left + r[key] / 2, i, str(r[key]), ha="center", va="center", fontsize=8.5,
                    color=cs.INK if color == "#6BAED6" else "white")
            left += r[key]
    names = [cs.ENTITY_NAMES[cs.SYSTEM_ENTITY[r["system"]]] for r in rows]
    ax.set_yticks(range(len(rows)), names)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(0, rows[0]["total"])
    ax.set_xlabel(f"Cặp (câu truy vấn, bản ghi liên quan theo nhãn gốc), tổng "
                  f"{rows[0]['total']}; tập kiểm tra, chế độ kết hợp")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5)
    cs.style(ax, "x")
    cs.save(fig, path)


def fig_backfill(rows: list[dict], path: Path) -> None:
    fig, ax = cs.figure(7.0)
    ordered = sorted(rows, key=lambda r: (r["comparison"], SYSTEMS.index(r["system"])))
    colors = [cs.ENTITY[cs.SYSTEM_ENTITY[r["system"]]][0] for r in ordered]
    markers = [cs.ENTITY[cs.SYSTEM_ENTITY[r["system"]]][1] for r in ordered]
    faces = ["white" if r["system"] == "f2" else c for r, c in zip(ordered, colors, strict=True)]
    _forest(ax, ordered, colors, markers, faces)
    labels = [f"{r['comparison']}, "
              f"{_lower_first(cs.ENTITY_NAMES[cs.SYSTEM_ENTITY[r['system']]])}"
              for r in ordered]
    ax.set_yticks(range(len(ordered)), labels, fontsize=8.5)
    for i, r in enumerate(ordered):
        _right_note(ax, i, f"{r['win']} / {r['tie']} / {r['loss']}")
    ax.annotate("thắng / hòa / thua", xy=(1.02, -0.85), xycoords=ax.get_yaxis_transform(),
                fontsize=8.5, annotation_clip=False, style="italic")
    ax.axhline(len(SYSTEMS) - 0.5, color=cs.GRID, linewidth=0.8)
    ax.set_xlim(-0.01, 0.22)
    ax.set_xticks(np.arange(0, 0.21, 0.05))
    cs.comma_axis(ax, "x", 2)
    ax.set_xlabel("Hiệu nDCG@10 ghép cặp, KTC 95%\n"
                  "(tập kiểm tra, bộ lọc chuẩn, tiếng Anh)")
    cs.style(ax, "x")
    cs.save(fig, path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path) -> dict[str, Any]:
    cs.apply()
    output.mkdir(parents=True, exist_ok=True)
    data = {k: load(v) for k, v in SOURCES.items()}
    rq3_files = {k: ROOT / v for k, v in data["rq3"]["sources"].items()}
    per_query = {k: load(v)["per_query"] for k, v in rq3_files.items()}
    figures = {
        "c01_main_differences.png": lambda p: fig_main_differences(
            main_differences(data["final"], data["v2_vs_v1"], data["lbr_context"]), p),
        "c02_oof_candidates.png": lambda p: fig_oof_deltas(oof_deltas(data), p),
        "c03_calibration.png": lambda p: fig_calibration(calibration_bars(data["calibration"]),
                                                         p),
        "c04_resolution_ceiling.png": lambda p: fig_ceiling(
            ceiling_curve(data["ceiling_v1"]),
            {"SED v1": error_split(data["ceiling_v1"]),
             "SED v2": error_split(data["ceiling_v2"])}, p),
        "c05_v2_ablation.png": lambda p: fig_ablation(ablation_rows(data["ablation"]), p),
        "c06_psds_grid.png": lambda p: fig_psds(psds_bars(data["final"], data["psds_grid"]), p),
        "c07_caption_vs_gt.png": lambda p: fig_caption_gt(caption_rows(data["caption_gt"]), p),
        "c08_checker_sensitivity.png": lambda p: fig_checker(*checker_rates(data["checker"]), p),
        "c09_retrieval_failures.png": lambda p: fig_failures(failure_split(data["failures"]), p),
        "c10_backfill_paired.png": lambda p: fig_backfill(backfill_rows(data["backfill"]), p),
        "c11_onset_bias.png": lambda p: redraw.fig_onset_bias(
            redraw.onset_bias(data["lbr_diag"]), p),
        "c12_rq1_seeds.png": lambda p: redraw.fig_rq1_seeds(
            redraw.rq1_branches(data["rq1_v1"]), redraw.rq1_branches(data["rq1_v2"]), p),
        "c13_rq2_errors.png": lambda p: redraw.fig_rq2_errors(redraw.rq2_rates(data["rq2"]), p),
        "c14_rq3_queries.png": lambda p: redraw.fig_rq3_queries(
            redraw.rq3_stores(data["rq3"], per_query), p),
    }
    for name, draw in figures.items():
        draw(output / name)
    manifest = {
        "figures": list(figures),
        "sources": {p.relative_to(ROOT).as_posix(): {
            "sha256": _sha256(p), "dirty": bool(data[k].get("git", {}).get("dirty", False))}
            for k, p in SOURCES.items()}
        | {p.relative_to(ROOT).as_posix(): {
            "sha256": _sha256(p), "dirty": bool(load(p).get("git", {}).get("dirty", False))}
           for p in rq3_files.values()},
        "style": "scripts/gon_chart_style.py",
        "git": git_state(ROOT),
    }
    (output / "charts_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = build(args.output)
    print(f"Đã ghi {len(manifest['figures'])} biểu đồ vào {args.output}")


if __name__ == "__main__":
    main()
