# Diễn đạt lớp gộp (taxonomy.md §7) — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.report_grouped_class_wording`. Lexicon sha256 `6f5634bb7837817c…`. Đơn vị: một caption có lớp gộp trong timeline. `specific` = gọi subclass như sự thật (vi phạm §7).

Giao thức: bản đầu của script (chưa có loại "liệt kê or") đã chạy trên cả dev và test; luật `disjunction` sau đó định bằng ví dụ **dev**, chỉ nới theo hướng có lợi cho caption — số `specific` ở đây là cận dưới của vi phạm.

| Nhánh / mức | Lớp | n | mức lớp | liệt kê "or" | **specific** | họ mơ hồ | không nhắc |
|---|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | `sirens_and_alarms` | 18 | 18 | 0 | 0 | 0 | 0 |
| constrained/e2e | `thunder_fireworks_gunshot` | 39 | 38 | 0 | 0 | 0 | 1 |
| constrained/oracle | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| constrained/oracle | `thunder_fireworks_gunshot` | 4 | 4 | 0 | 0 | 0 | 0 |
| template/e2e | `sirens_and_alarms` | 18 | 18 | 0 | 0 | 0 | 0 |
| template/e2e | `thunder_fireworks_gunshot` | 39 | 39 | 0 | 0 | 0 | 0 |
| template/oracle | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| template/oracle | `thunder_fireworks_gunshot` | 4 | 4 | 0 | 0 | 0 | 0 |
| unconstrained/e2e | `sirens_and_alarms` | 18 | 7 | 0 | 11 | 0 | 0 |
| unconstrained/e2e | `thunder_fireworks_gunshot` | 39 | 1 | 13 | 22 | 0 | 3 |
| unconstrained/oracle | `sirens_and_alarms` | 17 | 11 | 0 | 6 | 0 | 0 |
| unconstrained/oracle | `thunder_fireworks_gunshot` | 4 | 0 | 1 | 3 | 0 | 0 |

## Cụm `specific` đã dùng

- unconstrained/e2e: fireworks (18), thunder (14), sirens (10), gunshots (8), gunshot (3), thunderclaps (1), siren (1), alarm (1)
- unconstrained/oracle: sirens (5), thunder (3), fireworks (3), gunshots (2), alarm (1)
