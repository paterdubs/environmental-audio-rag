# RELATED_WORK.md — Khung nghiên cứu liên quan

> Chưa phải literature review hoàn chỉnh. Mỗi claim cuối cùng cần nguồn chính, DOI/URL và ngày truy cập.

## 1. Environmental sound classification

Nội dung cần tổng hợp:

- Isolated-event classification.
- Transfer learning từ pretrained audio encoders.
- Class imbalance và hierarchical labels.
- DataSEC: mục tiêu, collection, class/subclass và giới hạn provenance.

## 2. Polyphonic sound event detection

- Strong vs weak labels.
- Frame-level và event-level modeling.
- CRNN, Conformer và pretrained audio transformer.
- Threshold calibration, PSDS và event-based metrics.
- DataSED: monophonic/polyphonic annotation policies.

## 3. Cross-dataset transfer

- Domain shift isolated clips → continuous soundscapes.
- Duplicate leakage khi cùng nguồn xuất hiện ở nhiều dataset.
- Fine-tuning, frozen encoder và multi-task learning.
- Hierarchical coarse/subclass prediction.

## 4. Automated audio captioning

- Free-form AAC.
- Hallucination trong captioning.
- Event-conditioned và constrained generation.
- Đánh giá semantic quality so với factual event grounding.

## 5. Audio retrieval và RAG

- Text-to-audio retrieval.
- Retrieval trên metadata/event timeline.
- Hybrid structured + vector search.
- Evidence-bound generation và unsupported claims.

## 6. Khoảng trống dự kiến

Đề tài tập trung vào chuỗi thống nhất:

```text
isolated classification transfer
→ polyphonic temporal detection
→ evidence-grounded caption
→ event-aware RAG retrieval
```

Claim khoảng trống chỉ được chốt sau systematic search và bảng so sánh paper.

## 7. Bảng trích xuất tài liệu

| Paper | Task | Dataset | Labels | Model | Metric | Điểm dùng trong đề tài | Giới hạn |
|---|---|---|---|---|---|---|---|
| TODO | | | | | | | |

