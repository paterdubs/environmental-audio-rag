# Tầng S — per-class trên toàn dev

> **In-sample dev annotated**, không phải CV/OOF/test: họ/cấu hình chọn bằng CV mean đã lưu, θ/λ refit trên toàn dev. Không quét hoặc chọn lại. F1 onset+offset collar0.2s/20% qua sed_eval; null/— khi không xác định, kể cả lớp có GT nhưng Nsys=0; không tự quy về0. Macro dùng nanmean của sed_eval, bỏ lớp NaN. Δ=ứng viên−baseline, không có kiểm định ý nghĩa thống kê.

| Run | Họ thắng CV | Cấu hình | CV mean | Micro full dev | Macro full dev |
|---|---|---|---:|---:|---:|
| f2 | csebb | tau0.64_rel2 | 0.2383 | 0.2313 | 0.1529 |
| h5tri | theta | global\|25 | 0.2408 | 0.2408 | 0.1855 |

## h5tri so f2

Cảnh báo đổi họ thắng.

| Lớp | F1 baseline | Nsys/Nref baseline | F1 ứng viên | Nsys/Nref ứng viên | ΔF1 | ΔNsys | ΔNref |
|---|---:|---:|---:|---:|---:|---:|---:|
| bells | 0.3556 | 19/26 | 0.4762 | 16/26 | +0.1206 | -3 | +0 |
| birds | 0.0426 | 7/87 | 0.0153 | 44/87 | -0.0273 | +37 | +0 |
| cat_fights_and_moans | 0.1449 | 29/40 | 0.2254 | 31/40 | +0.0804 | +2 | +0 |
| chicken_coop | 0.1429 | 4/24 | 0.1579 | 14/24 | +0.0150 | +10 | +0 |
| cicadas_and_crickets | 0.4205 | 67/109 | 0.3886 | 66/109 | -0.0319 | -1 | +0 |
| crows_seagulls_magpies | 0.1250 | 4/28 | 0.1176 | 6/28 | -0.0074 | +2 | +0 |
| dog_barkings_and_howlings | 0.1053 | 26/88 | 0.0896 | 46/88 | -0.0157 | +20 | +0 |
| glass_breaking | 0.0000 | 6/17 | 0.1481 | 10/17 | +0.1481 | +4 | +0 |
| horn | 0.1538 | 5/21 | 0.0000 | 7/21 | -0.1538 | +2 | +0 |
| jet_aircrafts | 0.0000 | 8/17 | 0.0000 | 16/17 | +0.0000 | +8 | +0 |
| lawn_mower_brush_cutter_olive_shaker | 0.1143 | 7/28 | 0.1739 | 18/28 | +0.0596 | +11 | +0 |
| music | 0.0526 | 12/26 | 0.0455 | 18/26 | -0.0072 | +6 | +0 |
| propeller_aircrafts | 0.1053 | 17/21 | 0.0476 | 21/21 | -0.0576 | +4 | +0 |
| sirens_and_alarms | 0.1818 | 10/23 | 0.3111 | 22/23 | +0.1293 | +12 | +0 |
| thunder_fireworks_gunshot | 0.0000 | 2/18 | 0.0870 | 5/18 | +0.0870 | +3 | +0 |
| train | 0.0000 | 12/24 | 0.0408 | 25/24 | +0.0408 | +13 | +0 |
| vacuum_cleaner_fan_hairdryer | 0.2963 | 24/30 | 0.4906 | 23/30 | +0.1943 | -1 | +0 |
| vehicle_idling | 0.0625 | 4/28 | 0.0444 | 17/28 | -0.0181 | +13 | +0 |
| vehicle_pass_by | 0.0286 | 10/60 | 0.0417 | 36/60 | +0.0131 | +26 | +0 |
| voices | 0.3761 | 40/77 | 0.3857 | 63/77 | +0.0096 | +23 | +0 |
| workshop | 0.5029 | 81/94 | 0.6092 | 80/94 | +0.1063 | -1 | +0 |
