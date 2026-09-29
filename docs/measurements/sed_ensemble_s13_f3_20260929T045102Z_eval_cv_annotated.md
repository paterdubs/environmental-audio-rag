# Đánh giá SED — `sed_ensemble_s13_f3_20260929T045102Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_f3_20260929T045102Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1544 |
| Precision (micro) | 0.2248 |
| Recall (micro) | 0.1176 |
| F1 (macro, evaluation_protocol Q2) | 0.1387 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1175, 0.1940] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.4264 |
| psds_2 | 0.8065 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 18 |
| deletion | 259 |
| fragmentation | 10 |
| insertion | 2 |
| merging | 51 |

Số event tham chiếu: 740 · dự đoán: 387