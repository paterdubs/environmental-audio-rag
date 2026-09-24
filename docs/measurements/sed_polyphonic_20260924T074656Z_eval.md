# Đánh giá SED — `sed_polyphonic_20260924T074656Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T074656Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0497 |
| Precision | 0.0470 |
| Recall | 0.0527 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0323, 0.0689] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2596 |
| psds_2 | 0.6479 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 373 |
| deletion | 189 |
| fragmentation | 10 |
| insertion | 110 |
| merging | 76 |

Số event tham chiếu: 740 · dự đoán: 829