"""Chẩn đoán PSDS (ADR-0048 §2): vì sao event-F1 tăng mà PSDS không tăng (PAPER_NOTES S21).

Không tự tính PSDS: mọi đường cong và diện tích đến từ ``psds_eval`` (cùng bản vá numpy 2 của
``sed_metrics``). Module chỉ thêm (a) thống kê đọc từ đường PSD-ROC mà ``psds_eval`` đã dựng —
TPR trung bình tại vài eFPR, AUC theo lớp, PSDS khi ``alpha_st = 0`` — (b) vị trí của điểm vận
hành đã chọn trên trục (eFPR, TPR), và (c) luật H1–H4 đúng như ADR-0048 ghi trước khi đo.

Hai API nội bộ của ``psds_eval`` 0.5.3 (bản đã pin) được dùng: ``_auc`` (tĩnh) cho AUC theo lớp,
và ``_effective_fp_rate`` cho vị trí một điểm vận hành; cột đệm của thư viện có id ``"None"``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from ml.evaluation.sed_metrics import _patch_psds_eval_for_numpy2

EFPR_POINTS = (5.0, 10.0, 30.0, 60.0, 100.0)
SHRINK = 0.5  # ADR-0048 §2: |Δ| giảm ít nhất 50% hoặc đổi dấu
DETECTION_COLUMNS = ["filename", "event_label", "onset", "offset"]
EVALUATOR_KEYS = ("dtc_threshold", "gtc_threshold", "cttc_threshold")


def step_lookup(xp: Sequence[float], yp: Sequence[float], x: float) -> float:
    """Giá trị đường bậc thang tại x (như ``psds_eval`` không nội suy)."""
    index = int(np.searchsorted(np.asarray(xp, dtype=float), x, side="right")) - 1
    return 0.0 if index < 0 else float(np.nan_to_num(yp[index]))


def detection_frame(events_by_recording: Mapping[str, Iterable[Mapping[str, Any]]]) -> pd.DataFrame:
    rows = [{"filename": rid, "event_label": e["class_id"], "onset": e["onset_s"],
             "offset": e["offset_s"]} for rid, events in events_by_recording.items()
            for e in events]
    return pd.DataFrame(rows, columns=DETECTION_COLUMNS)


def grid_points(
    events_at: Callable[[float], Mapping[str, Iterable[Mapping[str, Any]]]],
    grid: Iterable[float],
) -> tuple[list[tuple[pd.DataFrame]], list[int]]:
    """Một điểm vận hành mỗi ngưỡng; ngưỡng không ra event bị bỏ như ``evaluate_run``."""
    points: list[tuple[pd.DataFrame]] = []
    sizes: list[int] = []
    for threshold in grid:
        frame = detection_frame(events_at(threshold))
        sizes.append(len(frame))
        if len(frame):
            points.append((frame,))
    return points, sizes


def build_evaluator(ground_truth: pd.DataFrame, metadata: pd.DataFrame,
                    scenario: Mapping[str, float], points: Iterable[tuple[pd.DataFrame]]) -> Any:
    _patch_psds_eval_for_numpy2()
    from psds_eval import PSDSEval

    evaluator = PSDSEval(ground_truth=ground_truth, metadata=metadata,
                         **{k: scenario[k] for k in EVALUATOR_KEYS if k in scenario})
    for point in points:
        evaluator.add_operating_point(*point)
    return evaluator


def curve_stats(evaluator: Any, scenario: Mapping[str, float], *,
                efpr_points: Sequence[float] = EFPR_POINTS) -> dict[str, Any]:
    alpha_ct = float(scenario.get("alpha_ct", 0.0))
    alpha_st = float(scenario.get("alpha_st", 1.0))
    max_efpr = float(scenario.get("max_efpr", 100.0))
    _, _, curve = evaluator.psd_roc_curves(alpha_ct)
    mean = np.nan_to_num(curve.mean)
    names = list(evaluator.class_names[1:])  # hàng c của yp ↔ class_names[c + 1]
    per_class = {
        name: float(evaluator._auc(curve.xp, np.nan_to_num(curve.yp[c]), max_efpr) / max_efpr)
        for c, name in enumerate(names)
    }
    return {
        "psds": float(evaluator.psds(alpha_ct, alpha_st, max_efpr).value),
        "psds_alpha_st0": float(evaluator.psds(alpha_ct, 0.0, max_efpr).value),
        "mean_tpr_at": {str(float(e)): step_lookup(curve.xp, mean, e) for e in efpr_points},
        "per_class_auc": per_class,
        "efpr_max": float(np.max(curve.xp)),
        "max_mean_tpr": float(np.max(mean)),
    }


def operating_position(ground_truth: pd.DataFrame, metadata: pd.DataFrame,
                       scenario: Mapping[str, float], detections: pd.DataFrame) -> dict[str, float]:
    """(TPR trung bình, eFPR trung bình) của đúng một điểm vận hành, theo tiêu chí của scenario."""
    evaluator = build_evaluator(ground_truth, metadata, scenario, [(detections,)])
    rates = evaluator._effective_fp_rate(float(scenario.get("alpha_ct", 0.0)))
    column = [i for i, op_id in enumerate(rates.id) if str(op_id) != "None"]
    if len(column) != 1:
        raise ValueError(f"cần đúng một điểm vận hành, có {len(column)}")
    return {"mean_tpr": float(np.nanmean(rates.tp_ratio[:, column[0]])),
            "mean_efpr": float(np.nanmean(rates.effective_fp_rate[:, column[0]]))}


def _rule(before: float, after: float) -> dict[str, Any]:
    shrunk = before < 0 and abs(after) <= SHRINK * abs(before)
    return {"delta_before": before, "delta_after": after, "supported": bool(after > 0 or shrunk)}


def evaluate_hypotheses(results: Mapping[str, Mapping[str, Any]], *, reference: str = "v1",
                        candidate: str = "v2") -> dict[str, Any]:
    """Luật ADR-0048 §2. Δ = candidate − reference; cấu hình chuẩn là lưới tuyến tính."""
    a, b = results[reference], results[candidate]

    def value(system: Mapping[str, Any], grid: str, scenario: str, field: str = "psds") -> float:
        return float(system["grids"][grid]["scenarios"][scenario][field])

    def delta(grid: str, scenario: str, field: str = "psds") -> float:
        return value(b, grid, scenario, field) - value(a, grid, scenario, field)

    base = {s: delta("linear", s) for s in ("psds_1", "psds_2")}
    gain = float(b["event_f1_micro"]) - float(a["event_f1_micro"])
    reproduced = gain > 0 and any(v <= 0 for v in base.values())
    out: dict[str, Any] = {"reference": reference, "candidate": candidate,
                           "delta_event_f1_micro": gain, "delta_psds_linear": base,
                           "reproduced": reproduced, "hypotheses": {}, "explained": False}
    if not reproduced:
        return out
    phenomena = [s for s, v in base.items() if v <= 0]
    hypotheses: dict[str, dict[str, Any]] = {
        "H1": {s: _rule(base[s], delta("log", s)) for s in phenomena},
        "H2": {s: _localised_gain(a, b, s) for s in phenomena},
        "H3": {s: _rule(base[s], delta("linear", s, "psds_alpha_st0")) for s in phenomena},
    }
    if "psds_1" in phenomena:
        hypotheses["H4"] = {"psds_1": _rule(base["psds_1"], delta("linear", "psds_1_dtc05"))}
    out["hypotheses"] = hypotheses
    out["explained"] = any(item["supported"] for h in hypotheses.values() for item in h.values())
    return out


def _localised_gain(a: Mapping[str, Any], b: Mapping[str, Any], scenario: str) -> dict[str, Any]:
    chosen = float(b["selected"][scenario]["mean_efpr"])
    tpr_a = a["grids"]["linear"]["scenarios"][scenario]["mean_tpr_at"]
    tpr_b = b["grids"]["linear"]["scenarios"][scenario]["mean_tpr_at"]
    low = [str(e) for e in EFPR_POINTS if e <= chosen]
    high = [str(e) for e in EFPR_POINTS if e > chosen]
    worse_high = sum(tpr_b[e] < tpr_a[e] for e in high)
    supported = (all(tpr_b[e] >= tpr_a[e] for e in low) and bool(high)
                 and worse_high >= len(high) / 2)
    return {"chosen_efpr": chosen, "low_efpr": low, "high_efpr": high,
            "tpr_reference": dict(tpr_a), "tpr_candidate": dict(tpr_b), "supported": supported}
