"""Chỉ số ứng dụng báo kèm, giữ nguyên metric chọn hệ thống (ADR-0041 §1).

Mọi F1 dùng sed_eval. Lớp không có quyết định positive giữ quy ước NaN của
thư viện; macro là nanmean của các F1 theo lớp, không tự điền điểm 0.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from ml.evaluation.sed_metrics import MissingMetricDependency, _events_for_recording, event_based_f1

EventRows = Mapping[str, Iterable[Mapping[str, Any]]]


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
