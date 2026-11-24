# RQ3 (test, bộ lọc gold): chế độ backfill so với vector_only và hybrid

> Sinh tự động bởi `scripts.build_final_tables` tại git `6422322`.

| Corpus | vector | hybrid | backfill | backfill − vector | backfill − hybrid | Tỷ lệ thỏa bộ lọc |
|---|---:|---:|---:|---:|---:|---:|
| f2 | 0.526 | 0.415 | 0.575 | +0.049 [+0.023, +0.079] | +0.160 [+0.120, +0.204] | 0.309 |
| B0 | 0.458 | 0.383 | 0.500 | +0.042 [+0.019, +0.069] | +0.116 [+0.082, +0.154] | 0.291 |
| LBR V2 | 0.491 | 0.404 | 0.532 | +0.041 [+0.021, +0.066] | +0.129 [+0.089, +0.172] | 0.286 |
| LBR V3 | 0.630 | 0.670 | 0.727 | +0.097 [+0.070, +0.126] | +0.057 [+0.036, +0.081] | 0.572 |

**Nguồn:** `docs/measurements/retrieval_backfill_test_20261124.json`.
