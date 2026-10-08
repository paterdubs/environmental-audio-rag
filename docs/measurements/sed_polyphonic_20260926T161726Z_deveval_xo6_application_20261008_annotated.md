# Đánh giá SED — `sed_polyphonic_20260926T161726Z` (dev)

> Sinh bởi `scripts.evaluate_run D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\ml\runs\sed_polyphonic_20260926T161726Z --split dev`. **Dev, in-sample** (hậu xử lý chọn trên chính dev) — chẩn đoán/ablation ADR-0030, không phải số chính thức.

Hậu xử lý: `postproc_cv.json`.

## Event-based F1 (dev)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.2095 |
| Precision (micro) | 0.2637 |
| Recall (micro) | 0.1738 |
| F1 (macro, evaluation_protocol Q2) | 0.1596 |
| Bootstrap 95% CI (theo recording, n=134) | [0.1569, 0.2703] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2731 |
| psds_2 | 0.6109 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 94 |
| deletion | 336 |
| fragmentation | 17 |
| insertion | 12 |
| merging | 50 |

Số event tham chiếu: 886 · dự đoán: 584

## Chỉ số ứng dụng (báo kèm, không dùng chọn hệ thống)

Event collar 1 s giữ offset percentage_of_length=0.2; khác chẩn đoán XO-2 dùng 0.5. Recall dưới đây dùng collar chuẩn 0.2 s.

| Metric | Micro | Macro |
|---|---:|---:|
| segment_f1_1s | 0.7074 | 0.6493 |
| event_f1_collar_1s | 0.3673 | 0.3146 |

Recall micro (chuẩn): 0.1738.

Số event dự đoán / tham chiếu: 0.6591422121896162.