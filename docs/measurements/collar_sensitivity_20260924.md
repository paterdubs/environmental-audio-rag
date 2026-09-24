# Chẩn đoán độ nhạy collar — event-based F1

> Sinh bởi `scripts.report_collar_sensitivity`. **Chẩn đoán, không phải số chính thức**: protocol dùng collar 0.2 s; postproc/θ giữ nguyên, không tuning. Collar thời điểm kết thúc giữ `max(collar, 20% độ dài)`.

| Run | collar 0.2 s | collar 0.5 s | collar 1 s | collar 2 s |
|---|---:|---:|---:|---:|
| `sed_polyphonic_20260923T173234Z` | 0.0220 | 0.0571 | 0.0802 | 0.0972 |
| `sed_polyphonic_20260924T054531Z` | 0.0569 | 0.1150 | 0.1682 | 0.2041 |
| `sed_polyphonic_20260924T070927Z` | 0.0511 | 0.1171 | 0.1817 | 0.2180 |
| `sed_polyphonic_20260924T074656Z` | 0.0497 | 0.1045 | 0.1542 | 0.1899 |
| `sed_polyphonic_20260924T033537Z` | 0.0561 | 0.1335 | 0.1869 | 0.2163 |
| `sed_polyphonic_20260924T061000Z` | 0.0396 | 0.0931 | 0.1489 | 0.1629 |
| `sed_polyphonic_20260924T072736Z` | 0.0514 | 0.1160 | 0.1554 | 0.1805 |
| `sed_polyphonic_20260924T080715Z` | 0.0506 | 0.0979 | 0.1417 | 0.1732 |

Precision / recall chi tiết trong file `.json` đi kèm.