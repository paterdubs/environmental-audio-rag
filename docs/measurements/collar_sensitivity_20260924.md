# Chẩn đoán độ nhạy collar — event-based F1

> Sinh bởi `scripts.report_collar_sensitivity`. **Chẩn đoán, không phải số chính thức**: protocol dùng collar 0.2 s; postproc/θ giữ nguyên, không tuning. Collar thời điểm kết thúc giữ `max(collar, 20% độ dài)`.

| Run | collar 0.2 s | collar 0.5 s | collar 1 s | collar 2 s |
|---|---:|---:|---:|---:|
| `sed_polyphonic_20260923T173234Z` | 0.0360 | 0.0680 | 0.0850 | 0.1021 |
| `sed_polyphonic_20260924T054531Z` | 0.0621 | 0.1317 | 0.1851 | 0.2224 |
| `sed_polyphonic_20260924T070927Z` | 0.0651 | 0.1372 | 0.2121 | 0.2495 |
| `sed_polyphonic_20260924T074656Z` | 0.0557 | 0.1179 | 0.1762 | 0.2176 |
| `sed_polyphonic_20260924T033537Z` | 0.0660 | 0.1499 | 0.2118 | 0.2421 |
| `sed_polyphonic_20260924T061000Z` | 0.0472 | 0.1123 | 0.1812 | 0.2017 |
| `sed_polyphonic_20260924T072736Z` | 0.0477 | 0.1077 | 0.1591 | 0.1909 |
| `sed_polyphonic_20260924T080715Z` | 0.0546 | 0.1070 | 0.1685 | 0.2083 |

Precision / recall chi tiết trong file `.json` đi kèm.