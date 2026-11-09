"""Chẩn đoán lỗi event của B0 trên OOF — sinh lại số ở Context của ADR-0045. Không đọc test.

Phân loại mỗi event bỏ sót (FN) theo quan hệ với box cùng lớp, đo posterior trong span của event
không có box nào, và tính trần "nếu biên của box 1-1 được sửa trong ±d giây" (oracle, chỉ để đo
khoảng cách, không dùng để chọn). Ghép cặp event dùng gán tối ưu với đúng tiêu chí chính; tổng TP
được kiểm khớp `sed_eval` trước khi báo.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from ml.evaluation.sed_metrics import event_counts_per_recording
from ml.postprocessing.lbr_crossfit import micro_f1_objective
from ml.provenance import git_state
from scripts.fit_lbr_oof import baseline_events, load, sebb_params

ROOT = Path(__file__).resolve().parents[1]
P_BINS = (0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001)
ORACLE_RANGES_S = (0.5, 1.0, 2.0)


def _on(e: dict) -> float:
    return float(e.get("onset", e.get("onset_s")))


def _off(e: dict) -> float:
    return float(e.get("offset", e.get("offset_s")))


def _lab(e: dict) -> str:
    return str(e.get("class_id", e.get("event_label")))


def _ok(r: dict, s: dict) -> bool:
    return (abs(_on(r) - _on(s)) <= 0.2
            and abs(_off(r) - _off(s)) <= max(0.2, 0.2 * (_off(r) - _on(r))))


def _overlap(a: dict, b: dict) -> bool:
    return min(_off(a), _off(b)) - max(_on(a), _on(b)) > 0


def match(ref: list[dict], est: list[dict]) -> tuple[set[int], set[int]]:
    """Chỉ số ref/est khớp trong một gán tối ưu theo tiêu chí chính (một lớp, một recording)."""
    if not ref or not est:
        return set(), set()
    ok = np.array([[_ok(r, s) for s in est] for r in ref], dtype=float)
    rows, cols = linear_sum_assignment(-ok)
    pairs = [(i, j) for i, j in zip(rows, cols, strict=True) if ok[i, j]]
    return {i for i, _ in pairs}, {j for _, j in pairs}


def categorize(ref: list[dict], est: list[dict], others: list[dict]) -> list[str]:
    """Loại của từng FN: miss_nothing, miss_other_class_overlap, fragmented, merged, bnd_*."""
    matched, _ = match(ref, est)
    kinds = []
    for i, r in enumerate(ref):
        if i in matched:
            continue
        hits = [s for s in est if _overlap(r, s)]
        if not hits:
            kinds.append("miss_other_class_overlap" if any(_overlap(r, o) for o in others)
                         else "miss_nothing")
        elif len(hits) > 1:
            kinds.append("fragmented")
        elif sum(_overlap(r2, hits[0]) for r2 in ref) > 1:
            kinds.append("merged")
        else:
            on_ok = abs(_on(r) - _on(hits[0])) <= 0.2
            kinds.append("bnd_offset" if on_ok else
                         "bnd_onset" if _ok({**r, "onset": _on(hits[0])}, hits[0]) else "bnd_both")
    return kinds


def _by_class(rows: list[dict], label: str) -> list[dict]:
    return sorted((e for e in rows if _lab(e) == label), key=_on)


def breakdown(ctx: dict, events: dict) -> dict:
    """Loại FN theo lớp, posterior max trong span của event không có box, lệch onset 1-1."""
    kinds: dict[str, Counter] = defaultdict(Counter)
    p_max, onset_err = [], defaultdict(list)
    index = {c: i for i, c in enumerate(ctx["class_ids"])}
    tp = 0
    for rid in ctx["recordings"]:
        for label in ctx["class_ids"]:
            ref = _by_class(ctx["reference"].get(rid, []), label)
            est = _by_class(events.get(rid, []), label)
            others = [e for e in events.get(rid, []) if _lab(e) != label]
            tp += len(match(ref, est)[0])
            for kind in categorize(ref, est, others):
                kinds[label][kind] += 1
            for r in ref:
                hits = [s for s in est if _overlap(r, s)]
                if not hits:
                    frames = ctx["probabilities"][rid][:, index[label]]
                    a = int(_on(r) * ctx["frame_rate"])
                    b = max(a + 1, int(np.ceil(_off(r) * ctx["frame_rate"])))
                    p_max.append(float(frames[a:b].max()))
                elif len(hits) == 1 and sum(_overlap(r2, hits[0]) for r2 in ref) == 1:
                    onset_err[label].append(_on(hits[0]) - _on(r))
    totals = sum(kinds.values(), Counter())
    return {"tp": tp, "fn_kinds": dict(totals), "fn_kinds_per_class": {c: dict(v) for c, v in
                                                                       kinds.items()},
            "missed_pmax_histogram": {"bins": list(P_BINS),
                                      "counts": np.histogram(p_max, P_BINS)[0].tolist()},
            "missed_pmax_median": float(np.median(p_max)) if p_max else None,
            "onset_error_median_per_class": {c: float(np.median(v)) for c, v in onset_err.items()}}


def oracle(ctx: dict, events: dict, max_fix_s: float) -> float:
    """Micro F1 (sed_eval) khi biên của box 1-1 được thay bằng biên nhãn nếu lệch ≤ max_fix_s."""
    fixed = {}
    for rid in ctx["recordings"]:
        rows = []
        for e in events.get(rid, []):
            ref = [r for r in ctx["reference"].get(rid, []) if _lab(r) == _lab(e) and
                   _overlap(r, e)]
            e = dict(e)
            if len(ref) == 1:
                r = ref[0]
                if abs(_on(r) - _on(e)) <= max_fix_s:
                    e["onset"] = _on(r)
                if abs(_off(r) - _off(e)) <= max_fix_s:
                    e["offset"] = _off(r)
            rows.append(e)
        fixed[rid] = rows
    counts = event_counts_per_recording(ctx["reference"], fixed,
                                        event_label_list=list(ctx["class_ids"]))
    nref, nsys, ntp = (sum(c[i] for c in counts.values()) for i in range(3))
    return 2 * ntp / (nref + nsys)


def render(result: dict) -> str:
    b = result["breakdown"]
    lines = ["# Chẩn đoán lỗi event — B0 OOF (ADR-0045 Context)", "",
             "> OOF 564 recording annotated; λ cSEBB chọn chéo fold (tái lập micro của tầng C). "
             "Oracle chỉ đo khoảng cách, không dùng để chọn. Không đọc test.", "",
             f"Micro F1 B0: **{result['micro_f1']:.4f}** · TP {b['tp']} (khớp sed_eval).", "",
             "| Loại FN | Số event |", "|---|---:|"]
    for kind, n in sorted(b["fn_kinds"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {kind} | {n} |")
    h = b["missed_pmax_histogram"]
    edges = zip(h["bins"][:-1], h["bins"][1:], strict=True)
    lines += ["", "Posterior max trong span của event không có box cùng lớp:", "",
              "| Khoảng | " + " | ".join(f"[{a:g}, {c:g})" for a, c in edges)
              + " |", "|---|" + "---:|" * len(h["counts"]),
              "| Số event | " + " | ".join(str(n) for n in h["counts"]) + " |", "",
              "| Trần: sửa biên box 1-1 trong ± | Micro F1 |", "|---|---:|"]
    for d, value in result["oracle"].items():
        lines.append(f"| {d} s | {value:.4f} |")
    lines += ["", "Lệch onset trung vị (dự đoán − nhãn, s) theo lớp, cặp 1-1:", "",
              "| Lớp | Trung vị |", "|---|---:|"]
    for c, v in sorted(b["onset_error_median_per_class"].items()):
        lines.append(f"| `{c}` | {v:+.2f} |")
    return "\n".join([*lines, ""])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="OOF B0")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/measurements")
    args = parser.parse_args()
    out = args.out_dir / f"lbr_diagnosis_{datetime.now(UTC):%Y%m%d}.json"
    if out.exists():
        raise FileExistsError(out)
    ctx = load(args.run)
    objective = micro_f1_objective(ctx["reference"], ctx["class_ids"])
    events = baseline_events(ctx, sebb_params(args.run), {"f1": objective})["f1"]
    counts = event_counts_per_recording(ctx["reference"], events,
                                        event_label_list=list(ctx["class_ids"]))
    nref, nsys, ntp = (sum(c[i] for c in counts.values()) for i in range(3))
    b = breakdown(ctx, events)
    if b["tp"] != ntp:
        raise ValueError(f"ghép cặp chẩn đoán ({b['tp']} TP) lệch sed_eval ({ntp} TP)")
    result = {"run": args.run.name, "micro_f1": 2 * ntp / (nref + nsys), "nref": nref,
              "nsys": nsys, "breakdown": b,
              "oracle": {f"{d:g}": oracle(ctx, events, d) for d in ORACLE_RANGES_S},
              "git": git_state(ROOT)}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
