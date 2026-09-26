# Đánh giá SED — `sed_polyphonic_20260925T213732Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260925T213732Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0614 |
| Precision | 0.0606 |
| Recall | 0.0622 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0412, 0.0827] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2687 |
| psds_2 | 0.6643 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 330 |
| deletion | 189 |
| fragmentation | 11 |
| insertion | 85 |
| merging | 74 |

Số event tham chiếu: 740 · dự đoán: 759