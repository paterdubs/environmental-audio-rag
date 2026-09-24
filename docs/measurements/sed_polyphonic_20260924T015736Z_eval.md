# Đánh giá SED — `sed_polyphonic_20260924T015736Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T015736Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0479 |
| Precision | 0.0460 |
| Recall | 0.0500 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0289, 0.0709] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2132 |
| psds_2 | 0.6690 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 329 |
| deletion | 152 |
| fragmentation | 14 |
| insertion | 120 |
| merging | 90 |

Số event tham chiếu: 740 · dự đoán: 804