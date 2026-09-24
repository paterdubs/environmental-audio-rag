# Đánh giá SED — `sed_polyphonic_20260924T033537Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T033537Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0561 |
| Precision | 0.0554 |
| Recall | 0.0568 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0376, 0.0762] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2441 |
| psds_2 | 0.6652 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 296 |
| deletion | 206 |
| fragmentation | 14 |
| insertion | 111 |
| merging | 69 |

Số event tham chiếu: 740 · dự đoán: 758