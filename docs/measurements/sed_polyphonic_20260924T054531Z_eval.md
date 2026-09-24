# Đánh giá SED — `sed_polyphonic_20260924T054531Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T054531Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0621 |
| Precision | 0.0575 |
| Recall | 0.0676 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0410, 0.0859] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2818 |
| psds_2 | 0.6456 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 410 |
| deletion | 167 |
| fragmentation | 10 |
| insertion | 97 |
| merging | 80 |

Số event tham chiếu: 740 · dự đoán: 870