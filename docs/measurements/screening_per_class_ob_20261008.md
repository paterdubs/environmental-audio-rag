# Tầng S — per-class trên toàn dev

> **In-sample dev annotated**, không phải CV/OOF/test: họ/cấu hình chọn bằng CV mean đã lưu, θ/λ refit trên toàn dev. Không quét hoặc chọn lại. F1 onset+offset collar0.2s/20% qua sed_eval; null/— khi không xác định, kể cả lớp có GT nhưng Nsys=0; không tự quy về0. Macro dùng nanmean của sed_eval, bỏ lớp NaN. Δ=ứng viên−baseline, không có kiểm định ý nghĩa thống kê.

| Run | Họ thắng CV | Cấu hình | CV mean | Micro full dev | Macro full dev |
|---|---|---|---:|---:|---:|
| t2b | theta | global\|25 | 0.2330 | 0.2268 | 0.1635 |
| ob | theta | global\|25 | 0.2327 | 0.2255 | 0.1798 |

## ob so t2b

Cùng họ thắng.

| Lớp | F1 baseline | Nsys/Nref baseline | F1 ứng viên | Nsys/Nref ứng viên | ΔF1 | ΔNsys | ΔNref |
|---|---:|---:|---:|---:|---:|---:|---:|
| bells | 0.3000 | 14/26 | 0.3415 | 15/26 | +0.0415 | +1 | +0 |
| birds | 0.0183 | 22/87 | 0.0508 | 31/87 | +0.0325 | +9 | +0 |
| cat_fights_and_moans | 0.2353 | 28/40 | 0.2222 | 32/40 | -0.0131 | +4 | +0 |
| chicken_coop | 0.1622 | 13/24 | 0.1667 | 12/24 | +0.0045 | -1 | +0 |
| cicadas_and_crickets | 0.3584 | 64/109 | 0.3657 | 66/109 | +0.0073 | +2 | +0 |
| crows_seagulls_magpies | 0.1176 | 6/28 | 0.1176 | 6/28 | +0.0000 | +0 | +0 |
| dog_barkings_and_howlings | 0.0845 | 54/88 | 0.0611 | 43/88 | -0.0234 | -11 | +0 |
| glass_breaking | 0.3226 | 14/17 | 0.4000 | 13/17 | +0.0774 | -1 | +0 |
| horn | 0.0000 | 7/21 | 0.0000 | 8/21 | +0.0000 | +1 | +0 |
| jet_aircrafts | 0.0000 | 15/17 | 0.0000 | 16/17 | +0.0000 | +1 | +0 |
| lawn_mower_brush_cutter_olive_shaker | 0.1463 | 13/28 | 0.2727 | 16/28 | +0.1264 | +3 | +0 |
| music | 0.0952 | 16/26 | 0.0455 | 18/26 | -0.0498 | +2 | +0 |
| propeller_aircrafts | 0.0000 | 14/21 | 0.0541 | 16/21 | +0.0541 | +2 | +0 |
| sirens_and_alarms | 0.1538 | 16/23 | 0.0909 | 21/23 | -0.0629 | +5 | +0 |
| thunder_fireworks_gunshot | 0.0000 | 8/18 | 0.2400 | 7/18 | +0.2400 | -1 | +0 |
| train | 0.0435 | 22/24 | 0.0426 | 23/24 | -0.0009 | +1 | +0 |
| vacuum_cleaner_fan_hairdryer | 0.3396 | 23/30 | 0.3019 | 23/30 | -0.0377 | +0 | +0 |
| vehicle_idling | 0.0526 | 10/28 | 0.0889 | 17/28 | +0.0363 | +7 | +0 |
| vehicle_pass_by | 0.0000 | 32/60 | 0.0000 | 35/60 | +0.0000 | +3 | +0 |
| voices | 0.3607 | 45/77 | 0.2923 | 53/77 | -0.0683 | +8 | +0 |
| workshop | 0.6437 | 80/94 | 0.6207 | 80/94 | -0.0230 | +0 | +0 |
