# RQ3 (test, bộ lọc gold): hiệu nDCG@10 ghép cặp giữa các chế độ và độ đúng bộ lọc

> Sinh tự động bởi `scripts.build_final_tables` tại git `358c8dd`.

| Corpus | hybrid − vector | hybrid − structured | Độ đúng bộ lọc (vector) | Độ đúng bộ lọc (hybrid) |
|---|---:|---:|---:|---:|
| f2 | -0.111 [-0.166, -0.059] | -0.001 [-0.008, +0.004] | 0.274 | 1.000 |
| B0 | -0.075 [-0.121, -0.028] | -0.008 [-0.016, -0.001] | 0.271 | 1.000 |
| LBR V2 | -0.087 [-0.136, -0.037] | -0.008 [-0.016, +0.000] | 0.273 | 1.000 |
| LBR V3 | +0.040 [+0.004, +0.079] | -0.013 [-0.034, +0.009] | 0.493 | 1.000 |

**Nguồn:** `docs/measurements/rq3_modes_20261123.json`.
