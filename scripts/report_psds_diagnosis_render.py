"""Bảng Markdown cho `scripts.report_psds_diagnosis` (tách riêng để file chính ngắn)."""

from __future__ import annotations

from typing import Any

VERDICT = {True: "đủ điều kiện", False: "không"}


def _f(value: float) -> str:
    return f"{value:.4f}"


def _psds_table(out: dict) -> list[str]:
    lines = ["## PSDS theo lưới và biến thể", "",
             "| Hệ thống | Lưới | Điểm | Event ở ngưỡng thấp nhất | PSDS-1 | PSDS-2 | "
             "PSDS-1 α_st=0 | PSDS-2 α_st=0 | PSDS-1 DTC=GTC=0.5 | eFPR lớn nhất (PSDS-2) | "
             "Bỏ vì >50,000 event |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label, res in out["results"].items():
        for grid, g in res["grids"].items():
            s = g["scenarios"]
            lines.append(
                f"| {label} | {grid} | {g['n_points']}/{g['n_grid']} | "
                f"{g['events_at_lowest_threshold']} | {_f(s['psds_1']['psds'])} | "
                f"{_f(s['psds_2']['psds'])} | {_f(s['psds_1']['psds_alpha_st0'])} | "
                f"{_f(s['psds_2']['psds_alpha_st0'])} | {_f(s['psds_1_dtc05']['psds'])} | "
                f"{s['psds_2']['efpr_max']:.1f} | {g.get('n_skipped_over_cap', 0)} |")
    return lines


def _tpr_table(out: dict) -> list[str]:
    efprs = [str(float(e)) for e in out["efpr_points"]]
    lines = ["", "## TPR trung bình các lớp tại eFPR (lưới tuyến tính) và điểm đã chọn", "",
             "| Hệ thống | Tiêu chí | event-F1 micro | Điểm đã chọn (eFPR, TPR) | "
             + " | ".join(f"TPR@{float(e):g}" for e in efprs) + " |",
             "|---|---|---:|---|" + "---:|" * len(efprs)]
    for label, res in out["results"].items():
        for scenario in ("psds_1", "psds_2"):
            sel = res["selected"][scenario]
            tpr = res["grids"]["linear"]["scenarios"][scenario]["mean_tpr_at"]
            lines.append(f"| {label} | {scenario} | {_f(res['event_f1_micro'])} | "
                         f"({sel['mean_efpr']:.1f}, {sel['mean_tpr']:.3f}) | "
                         + " | ".join(f"{tpr[e]:.3f}" for e in efprs) + " |")
    return lines


def _per_class(out: dict) -> list[str]:
    results = out["results"]
    if not {"v1", "v2"} <= set(results):
        return []
    lines = ["", "## AUC theo lớp (lưới tuyến tính, v1 → v2)", "",
             "| Lớp | PSDS-1 v1 | PSDS-1 v2 | Δ | PSDS-2 v1 | PSDS-2 v2 | Δ |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    a = results["v1"]["grids"]["linear"]["scenarios"]
    b = results["v2"]["grids"]["linear"]["scenarios"]
    for cls in a["psds_1"]["per_class_auc"]:
        x1, y1 = a["psds_1"]["per_class_auc"][cls], b["psds_1"]["per_class_auc"][cls]
        x2, y2 = a["psds_2"]["per_class_auc"][cls], b["psds_2"]["per_class_auc"][cls]
        lines.append(f"| {cls} | {x1:.3f} | {y1:.3f} | {y1 - x1:+.3f} | {x2:.3f} | {y2:.3f} | "
                     f"{y2 - x2:+.3f} |")
    return lines


def _hypotheses(h: dict[str, Any] | None) -> list[str]:
    if h is None:
        return []
    lines = ["", "## Luật ghi trước (ADR-0048 §2)", "",
             f"Δ = {h['candidate']} − {h['reference']}. Δ event-F1 micro dev "
             f"{h['delta_event_f1_micro']:+.4f}; Δ PSDS lưới tuyến tính: "
             + ", ".join(f"{k} {v:+.4f}" for k, v in h["delta_psds_linear"].items()) + ".", "",
             f"**Tái hiện S21 trên dev:** {'có' if h['reproduced'] else 'không'}."]
    if not h["reproduced"]:
        lines += ["", "Dev không tái hiện S21 → không diễn giải giả thuyết nào."]
        return lines
    lines += ["", "| Giả thuyết | Tiêu chí | Δ trước | Δ sau | Kết luận |",
              "|---|---|---:|---:|---|"]
    for name, by_scenario in h["hypotheses"].items():
        for scenario, item in by_scenario.items():
            if name == "H2":
                lines.append(f"| H2 | {scenario} | eFPR chọn {item['chosen_efpr']:.1f} | "
                             f"thấp {item['low_efpr']} / cao {item['high_efpr']} | "
                             f"{VERDICT[item['supported']]} |")
            else:
                lines.append(f"| {name} | {scenario} | {item['delta_before']:+.4f} | "
                             f"{item['delta_after']:+.4f} | {VERDICT[item['supported']]} |")
    lines += ["", f"**Đã giải thích S21 trên dev:** {'có' if h['explained'] else 'chưa'} "
              "(ít nhất một giả thuyết đủ điều kiện)."]
    return lines


def render_markdown(out: dict) -> str:
    inputs = "; ".join(f"{k}: `{v['predictions']}` + `{v['postproc']}` ({v['family']}, "
                       f"n={v['n_recordings']})" for k, v in out["inputs"].items())
    lines = [f"# Chẩn đoán PSDS trên dev — {out['eval_set']} (ADR-0048 §2)", "",
             "> Sinh bởi `scripts.report_psds_diagnosis`. Chỉ dev; v1, v2, f2 là in-sample đối với "
             "hậu xử lý đã chọn trên dev, B0 dùng posterior OOF. Không đọc test.", "",
             f"Đầu vào: {inputs}.", ""]
    lines += _psds_table(out) + _tpr_table(out) + _per_class(out) + _hypotheses(out["hypotheses"])
    for label, check in out["consistency_checks"].items():
        lines += ["", f"Kiểm nhất quán {label}: PSDS lưới tuyến tính tính lại "
                      f"{'trùng' if check['match'] else 'LỆCH'} `{check['file']}`."]
    lines += ["", f"git: `{out['git']['revision']}` dirty={out['git']['dirty']}"]
    return "\n".join(lines) + "\n"
