# Đánh giá SED — `sed_ensemble_s13_f1_20260929T045044Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_f1_20260929T045044Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1817 |
| Precision (micro) | 0.2335 |
| Recall (micro) | 0.1486 |
| F1 (macro, evaluation_protocol Q2) | 0.1521 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1363, 0.2284] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.4341 |
| psds_2 | 0.8016 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 20 |
| deletion | 222 |
| fragmentation | 21 |
| insertion | 5 |
| merging | 51 |

Số event tham chiếu: 740 · dự đoán: 471