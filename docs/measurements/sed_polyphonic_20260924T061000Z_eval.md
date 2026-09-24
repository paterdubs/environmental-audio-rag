# Đánh giá SED — `sed_polyphonic_20260924T061000Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T061000Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0396 |
| Precision | 0.0347 |
| Recall | 0.0459 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0224, 0.0570] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2533 |
| psds_2 | 0.6384 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 480 |
| deletion | 164 |
| fragmentation | 10 |
| insertion | 135 |
| merging | 77 |

Số event tham chiếu: 740 · dự đoán: 979