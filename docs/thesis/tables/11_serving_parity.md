# Bảng parity giữa pipeline nghiên cứu và phục vụ

> Sinh tự động bởi `scripts.build_thesis_tables` tại git `0b2069f`.

| Thiết bị | Torch | Recording trùng event | Tổng recording | Event chuẩn | Event phục vụ | Event trùng | Trong collar | Δp lớn nhất |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Host CUDA | 2.11.0+cu128 | 142 | 142 | 299 | 299 | 299 | 299 | 0.005014 |
| Container CPU | 2.14.0+cpu | 132 | 142 | 299 | 300 | 290 | 294 | 0.023931 |

**Nguồn:** `docs/measurements/inference_parity_20260929.json`; `docs/measurements/inference_parity_cpu_20261002.json`.
