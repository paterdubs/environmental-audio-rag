# Đánh giá SED — `sed_polyphonic_20260923T173234Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260923T173234Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0360 |
| Precision | 0.0286 |
| Recall | 0.0486 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0221, 0.0516] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2059 |
| psds_2 | 0.4514 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 834 |
| deletion | 230 |
| fragmentation | 10 |
| insertion | 125 |
| merging | 74 |

Số event tham chiếu: 740 · dự đoán: 1259