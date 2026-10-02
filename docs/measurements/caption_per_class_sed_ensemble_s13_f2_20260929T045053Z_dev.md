# Lỗi grounding theo lớp — `sed_ensemble_s13_f2_20260929T045053Z` (dev)

> Sinh bởi `scripts.report_caption_per_class`. Lexicon `6f5634bb…`. Ô omission: số caption bỏ sót lớp / số caption có lớp đó trong timeline.

## Omission theo lớp — e2e

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 0/4 | 0/4 | 0/4 | 0/4 |
| `birds` | 0/5 | 0/5 | 0/5 | 0/5 |
| `cat_fights_and_moans` | 0/3 | 0/3 | 0/3 | 0/3 |
| `chicken_coop` | 0/3 | 0/3 | 0/3 | 0/3 |
| `cicadas_and_crickets` | 0/8 | 0/8 | 0/8 | 0/8 |
| `crows_seagulls_magpies` | 0/2 | 0/2 | 0/2 | 0/2 |
| `dog_barkings_and_howlings` | 0/7 | 0/7 | 0/7 | 0/7 |
| `glass_breaking` | 0/2 | 0/2 | 0/2 | 0/2 |
| `horn` | 0/3 | 0/3 | 0/3 | 0/3 |
| `jet_aircrafts` | 0/8 | 0/8 | 0/8 | 0/8 |
| `lawn_mower_brush_cutter_olive_shaker` | 0/2 | 0/2 | 0/2 | 0/2 |
| `music` | 0/4 | 0/4 | 0/4 | 0/4 |
| `propeller_aircrafts` | 0/17 | 0/17 | 0/17 | 0/17 |
| `sirens_and_alarms` | 0/10 | 0/10 | 0/10 | 0/10 |
| `thunder_fireworks_gunshot` | 0/2 | 0/2 | 0/2 | 0/2 |
| `train` | 0/12 | 0/12 | 0/12 | 0/12 |
| `vacuum_cleaner_fan_hairdryer` | 1/6 | 0/6 | 0/6 | 0/6 |
| `vehicle_idling` | 0/2 | 0/2 | 0/2 | 0/2 |
| `vehicle_pass_by` | 1/7 | 0/7 | 0/7 | 0/7 |
| `voices` | 1/17 | 0/17 | 0/17 | 0/17 |
| `workshop` | 1/18 | 0/18 | 0/18 | 0/18 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — e2e

- **constrained/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/e2e** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/e2e** — không bằng chứng: music (2), thunder_fireworks_gunshot (2); quá mức: crows_seagulls_magpies (2), lawn_mower_brush_cutter_olive_shaker (2), thunder_fireworks_gunshot (2), vacuum_cleaner_fan_hairdryer (6); ngoài taxonomy: 0

## Omission theo lớp — oracle

| Lớp | constrained | constrained_cover | template | unconstrained |
|---|---:|---:|---:|---:|
| `bells` | 1/7 | 0/7 | 0/7 | 1/7 |
| `birds` | 3/17 | 0/17 | 0/17 | 2/17 |
| `cat_fights_and_moans` | 1/3 | 0/3 | 0/3 | 0/3 |
| `chicken_coop` | 2/7 | 0/7 | 0/7 | 0/7 |
| `cicadas_and_crickets` | 1/11 | 0/11 | 0/11 | 0/11 |
| `crows_seagulls_magpies` | 5/7 | 0/7 | 0/7 | 2/7 |
| `dog_barkings_and_howlings` | 2/11 | 0/11 | 0/11 | 0/11 |
| `glass_breaking` | 0/3 | 0/3 | 0/3 | 0/3 |
| `horn` | 5/12 | 0/12 | 0/12 | 2/12 |
| `jet_aircrafts` | 2/15 | 0/15 | 0/15 | 0/15 |
| `lawn_mower_brush_cutter_olive_shaker` | 2/8 | 0/8 | 0/8 | 2/8 |
| `music` | 0/9 | 0/9 | 0/9 | 0/9 |
| `propeller_aircrafts` | 1/19 | 0/19 | 0/19 | 0/19 |
| `sirens_and_alarms` | 0/17 | 0/17 | 0/17 | 0/17 |
| `thunder_fireworks_gunshot` | 0/4 | 0/4 | 0/4 | 0/4 |
| `train` | 1/22 | 0/22 | 0/22 | 0/22 |
| `vacuum_cleaner_fan_hairdryer` | 1/7 | 0/7 | 0/7 | 1/7 |
| `vehicle_idling` | 7/15 | 0/15 | 0/15 | 2/15 |
| `vehicle_pass_by` | 5/28 | 0/28 | 0/28 | 1/28 |
| `voices` | 8/30 | 0/30 | 0/30 | 2/30 |
| `workshop` | 2/20 | 0/20 | 0/20 | 1/20 |

## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — oracle

- **constrained/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **constrained_cover/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **template/oracle** — không bằng chứng: 0; quá mức: 0; ngoài taxonomy: 0
- **unconstrained/oracle** — không bằng chứng: thunder_fireworks_gunshot (4); quá mức: cicadas_and_crickets (1), crows_seagulls_magpies (5), lawn_mower_brush_cutter_olive_shaker (5), sirens_and_alarms (6), thunder_fireworks_gunshot (4), vacuum_cleaner_fan_hairdryer (5); ngoài taxonomy: 0
