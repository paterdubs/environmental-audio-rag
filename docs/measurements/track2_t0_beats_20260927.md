# Track 2a — cổng T0 bước 3 (BEATs đóng băng), 2026-09-27

Sinh bởi `scripts/measure_beats_t0.py`; chỉ cửa sổ dev, không chạm test.

| Đo | Giá trị |
|---|---|
| Checkpoint SHA-256 | `db13a79ae90a0cfd0f9911a6a1d8cdb89324322bee642dcfe32de022123b8b54` |
| Tensor / tham số encoder | 250 / 90,354,032 |
| GPU | NVIDIA GeForce RTX 3070 Laptop GPU (8192 MB) |
| Đỉnh VRAM forward encoder, batch 8 | 771.3 MB |
| Đỉnh VRAM forward encoder, batch 16 | 1186.6 MB |
| Đỉnh VRAM forward encoder, batch 24 | 1603.9 MB |
| Đỉnh VRAM forward encoder, batch 32 | 2019.7 MB |
| Đỉnh VRAM một bước train head, batch 24 | 1614.5 MB |
| Encoder, giây/cửa sổ (batch 24, fp16) | 0.0111 |
| Ước tính giây/epoch (train 4311 + dev 1462 cửa sổ) | 64 |
| fbank_gpu_vs_cpu_max_abs | 0.000124 |
| embedding_fp16_vs_fp32_max_abs | 0.00271 |
| embedding_fp16_vs_fp32_min_cosine | 1 |

## Head AudioSet-strong của chính checkpoint trên một event dev mỗi lớp

Kiểm đường ống encoder có "nghe" đúng không; không phải metric.

| Lớp DataSED | Recording @ s | Nhãn trong cửa sổ | Top-3 AudioSet |
|---|---|---|---|
| bells | S-0022 @ 0 | bells, birds, vehicle_pass_by | Church bell 0.35; Background noise 0.35; Bell 0.31 |
| birds | S-0009 @ 0 | birds, thunder_fireworks_gunshot | Wind 0.28; Thunderstorm 0.27; Wind noise (microphone) 0.25 |
| cat_fights_and_moans | S-0133 @ 0 | cat_fights_and_moans | Mechanisms 0.58; Background noise 0.40; Caterwaul 0.31 |
| chicken_coop | S-0060 @ 0 | birds, chicken_coop, lawn_mower_brush_cutter_olive_shaker | Wind 0.33; Background noise 0.27; Generic impact sounds 0.26 |
| cicadas_and_crickets | S-0173 @ 0 | cicadas_and_crickets, dog_barkings_and_howlings | Mechanisms 0.43; Bark 0.40; Wind 0.34 |
| crows_seagulls_magpies | S-0012 @ 0 | birds, crows_seagulls_magpies, thunder_fireworks_gunshot | Wind 0.33; Sound effect 0.31; Background noise 0.25 |
| dog_barkings_and_howlings | S-0074 @ 20 | dog_barkings_and_howlings, lawn_mower_brush_cutter_olive_shaker, voices | Female speech, woman speaking 0.39; Mechanisms 0.35; Wind 0.34 |
| glass_breaking | S-0088 @ 0 | glass_breaking | Mechanisms 0.88; Coin (dropping) 0.58; Surface contact 0.56 |
| horn | S-0021 @ 0 | horn, vehicle_pass_by | Wind 0.40; Vehicle horn, car horn, honking, toot 0.24; Generic impact sounds 0.17 |
| jet_aircrafts | S-0009 @ 20 | birds, jet_aircrafts, thunder_fireworks_gunshot | Wind 0.41; Bird vocalization, bird call, bird song 0.29; Chirp, tweet 0.22 |
| lawn_mower_brush_cutter_olive_shaker | S-0060 @ 0 | birds, chicken_coop, lawn_mower_brush_cutter_olive_shaker | Wind 0.33; Background noise 0.27; Generic impact sounds 0.26 |
| music | S-0025 @ 0 | music | Mechanisms 0.51; Music 0.42; Generic impact sounds 0.35 |
| propeller_aircrafts | S-0096 @ 100 | propeller_aircrafts, vehicle_idling, vehicle_pass_by | Wind 0.44; Car passing by 0.18; Motor vehicle (road) 0.11 |
| sirens_and_alarms | S-0033 @ 60 | birds, crows_seagulls_magpies, horn, sirens_and_alarms, train, vehicle_pass_by | Background noise 0.34; Mechanisms 0.19; Wind 0.19 |
| thunder_fireworks_gunshot | S-0009 @ 0 | birds, thunder_fireworks_gunshot | Wind 0.28; Thunderstorm 0.27; Wind noise (microphone) 0.25 |
| train | S-0033 @ 0 | crows_seagulls_magpies, train | Background noise 0.39; Wind 0.33; Motor vehicle (road) 0.26 |
| vacuum_cleaner_fan_hairdryer | S-0061 @ 10 | bells, birds, horn, vacuum_cleaner_fan_hairdryer | Accelerating, revving, vroom 0.32; Background noise 0.24; Bird vocalization, bird call, bird song 0.20 |
| vehicle_idling | S-0021 @ 60 | horn, vehicle_idling, vehicle_pass_by | Wind 0.42; Mechanisms 0.26; Generic impact sounds 0.21 |
| vehicle_pass_by | S-0009 @ 30 | birds, jet_aircrafts, thunder_fireworks_gunshot, vehicle_pass_by | Background noise 0.26; Wind 0.23; Bird vocalization, bird call, bird song 0.21 |
| voices | S-0024 @ 10 | voices | Generic impact sounds 0.46; Mechanisms 0.38; Male speech, man speaking 0.33 |
| workshop | S-0024 @ 30 | voices, workshop | Mechanisms 0.59; Male speech, man speaking 0.24; Background noise 0.22 |
