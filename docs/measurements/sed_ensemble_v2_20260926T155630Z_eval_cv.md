# Đánh giá SED — `sed_ensemble_v2_20260926T155630Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_v2_20260926T155630Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1476 |
| Precision (micro) | 0.2024 |
| Recall (micro) | 0.1162 |
| F1 (macro, evaluation_protocol Q2) | 0.1369 |
| Bootstrap 95% CI (theo recording, n=142) | [0.1088, 0.1866] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3447 |
| psds_2 | 0.6744 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 47 |
| deletion | 274 |
| fragmentation | 10 |
| insertion | 27 |
| merging | 54 |

Số event tham chiếu: 740 · dự đoán: 425