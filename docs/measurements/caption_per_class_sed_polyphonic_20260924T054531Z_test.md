# Lỗi grounding theo lớp — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.report_caption_per_class`. Lexicon `6f5634bb…`. Ô omission: số caption bỏ sót lớp / số caption có lớp đó trong timeline.

## Omission theo lớp — e2e

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 1/5 | 0/5 | 0/5 | 1/5 |
| `birds` | 17/56 | 0/56 | 0/56 | 4/56 |
| `cat_fights_and_moans` | 2/4 | 0/4 | 0/4 | 0/4 |
| `chicken_coop` | 4/8 | 0/8 | 0/8 | 0/8 |
| `cicadas_and_crickets` | 5/9 | 0/9 | 0/9 | 0/9 |
| `crows_seagulls_magpies` | 5/8 | 0/8 | 0/8 | 4/8 |
| `dog_barkings_and_howlings` | 12/16 | 0/16 | 0/16 | 0/16 |
| `glass_breaking` | 1/4 | 0/4 | 0/4 | 0/4 |
| `horn` | 11/14 | 0/14 | 0/14 | 5/14 |
| `jet_aircrafts` | 22/35 | 0/35 | 0/35 | 1/35 |
| `lawn_mower_brush_cutter_olive_shaker` | 10/24 | 0/24 | 0/24 | 2/24 |
| `music` | 8/21 | 0/21 | 0/21 | 4/21 |
| `propeller_aircrafts` | 7/19 | 0/19 | 0/19 | 3/19 |
| `sirens_and_alarms` | 0/18 | 0/18 | 0/18 | 0/18 |
| `thunder_fireworks_gunshot` | 1/39 | 0/39 | 0/39 | 3/39 |
| `train` | 16/31 | 0/31 | 0/31 | 0/31 |
| `vacuum_cleaner_fan_hairdryer` | 2/7 | 0/7 | 0/7 | 0/7 |
| `vehicle_idling` | 29/35 | 0/35 | 0/35 | 9/35 |
| `vehicle_pass_by` | 43/73 | 0/73 | 0/73 | 7/73 |
| `voices` | 14/38 | 0/38 | 0/38 | 7/38 |
| `workshop` | 1/18 | 0/18 | 0/18 | 1/18 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — e2e

- **constrained/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/e2e** — không bằng chứng: birds (1); quá mức: cicadas_and_crickets (3), crows_seagulls_magpies (4), lawn_mower_brush_cutter_olive_shaker (21), sirens_and_alarms (11), thunder_fireworks_gunshot (35), vacuum_cleaner_fan_hairdryer (6); ngoài taxonomy: 0

## Omission theo lớp — oracle

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 0/6 | 0/6 | 0/6 | 0/6 |
| `birds` | 3/15 | 0/15 | 0/15 | 2/15 |
| `cat_fights_and_moans` | 0/4 | 0/4 | 0/4 | 0/4 |
| `chicken_coop` | 2/9 | 0/9 | 0/9 | 0/9 |
| `cicadas_and_crickets` | 0/11 | 0/11 | 0/11 | 0/11 |
| `crows_seagulls_magpies` | 1/8 | 0/8 | 0/8 | 2/8 |
| `dog_barkings_and_howlings` | 4/12 | 0/12 | 0/12 | 0/12 |
| `glass_breaking` | 1/4 | 0/4 | 0/4 | 0/4 |
| `horn` | 7/13 | 0/13 | 0/13 | 0/13 |
| `jet_aircrafts` | 4/14 | 0/14 | 0/14 | 0/14 |
| `lawn_mower_brush_cutter_olive_shaker` | 0/11 | 0/11 | 0/11 | 0/11 |
| `music` | 2/9 | 0/9 | 0/9 | 0/9 |
| `propeller_aircrafts` | 2/17 | 0/17 | 0/17 | 1/17 |
| `sirens_and_alarms` | 0/17 | 0/17 | 0/17 | 0/17 |
| `thunder_fireworks_gunshot` | 0/4 | 0/4 | 0/4 | 0/4 |
| `train` | 1/23 | 0/23 | 0/23 | 0/23 |
| `vacuum_cleaner_fan_hairdryer` | 1/7 | 0/7 | 0/7 | 0/7 |
| `vehicle_idling` | 6/16 | 0/16 | 0/16 | 0/16 |
| `vehicle_pass_by` | 9/26 | 0/26 | 0/26 | 1/26 |
| `voices` | 5/27 | 0/27 | 0/27 | 1/27 |
| `workshop` | 3/19 | 0/19 | 0/19 | 0/19 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — oracle

- **constrained/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/oracle** — không bằng chứng: music (1), thunder_fireworks_gunshot (5); quá mức: cicadas_and_crickets (1), crows_seagulls_magpies (6), lawn_mower_brush_cutter_olive_shaker (11), sirens_and_alarms (6), thunder_fireworks_gunshot (4), vacuum_cleaner_fan_hairdryer (7); ngoài taxonomy: 0
