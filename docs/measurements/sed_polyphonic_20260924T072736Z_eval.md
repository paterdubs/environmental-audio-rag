# Đánh giá SED — `sed_polyphonic_20260924T072736Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T072736Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0477 |
| Precision | 0.0436 |
| Recall | 0.0527 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0284, 0.0702] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3093 |
| psds_2 | 0.6634 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 435 |
| deletion | 155 |
| fragmentation | 13 |
| insertion | 98 |
| merging | 82 |

Số event tham chiếu: 740 · dự đoán: 894