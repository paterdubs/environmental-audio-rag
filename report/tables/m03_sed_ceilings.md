# Chẩn đoán trần và phân rã lỗi SED trên tập dev

> Sinh tự động bởi `scripts.build_midterm_tables` tại git `1eb3012`.

| Đại lượng | Event-F1 (micro) | Chỉ onset | Chỉ offset | Segment-F1 1 s |
|---|---:|---:|---:|---:|
| Trần độ phân giải: mô hình hoàn hảo, khối 0.32 s | 1.0000 | — | — | — |
| Trần độ phân giải: mô hình hoàn hảo, khối 0.64 s | 0.6294 | — | — | — |
| Trần độ phân giải: mô hình hoàn hảo, khối 1.28 s | 0.3032 | — | — | — |
| Trần người: 8 cặp bản ghi trùng chú giải hai lần | 0.5785 | — | — | — |
| Hệ v1 (ensemble C) | 0.1588 | 0.2325 | 0.4975 | 0.6542 |
| Hệ v2 (ensemble 3 seed) | 0.2120 | 0.2708 | 0.4914 | 0.6869 |
| Phân rã v1: khớp / lệch biên / bỏ sót (trên 886 sự kiện) | 112 / 417 / 357 | — | — | — |
| Phân rã v2: khớp / lệch biên / bỏ sót (trên 886 sự kiện) | 148 / 377 / 361 | — | — | — |

**Nguồn:** `docs/measurements/sed_ceilings_20260926.json`; `docs/measurements/sed_ceilings_v2_20260926.json`.
