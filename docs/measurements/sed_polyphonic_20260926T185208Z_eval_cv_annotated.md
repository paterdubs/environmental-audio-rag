# Đánh giá SED — `sed_polyphonic_20260926T185208Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T185208Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1185 |
| Precision (micro) | 0.1550 |
| Recall (micro) | 0.0959 |
| F1 (macro, evaluation_protocol Q2) | 0.1016 |
| Bootstrap 95% CI (theo recording, n=139) | [0.0862, 0.1555] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3186 |
| psds_2 | 0.6957 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 81 |
| deletion | 242 |
| fragmentation | 9 |
| insertion | 16 |
| merging | 61 |

Số event tham chiếu: 740 · dự đoán: 458