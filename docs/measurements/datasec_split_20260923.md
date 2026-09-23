# Phân bố lớp split DataSEC

Báo cáo sinh tự động từ `data/splits/datasec_classification.csv`; 
không dùng để chọn lại split hoặc tuning trên test.

- Split SHA-256: `e8d3099010ac2937e5bb9c542a29f51fe50712525a7d35d077c0cedec75ec60a`
- Taxonomy SHA-256: `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`
- Số clip: train=3434 · validation=744 · test=740

## 22 lớp coarse

| class_id | train | validation | test | total |
|---|---:|---:|---:|---:|
| `bells` | 46 | 10 | 10 | 66 |
| `birds` | 48 | 10 | 11 | 69 |
| `cat_fights_and_moans` | 34 | 7 | 7 | 48 |
| `chicken_coop` | 41 | 8 | 9 | 58 |
| `cicadas_and_crickets` | 48 | 11 | 11 | 70 |
| `crows_seagulls_magpies` | 66 | 16 | 16 | 98 |
| `dog_barkings_and_howlings` | 47 | 10 | 10 | 67 |
| `glass_breaking` | 54 | 16 | 13 | 83 |
| `horn` | 39 | 9 | 8 | 56 |
| `jet_aircrafts` | 72 | 16 | 15 | 103 |
| `lawn_mower_brush_cutter_olive_shaker` | 68 | 15 | 14 | 97 |
| `music` | 678 | 145 | 145 | 968 |
| `propeller_aircrafts` | 74 | 16 | 16 | 106 |
| `sirens_and_alarms` | 65 | 15 | 15 | 95 |
| `thunder_fireworks_gunshot` | 165 | 35 | 35 | 235 |
| `train` | 45 | 10 | 9 | 64 |
| `vacuum_cleaner_fan_hairdryer` | 66 | 14 | 14 | 94 |
| `vehicle_idling` | 79 | 17 | 16 | 112 |
| `vehicle_pass_by` | 151 | 32 | 33 | 216 |
| `voices` | 1330 | 285 | 285 | 1900 |
| `wind_turbine` | 69 | 15 | 15 | 99 |
| `workshop` | 149 | 32 | 33 | 214 |

## 28 subclass

| class_id | train | validation | test | total |
|---|---:|---:|---:|---:|
| `cicadas` | 34 | 8 | 8 | 50 |
| `crickets` | 14 | 3 | 3 | 20 |
| `crows` | 32 | 7 | 8 | 47 |
| `seagulls` | 21 | 6 | 5 | 32 |
| `magpies` | 13 | 3 | 3 | 19 |
| `lawn_mower` | 15 | 3 | 3 | 21 |
| `brush_cutter` | 39 | 9 | 8 | 56 |
| `olive_shaker` | 14 | 3 | 3 | 20 |
| `airplanes` | 35 | 7 | 8 | 50 |
| `helicopters` | 39 | 9 | 8 | 56 |
| `sirens` | 42 | 9 | 9 | 60 |
| `alarms` | 23 | 6 | 6 | 35 |
| `thunder` | 18 | 4 | 4 | 26 |
| `fireworks` | 48 | 10 | 10 | 68 |
| `gunshot` | 99 | 21 | 21 | 141 |
| `vacuum_cleaner` | 21 | 5 | 4 | 30 |
| `fan` | 22 | 5 | 5 | 32 |
| `hairdryer` | 23 | 4 | 5 | 32 |
| `car_truck_idling` | 57 | 12 | 12 | 81 |
| `motorbike_idling` | 22 | 5 | 4 | 31 |
| `car_pass_by` | 77 | 16 | 17 | 110 |
| `motorbike_pass_by` | 40 | 8 | 9 | 57 |
| `truck_pass_by` | 34 | 8 | 7 | 49 |
| `air_compressor` | 21 | 4 | 5 | 30 |
| `drill` | 31 | 7 | 7 | 45 |
| `grinder` | 25 | 5 | 5 | 35 |
| `jackhammer` | 43 | 9 | 10 | 62 |
| `saw` | 29 | 7 | 6 | 42 |

## Subclass low-support (tổng < 25)

Các số là số tuyệt đối, không báo tỷ lệ vì mẫu dev/test quá nhỏ.

| class_id | train | validation | test | total |
|---|---:|---:|---:|---:|
| `crickets` | 14 | 3 | 3 | 20 |
| `magpies` | 13 | 3 | 3 | 19 |
| `lawn_mower` | 15 | 3 | 3 | 21 |
| `olive_shaker` | 14 | 3 | 3 | 20 |
