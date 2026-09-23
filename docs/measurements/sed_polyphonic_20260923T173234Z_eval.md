# Đánh giá SED — `sed_polyphonic_20260923T173234Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260923T173234Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0220 |
| Precision | 0.0175 |
| Recall | 0.0297 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0127, 0.0325] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.1820 |
| psds_2 | 0.4475 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 798 |
| deletion | 235 |
| fragmentation | 11 |
| insertion | 155 |
| merging | 72 |

Số event tham chiếu: 740 · dự đoán: 1256