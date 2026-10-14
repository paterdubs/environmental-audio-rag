# Đánh giá SED — `sed_ensemble_B0_final_test_20261014T085016Z` (test)

> Sinh bởi `scripts.evaluate_run D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\ml\runs\sed_ensemble_B0_final_test_20261014T085016Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `sebb_cv_selection_annotated.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.1806 |
| Precision (micro) | 0.2841 |
| Recall (micro) | 0.1324 |
| F1 (macro, evaluation_protocol Q2) | 0.1366 |
| Bootstrap 95% CI (theo recording, n=139) | [0.1261, 0.2384] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.3131 |
| psds_2 | 0.7310 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 6 |
| deletion | 344 |
| fragmentation | 11 |
| insertion | 6 |
| merging | 25 |

Số event tham chiếu: 740 · dự đoán: 345

## Chỉ số ứng dụng (báo kèm, không dùng chọn hệ thống)

Event collar 1 s giữ offset percentage_of_length=0.2; khác chẩn đoán XO-2 dùng 0.5. Recall dưới đây dùng collar chuẩn 0.2 s.

| Metric | Micro | Macro |
|---|---:|---:|
| segment_f1_1s | 0.7260 | 0.6596 |
| event_f1_collar_1s | 0.3889 | 0.3185 |

Recall micro (chuẩn): 0.1324.

Số event dự đoán / tham chiếu: 0.46621621621621623.