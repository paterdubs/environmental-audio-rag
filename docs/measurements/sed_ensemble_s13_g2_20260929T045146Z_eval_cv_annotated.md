# Đánh giá SED — `sed_ensemble_s13_g2_20260929T045146Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_s13_g2_20260929T045146Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `sebb_cv_selection_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1722 |
| Precision (micro) | 0.2735 |
| Recall (micro) | 0.1257 |
| F1 (macro, evaluation_protocol Q2) | 0.1421 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1232, 0.2218] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3338 |
| psds_2 | 0.7349 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 5 |
| deletion | 303 |
| fragmentation | 5 |
| insertion | 5 |
| merging | 33 |

Số event tham chiếu: 740 · dự đoán: 340