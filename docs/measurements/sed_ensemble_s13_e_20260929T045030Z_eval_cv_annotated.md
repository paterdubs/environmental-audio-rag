# Đánh giá SED — `sed_ensemble_s13_e_20260929T045030Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_e_20260929T045030Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1392 |
| Precision (micro) | 0.2047 |
| Recall (micro) | 0.1054 |
| F1 (macro, evaluation_protocol Q2) | 0.1230 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1038, 0.1768] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3651 |
| psds_2 | 0.7155 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 37 |
| deletion | 263 |
| fragmentation | 5 |
| insertion | 5 |
| merging | 59 |

Số event tham chiếu: 740 · dự đoán: 381