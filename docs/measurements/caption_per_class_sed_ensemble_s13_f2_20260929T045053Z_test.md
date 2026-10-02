# Lỗi grounding theo lớp — `sed_ensemble_s13_f2_20260929T045053Z` (test)

> Sinh bởi `scripts.report_caption_per_class`. Lexicon `6f5634bb…`. Ô omission: số caption bỏ sót lớp / số caption có lớp đó trong timeline.

## Omission theo lớp — e2e

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 0/5 | 0/5 | 0/5 | 0/5 |
| `birds` | 0/1 | 0/1 | 0/1 | 0/1 |
| `cat_fights_and_moans` | 0/1 | 0/1 | 0/1 | 0/1 |
| `chicken_coop` | 0/5 | 0/5 | 0/5 | 0/5 |
| `cicadas_and_crickets` | 0/10 | 0/10 | 0/10 | 0/10 |
| `crows_seagulls_magpies` | 0/1 | 0/1 | 0/1 | 0/1 |
| `dog_barkings_and_howlings` | 0/6 | 0/6 | 0/6 | 0/6 |
| `glass_breaking` | 0/3 | 0/3 | 0/3 | 0/3 |
| `horn` | 1/6 | 0/6 | 0/6 | 0/6 |
| `jet_aircrafts` | 0/5 | 0/5 | 0/5 | 0/5 |
| `lawn_mower_brush_cutter_olive_shaker` | 0/7 | 0/7 | 0/7 | 0/7 |
| `music` | 0/7 | 0/7 | 0/7 | 0/7 |
| `propeller_aircrafts` | 0/13 | 0/13 | 0/13 | 0/13 |
| `sirens_and_alarms` | 0/13 | 0/13 | 0/13 | 0/13 |
| `thunder_fireworks_gunshot` | 0/4 | 0/4 | 0/4 | 0/4 |
| `train` | 0/14 | 0/14 | 0/14 | 0/14 |
| `vacuum_cleaner_fan_hairdryer` | 1/9 | 0/9 | 0/9 | 0/9 |
| `vehicle_idling` | 0/6 | 0/6 | 0/6 | 1/6 |
| `vehicle_pass_by` | 2/10 | 0/10 | 0/10 | 0/10 |
| `voices` | 0/9 | 0/9 | 0/9 | 1/9 |
| `workshop` | 0/12 | 0/12 | 0/12 | 0/12 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — e2e

- **constrained/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/e2e** — không bằng chứng: music (3), thunder_fireworks_gunshot (1); quá mức: crows_seagulls_magpies (1), lawn_mower_brush_cutter_olive_shaker (7), thunder_fireworks_gunshot (6), vacuum_cleaner_fan_hairdryer (9); ngoài taxonomy: 0

## Omission theo lớp — oracle

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 0/6 | 0/6 | 0/6 | 0/6 |
| `birds` | 3/15 | 0/15 | 0/15 | 2/15 |
| `cat_fights_and_moans` | 0/4 | 0/4 | 0/4 | 0/4 |
| `chicken_coop` | 2/9 | 0/9 | 0/9 | 1/9 |
| `cicadas_and_crickets` | 0/11 | 0/11 | 0/11 | 0/11 |
| `crows_seagulls_magpies` | 1/8 | 0/8 | 0/8 | 1/8 |
| `dog_barkings_and_howlings` | 4/12 | 0/12 | 0/12 | 0/12 |
| `glass_breaking` | 1/4 | 0/4 | 0/4 | 0/4 |
| `horn` | 6/13 | 0/13 | 0/13 | 0/13 |
| `jet_aircrafts` | 4/14 | 0/14 | 0/14 | 1/14 |
| `lawn_mower_brush_cutter_olive_shaker` | 0/11 | 0/11 | 0/11 | 0/11 |
| `music` | 1/9 | 0/9 | 0/9 | 0/9 |
| `propeller_aircrafts` | 2/17 | 0/17 | 0/17 | 1/17 |
| `sirens_and_alarms` | 0/17 | 0/17 | 0/17 | 0/17 |
| `thunder_fireworks_gunshot` | 0/4 | 0/4 | 0/4 | 0/4 |
| `train` | 1/23 | 0/23 | 0/23 | 0/23 |
| `vacuum_cleaner_fan_hairdryer` | 1/7 | 0/7 | 0/7 | 0/7 |
| `vehicle_idling` | 6/16 | 0/16 | 0/16 | 3/16 |
| `vehicle_pass_by` | 9/26 | 0/26 | 0/26 | 1/26 |
| `voices` | 5/27 | 0/27 | 0/27 | 1/27 |
| `workshop` | 3/19 | 0/19 | 0/19 | 0/19 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — oracle

- **constrained/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/oracle** — không bằng chứng: thunder_fireworks_gunshot (3); quá mức: cicadas_and_crickets (2), crows_seagulls_magpies (7), lawn_mower_brush_cutter_olive_shaker (11), sirens_and_alarms (7), thunder_fireworks_gunshot (4), vacuum_cleaner_fan_hairdryer (7); ngoài taxonomy: 0
