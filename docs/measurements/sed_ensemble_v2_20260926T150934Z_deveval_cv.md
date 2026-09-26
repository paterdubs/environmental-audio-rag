# Đánh giá SED — `sed_ensemble_v2_20260926T150934Z` (dev)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_v2_20260926T150934Z --split dev`. **Dev, in-sample** (hậu xử lý chọn trên chính dev) — chẩn đoán/ablation ADR-0030, không phải số chính thức.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (dev)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.2120 |
| Precision (micro) | 0.2902 |
| Recall (micro) | 0.1670 |
| F1 (macro, evaluation_protocol Q2) | 0.1494 |
| Bootstrap 95% CI (theo recording, n=137) | [0.1540, 0.2758] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2921 |
| psds_2 | 0.6292 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 37 |
| deletion | 361 |
| fragmentation | 13 |
| insertion | 17 |
| merging | 42 |

Số event tham chiếu: 886 · dự đoán: 510