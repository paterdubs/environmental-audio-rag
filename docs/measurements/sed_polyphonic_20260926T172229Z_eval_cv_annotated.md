# Đánh giá SED — `sed_polyphonic_20260926T172229Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T172229Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1320 |
| Precision (micro) | 0.1729 |
| Recall (micro) | 0.1068 |
| F1 (macro, evaluation_protocol Q2) | 0.1228 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0961, 0.1677] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3277 |
| psds_2 | 0.6851 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 61 |
| deletion | 243 |
| fragmentation | 15 |
| insertion | 11 |
| merging | 56 |

Số event tham chiếu: 740 · dự đoán: 457