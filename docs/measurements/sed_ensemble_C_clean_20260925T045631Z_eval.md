# Đánh giá SED — `sed_ensemble_C_clean_20260925T045631Z`

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_C_clean_20260925T045631Z`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 | 0.0636 |
| Precision | 0.0701 |
| Recall | 0.0581 |
| Bootstrap 95% CI (theo recording, n=142) | [0.0395, 0.0886] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3166 |
| psds_2 | 0.7053 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 229 |
| deletion | 232 |
| fragmentation | 12 |
| insertion | 58 |
| merging | 66 |

Số event tham chiếu: 740 · dự đoán: 613