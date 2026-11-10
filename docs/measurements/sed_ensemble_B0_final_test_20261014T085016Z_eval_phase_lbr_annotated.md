# Đánh giá SED — `sed_ensemble_B0_final_test_20261014T085016Z` (test)

> Sinh bởi `scripts.evaluate_run ml\runs\sed_ensemble_B0_final_test_20261014T085016Z --split test`. Test chạy **một lần**, postproc đã đóng băng trước khi mở test.

Hậu xử lý: `manifest.json`.

## Event-based F1 (test)

| Metric | Giá trị |
|---|---:|
| F1 (micro) | 0.2965 |
| Precision (micro) | 0.4424 |
| Recall (micro) | 0.2230 |
| F1 (macro, evaluation_protocol Q2) | 0.2356 |
| Bootstrap 95% CI (theo recording, n=139) | [0.2293, 0.3603] |

## PSDS

| Scenario | Giá trị |
|---|---:|
| psds_1 | 0.2146 |
| psds_2 | 0.2960 |

## Phân tích lỗi (mô tả, không thay thế event-based F1)

| Loại | Số lượt |
|---|---:|
| confusion | 12 |
| deletion | 361 |
| fragmentation | 6 |
| insertion | 5 |
| merging | 14 |

Số event tham chiếu: 740 · dự đoán: 373

## Chỉ số ứng dụng (báo kèm, không dùng chọn hệ thống)

Event collar 1 s giữ offset percentage_of_length=0.2; khác chẩn đoán XO-2 dùng 0.5. Recall dưới đây dùng collar chuẩn 0.2 s.

| Metric | Micro | Macro |
|---|---:|---:|
| segment_f1_1s | 0.5965 | 0.5684 |
| event_f1_collar_1s | 0.5157 | 0.4496 |

Recall micro (chuẩn): 0.2230.

Số event dự đoán / tham chiếu: 0.504054054054054.

## LBR `sed_lbr_B0_20261109T172809Z` (variant v2)

Ngưỡng đóng băng: {'f1': 0.01, 'recall_first': 0.005}. Điểm `f1` là số chính; các cột từ collar 1 s trở đi là thước ứng dụng ADR-0046 (báo kèm, không dùng để chọn).

### 21 lớp

| Hệ thống | Macro | Micro | Nsys/Nref | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 (cSEBB, λ đóng băng) | 0.1366 | 0.1806 | 345/740 | 0.3889 | 0.7260 | 0.9706 | 0.5351 | 0.6899 |
| LBR — f1 | 0.2356 | 0.2965 | 373/740 | 0.5157 | 0.5965 | 0.9545 | 0.5108 | 0.6655 |
| LBR — recall_first | 0.2320 | 0.2917 | 412/740 | 0.5226 | 0.6652 | 0.9451 | 0.5811 | 0.7197 |

### 19 lớp Việt Nam

| Hệ thống | Macro | Micro | Nsys/Nref | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 (cSEBB, λ đóng băng) | 0.1463 | 0.1892 | 325/690 | 0.4059 | 0.7090 | 0.9713 | 0.5391 | 0.6934 |
| LBR — f1 | 0.2542 | 0.3120 | 355/690 | 0.5263 | 0.6344 | 0.9548 | 0.5203 | 0.6735 |
| LBR — recall_first | 0.2504 | 0.3068 | 392/690 | 0.5342 | 0.6882 | 0.9446 | 0.5928 | 0.7284 |

Δ micro LBR − B0 (thước chính, 21 lớp, ghép cặp theo recording): +0.1159 [+0.0741, +0.1593].

> Run LBR ứng dụng, chấm kèm trong cùng lượt mở test — không phải số chính (ADR-0045 §11).

## LBR `sed_lbr_B0v3_20261110T042337Z` (variant v3)

Ngưỡng đóng băng: {'f1': 0.85, 'recall_first': 0.005}. Điểm `f1` là số chính; các cột từ collar 1 s trở đi là thước ứng dụng ADR-0046 (báo kèm, không dùng để chọn).

### 21 lớp

| Hệ thống | Macro | Micro | Nsys/Nref | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 (cSEBB, λ đóng băng) | 0.1366 | 0.1806 | 345/740 | 0.3889 | 0.7260 | 0.9706 | 0.5351 | 0.6899 |
| LBR — f1 | 0.1955 | 0.2731 | 395/740 | 0.4652 | 0.7752 | 0.9836 | 0.6486 | 0.7818 |
| LBR — recall_first | 0.1754 | 0.2287 | 668/740 | 0.4190 | 0.7821 | 0.7812 | 0.8203 | 0.8003 |

### 19 lớp Việt Nam

| Hệ thống | Macro | Micro | Nsys/Nref | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 (cSEBB, λ đóng băng) | 0.1463 | 0.1892 | 325/690 | 0.4059 | 0.7090 | 0.9713 | 0.5391 | 0.6934 |
| LBR — f1 | 0.2135 | 0.2892 | 375/690 | 0.4789 | 0.7666 | 0.9827 | 0.6594 | 0.7892 |
| LBR — recall_first | 0.1914 | 0.2424 | 630/690 | 0.4258 | 0.7787 | 0.7810 | 0.8319 | 0.8056 |

Δ micro LBR − B0 (thước chính, 21 lớp, ghép cặp theo recording): +0.0925 [+0.0549, +0.1331].