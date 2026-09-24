# Ablation A3 — median filter — `sed_polyphonic_20260924T015736Z`

> Sinh bởi `scripts.report_median_filter_ablation ml\runs\sed_polyphonic_20260924T015736Z`. θ và duration prior khác giữ nguyên từ `postproc.json` đã đóng băng; chỉ `median_w` đổi (1 = không lọc). Không sửa artifact chính thức.

## Tổng hợp (test, đa lớp đồng thời)

| Cấu hình | Event F1 |
|---|---:|
| Có lọc (chính thức) | 0.0479 |
| Không lọc (median_w=1) | 0.0444 |
| Δ (có lọc − không lọc) | +0.0035 |

## Từng lớp, sắp theo d_min_s tăng dần (lớp ngắn/xung trước)

| class_id | d_min_s (train) | F1 có lọc | F1 không lọc | Δ |
|---|---:|---:|---:|---:|
| horn | 0.624 | 0.0000 | 0.0000 | 0.0000 |
| crows_seagulls_magpies | 0.755 | 0.0000 | 0.0000 | 0.0000 |
| dog_barkings_and_howlings | 0.794 | 0.0952 | 0.0952 | 0.0000 |
| voices | 0.820 | 0.0952 | 0.0952 | 0.0000 |
| glass_breaking | 0.888 | 0.1224 | 0.1224 | 0.0000 |
| birds | 1.045 | 0.0153 | 0.0152 | 0.0001 |
| chicken_coop | 1.045 | 0.0000 | 0.0000 | 0.0000 |
| thunder_fireworks_gunshot | 1.112 | 0.0000 | 0.0000 | 0.0000 |
| cicadas_and_crickets | 1.309 | 0.0000 | 0.0000 | 0.0000 |
| cat_fights_and_moans | 1.478 | 0.1333 | 0.1250 | 0.0083 |
| workshop | 1.602 | 0.1458 | 0.1443 | 0.0015 |
| sirens_and_alarms | 2.340 | 0.0357 | 0.0357 | 0.0000 |
| lawn_mower_brush_cutter_olive_shaker | 2.424 | 0.0385 | 0.0385 | 0.0000 |
| bells | 2.478 | 0.2326 | 0.2326 | 0.0000 |
| vehicle_idling | 2.510 | 0.0000 | 0.0000 | 0.0000 |
| vehicle_pass_by | 2.862 | 0.0000 | 0.0000 | 0.0000 |
| music | 3.144 | 0.1039 | 0.0769 | 0.0270 |
| jet_aircrafts | 3.579 | 0.0357 | 0.0000 | 0.0357 |
| vacuum_cleaner_fan_hairdryer | 5.755 | 0.1143 | 0.1111 | 0.0032 |
| train | 9.440 | 0.0000 | 0.0000 | 0.0000 |
| propeller_aircrafts | 12.763 | 0.0408 | 0.0408 | 0.0000 |