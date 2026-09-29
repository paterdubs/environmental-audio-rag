# Đánh giá SED — `sed_polyphonic_20260926T064832Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T064832Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1295 |
| Precision (micro) | 0.1751 |
| Recall (micro) | 0.1027 |
| F1 (macro, evaluation_protocol Q2) | 0.1141 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0915, 0.1715] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3441 |
| psds_2 | 0.6609 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 59 |
| deletion | 279 |
| fragmentation | 12 |
| insertion | 10 |
| merging | 49 |

Số event tham chiếu: 740 · dự đoán: 434