"""Chỉ số ứng dụng báo kèm, giữ nguyên metric chọn hệ thống (ADR-0041 §1).

Mọi F1 dùng sed_eval. Lớp không có quyết định positive giữ quy ước NaN của
thư viện; macro là nanmean của các F1 theo lớp, không tự điền điểm 0.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from ml.evaluation.sed_metrics import MissingMetricDependency, _events_for_recording, event_based_f1

EventRows = Mapping[str, Iterable[Mapping[str, Any]]]

# ADR-0046 §2: tiêu chí giao nhau của PSDS-2; §4: hai lớp hiếm ở Việt Nam.
INTERSECTION_CRITERIA = {"dtc_threshold": 0.1, "gtc_threshold": 0.1, "cttc_threshold": 0.3}
VN_EXCLUDED_CLASSES = ("propeller_aircrafts", "crows_seagulls_magpies")
RECALL_FIRST_PRECISION_FLOOR = 0.6


def segment_f1(reference: EventRows, estimate: EventRows, class_ids: Sequence[str],
               resolution: float = 1.0) -> dict:
    """Micro/macro/per-class F1 trên lưới `resolution` giây của sed_eval."""
    try:
        from sed_eval.sound_event import SegmentBasedMetrics
    except ImportError as exc:
        raise MissingMetricDependency(
            "segment F1 requires sed_eval; install requirements-eval.txt") from exc
    metric = SegmentBasedMetrics(event_label_list=list(class_ids),
                                 time_resolution=float(resolution))
    for recording_id in sorted(set(reference) | set(estimate)):
        ref = _events_for_recording(reference, recording_id)
        est = _events_for_recording(estimate, recording_id)
        if ref or est:
            metric.evaluate(reference_event_list=ref, estimated_event_list=est)
    result = metric.results()
    return {"micro": result["overall"]["f_measure"]["f_measure"],
            "macro": result["class_wise_average"]["f_measure"]["f_measure"],
            "per_class": {c: result["class_wise"][c]["f_measure"]["f_measure"]
                          for c in class_ids}}


def event_f1_collar(reference: EventRows, estimate: EventRows, class_ids: Sequence[str],
                    collar: float = 1.0) -> dict:
    """Đổi collar tuyệt đối; giữ offset percentage_of_length=0.2 của protocol."""
    result = event_based_f1(reference, estimate, event_label_list=list(class_ids),
                            t_collar=float(collar))
    return {"micro": result["f_measure"]["f_measure"], "macro": result["macro"]["f_measure"]}


def application_metrics(reference: EventRows, estimate: EventRows, class_ids: Sequence[str],
                        *, recall_micro: float) -> dict:
    """Recall chuẩn và tỉ lệ số event, kèm hai F1 chỉ để mô tả ứng dụng."""
    n_reference = sum(len(rows) for rows in reference.values())
    n_estimate = sum(len(rows) for rows in estimate.values())
    return {"segment_f1_1s": segment_f1(reference, estimate, class_ids),
            "event_f1_collar_1s": event_f1_collar(reference, estimate, class_ids),
            "recall_micro": recall_micro,
            "n_events_estimate_over_reference": n_estimate / n_reference if n_reference else None}


def vn_class_ids(class_ids: Sequence[str]) -> tuple[str, ...]:
    """Tập lớp ứng dụng Việt Nam (ADR-0046 §4): bỏ đúng hai lớp, giữ thứ tự."""
    return tuple(c for c in class_ids if c not in VN_EXCLUDED_CLASSES)


def restrict_classes(events: EventRows, keep: Sequence[str]) -> dict[str, list[dict]]:
    """Lọc nhãn hoặc dự đoán về tập lớp `keep`; giữ nguyên mọi recording."""
    allowed = set(keep)
    return {rid: [dict(e) for e in rows if e.get("class_id", e.get("event_label")) in allowed]
            for rid, rows in events.items()}


def _psds_frame(events: EventRows, recordings: Sequence[str], keep: set[str]) -> pd.DataFrame:
    rows = [{"filename": rid, "onset": float(e.get("onset", e.get("onset_s"))),
             "offset": float(e.get("offset", e.get("offset_s"))),
             "event_label": str(e.get("class_id", e.get("event_label")))}
            for rid in recordings for e in events.get(rid, [])
            if e.get("class_id", e.get("event_label")) in keep]
    return pd.DataFrame(rows, columns=["filename", "onset", "offset", "event_label"])


def intersection_counts(reference: EventRows, estimate: EventRows, class_ids: Sequence[str],
                        durations: Mapping[str, float]) -> dict[str, tuple[int, int, int]]:
    """(TP, FP, số nhãn) mỗi lớp theo DTC/GTC/CTTC của `psds_eval` (ADR-0046 §2).

    TP là số nhãn được phủ (GTC), FP là số dự đoán không đạt DTC, kể cả cross-trigger — đúng
    định nghĩa mà `PSDSEval.compute_macro_f_score` dùng. Dự đoán thuộc lớp không có nhãn nào
    trong tập được đếm là FP. Chỉ xét recording có trong `durations`.
    """
    try:
        from psds_eval import PSDSEval
        from psds_eval.psds import WORLD
    except ImportError as exc:
        raise MissingMetricDependency(
            "intersection F1 requires psds_eval; install requirements-eval.txt") from exc
    recordings = sorted(durations)
    keep = set(class_ids)
    gt = _psds_frame(reference, recordings, keep)
    det = _psds_frame(estimate, recordings, keep)
    n_gt = gt["event_label"].value_counts()
    # Lớp không có nhãn nào trong tập: psds_eval không biết lớp đó, nhưng mọi dự đoán của nó
    # không thể đạt DTC → đếm thẳng là FP thay vì để thư viện bỏ qua.
    unseen = ~det["event_label"].isin(set(gt["event_label"]))
    n_unseen = det.loc[unseen, "event_label"].value_counts()
    result = {c: (0, int(n_unseen.get(c, 0)), int(n_gt.get(c, 0))) for c in class_ids}
    det = det.loc[~unseen]
    if det.empty or gt.empty:
        return {c: (0, int((det["event_label"] == c).sum()) + fp, n)
                for c, (_, fp, n) in result.items()}
    metadata = pd.DataFrame({"filename": recordings,
                             "duration": [float(durations[r]) for r in recordings]})
    evaluator = PSDSEval(ground_truth=gt, metadata=metadata, **INTERSECTION_CRITERIA)
    counts, _, _, _ = evaluator._evaluate_detections(evaluator._init_det_table(det))
    names = sorted(set(evaluator.class_names) - {WORLD})
    for name, tp, fp in zip(names, np.diag(counts)[:-1], counts[:-1, -1], strict=True):
        result[name] = (int(tp), int(fp) + result[name][1], int(n_gt.get(name, 0)))
    return result


def intersection_metrics(counts: Mapping[str, tuple[int, int, int]]) -> dict:
    """Micro P/R/F1 và macro F1 từ bảng đếm của `intersection_counts`.

    `macro_f1`: số nhãn lấy thẳng từ ground truth, nên lớp có nhãn mà không TP nào được 0.
    `macro_f1_psds_eval`: ngữ nghĩa của `PSDSEval.compute_macro_f_score` — thư viện suy số nhãn
    bằng tp / tp_ratio, lớp 0 TP thành NaN và bị bỏ khỏi trung bình (thổi phồng macro). Báo cả
    hai để minh bạch; số chính là `macro_f1` (ADR-0046, Evidence).
    """
    def f1(tp: float, fp: float, n: float) -> float:
        fn = n - tp
        return float(2 * tp / (2 * tp + fn + fp)) if (2 * tp + fn + fp) else float("nan")
    tp, fp, n = (sum(v[i] for v in counts.values()) for i in range(3))
    per_class = {c: {"tp": v[0], "fp": v[1], "n_reference": v[2], "f1": f1(*v)}
                 for c, v in counts.items()}
    return {"micro": {"precision": tp / (tp + fp) if tp + fp else 0.0,
                      "recall": tp / n if n else 0.0, "f1": f1(tp, fp, n)},
            "macro_f1": float(np.nanmean([v["f1"] for v in per_class.values()])),
            "macro_f1_psds_eval": float(np.nanmean(
                [v["f1"] if v["tp"] > 0 else np.nan for v in per_class.values()] or [np.nan])),
            "per_class": per_class, "criteria": dict(INTERSECTION_CRITERIA)}


def recall_first_objective(reference: EventRows, class_ids: Sequence[str],
                           durations: Mapping[str, float],
                           floor: float = RECALL_FIRST_PRECISION_FLOOR
                           ) -> Callable[[EventRows, list[str]], float]:
    """Điểm "ưu tiên phát hiện" (ADR-0046 §3): recall giao nhau nếu precision ≥ sàn.

    Dưới sàn trả `precision − 1` (< 0), nên mọi điểm đạt sàn đều thắng, và khi không điểm nào
    đạt thì điểm có precision cao nhất thắng.
    """
    def score(estimate: EventRows, recordings: list[str]) -> float:
        micro = intersection_metrics(intersection_counts(
            reference, estimate, class_ids, {r: durations[r] for r in recordings}))["micro"]
        return micro["recall"] if micro["precision"] >= floor else micro["precision"] - 1.0
    return score
