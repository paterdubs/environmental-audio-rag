# Đánh giá SED — `sed_ensemble_C_clean_20260925T045631Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_C_clean_20260925T045631Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.0945 |
| Precision (micro) | 0.1340 |
| Recall (micro) | 0.0730 |
| F1 (macro, evaluation_protocol Q2) | 0.0924 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0639, 0.1258] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3486 |
| psds_2 | 0.6991 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 36 |
| deletion | 293 |
| fragmentation | 23 |
| insertion | 10 |
| merging | 55 |

Số event tham chiếu: 740 · dự đoán: 403