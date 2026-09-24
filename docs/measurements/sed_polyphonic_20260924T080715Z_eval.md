# Đánh giá SED — `sed_polyphonic_20260924T080715Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T080715Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0506 |
| Precision | 0.0434 |
| Recall | 0.0608 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0357, 0.0674] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2431 |
| psds_2 | 0.6460 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 529 |
| deletion | 158 |
| fragmentation | 9 |
| insertion | 150 |
| merging | 86 |

Số event tham chiếu: 740 · dự đoán: 1038