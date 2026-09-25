# Đánh giá SED — `sed_ensemble_C_clean_20260925T045631Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_C_clean_20260925T045631Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0941 |
| Precision | 0.1324 |
| Recall | 0.0730 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0624, 0.1277] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3489 |
| psds_2 | 0.6987 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 36 |
| deletion | 293 |
| fragmentation | 23 |
| insertion | 15 |
| merging | 55 |

Số event tham chiếu: 740 · dự đoán: 408