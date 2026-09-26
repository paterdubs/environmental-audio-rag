# Đánh giá SED — `sed_polyphonic_20260925T211704Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260925T211704Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0548 |
| Precision | 0.0508 |
| Recall | 0.0595 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0363, 0.0733] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2722 |
| psds_2 | 0.6656 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 448 |
| deletion | 193 |
| fragmentation | 10 |
| insertion | 80 |
| merging | 73 |

Số event tham chiếu: 740 · dự đoán: 866