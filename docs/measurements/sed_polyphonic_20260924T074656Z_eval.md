# Đánh giá SED — `sed_polyphonic_20260924T074656Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T074656Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0557 |
| Precision | 0.0535 |
| Recall | 0.0581 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0369, 0.0763] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3002 |
| psds_2 | 0.6525 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 366 |
| deletion | 186 |
| fragmentation | 10 |
| insertion | 89 |
| merging | 78 |

Số event tham chiếu: 740 · dự đoán: 804