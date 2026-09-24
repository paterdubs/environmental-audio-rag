# Ablation A3 — median filter — `sed_polyphonic_20260923T173234Z`

> Sinh bởi `scripts.report_median_filter_ablation ml\runs\sed_polyphonic_20260923T173234Z`. θ và duration prior khác giữ nguyên từ `postproc.json` đã đóng băng; chỉ `median_w` đổi (1 = không lọc). Không sửa artifact chính thức.

⚠️ Nếu run này là nhánh A (scratch, dò đường): hầu hết lớp có F1 gần 0 vì model gần như chưa học được — kết luận từ ablation này **chưa đại diện**, chạy lại trên nhánh B/C (đã pretrain) trước khi kết luận trong báo cáo cuối.

## Tổng hợp (test, đa lớp đồng thời)

| Cấu hình | Event F1 |
|---|---:|
| Có lọc (chính thức) | 0.0220 |
| Không lọc (median_w=1) | 0.0195 |
| Δ (có lọc − không lọc) | +0.0025 |

## Từng lớp, sắp theo d_min_s tăng dần (lớp ngắn/xung trước)

| class_id | d_min_s (train) | F1 có lọc | F1 không lọc | Δ |
|---|---:|---:|---:|---:|
| horn | 0.624 | 0.0000 | 0.0000 | 0.0000 |
| crows_seagulls_magpies | 0.755 | 0.0000 | 0.0000 | 0.0000 |
| dog_barkings_and_howlings | 0.794 | 0.0000 | 0.0000 | 0.0000 |
| voices | 0.820 | 0.0190 | 0.0170 | 0.0019 |
| glass_breaking | 0.888 | 0.0556 | 0.0227 | 0.0328 |
| birds | 1.045 | 0.0000 | 0.0000 | 0.0000 |
| chicken_coop | 1.045 | 0.0000 | 0.0000 | 0.0000 |
| thunder_fireworks_gunshot | 1.112 | 0.0000 | 0.0000 | 0.0000 |
| cicadas_and_crickets | 1.309 | 0.0000 | 0.0000 | 0.0000 |
| cat_fights_and_moans | 1.478 | 0.0000 | 0.0000 | 0.0000 |
| workshop | 1.602 | 0.0588 | 0.0347 | 0.0241 |
| sirens_and_alarms | 2.340 | 0.0301 | 0.0426 | -0.0125 |
| lawn_mower_brush_cutter_olive_shaker | 2.424 | 0.0000 | 0.0000 | 0.0000 |
| bells | 2.478 | 0.1176 | 0.0755 | 0.0422 |
| vehicle_idling | 2.510 | 0.0000 | 0.0000 | 0.0000 |
| vehicle_pass_by | 2.862 | 0.0080 | 0.0000 | 0.0080 |
| music | 3.144 | 0.0690 | 0.0789 | -0.0100 |
| jet_aircrafts | 3.579 | 0.0000 | 0.0000 | 0.0000 |
| vacuum_cleaner_fan_hairdryer | 5.755 | 0.0408 | 0.0312 | 0.0096 |
| train | 9.440 | 0.0482 | 0.0426 | 0.0056 |
| propeller_aircrafts | 12.763 | 0.0000 | 0.0476 | -0.0476 |