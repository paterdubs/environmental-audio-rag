# Kết quả mô hình phân loại DataSEC trên tập test

> Sinh tự động bởi `scripts.build_midterm_tables` tại git `1eb3012`.

| Chỉ số | Giá trị | Ghi chú |
|---|---:|---|
| Macro-F1 lớp gộp (22 lớp) | 0.8466 | 740 đoạn test |
| Macro-F1 lớp con, mọi nút (28) | 0.6266 | Gồm cả nút có n_test < 10 |
| Macro-F1 lớp con, nút có n_test ≥ 10 (5) | 0.8453 | Con số diễn giải được |
| Tỷ lệ nhất quán cha–con | 0.9526 | 203 đoạn có lớp con |
| ECE trước hiệu chuẩn (T = 1) | 0.033190 | Đầu lớp gộp |
| ECE sau temperature scaling (T = 1.5681, chọn trên dev) | 0.056394 | Tăng, không giảm |

**Nguồn:** `ml/runs/classifier_datasec_20260923T121808Z/metrics.json`; `docs/measurements/ece_datasec_20260923.md`.
