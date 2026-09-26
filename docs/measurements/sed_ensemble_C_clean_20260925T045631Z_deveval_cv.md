# Đánh giá SED — `sed_ensemble_C_clean_20260925T045631Z` (dev)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_C_clean_20260925T045631Z --split dev`. **Dev, in-sample** (hậu xử lý chọn trên chính dev) — chẩn đoán/ablation ADR-0030, không phải số chính thức.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (dev)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1588 |
| Precision (micro) | 0.2133 |
| Recall (micro) | 0.1264 |
| F1 (macro, evaluation_protocol Q2) | 0.1308 |
| Bootstrap 95% CI (theo recording, n=137) | [0.1216, 0.2016] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2806 |
| psds_2 | 0.6372 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 28 |
| deletion | 357 |
| fragmentation | 18 |
| insertion | 18 |
| merging | 47 |

Số event tham chiếu: 886 · dự đoán: 525