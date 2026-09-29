# Đánh giá SED — `sed_ensemble_v2_20260926T155630Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_v2_20260926T155630Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1500 |
| Precision (micro) | 0.2113 |
| Recall (micro) | 0.1162 |
| F1 (macro, evaluation_protocol Q2) | 0.1389 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1119, 0.1909] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3458 |
| psds_2 | 0.6767 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 47 |
| deletion | 274 |
| fragmentation | 10 |
| insertion | 9 |
| merging | 54 |

Số event tham chiếu: 740 · dự đoán: 407