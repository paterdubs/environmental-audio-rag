# RQ1 — so sánh ba nhánh SED (C − B, C − A)

> Sinh bởi `scripts.report_rq1_delta ml\runs\sed_polyphonic_20260923T173234Z ml\runs\sed_polyphonic_20260924T054531Z ml\runs\sed_polyphonic_20260924T061000Z`. Không tính lại metric, chỉ đọc `evaluation.json` đã có.

⚠️ **Số thăm dò, chưa khoá chính thức** — 1 seed mỗi nhánh, chưa qua D2-style seed-reproducibility check. Không trích dẫn như kết luận cuối của RQ1.

## Ba nhánh

| | Nhánh A (scratch) | Nhánh B (AudioSet) | Nhánh C (AudioSet→DataSEC) |
|---|---:|---:|---:|
| run_id | `sed_polyphonic_20260923T173234Z` | `sed_polyphonic_20260924T054531Z` | `sed_polyphonic_20260924T061000Z` |
| event-based F1 | 0.0220 | 0.0569 | 0.0396 |
| PSDS-1 | 0.1820 | 0.2444 | 0.2533 |
| PSDS-2 | 0.4475 | 0.6442 | 0.6384 |
| git.dirty | False | False | False |

## Δ = C − B — **câu trả lời RQ1** (đóng góp riêng của pretraining DataSEC)

| Metric | Δ |
|---|---:|
| event-based F1 | -0.0173 |
| PSDS-1 | +0.0089 |
| PSDS-2 | -0.0058 |

## Δ = C − A — tổng lợi ích pretraining (KHÔNG phải RQ1, ADR-0002)

| Metric | Δ |
|---|---:|
| event-based F1 | +0.0175 |
| PSDS-1 | +0.0713 |
| PSDS-2 | +0.1909 |