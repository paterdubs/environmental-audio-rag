# Event-F1 theo lớp của B0 và LBR V2 trên test annotated (n = 139 bản ghi)

> Sinh tự động bởi `scripts.build_final_tables` tại git `7997cec`.

| Lớp | Sự kiện tham chiếu | B0 F1 | LBR V2 F1 | LBR V2 precision | LBR V2 recall |
|---|---:|---:|---:|---:|---:|
| `bells` | 28 | 0.2500 | 0.4000 | 0.4545 | 0.3571 |
| `birds` | 29 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `cat_fights_and_moans` | 9 | khớp 0/9 | khớp 3/9 | — | — |
| `chicken_coop` | 34 | 0.1176 | 0.2500 | 0.3182 | 0.2059 |
| `cicadas_and_crickets` | 70 | 0.3182 | 0.5588 | 0.5758 | 0.5429 |
| `crows_seagulls_magpies` | 24 | 0.0000 | 0.0588 | 0.1000 | 0.0417 |
| `dog_barkings_and_howlings` | 39 | 0.0741 | 0.1333 | 0.1905 | 0.1026 |
| `glass_breaking` | 31 | 0.1967 | 0.2769 | 0.2647 | 0.2903 |
| `horn` | 30 | 0.0541 | 0.1026 | 0.2222 | 0.0667 |
| `jet_aircrafts` | 15 | 0.0000 | 0.1176 | 0.5000 | 0.0667 |
| `lawn_mower_brush_cutter_olive_shaker` | 35 | 0.0465 | 0.1905 | 0.5714 | 0.1143 |
| `music` | 36 | 0.5161 | 0.5000 | 0.6250 | 0.4167 |
| `propeller_aircrafts` | 26 | 0.0976 | 0.0588 | 0.1250 | 0.0385 |
| `sirens_and_alarms` | 25 | 0.0976 | 0.1111 | 0.1818 | 0.0800 |
| `thunder_fireworks_gunshot` | 32 | 0.0000 | 0.1000 | 0.2500 | 0.0625 |
| `train` | 28 | 0.0526 | 0.1026 | 0.1818 | 0.0714 |
| `vacuum_cleaner_fan_hairdryer` | 17 | 0.3030 | 0.5625 | 0.6000 | 0.5294 |
| `vehicle_idling` | 33 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `vehicle_pass_by` | 70 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `voices` | 60 | 0.1573 | 0.2637 | 0.3871 | 0.2000 |
| `workshop` | 69 | 0.4505 | 0.6992 | 0.7963 | 0.6232 |

**Nguồn:** `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_o_annotated.json`; `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json`; `data/annotations/datased_polyphonic_events.csv`; `data/splits/datased_polyphonic.csv`; `data/manifests/datased_polyphonic_unannotated.csv`.
