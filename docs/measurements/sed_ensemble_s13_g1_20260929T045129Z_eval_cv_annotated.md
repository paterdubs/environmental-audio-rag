# Đánh giá SED — `sed_ensemble_s13_g1_20260929T045129Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_g1_20260929T045129Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1774 |
| Precision (micro) | 0.2447 |
| Recall (micro) | 0.1392 |
| F1 (macro, evaluation_protocol Q2) | 0.1617 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1337, 0.2260] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3724 |
| psds_2 | 0.7659 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 19 |
| deletion | 254 |
| fragmentation | 15 |
| insertion | 2 |
| merging | 50 |

Số event tham chiếu: 740 · dự đoán: 421