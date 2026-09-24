# Đánh giá SED — `sed_polyphonic_20260924T015736Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T015736Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0616 |
| Precision | 0.0656 |
| Recall | 0.0581 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0380, 0.0909] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2558 |
| psds_2 | 0.6713 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 234 |
| deletion | 161 |
| fragmentation | 15 |
| insertion | 73 |
| merging | 89 |

Số event tham chiếu: 740 · dự đoán: 655