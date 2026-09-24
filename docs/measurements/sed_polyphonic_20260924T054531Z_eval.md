# Đánh giá SED — `sed_polyphonic_20260924T054531Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T054531Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0569 |
| Precision | 0.0525 |
| Recall | 0.0622 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0389, 0.0771] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2444 |
| psds_2 | 0.6442 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 391 |
| deletion | 181 |
| fragmentation | 14 |
| insertion | 123 |
| merging | 73 |

Số event tham chiếu: 740 · dự đoán: 877