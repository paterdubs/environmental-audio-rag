# Đánh giá SED — `sed_polyphonic_20260926T033312Z` (dev)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_polyphonic_20260926T033312Z --split dev`. **Dev, in-sample** (hậu xử lý chọn trên chính dev) — chẩn đoán/ablation ADR-0030, không phải số chính thức.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (dev)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1947 |
| Precision (micro) | 0.2695 |
| Recall (micro) | 0.1524 |
| F1 (macro, evaluation_protocol Q2) | 0.1354 |
| Bootstrap 95% CI (theo recording, n=137) | [0.1373, 0.2567] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2570 |
| psds_2 | 0.6185 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 36 |
| deletion | 374 |
| fragmentation | 14 |
| insertion | 16 |
| merging | 42 |

Số event tham chiếu: 886 · dự đoán: 501