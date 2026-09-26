# Đánh giá SED — `sed_polyphonic_20260925T205837Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260925T205837Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0725 |
| Precision | 0.0822 |
| Recall | 0.0649 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0492, 0.0965] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3010 |
| psds_2 | 0.6292 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 174 |
| deletion | 219 |
| fragmentation | 14 |
| insertion | 50 |
| merging | 71 |

Số event tham chiếu: 740 · dự đoán: 584