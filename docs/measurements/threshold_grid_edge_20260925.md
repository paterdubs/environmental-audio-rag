# Lưới θ có cắt cụt điểm tối ưu không (dev)

> Sinh bởi `scripts.report_threshold_edge`. Event-F1 trên **toàn dev**, θ global; biên trên của lưới hiện tại = 0.95. Không mở file test.

| Run | g_max percentile | θ=0.90 | θ=0.95 | θ=0.97 | θ=0.98 | θ=0.99 | đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sed_ensemble_B_clean_20260925T045606Z` | 50 | 0.0843 | 0.0944 | 0.0988 | 0.0679 | 0.0509 | 0.97 |
| `sed_ensemble_B_clean_20260925T045606Z` | 25 | 0.1266 | 0.1373 | 0.1364 | 0.1127 | 0.0863 | 0.95 |
| `sed_ensemble_C_clean_20260925T045631Z` | 50 | 0.0799 | 0.1024 | 0.0981 | 0.0900 | 0.0746 | 0.95 |
| `sed_ensemble_C_clean_20260925T045631Z` | 25 | 0.1233 | 0.1588 | 0.1408 | 0.1416 | 0.1051 | 0.95 |
| `sed_ensemble_BC_clean_20260925T045658Z` | 50 | 0.0923 | 0.0973 | 0.1016 | 0.0803 | 0.0515 | 0.97 |
| `sed_ensemble_BC_clean_20260925T045658Z` | 25 | 0.1390 | 0.1395 | 0.1446 | 0.1232 | 0.0797 | 0.97 |
