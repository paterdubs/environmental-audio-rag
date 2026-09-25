# Đánh giá SED — `sed_ensemble_BC_clean_20260925T045658Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_BC_clean_20260925T045658Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.1001 |
| Precision | 0.1532 |
| Recall | 0.0743 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0656, 0.1336] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3402 |
| psds_2 | 0.7074 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 21 |
| deletion | 335 |
| fragmentation | 25 |
| insertion | 9 |
| merging | 49 |

Số event tham chiếu: 740 · dự đoán: 359