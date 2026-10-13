# Phân bố xác suất và sai số biên — dev (PLAN nợ #22)

> Sinh bởi `scripts.report_boundary_errors`. Chỉ dev; hậu xử lý = file đã chọn trên dev của từng run (in-sample). git `f0b088c`.

## 1. Xác suất trên frame âm / dương (macro theo lớp)

| Hệ thống | âm: trung vị | âm ≥ 0.5 | âm ≥ 0.95 | dương: trung vị | dương ≥ 0.5 | dương ≥ 0.95 |
|---|---:|---:|---:|---:|---:|---:|
| t2b | 0.005 | 0.019 | 0.002 | 0.805 | 0.746 | 0.528 |
| oc_gru | 0.005 | 0.015 | 0.002 | 0.784 | 0.747 | 0.531 |
| do4 | 0.011 | 0.025 | 0.003 | 0.811 | 0.764 | 0.550 |
| oc_tf_kd | 0.006 | 0.015 | 0.003 | 0.798 | 0.748 | 0.546 |

## 2. Sai số biên có dấu (dự đoán − tham chiếu, giây)

| Hệ thống | Biên | n | trung vị | [q25, q75] | trong ±0.2 s | trễ > 0.2 s | sớm < −0.2 s |
|---|---|---:|---:|---|---:|---:|---:|
| t2b | onset | 539 | +0.04 | [-0.36, +0.35] | 0.371 | 0.347 | 0.282 |
| t2b | offset | 539 | -0.02 | [-0.45, +0.39] | 0.354 | 0.314 | 0.332 |
| oc_gru | onset | 603 | -0.01 | [-0.50, +0.29] | 0.370 | 0.299 | 0.332 |
| oc_gru | offset | 603 | +0.01 | [-0.39, +0.53] | 0.328 | 0.348 | 0.323 |
| do4 | onset | 625 | -0.08 | [-2.87, +0.14] | 0.334 | 0.219 | 0.446 |
| do4 | offset | 625 | +0.12 | [-0.14, +2.23] | 0.333 | 0.451 | 0.216 |
| oc_tf_kd | onset | 578 | +0.04 | [-0.20, +0.32] | 0.413 | 0.339 | 0.247 |
| oc_tf_kd | offset | 578 | -0.07 | [-0.44, +0.27] | 0.353 | 0.285 | 0.362 |

Chi tiết theo lớp trong file `.json` đi kèm.
