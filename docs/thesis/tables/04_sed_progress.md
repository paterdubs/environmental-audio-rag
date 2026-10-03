# Bảng tiến triển SED v1 → v2 → S13 trên test annotated

> Sinh tự động bởi `scripts.build_thesis_tables` tại git `0b2069f`.

| Hệ thống | Hậu xử lý | Macro-F1 | Micro-F1 | 95% CI micro | PSDS-1 | PSDS-2 | n |
|---|---|---:|---:|---|---:|---:|---:|
| v1 — ensemble C | theta | 0.0924 | 0.0945 | [0.0639, 0.1258] | 0.3486 | 0.6991 | 139 |
| v2 — ensemble 3 seed | theta | 0.1389 | 0.1500 | [0.1119, 0.1909] | 0.3458 | 0.6767 | 139 |
| S13 — T2b×3 + cSEBB (khóa) | csebb | 0.1206 | 0.1643 | [0.1103, 0.2242] | 0.3164 | 0.7253 | 139 |

**Nguồn:** `docs/measurements/s13_test_20261018.json`.
