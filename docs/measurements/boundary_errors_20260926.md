# Phân bố xác suất và sai số biên — dev (PLAN nợ #22)

> Sinh bởi `scripts.report_boundary_errors`. Chỉ dev; hậu xử lý = file đã chọn trên dev của từng run (in-sample). git `550daec`.

## 1. Xác suất trên frame âm / dương (macro theo lớp)

| Hệ thống | âm: trung vị | âm ≥ 0.5 | âm ≥ 0.95 | dương: trung vị | dương ≥ 0.5 | dương ≥ 0.95 |
|---|---:|---:|---:|---:|---:|---:|
| v1 ensemble C (hệ thống ADR-0024) | 0.008 | 0.023 | 0.003 | 0.771 | 0.701 | 0.466 |
| v1 run đơn B 054531Z | 0.004 | 0.027 | 0.008 | 0.728 | 0.657 | 0.510 |
| v2 seed 20260922 (1/3 seed, sơ bộ) | 0.003 | 0.016 | 0.003 | 0.767 | 0.698 | 0.508 |

## 2. Sai số biên có dấu (dự đoán − tham chiếu, giây)

| Hệ thống | Biên | n | trung vị | [q25, q75] | trong ±0.2 s | trễ > 0.2 s | sớm < −0.2 s |
|---|---|---:|---:|---|---:|---:|---:|
| v1 ensemble C (hệ thống ADR-0024) | onset | 529 | +0.00 | [-0.39, +0.51] | 0.302 | 0.365 | 0.333 |
| v1 ensemble C (hệ thống ADR-0024) | offset | 529 | -0.03 | [-0.54, +0.42] | 0.268 | 0.346 | 0.386 |
| v1 run đơn B 054531Z | onset | 563 | -0.09 | [-1.10, +0.35] | 0.261 | 0.316 | 0.423 |
| v1 run đơn B 054531Z | offset | 563 | +0.10 | [-0.40, +0.94] | 0.243 | 0.421 | 0.336 |
| v2 seed 20260922 (1/3 seed, sơ bộ) | onset | 512 | -0.02 | [-0.62, +0.32] | 0.352 | 0.303 | 0.346 |
| v2 seed 20260922 (1/3 seed, sơ bộ) | offset | 512 | +0.00 | [-0.52, +0.53] | 0.332 | 0.338 | 0.330 |

Chi tiết theo lớp trong file `.json` đi kèm.
