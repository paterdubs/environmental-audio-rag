# Đánh giá SED — `sed_ensemble_s13_f2_20260929T045053Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_f2_20260929T045053Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `sebb_cv_selection_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1643 |
| Precision (micro) | 0.2881 |
| Recall (micro) | 0.1149 |
| F1 (macro, evaluation_protocol Q2) | 0.1206 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1103, 0.2242] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3164 |
| psds_2 | 0.7253 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 7 |
| deletion | 349 |
| fragmentation | 4 |
| insertion | 1 |
| merging | 34 |

Số event tham chiếu: 740 · dự đoán: 295