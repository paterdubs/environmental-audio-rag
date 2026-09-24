# Đánh giá SED — `sed_polyphonic_20260924T021958Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T021958Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0518 |
| Precision | 0.0498 |
| Recall | 0.0541 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0353, 0.0703] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2950 |
| psds_2 | 0.6467 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 356 |
| deletion | 175 |
| fragmentation | 11 |
| insertion | 94 |
| merging | 76 |

Số event tham chiếu: 740 · dự đoán: 803