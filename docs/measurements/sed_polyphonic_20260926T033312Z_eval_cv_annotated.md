# Đánh giá SED — `sed_polyphonic_20260926T033312Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T033312Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1275 |
| Precision (micro) | 0.1758 |
| Recall (micro) | 0.1000 |
| F1 (macro, evaluation_protocol Q2) | 0.1211 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0893, 0.1662] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3233 |
| psds_2 | 0.6679 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 48 |
| deletion | 278 |
| fragmentation | 21 |
| insertion | 8 |
| merging | 54 |

Số event tham chiếu: 740 · dự đoán: 421