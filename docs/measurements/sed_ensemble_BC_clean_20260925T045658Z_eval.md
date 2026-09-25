# Đánh giá SED — `sed_ensemble_BC_clean_20260925T045658Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_BC_clean_20260925T045658Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0696 |
| Precision | 0.0812 |
| Recall | 0.0608 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0471, 0.0969] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3147 |
| psds_2 | 0.7157 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 178 |
| deletion | 223 |
| fragmentation | 11 |
| insertion | 44 |
| merging | 74 |

Số event tham chiếu: 740 · dự đoán: 554