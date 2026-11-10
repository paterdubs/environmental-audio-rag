"""Bảng Markdown cho `scripts.report_rq2_llm_systems`."""

from __future__ import annotations

from typing import Any

METRICS = (("hallucination_rate", "Hallucination ↓"), ("omission_rate", "Omission ↓"),
           ("temporal_order_eligible", "Thứ tự (≥2 mention) ↑"),
           ("over_specific_rate", "Gọi tên quá mức ↓"),
           ("context_term_rate", "Suy diễn bối cảnh ↓"), ("forbidden_term_rate", "Từ cấm (G3) ↓"))


def _ci(entry: dict[str, float], signed: bool = False) -> str:
    f = "+.3f" if signed else ".3f"
    return f"{entry['estimate']:{f}} [{entry['lower']:{f}}, {entry['upper']:{f}}]"


def _table(cells: dict[str, dict[str, Any]], title: str) -> list[str]:
    systems = list(cells)
    lines = [f"### {title}", "", "| Metric | " + " | ".join(systems) + " |",
             "|---|" + "---:|" * len(systems)]
    for key, name in METRICS:
        lines.append(f"| {name} | " + " | ".join(_ci(cells[s]["ci"][key]) for s in systems) + " |")
    lines.append("| Caption bị cắt | " + " | ".join(str(cells[s]["n_truncated"]) for s in systems)
                 + " |")
    lines.append("| n | " + " | ".join(str(int(cells[s]["summary"]["n"])) for s in systems) + " |")
    return lines + [""]


def _paired(paired: dict[str, Any]) -> list[str]:
    lines = ["## Hiệu số cặp theo recording (mức e2e)", "",
             "| Nhánh | So sánh | " + " | ".join(name for _, name in METRICS) + " |",
             "|---|---|" + "---:|" * len(METRICS)]
    for branch, comparisons in paired.items():
        for name, metrics in comparisons.items():
            if "skipped" in metrics:
                lines.append(f"| {branch} | {name} | bỏ qua: {metrics['skipped']} |"
                             + " |" * (len(METRICS) - 1))
                continue
            lines.append(f"| {branch} | {name} | "
                         + " | ".join(_ci(metrics[k], signed=True) for k, _ in METRICS) + " |")
    return lines + [""]


def render_markdown(out: dict[str, Any]) -> str:
    systems = ", ".join(f"{k}: `{v}`" for k, v in out["systems"].items())
    lines = [f"# RQ2 — caption LLM theo hệ thống SED ({out['split']}, {out['eval_set']}, "
             "ADR-0048 §1)", "",
             "> Sinh bởi `scripts.report_rq2_llm_systems`. Chấm lại bằng "
             "`score_captions.score_sources`, lexicon EN đóng băng "
             f"`{out['lexicon_sha256'][:8]}…`. CI 95% bootstrap theo recording. Chỉ mô tả — "
             "không chọn hay đổi gì từ các số này.", "", f"Hệ thống: {systems}.", ""]
    lines += ["## Mức e2e (timeline = SED của từng hệ thống)", ""]
    for branch, cells in out["e2e"].items():
        lines += _table(cells, branch)
    lines += _paired(out["paired"])
    check = out.get("oracle_check")
    if check is not None:
        state = "trùng" if check["ok"] else "LỆCH — không dùng lại"
        lines += ["## Mức oracle (timeline = ground truth, dùng lại caption S8 của f2)", "",
                  f"Kiểm timeline oracle: {check['identical']}/{check['n']} trùng ground truth "
                  f"dựng lại → {state}.", ""]
        for branch, cell in out["oracle"].items():
            lines += _table({"oracle": cell}, branch)
    lines += [f"git: `{out['git']['revision']}` dirty={out['git']['dirty']}"]
    return "\n".join(lines) + "\n"
