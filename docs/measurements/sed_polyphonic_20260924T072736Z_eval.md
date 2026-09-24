# Đánh giá SED — `sed_polyphonic_20260924T072736Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T072736Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0514 |
| Precision | 0.0461 |
| Recall | 0.0581 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0321, 0.0729] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2758 |
| psds_2 | 0.6491 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 432 |
| deletion | 161 |
| fragmentation | 12 |
| insertion | 130 |
| merging | 77 |

Số event tham chiếu: 740 · dự đoán: 933