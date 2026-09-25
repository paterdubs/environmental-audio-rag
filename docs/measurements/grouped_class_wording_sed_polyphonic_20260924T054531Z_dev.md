# Diễn đạt lớp gộp (taxonomy.md §7) — `sed_polyphonic_20260924T054531Z` (dev)

> Sinh bởi `scripts.report_grouped_class_wording`. Lexicon sha256 `6f5634bb7837817c…`. Đơn vị: một caption có lớp gộp trong timeline. `specific` = gọi subclass như sự thật (vi phạm §7).

Giao thức: bản đầu của script (chưa có loại "liệt kê or") đã chạy trên cả dev và test; luật `disjunction` sau đó định bằng ví dụ **dev**, chỉ nới theo hướng có lợi cho caption — số `specific` ở đây là cận dưới của vi phạm.

| Nhánh / mức | Lớp | n | mức lớp | liệt kê "or" | **specific** | họ mơ hồ | không nhắc |
|---|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| constrained/e2e | `thunder_fireworks_gunshot` | 50 | 49 | 0 | 0 | 0 | 1 |
| constrained/oracle | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| constrained/oracle | `thunder_fireworks_gunshot` | 4 | 4 | 0 | 0 | 0 | 0 |
| template/e2e | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| template/e2e | `thunder_fireworks_gunshot` | 50 | 50 | 0 | 0 | 0 | 0 |
| template/oracle | `sirens_and_alarms` | 17 | 17 | 0 | 0 | 0 | 0 |
| template/oracle | `thunder_fireworks_gunshot` | 4 | 4 | 0 | 0 | 0 | 0 |
| unconstrained/e2e | `sirens_and_alarms` | 17 | 5 | 0 | 12 | 0 | 0 |
| unconstrained/e2e | `thunder_fireworks_gunshot` | 50 | 0 | 21 | 27 | 0 | 2 |
| unconstrained/oracle | `sirens_and_alarms` | 17 | 11 | 0 | 6 | 0 | 0 |
| unconstrained/oracle | `thunder_fireworks_gunshot` | 4 | 0 | 0 | 4 | 0 | 0 |

## Cụm `specific` đã dùng

- unconstrained/e2e: thunder (17), fireworks (14), sirens (12), gunshot (7), gunshots (6), thunderclaps (3)
- unconstrained/oracle: sirens (5), thunder (4), fireworks (3), gunshots (2), siren (1)
