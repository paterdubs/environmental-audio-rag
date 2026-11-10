"""Bảng Markdown cho `scripts.report_final_numbers`."""

from __future__ import annotations

from typing import Any

SED_LABELS = {"f2": "f2 (mốc S13)", "B0": "B0 (hệ thống cuối giai đoạn O)",
              "lbrv2_f1": "**LBR V2, điểm f1 (số chính)**", "lbrv3_f1": "LBR V3, điểm f1",
              "lbrv3_recall_first": "LBR V3, recall_first (demo)"}


def v(cell: dict[str, Any] | None, fmt: str = ".4f") -> str:
    return "—" if cell is None else format(cell["value"], fmt)


def ci(lo: dict[str, Any], hi: dict[str, Any], fmt: str = ".4f") -> str:
    return f"[{v(lo, fmt)}, {v(hi, fmt)}]"


def _sed(out: dict[str, Any]) -> list[str]:
    s = out["sed"]
    lines = [f"## SED — test annotated n={s['n_recordings']['value']}, 21 lớp", "",
             "| Hệ thống | Macro | Micro [CI 95%] | Δ micro so B0 [CI] | Nsys/Nref | Giao nhau R | "
             "Giao nhau P | Segment-F1 1 s | PSDS-1 / PSDS-2 lưới tuyến tính | PSDS-1 / PSDS-2 "
             "lưới log |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key, row in s["rows"].items():
        micro = v(row["micro"]) + (" " + ci(row["micro_ci"]["lower"], row["micro_ci"]["upper"])
                                   if "micro_ci" in row else "")
        delta = row.get("delta_micro_vs_b0")
        delta_s = ("—" if delta is None else f"{v(delta['estimate'], '+.4f')} "
                   f"{ci(delta['lower'], delta['upper'], '+.4f')}")
        lin = row.get("psds_linear")
        log = row.get("psds_log")
        lines.append(
            f"| {SED_LABELS[key]} | {v(row['macro'])} | {micro} | {delta_s} | "
            f"{v(row['nsys'], 'd')}/{v(row['nref'], 'd')} | "
            f"{v(row.get('intersection_recall'))} | {v(row.get('intersection_precision'))} | "
            f"{v(row.get('segment_f1_1s'))} | "
            + (f"{v(lin['psds_1'])} / {v(lin['psds_2'])}" if lin else "—") + " | "
            + (f"{v(log['psds_1'])} / {v(log['psds_2'])}" if log else "—") + " |")
    d = s["b0_minus_f2"]
    vn = s["lbrv3_recall_first_vn"]
    old = s["rows"]["lbrv2_f1"]["psds_old_grid"]
    lines += ["", f"- B0 − f2 micro: {v(d['estimate'], '+.4f')} "
                  f"{ci(d['lower'], d['upper'], '+.4f')} (CI chứa 0).",
              f"- PSDS của LBR trên `T_GRID` cũ (V2): {v(old['psds_1'])} / {v(old['psds_2'])} — "
              "lưới cắt phần lớn box; lưới log ghi trước ở ADR-0047, B0 cùng lưới ở ADR-0048 §3.",
              f"- V3 recall_first trên 19 lớp Việt Nam (ADR-0046): giao nhau R {v(vn['recall'])}, "
              f"P {v(vn['precision'])}.", ""]
    return lines


def _rq1(out: dict[str, Any]) -> list[str]:
    lines = ["## RQ1 — DataSEC có giúp thêm so với AudioSet? (C − B, event-F1 micro)", "",
             "| Recipe | B mean ± sd (n) | C mean ± sd (n) | Bootstrap C − B [CI] | "
             "Welch p event-F1 / PSDS-1 / PSDS-2 |", "|---|---:|---:|---:|---:|"]
    for name, r in out["rq1"].items():
        b, c = r["branches"]["B"], r["branches"]["C"]
        boot, p = r["bootstrap_c_minus_b"], r["welch_p"]
        lines.append(f"| {name} | {v(b['mean'])} ± {v(b['sd'])} ({v(b['n'], 'd')}) | "
                     f"{v(c['mean'])} ± {v(c['sd'])} ({v(c['n'], 'd')}) | "
                     f"{v(boot['estimate'], '+.4f')} {ci(boot['lower'], boot['upper'], '+.4f')} | "
                     f"{v(p['event_f1'], '.3f')} / {v(p['psds_1'], '.3f')} / "
                     f"{v(p['psds_2'], '.3f')} |")
    return lines + [""]


def _rq2(out: dict[str, Any]) -> list[str]:
    r = out["rq2"]
    lines = ["## RQ2 — caption bị ràng buộc vào timeline (test annotated)", "",
             "Template EN/VI: hallucination, omission, từ cấm, gọi tên quá mức bằng "
             + ", ".join(f"{label} " + "/".join(v(r["template"][label][lang]["hallucination_rate"],
                                                  ".3f") for lang in ("en", "vi"))
                         for label in r["template"]) + " (hallucination EN/VI; mọi ô còn lại "
             "xem JSON).", ""]
    metrics = (("hallucination_rate", "Halluc."), ("omission_rate", "Omission"),
               ("context_term_rate", "Bối cảnh"), ("over_specific_rate", "Quá mức"))
    for branch, cells in r["llm_e2e"].items():
        lines += [f"### {branch} (mức e2e)", "",
                  "| Hệ thống | " + " | ".join(n for _, n in metrics) + " | Bị cắt |",
                  "|---|" + "---:|" * (len(metrics) + 1)]
        for label, cell in cells.items():
            lines.append(f"| {label} | " + " | ".join(
                f"{v_ci(cell[m])}" for m, _ in metrics) + f" | {v(cell['n_truncated'], 'd')} |")
        lines.append("")
    if r["llm_oracle"]:
        check = r["oracle_check"]
        lines += [f"Mức oracle (caption S8, timeline ground truth; kiểm {check['identical']}/"
                  f"{check['n']} trùng):", "", "| Nhánh | " + " | ".join(n for _, n in metrics)
                  + " |", "|---|" + "---:|" * len(metrics)]
        for branch, cell in r["llm_oracle"].items():
            lines.append(f"| {branch} | " + " | ".join(v_ci(cell[m]) for m, _ in metrics) + " |")
        lines.append("")
    return lines


def v_ci(cell: dict[str, Any]) -> str:
    value = cell["value"]
    return f"{value['estimate']:.3f} [{value['lower']:.3f}, {value['upper']:.3f}]"


def _rq3(out: dict[str, Any]) -> list[str]:
    lines = ["## RQ3 — truy vấn có temporal predicate (test, nDCG@10 [CI 95%])", "",
             "| Corpus | structured/en | vector/en | hybrid/en | hybrid/vi | hybrid/en parsed | "
             "Unsupported | Có trả lời | Trích đúng GT |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label, r in out["rq3"].items():
        n = r["ndcg10_gold"]
        a = r["answers_hybrid_en"]
        lines.append(f"| {label} | " + " | ".join(
            f"{v(n[c]['estimate'], '.3f')} {ci(n[c]['lower'], n[c]['upper'], '.3f')}"
            for c in ("structured_only/en", "vector_only/en", "hybrid/en", "hybrid/vi"))
            + f" | {v(r['ndcg10_parsed_hybrid_en'], '.3f')} | "
            f"{v(a['unsupported_claim_rate'], '.3f')} | {v(a['answered'], 'd')}/{v(a['n'], 'd')} | "
            f"{v(a['cited_relevant_share'], '.3f')} |")
    return lines + [""]


def _psds(out: dict[str, Any]) -> list[str]:
    p = out["psds_diagnosis"]
    verdicts = "; ".join(f"{name}: " + ", ".join(f"{s} {'đủ' if ok else 'không'}"
                                                for s, ok in by.items())
                         for name, by in p["supported"].items()) or "—"
    return ["## Chẩn đoán PSDS v1 → v2 trên dev (ADR-0048 §2)", "",
            f"Tái hiện S21: {'có' if p['reproduced'] else 'không'}; đã giải thích: "
            f"{'có' if p['explained'] else 'chưa'}. Giả thuyết: {verdicts}. Nguồn "
            f"`{p['source']}`.", ""]


def _demo(out: dict[str, Any]) -> list[str]:
    d = out["demo"]
    p = d["parity"]
    return ["## Phục vụ demo LBR V3 recall_first", "",
            f"Parity CUDA so với output đóng băng: {v(p['n_shared_events'], 'd')}/"
            f"{v(p['n_events'], 'd')} event trùng khít, {v(p['n_within_frame'], 'd')} trong 1 "
            f"frame, {v(p['n_within_collar'], 'd')} trong collar 0.2 s; Δ xác suất lớn nhất "
            f"{v(p['prob_max_abs'], '.4f')}. E2E upload + phân tích "
            f"{v(d['e2e']['upload_elapsed_s'], '.1f')} s, RAG "
            f"{v(d['e2e']['rag_elapsed_s'], '.2f')} s.",
            ""]


def render_markdown(out: dict[str, Any]) -> str:
    lines = ["# Số chính của luận văn (R5)", "",
             "> Sinh bởi `scripts.report_final_numbers` — chỉ đọc artifact đã có, không tính lại "
             "metric. Nguồn từng ô ở JSON đi kèm (`source` + `key`). Báo cáo, slide và SYSTEM "
             "§8.4 trích từ file này; `check_doc_claims` đối chiếu.", ""]
    lines += _sed(out) + _rq1(out) + _rq2(out) + _rq3(out) + _psds(out) + _demo(out)
    lines += [f"git: `{out['git']['revision']}` dirty={out['git']['dirty']}"]
    return "\n".join(lines) + "\n"
