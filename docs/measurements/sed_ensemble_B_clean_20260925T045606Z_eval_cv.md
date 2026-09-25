# Đánh giá SED — `sed_ensemble_B_clean_20260925T045606Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_B_clean_20260925T045606Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0969 |
| Precision | 0.1346 |
| Recall | 0.0757 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0651, 0.1298] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3174 |
| psds_2 | 0.6800 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 39 |
| deletion | 313 |
| fragmentation | 25 |
| insertion | 28 |
| merging | 48 |

Số event tham chiếu: 740 · dự đoán: 416