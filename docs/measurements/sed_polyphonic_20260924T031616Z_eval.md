# Đánh giá SED — `sed_polyphonic_20260924T031616Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T031616Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0468 |
| Precision | 0.0422 |
| Recall | 0.0527 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0325, 0.0644] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2419 |
| psds_2 | 0.6408 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 395 |
| deletion | 167 |
| fragmentation | 6 |
| insertion | 161 |
| merging | 76 |

Số event tham chiếu: 740 · dự đoán: 925