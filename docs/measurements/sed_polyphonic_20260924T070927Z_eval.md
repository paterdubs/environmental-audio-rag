# Đánh giá SED — `sed_polyphonic_20260924T070927Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T070927Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0511 |
| Precision | 0.0509 |
| Recall | 0.0514 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0340, 0.0691] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2499 |
| psds_2 | 0.6408 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 279 |
| deletion | 196 |
| fragmentation | 14 |
| insertion | 109 |
| merging | 68 |

Số event tham chiếu: 740 · dự đoán: 746