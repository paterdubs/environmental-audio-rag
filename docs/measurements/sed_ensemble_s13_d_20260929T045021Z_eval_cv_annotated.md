# Đánh giá SED — `sed_ensemble_s13_d_20260929T045021Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_d_20260929T045021Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1323 |
| Precision (micro) | 0.1816 |
| Recall (micro) | 0.1041 |
| F1 (macro, evaluation_protocol Q2) | 0.1161 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0976, 0.1695] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3440 |
| psds_2 | 0.7115 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 51 |
| deletion | 243 |
| fragmentation | 8 |
| insertion | 7 |
| merging | 63 |

Số event tham chiếu: 740 · dự đoán: 424