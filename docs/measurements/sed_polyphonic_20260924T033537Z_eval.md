# Đánh giá SED — `sed_polyphonic_20260924T033537Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T033537Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0660 |
| Precision | 0.0672 |
| Recall | 0.0649 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0464, 0.0878] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2779 |
| psds_2 | 0.6711 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 282 |
| deletion | 209 |
| fragmentation | 13 |
| insertion | 83 |
| merging | 69 |

Số event tham chiếu: 740 · dự đoán: 714