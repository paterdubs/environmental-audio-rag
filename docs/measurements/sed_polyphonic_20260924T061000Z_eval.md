# Đánh giá SED — `sed_polyphonic_20260924T061000Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T061000Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0472 |
| Precision | 0.0447 |
| Recall | 0.0500 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0301, 0.0671] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2873 |
| psds_2 | 0.6462 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 360 |
| deletion | 167 |
| fragmentation | 13 |
| insertion | 100 |
| merging | 76 |

Số event tham chiếu: 740 · dự đoán: 827