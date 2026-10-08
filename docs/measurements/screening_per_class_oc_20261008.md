# Tầng S — per-class trên toàn dev

> **In-sample dev annotated**, không phải CV/OOF/test: họ/cấu hình chọn bằng CV mean đã lưu, θ/λ refit trên toàn dev. Không quét hoặc chọn lại. F1 onset+offset collar0.2s/20% qua sed_eval; null/— khi không xác định, kể cả lớp có GT nhưng Nsys=0; không tự quy về0. Macro dùng nanmean của sed_eval, bỏ lớp NaN. Δ=ứng viên−baseline, không có kiểm định ý nghĩa thống kê.

| Run | Họ thắng CV | Cấu hình | CV mean | Micro full dev | Macro full dev |
|---|---|---|---:|---:|---:|
| t2b | theta | global\|25 | 0.2330 | 0.2268 | 0.1635 |
| oc | theta | global\|25 | 0.2318 | 0.2228 | 0.1741 |

## oc so t2b

Cùng họ thắng.

| Lớp | F1 baseline | Nsys/Nref baseline | F1 ứng viên | Nsys/Nref ứng viên | ΔF1 | ΔNsys | ΔNref |
|---|---:|---:|---:|---:|---:|---:|---:|
| bells | 0.3000 | 14/26 | 0.1622 | 11/26 | -0.1378 | -3 | +0 |
| birds | 0.0183 | 22/87 | 0.0157 | 40/87 | -0.0026 | +18 | +0 |
| cat_fights_and_moans | 0.2353 | 28/40 | 0.2778 | 32/40 | +0.0425 | +4 | +0 |
| chicken_coop | 0.1622 | 13/24 | 0.3158 | 14/24 | +0.1536 | +1 | +0 |
| cicadas_and_crickets | 0.3584 | 64/109 | 0.3034 | 69/109 | -0.0550 | +5 | +0 |
| crows_seagulls_magpies | 0.1176 | 6/28 | 0.1250 | 4/28 | +0.0074 | -2 | +0 |
| dog_barkings_and_howlings | 0.0845 | 54/88 | 0.1606 | 49/88 | +0.0761 | -5 | +0 |
| glass_breaking | 0.3226 | 14/17 | 0.3448 | 12/17 | +0.0222 | -2 | +0 |
| horn | 0.0000 | 7/21 | 0.0000 | 7/21 | +0.0000 | +0 | +0 |
| jet_aircrafts | 0.0000 | 15/17 | 0.0000 | 12/17 | +0.0000 | -3 | +0 |
| lawn_mower_brush_cutter_olive_shaker | 0.1463 | 13/28 | 0.1304 | 18/28 | -0.0159 | +5 | +0 |
| music | 0.0952 | 16/26 | 0.0833 | 22/26 | -0.0119 | +6 | +0 |
| propeller_aircrafts | 0.0000 | 14/21 | 0.0930 | 22/21 | +0.0930 | +8 | +0 |
| sirens_and_alarms | 0.1538 | 16/23 | 0.1224 | 26/23 | -0.0314 | +10 | +0 |
| thunder_fireworks_gunshot | 0.0000 | 8/18 | 0.0769 | 8/18 | +0.0769 | +0 | +0 |
| train | 0.0435 | 22/24 | 0.0000 | 25/24 | -0.0435 | +3 | +0 |
| vacuum_cleaner_fan_hairdryer | 0.3396 | 23/30 | 0.3929 | 26/30 | +0.0532 | +3 | +0 |
| vehicle_idling | 0.0526 | 10/28 | 0.0444 | 17/28 | -0.0082 | +7 | +0 |
| vehicle_pass_by | 0.0000 | 32/60 | 0.0800 | 40/60 | +0.0800 | +8 | +0 |
| voices | 0.3607 | 45/77 | 0.3529 | 59/77 | -0.0077 | +14 | +0 |
| workshop | 0.6437 | 80/94 | 0.5749 | 73/94 | -0.0688 | -7 | +0 |
