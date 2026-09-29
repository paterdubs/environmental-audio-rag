# Đánh giá SED — `sed_ensemble_s13_f4_20260929T045115Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_f4_20260929T045115Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1543 |
| Precision (micro) | 0.2195 |
| Recall (micro) | 0.1189 |
| F1 (macro, evaluation_protocol Q2) | 0.1368 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1163, 0.1912] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3988 |
| psds_2 | 0.7688 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 25 |
| deletion | 233 |
| fragmentation | 10 |
| insertion | 3 |
| merging | 57 |

Số event tham chiếu: 740 · dự đoán: 401