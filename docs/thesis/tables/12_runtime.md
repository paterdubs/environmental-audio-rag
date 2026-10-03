# Bảng thời gian xử lý đã đo

> Sinh tự động bởi `scripts.build_thesis_tables` tại git `0b2069f`.

| Thành phần | Môi trường | Phép đo | Thời gian (s) | Ghi chú |
|---|---|---|---:|---|
| Frame-MobileNet T0 | GPU train+dev | Giây/epoch ước tính | 54.81 | batch=24 |
| BEATs T0 | GPU train+dev | Giây/epoch ước tính | 63.92 | batch=24 |
| Demo f2 | CPU container | Upload + phân tích recording | 2.012 | S-0016 |
| Demo RAG | CPU container + BGE-M3 | Hybrid query | 0.250 | 1 evidence |

**Nguồn:** `docs/measurements/track2_t0_frame_mn_20260927.json`; `docs/measurements/track2_t0_beats_20260927.json`; `docs/measurements/demo_f2_e2e_20261002.json`.
