"""Hình phân tích cho báo cáo cuối: dữ liệu, quá trình huấn luyện, hành trình SED, chẩn đoán lỗi.

Mọi số đọc lại từ artifact đã đóng băng (measurement JSON, `logs/history.json` của run, evaluation
đã lưu); không tính lại metric trên test và không đọc `predictions/test.npz`. Chẩn đoán lỗi chỉ dùng
dự đoán ngoài mẫu (OOF) trên train ∪ dev.

    .venv/Scripts/python.exe -m scripts.build_research_figures
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates  # noqa: E402
import matplotlib.patches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from ml.provenance import git_state  # noqa: E402
from scripts.report_docx import figure_labels  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
DEFAULT_OUTPUT = ROOT / "report" / "research_figures"
DPI = 300
INK, MUTED, GRID = "#1f2328", "#57606a", "#d0d7de"
BLUE, ORANGE, GREEN, GRAY = "#2a78d6", "#eb6834", "#2f9e44", "#8c959f"
SPLIT_COLORS = {"train": BLUE, "validation": ORANGE, "test": GREEN}
SPLIT_NAMES = {"train": "train", "validation": "dev", "test": "test"}

SOURCES = {
    "profile": M / "data_profile_20261008_lf.json",
    "s13_test": M / "s13_test_20261018.json",
    "s13_rank": M / "s13_ranking_annotated_20260928.json",
    "final": M / "final_numbers_20261110.json",
    "lbr_context": M / "lbr_context_20261123.json",
    "calibration": M / "calibration_20261123.json",
    "lbr_diag": M / "lbr_diagnosis_20261109.json",
    "served": ROOT / "ml/runs/sed_served_B0_20261107T175659Z/manifest.json",
    "eval_dir": ROOT / "ml/runs/sed_ensemble_B0_final_test_20261014T085016Z",
    "rq1_v1": M / "rq1_multiseed_clean_20260924.json",
    "rq1_v2": M / "rq1_v2_multiseed_20260929.json",
    "rq2": M / "rq2_llm_systems_20261110_test_annotated.json",
    "rq3": M / "rq3_modes_20261123.json",
    "registry": M / "run_registry_20261123.json",
    "backfill": M / "retrieval_backfill_test_20261124.json",
}
TASK_GROUPS = {
    "Huấn luyện SED": ("sed_polyphonic",),
    "Suy luận lại, OOF, ensemble": ("sed_rewindow", "sed_oof", "sed_ensemble", "sed_filtered",
                                    "pseudo_labels", "sed_served"),
    "LBR": ("sed_lbr", "sed_lbr_oof_events"),
    "Bộ phân loại DataSEC": ("classifier_datasec",),
    "Kho truy hồi": ("retrieval_index",),
}
PHASES = (("20260922", "20260925", "v1, RQ1"), ("20260926", "20260929", "v2, Track 2, S13"),
          ("20261008", "20261014", "Giai đoạn O"), ("20261107", "20261110", "P, LBR"))
SYSTEM_NAMES = {"f2": "f2", "B0": "B0", "lbrv2": "LBR V2", "lbrv3": "LBR V3"}
METHOD_NAMES = {"template": "Mẫu cố định", "unconstrained": "LLM tự do",
                "constrained": "LLM ràng buộc", "constrained_cover": "LLM ràng buộc + phủ"}
FN_KINDS = {
    "miss_nothing": "Không có hộp nào chồng",
    "miss_other_class_overlap": "Chỉ có hộp lớp khác chồng",
    "bnd_onset": "Lệch biên đầu",
    "bnd_offset": "Lệch biên cuối",
    "bnd_both": "Lệch cả hai biên",
    "merged": "Bị gộp với sự kiện khác",
    "fragmented": "Bị cắt vụn",
}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _value(cell: Any) -> float:
    return float(cell["value"]) if isinstance(cell, dict) else float(cell)


def _style(ax: plt.Axes, axis: str = "y") -> None:
    ax.grid(axis=axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


FIGURE_NAMES: figure_labels.Names = ()


def _save(fig: plt.Figure, path: Path) -> None:
    figure_labels.relabel(fig, FIGURE_NAMES)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------- dữ liệu thuần (có test) ----------

def journey_rows(s13_test: dict, s13_rank: dict, final: dict, lbr_context: dict) -> list[dict]:
    """Từng thế hệ SED: điểm test annotated (micro, CI, macro) và điểm dùng để chọn."""
    tests = {r["label"]: r for r in s13_test["results"]}
    cv = {r["label"]: r["annotated"]["score"]["mean"] for r in s13_rank["ranking"]}
    rows = [{"name": name, "micro": tests[label]["micro"], "lower": tests[label]["micro_ci_lower"],
             "upper": tests[label]["micro_ci_upper"], "macro": tests[label]["macro"],
             "select": cv[label], "select_kind": "dev CV"}
            for label, name in (("a", "v1"), ("c", "v2"), ("f2", "f2"))]
    sed = final["sed"]["rows"]
    oof = lbr_context["rows"]
    for key, name, oof_key in (("B0", "B0", "B0"), ("lbrv2_f1", "B0 + LBR V2", "LBR_v2")):
        row = sed[key]
        rows.append({"name": name, "micro": _value(row["micro"]),
                     "lower": _value(row["micro_ci"]["lower"]),
                     "upper": _value(row["micro_ci"]["upper"]), "macro": _value(row["macro"]),
                     "select": oof[oof_key]["micro"], "select_kind": "OOF"})
    return rows


def fn_breakdown(diag: dict) -> list[tuple[str, int]]:
    kinds = diag["breakdown"]["fn_kinds"]
    return sorted(((FN_KINDS[k], v) for k, v in kinds.items()), key=lambda kv: kv[1])


def per_class_pairs(b0: dict, v2: dict, counts: dict[str, int], min_n: int) -> list[tuple]:
    """(lớp, n, F1 B0, F1 V2) cho lớp có ít nhất `min_n` sự kiện tham chiếu, xếp theo F1 V2."""
    rows = [(cid, counts[cid], b0["event_based_f1_per_class"][cid]["f_measure"],
             scores["f_measure"]) for cid, scores in v2["event_based_f1_per_class"].items()
            if counts[cid] >= min_n]
    return sorted(rows, key=lambda r: r[3])


def fold_histories(served_manifest: dict) -> list[list[dict]]:
    members = served_manifest["command"]
    runs = [m for m in members if m.startswith("ml/runs/sed_polyphonic_")]
    return [load(ROOT / run / "logs" / "history.json")["epochs"] for run in runs]


def query_diffs(per_query: list[dict], a: str = "hybrid", b: str = "vector_only",
                language: str = "en") -> list[float]:
    """Hiệu nDCG@10 (a − b) theo từng truy vấn có bản ghi liên quan, cùng ngôn ngữ."""
    scores: dict[str, dict[str, float]] = {}
    for row in per_query:
        if row["language"] == language and row["n_relevant"] > 0:
            scores.setdefault(row["query_id"], {})[row["mode"]] = row["ndcg@10"]
    return [s[a] - s[b] for s in scores.values() if a in s and b in s]


def rq2_rates(rq2: dict, metric: str) -> dict[str, dict[str, float]]:
    return {method: {sys: rq2["e2e"][method][sys]["summary"][metric] for sys in SYSTEM_NAMES}
            for method in METHOD_NAMES}


def runs_per_day(registry: dict) -> tuple[list[str], dict[str, list[int]]]:
    """Ngày (YYYYMMDD) và số run mỗi ngày theo nhóm loại; loại lạ dồn vào nhóm cuối."""
    lookup = {task: group for group, tasks in TASK_GROUPS.items() for task in tasks}
    days = sorted(registry["per_day"])
    counts = {group: [0] * len(days) for group in TASK_GROUPS}
    fallback = list(TASK_GROUPS)[-1]
    for i, day in enumerate(days):
        for task, n in registry["per_day"][day].items():
            counts[lookup.get(task, fallback)][i] += n
    return days, counts


# ---------- hình ----------

def fig_data_profile(profile: dict, path: Path) -> None:
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 4.4))
    sec = sorted(profile["datasec_by_class"], key=lambda r: r["count"])
    a.barh([r["class_id"] for r in sec], [r["count"] for r in sec], color=BLUE)
    a.set_xscale("log")
    a.set_xlabel("Số tệp (thang log)")
    a.set_title("DataSEC (bản 3): số tệp theo lớp", fontsize=9)
    a.tick_params(axis="y", labelsize=6.5)
    _style(a, "x")
    counts: dict[str, dict[str, int]] = {}
    for r in profile["poly_by_class_split"]:
        counts.setdefault(r["class_id"], {})[r["split"]] = r["count"]
    order = sorted(counts, key=lambda c: sum(counts[c].values()))
    left = [0] * len(order)
    for split in ("train", "validation", "test"):
        values = [counts[c].get(split, 0) for c in order]
        b.barh(order, values, left=left, color=SPLIT_COLORS[split], label=SPLIT_NAMES[split])
        left = [x + v for x, v in zip(left, values, strict=True)]
    b.set_xlabel("Số sự kiện đa âm")
    b.set_title("DataSED: sự kiện theo lớp và tập", fontsize=9)
    b.tick_params(axis="y", labelsize=6.5)
    b.legend(frameon=False, fontsize=7, loc="lower right")
    _style(b, "x")
    fig.tight_layout()
    _save(fig, path)


def fig_event_duration(profile: dict, path: Path) -> None:
    rows: dict[str, dict] = {r["class_id"]: r for r in profile["poly_by_class_split"]
                             if r["split"] == "train"}
    order = sorted(rows, key=lambda c: rows[c]["quantiles"]["0.5"])
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    for i, cid in enumerate(order):
        q = rows[cid]["quantiles"]
        ax.plot([q["0.05"], q["0.95"]], [i, i], color=GRAY, linewidth=1)
        ax.plot([q["0.25"], q["0.75"]], [i, i], color=BLUE, linewidth=5, solid_capstyle="butt")
        ax.plot(q["0.5"], i, "o", color=INK, markersize=3)
    ax.axvline(0.2, color=ORANGE, linestyle="--", linewidth=0.9)
    ax.text(0.21, len(order) - 0.6, "collar 0,2 s", color=ORANGE, fontsize=7)
    ax.set_yticks(range(len(order)), order, fontsize=6.5)
    ax.set_xscale("log")
    ax.set_xlabel("Độ dài sự kiện (giây, log): vạch xám p5–p95, khối xanh p25–p75, "
                  "chấm trung vị")
    _style(ax, "x")
    fig.tight_layout()
    _save(fig, path)


def fig_training_curves(histories: list[list[dict]], path: Path) -> None:
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for i, epochs in enumerate(histories):
        x = [e["epoch"] for e in epochs]
        a.plot(x, [e["train"]["loss"] for e in epochs], color=BLUE, alpha=0.5, linewidth=0.9,
               label="train" if i == 0 else None)
        a.plot(x, [e["validation"]["loss"] for e in epochs], color=ORANGE, alpha=0.7,
               linewidth=0.9, label="dev của fold" if i == 0 else None)
        ap = [e["validation"]["macro_average_precision"] for e in epochs]
        best = max(range(len(ap)), key=ap.__getitem__)
        b.plot(x, ap, color=BLUE, alpha=0.7, linewidth=0.9)
        b.plot(x[best], ap[best], "o", color=ORANGE, markersize=3.5)
    a.set_xlabel("Epoch")
    a.set_ylabel("Loss")
    a.set_title("Loss huấn luyện và dev, 5 fold", fontsize=9)
    a.legend(frameon=False, fontsize=7)
    b.set_xlabel("Epoch")
    b.set_ylabel("Macro AP theo frame (dev của fold)")
    b.set_title("Chỉ số chọn checkpoint; chấm cam: epoch được chọn", fontsize=9)
    for ax in (a, b):
        _style(ax)
    fig.tight_layout()
    _save(fig, path)


def fig_journey(rows: list[dict], human: float, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    x = list(range(len(rows)))
    micro = [r["micro"] for r in rows]
    err = [[r["micro"] - r["lower"] for r in rows], [r["upper"] - r["micro"] for r in rows]]
    ax.errorbar(x, micro, yerr=err, fmt="o", color=BLUE, capsize=3, label="Test: micro (CI 95%)")
    ax.plot(x, [r["macro"] for r in rows], "s", color=GREEN, markersize=4, label="Test: macro")
    ax.plot(x, [r["select"] for r in rows], "D", mfc="none", color=ORANGE, markersize=4.5,
            label="Điểm dùng để chọn (dev CV hoặc OOF)")
    ax.axhline(human, color=MUTED, linestyle="--", linewidth=0.9)
    note = f"đồng thuận hai lần gán nhãn {human:.3f}".replace(".", ",")
    ax.text(x[-1] + 0.3, human + 0.012, note, fontsize=7, color=MUTED, ha="right")
    labels = [f"{r['name']}\n({r['select_kind']})" for r in rows]
    ax.set_xticks(x, labels, fontsize=7.5)
    ax.set_ylabel("Event-F1 (collar 0,2 s)")
    ax.set_ylim(0, max(human, max(r["upper"] for r in rows)) + 0.08)
    ax.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(0, 0.86))
    _style(ax)
    fig.tight_layout()
    _save(fig, path)


def fig_fn_breakdown(diag: dict, path: Path) -> None:
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.4, 1]})
    kinds = fn_breakdown(diag)
    a.barh([k for k, _ in kinds], [v for _, v in kinds], color=BLUE)
    for i, (_, v) in enumerate(kinds):
        a.text(v + 10, i, str(v), va="center", fontsize=7)
    a.set_xlabel("Số sự kiện bị bỏ sót (B0, OOF)")
    a.set_title(f"Loại bỏ sót: {sum(v for _, v in kinds)} sự kiện", fontsize=9)
    _style(a, "x")
    hist = diag["breakdown"]["missed_pmax_histogram"]
    edges, counts = hist["bins"], hist["counts"]
    labels = [f"{edges[i]:.1f}–{min(edges[i + 1], 1.0):.1f}".replace(".", ",")
              for i in range(len(counts))]
    b.bar(labels, counts, color=ORANGE)
    b.set_xlabel("Xác suất lớn nhất của mô hình trong sự kiện bị bỏ sót")
    b.set_ylabel("Số sự kiện")
    b.tick_params(axis="x", labelsize=6.5, rotation=35)
    _style(b)
    fig.tight_layout()
    _save(fig, path)


def fig_onset_bias(diag: dict, path: Path) -> None:
    errors = diag["breakdown"]["onset_error_median_per_class"]
    order = sorted(errors, key=errors.get)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    values = [errors[c] for c in order]
    ax.axvspan(-0.2, 0.2, color=GRID, alpha=0.5, zorder=0, label="trong collar ±0,2 s")
    ax.barh(order, values, color=[ORANGE if v < -0.2 else BLUE for v in values], zorder=2)
    ax.axvline(0, color=INK, linewidth=0.8, zorder=3)
    ax.set_xlabel("Trung vị (onset dự đoán − onset tham chiếu), giây; âm = đoán sớm")
    ax.tick_params(axis="y", labelsize=6.5)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    _style(ax, "x")
    fig.tight_layout()
    _save(fig, path)


def fig_per_class(pairs: list[tuple], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for i, (_, _, b0, v2) in enumerate(pairs):
        ax.plot([b0, v2], [i, i], color=GRID, linewidth=2)
        ax.plot(b0, i, "o", color=GRAY, markersize=4)
        ax.plot(v2, i, "o", color=BLUE, markersize=4)
    ax.set_yticks(range(len(pairs)), [f"{c} (n={n})" for c, n, _, _ in pairs], fontsize=6.5)
    ax.plot([], [], "o", color=GRAY, label="B0")
    ax.plot([], [], "o", color=BLUE, label="B0 + LBR V2")
    ax.set_xlabel("Event-F1 theo lớp trên test annotated (collar 0,2 s)")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    _style(ax, "x")
    fig.tight_layout()
    _save(fig, path)


def fig_dev_vs_test(s13_test: dict, s13_rank: dict, path: Path) -> float:
    from scipy.stats import spearmanr

    cv = {r["label"]: r["annotated"]["score"]["mean"] for r in s13_rank["ranking"]}
    rows = [(r["label"], cv[r["label"]], r["micro"]) for r in s13_test["results"]
            if r["label"] in cv]
    rho = float(spearmanr([r[1] for r in rows], [r[2] for r in rows]).statistic)
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    for label, x, y in rows:
        ax.plot(x, y, "o", color=ORANGE if label == s13_test["selected"] else BLUE)
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(4, 2), fontsize=7)
    ax.set_xlabel("Micro, kiểm chứng chéo 5 fold trên dev")
    ax.set_ylabel("Micro trên test annotated")
    ax.set_title(f"{len(rows)} ứng viên vòng S13; Spearman ρ = {rho:.2f}".replace(".", ","),
                 fontsize=9)
    _style(ax, "both")
    fig.tight_layout()
    _save(fig, path)
    return rho


def fig_rq1_seeds(v1: dict, v2: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.8))
    for ax, data, title in ((axes[0], v1, "Công thức v1, test all"),
                            (axes[1], v2, "Công thức v2, test annotated")):
        for i, branch in enumerate(("B", "C")):
            s = data["branches"][branch]["event_f1"]
            ax.plot([i, i], [s["min"], s["max"]], color=GRAY, linewidth=1)
            color = BLUE if branch == "B" else ORANGE
            ax.errorbar(i, s["mean"], yerr=s["sd"], fmt="o", color=color, capsize=4)
            ax.text(i + 0.08, s["mean"], f"n={s['n']}", fontsize=7, va="center")
        p = data["welch"]["event_f1"]["p"]
        ax.set_xticks([0, 1], ["B: AudioSet", "C: AudioSet → DataSEC"], fontsize=7.5)
        ax.set_xlim(-0.5, 1.6)
        ax.set_title(f"{title}; Welch p = {p:.2f}".replace(".", ","), fontsize=8.5)
        ax.set_ylabel("Event-F1 micro")
        _style(ax)
    fig.tight_layout()
    _save(fig, path)


def fig_rq2_errors(rq2: dict, path: Path) -> None:
    metrics = (("omission_rate", "Tỷ lệ bỏ sót sự kiện"),
               ("hallucination_rate", "Tỷ lệ bịa sự kiện"),
               ("context_term_rate", "Tỷ lệ mô tả có suy diễn bối cảnh"))
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), sharey=False)
    colors = [GRAY, BLUE, ORANGE, GREEN]
    width = 0.2
    for ax, (metric, title) in zip(axes, metrics, strict=True):
        rates = rq2_rates(rq2, metric)
        for j, (method, label) in enumerate(METHOD_NAMES.items()):
            xs = [i + (j - 1.5) * width for i in range(len(SYSTEM_NAMES))]
            values = [rates[method][s] for s in SYSTEM_NAMES]
            ax.bar(xs, values, width, color=colors[j], label=label)
            zeros = [x for x, v in zip(xs, values, strict=True) if v == 0]
            ax.plot(zeros, [0] * len(zeros), "^", color=colors[j], markersize=3.5)
        ax.set_xticks(range(len(SYSTEM_NAMES)), list(SYSTEM_NAMES.values()), fontsize=7)
        ax.set_ylim(bottom=-0.04 * ax.get_ylim()[1])
        ax.set_title(title, fontsize=8.5)
        _style(ax)
    axes[0].legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.tight_layout()
    _save(fig, path)


def fig_rq3_queries(rq3: dict, path: Path) -> list[dict]:
    stores = []
    for key, source in rq3["sources"].items():
        diffs = query_diffs(load(ROOT / source)["per_query"])
        est = rq3["systems"][key]["paired"]["hybrid−vector_only/en"]
        stores.append({"key": key, "diffs": diffs, "neg": sum(d < -1e-9 for d in diffs),
                       "zero": sum(abs(d) <= 1e-9 for d in diffs),
                       "pos": sum(d > 1e-9 for d in diffs), **est})
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for i, s in enumerate(stores):
        jitter = [(k % 9 - 4) * 0.035 for k in range(len(s["diffs"]))]
        ax.scatter([i + j for j in jitter], s["diffs"], s=6, color=GRAY, alpha=0.6, zorder=2)
        yerr = [[s["estimate"] - s["lower"]], [s["upper"] - s["estimate"]]]
        ax.errorbar(i, s["estimate"], yerr=yerr, fmt="D", color=ORANGE, capsize=4, zorder=3)
        ax.text(i, 1.08, f"−{s['neg']} / ={s['zero']} / +{s['pos']}", ha="center", fontsize=7)
    ax.axhline(0, color=INK, linewidth=0.8)
    ax.set_xticks(range(len(stores)), [SYSTEM_NAMES[s["key"]] for s in stores])
    ax.set_ylim(-1.05, 1.18)
    ax.set_ylabel("nDCG@10: hybrid − vector_only")
    _style(ax)
    fig.tight_layout()
    _save(fig, path)
    return [{k: v for k, v in s.items() if k != "diffs"} for s in stores]


def fig_rq3_backfill(backfill: dict, path: Path) -> None:
    modes = (("vector_only", "vector_only", GRAY), ("hybrid", "hybrid", BLUE),
             ("backfill", "backfill", ORANGE))
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    width = 0.26
    for i, key in enumerate(SYSTEM_NAMES):
        s = backfill["results"][f"{key}/gold/en"]["summary"]
        for j, (mode, _, color) in enumerate(modes):
            ax.bar(i + (j - 1) * width, s["mean"][mode]["ndcg@10"], width, color=color)
        share = s["mean"]["backfill"]["tier1_share"]
        ax.text(i + width, s["mean"]["backfill"]["ndcg@10"] + 0.015, f"{share:.0%}",
                ha="center", fontsize=6.5, color=MUTED)
    handles = [matplotlib.patches.Patch(color=color, label=label) for _, label, color in modes]
    ax.set_xticks(range(len(SYSTEM_NAMES)), list(SYSTEM_NAMES.values()))
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("nDCG@10 (test, bộ lọc gold, EN)")
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="upper left", ncol=3)
    _style(ax)
    fig.tight_layout()
    _save(fig, path)


def fig_run_timeline(registry: dict, path: Path) -> None:
    from datetime import date

    def as_date(stamp: str) -> date:
        return date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))

    days, counts = runs_per_day(registry)
    x = [as_date(d) for d in days]
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    bottom = [0] * len(days)
    for (group, values), color in zip(counts.items(), (BLUE, GRAY, ORANGE, GREEN, "#8250df"),
                                      strict=True):
        ax.bar(x, values, bottom=bottom, color=color, width=0.8, label=group)
        bottom = [b + v for b, v in zip(bottom, values, strict=True)]
    top = max(bottom)
    for start, end, label in PHASES:
        ax.axvspan(as_date(start), as_date(end), color=GRID, alpha=0.35, zorder=0)
        ax.text(as_date(start), top * 1.04, label, fontsize=7, color=MUTED)
    ax.set_ylim(0, top * 1.15)
    ax.set_ylabel("Số lần chạy được tạo")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d/%m"))
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=3,
              bbox_to_anchor=(0.5, -0.12))
    ax.set_title(f"{registry['n_runs']} lần chạy trong ml/runs theo ngày tạo", fontsize=9)
    _style(ax)
    fig.tight_layout()
    _save(fig, path)


def build(output: Path) -> dict[str, Any]:
    from scripts.build_midterm_tables import annotated_test_counts

    output.mkdir(parents=True, exist_ok=True)
    data = {k: load(v) for k, v in SOURCES.items() if v.suffix == ".json"}
    ev = SOURCES["eval_dir"]
    b0 = load(ev / "evaluation_phase_o_annotated.json")
    v2 = load(ev / "evaluation_phase_lbr_annotated.json")
    human = data["calibration"]["human"]["micro_f1"]
    fig_data_profile(data["profile"], output / "r01_data_profile.png")
    fig_event_duration(data["profile"], output / "r02_event_duration.png")
    fig_training_curves(fold_histories(data["served"]), output / "r03_training_curves.png")
    fig_journey(journey_rows(data["s13_test"], data["s13_rank"], data["final"],
                             data["lbr_context"]), human, output / "r04_sed_journey.png")
    fig_fn_breakdown(data["lbr_diag"], output / "r05_fn_breakdown.png")
    fig_onset_bias(data["lbr_diag"], output / "r06_onset_bias.png")
    fig_per_class(per_class_pairs(b0, v2, annotated_test_counts(), 10),
                  output / "r07_per_class.png")
    rho = fig_dev_vs_test(data["s13_test"], data["s13_rank"], output / "r08_dev_vs_test.png")
    fig_rq1_seeds(data["rq1_v1"], data["rq1_v2"], output / "r09_rq1_seeds.png")
    fig_rq2_errors(data["rq2"], output / "r10_rq2_errors.png")
    rq3_counts = fig_rq3_queries(data["rq3"], output / "r11_rq3_queries.png")
    fig_run_timeline(data["registry"], output / "r12_run_timeline.png")
    fig_rq3_backfill(data["backfill"], output / "r13_rq3_backfill.png")
    manifest = {"figures": sorted(p.name for p in output.glob("r*.png")),
                "sources": [p.relative_to(ROOT).as_posix() for p in SOURCES.values()],
                "spearman_dev_test": rho, "rq3_query_counts": rq3_counts,
                "git": git_state(ROOT)}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    return manifest


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--labels", type=Path, help="display.yaml có figure_names (bản tinh gọn)")
    args = parser.parse_args()
    global FIGURE_NAMES
    FIGURE_NAMES = figure_labels.load(args.labels)
    manifest = build(args.output)
    rho = manifest["spearman_dev_test"]
    print(f"Đã ghi {len(manifest['figures'])} hình; Spearman dev–test {rho:.3f}")


if __name__ == "__main__":
    main()
