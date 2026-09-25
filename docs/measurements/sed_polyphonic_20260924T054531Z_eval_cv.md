# Đánh giá SED — `sed_polyphonic_20260924T054531Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260924T054531Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.1048 |
| Precision | 0.1174 |
| Recall | 0.0946 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0772, 0.1380] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2934 |
| psds_2 | 0.6312 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 149 |
| deletion | 247 |
| fragmentation | 24 |
| insertion | 47 |
| merging | 56 |

Số event tham chiếu: 740 · dự đoán: 596