# Đánh giá SED — `sed_polyphonic_20260924T031616Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T031616Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0572 |
| Precision | 0.0540 |
| Recall | 0.0608 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0401, 0.0781] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2753 |
| psds_2 | 0.6528 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 343 |
| deletion | 166 |
| fragmentation | 6 |
| insertion | 118 |
| merging | 77 |

Số event tham chiếu: 740 · dự đoán: 834