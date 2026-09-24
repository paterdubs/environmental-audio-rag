# Đánh giá SED — `sed_polyphonic_20260924T080715Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T080715Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0546 |
| Precision | 0.0472 |
| Recall | 0.0649 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0382, 0.0729] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2824 |
| psds_2 | 0.6557 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 555 |
| deletion | 162 |
| fragmentation | 5 |
| insertion | 106 |
| merging | 84 |

Số event tham chiếu: 740 · dự đoán: 1017