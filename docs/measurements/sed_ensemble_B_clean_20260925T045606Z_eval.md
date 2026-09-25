# Đánh giá SED — `sed_ensemble_B_clean_20260925T045606Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_B_clean_20260925T045606Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0553 |
| Precision | 0.0567 |
| Recall | 0.0541 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0355, 0.0773] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2996 |
| psds_2 | 0.6929 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 288 |
| deletion | 192 |
| fragmentation | 12 |
| insertion | 73 |
| merging | 81 |

Số event tham chiếu: 740 · dự đoán: 706