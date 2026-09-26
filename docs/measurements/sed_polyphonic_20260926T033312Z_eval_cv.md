# Đánh giá SED — `sed_polyphonic_20260926T033312Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T033312Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1255 |
| Precision (micro) | 0.1686 |
| Recall (micro) | 0.1000 |
| F1 (macro, evaluation_protocol Q2) | 0.1198 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0883, 0.1643] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3225 |
| psds_2 | 0.6657 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 48 |
| deletion | 278 |
| fragmentation | 21 |
| insertion | 26 |
| merging | 54 |

Số event tham chiếu: 740 · dự đoán: 439