# Cặp lớp bị nhầm thật (substitution) — corpus `dev`, 7 run

> Sinh bởi `scripts.report_confusable_pairs`. Substitution a→b: event tham chiếu `a` bị bỏ lỡ và bị chồng bởi một dự đoán sai `b` (không có `b` thật chồng lên) — đa âm không bị tính là nhầm. Đếm theo cặp event, gộp hai chiều. "Run có" = số run có ít nhất một lượt; cặp chỉ ở 1 run là nhiễu seed.

Tổng substitution: 1482 lượt trên 6202 event tham chiếu (cộng qua các run).

| # | Cặp | Tổng | TB/run | Run có | a→b | b→a | Chồng lấp (s) | Trong bảng §8 |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|
| 1 | `cicadas_and_crickets` ↔ `crows_seagulls_magpies` | 46 | 6.6 | 4/7 | 46 | 0 | 117 |  |
| 2 | `cicadas_and_crickets` ↔ `thunder_fireworks_gunshot` | 36 | 5.1 | 5/7 | 36 | 0 | 66 |  |
| 3 | `horn` ↔ `sirens_and_alarms` | 34 | 4.9 | 7/7 | 27 | 7 | 308 | ✓ |
| 4 | `birds` ↔ `cicadas_and_crickets` | 32 | 4.6 | 6/7 | 0 | 32 | 86 | ✓ |
| 5 | `birds` ↔ `train` | 31 | 4.4 | 5/7 | 29 | 2 | 128 |  |
| 6 | `lawn_mower_brush_cutter_olive_shaker` ↔ `workshop` | 29 | 4.1 | 6/7 | 1 | 28 | 258 | ✓ |
| 7 | `cicadas_and_crickets` ↔ `sirens_and_alarms` | 28 | 4.0 | 4/7 | 28 | 0 | 125 |  |
| 8 | `jet_aircrafts` ↔ `vehicle_pass_by` | 28 | 4.0 | 7/7 | 10 | 18 | 351 |  |
| 9 | `birds` ↔ `vehicle_idling` | 27 | 3.9 | 7/7 | 8 | 19 | 166 |  |
| 10 | `jet_aircrafts` ↔ `thunder_fireworks_gunshot` | 23 | 3.3 | 6/7 | 13 | 10 | 133 |  |
| 11 | `birds` ↔ `crows_seagulls_magpies` | 22 | 3.1 | 5/7 | 21 | 1 | 73 | ✓ |
| 12 | `train` ↔ `vehicle_pass_by` | 22 | 3.1 | 7/7 | 10 | 12 | 216 | ✓ |
| 13 | `birds` ↔ `sirens_and_alarms` | 21 | 3.0 | 7/7 | 2 | 19 | 77 |  |
| 14 | `jet_aircrafts` ↔ `music` | 21 | 3.0 | 5/7 | 0 | 21 | 444 |  |
| 15 | `chicken_coop` ↔ `jet_aircrafts` | 20 | 2.9 | 7/7 | 20 | 0 | 40 |  |
| 16 | `crows_seagulls_magpies` ↔ `vehicle_pass_by` | 20 | 2.9 | 5/7 | 13 | 7 | 45 |  |
| 17 | `glass_breaking` ↔ `workshop` | 20 | 2.9 | 7/7 | 20 | 0 | 128 |  |
| 18 | `chicken_coop` ↔ `vehicle_pass_by` | 19 | 2.7 | 7/7 | 19 | 0 | 30 |  |
| 19 | `lawn_mower_brush_cutter_olive_shaker` ↔ `vehicle_pass_by` | 19 | 2.7 | 7/7 | 10 | 9 | 321 |  |
| 20 | `music` ↔ `vehicle_idling` | 19 | 2.7 | 7/7 | 15 | 4 | 245 |  |

## Cặp giả thuyết âm học trong bảng §8

| Cặp | Tổng | Run có | Hạng |
|---|---:|---:|---:|
| `bells` ↔ `sirens_and_alarms` | 13 | 7/7 | 40 |
| `birds` ↔ `chicken_coop` | 4 | 3/7 | 107 |
| `birds` ↔ `cicadas_and_crickets` | 32 | 6/7 | 4 |
| `birds` ↔ `crows_seagulls_magpies` | 22 | 5/7 | 11 |
| `cat_fights_and_moans` ↔ `dog_barkings_and_howlings` | 0 | 0/7 | — |
| `glass_breaking` ↔ `thunder_fireworks_gunshot` | 10 | 3/7 | 58 |
| `horn` ↔ `sirens_and_alarms` | 34 | 7/7 | 3 |
| `jet_aircrafts` ↔ `propeller_aircrafts` | 8 | 6/7 | 74 |
| `lawn_mower_brush_cutter_olive_shaker` ↔ `workshop` | 29 | 6/7 | 6 |
| `music` ↔ `voices` | 10 | 5/7 | 59 |
| `propeller_aircrafts` ↔ `wind_turbine` | 0 | 0/7 | — |
| `train` ↔ `vehicle_pass_by` | 22 | 7/7 | 12 |
| `vacuum_cleaner_fan_hairdryer` ↔ `workshop` | 1 | 1/7 | 153 |
| `vehicle_idling` ↔ `vehicle_pass_by` | 18 | 6/7 | 23 |
| `vehicle_idling` ↔ `workshop` | 13 | 5/7 | 43 |

Runs: `sed_polyphonic_20260924T033537Z`, `sed_polyphonic_20260924T054531Z`, `sed_polyphonic_20260924T061000Z`, `sed_polyphonic_20260924T070927Z`, `sed_polyphonic_20260924T072736Z`, `sed_polyphonic_20260924T074656Z`, `sed_polyphonic_20260924T080715Z`
