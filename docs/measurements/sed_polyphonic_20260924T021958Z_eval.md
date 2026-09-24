# Đánh giá SED — `sed_polyphonic_20260924T021958Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T021958Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0568 |
| Precision | 0.0582 |
| Recall | 0.0554 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0376, 0.0779] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2512 |
| psds_2 | 0.6290 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 281 |
| deletion | 209 |
| fragmentation | 9 |
| insertion | 85 |
| merging | 68 |

Số event tham chiếu: 740 · dự đoán: 704