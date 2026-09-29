# Đánh giá SED — `sed_polyphonic_20260926T053024Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T053024Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1401 |
| Precision (micro) | 0.1830 |
| Recall (micro) | 0.1135 |
| F1 (macro, evaluation_protocol Q2) | 0.1310 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1029, 0.1790] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3241 |
| psds_2 | 0.6488 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 83 |
| deletion | 256 |
| fragmentation | 9 |
| insertion | 13 |
| merging | 58 |

Số event tham chiếu: 740 · dự đoán: 459