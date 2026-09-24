# Ablation A3 — median filter — `sed_polyphonic_20260923T173234Z`

> Sinh bởi `scripts.report_median_filter_ablation ml\runs\sed_polyphonic_20260923T173234Z`. θ và duration prior khác giữ nguyên từ `postproc.json` đã đóng băng; chỉ `median_w` đổi (1 = không lọc). Không sửa artifact chính thức.

⚠️ **11/21 lớp có F1=0** ở cấu hình chính thức — model chưa học đủ để ablation này có tín hiệu đại diện. Chạy lại trên một nhánh mạnh hơn trước khi kết luận trong báo cáo cuối.

## Tổng hợp (test, đa lớp đồng thời)

| Cấu hình | Event F1 |
|---|---:|
| Có lọc (chính thức) | 0.0360 |
| Không lọc (median_w=1) | 0.0297 |
| Δ (có lọc − không lọc) | +0.0063 |

## Từng lớp, sắp theo d_min_s tăng dần (lớp ngắn/xung trước)

| class_id | d_min_s (train) | F1 có lọc | F1 không lọc | Δ |
|---|---:|---:|---:|---:|
| horn | 0.624 | 0.0000 | 0.0000 | 0.0000 |
| crows_seagulls_magpies | 0.755 | 0.0253 | 0.0217 | 0.0036 |
| dog_barkings_and_howlings | 0.794 | 0.0000 | 0.0000 | 0.0000 |
| voices | 0.820 | 0.0481 | 0.0349 | 0.0131 |
| glass_breaking | 0.888 | 0.0580 | 0.0238 | 0.0342 |
| birds | 1.045 | 0.0000 | 0.0000 | 0.0000 |
| chicken_coop | 1.045 | 0.0000 | 0.0000 | 0.0000 |
| thunder_fireworks_gunshot | 1.112 | 0.0000 | 0.0000 | 0.0000 |
| cicadas_and_crickets | 1.309 | 0.0000 | 0.0000 | 0.0000 |
| cat_fights_and_moans | 1.478 | 0.0000 | 0.0000 | 0.0000 |
| workshop | 1.602 | 0.1549 | 0.1486 | 0.0063 |
| sirens_and_alarms | 2.340 | 0.0465 | 0.0584 | -0.0119 |
| lawn_mower_brush_cutter_olive_shaker | 2.424 | 0.0000 | 0.0000 | 0.0000 |
| bells | 2.478 | 0.0308 | 0.0000 | 0.0308 |
| vehicle_idling | 2.510 | 0.0000 | 0.0000 | 0.0000 |
| vehicle_pass_by | 2.862 | 0.0081 | 0.0000 | 0.0081 |
| music | 3.144 | 0.0862 | 0.0795 | 0.0067 |
| jet_aircrafts | 3.579 | 0.0000 | 0.0000 | 0.0000 |
| vacuum_cleaner_fan_hairdryer | 5.755 | 0.0690 | 0.0305 | 0.0384 |
| train | 9.440 | 0.0759 | 0.0667 | 0.0093 |
| propeller_aircrafts | 12.763 | 0.0000 | 0.0000 | 0.0000 |