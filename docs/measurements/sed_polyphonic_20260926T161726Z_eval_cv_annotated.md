# Đánh giá SED — `sed_polyphonic_20260926T161726Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T161726Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1378 |
| Precision (micro) | 0.1858 |
| Recall (micro) | 0.1095 |
| F1 (macro, evaluation_protocol Q2) | 0.1196 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0999, 0.1769] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3251 |
| psds_2 | 0.6804 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 57 |
| deletion | 243 |
| fragmentation | 12 |
| insertion | 12 |
| merging | 59 |

Số event tham chiếu: 740 · dự đoán: 436