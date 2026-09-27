# Track 2b — cổng T0 bước 3 (frame_mn10 fine-tune toàn bộ), 2026-09-27

Sinh bởi `scripts/measure_frame_mn_t0.py`; chỉ cửa sổ train/dev, không chạm test.

| Đo | Giá trị |
|---|---|
| Checkpoint SHA-256 | `4a0fe320d5369987b772394c51881fb20a602967e6842f72f3e5c8181065ece7` |
| Tensor / tham số encoder | 308 / 2,971,664 |
| GPU | NVIDIA GeForce RTX 3070 Laptop GPU (8192 MB) |
| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch 8 | 854.5 MB |
| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch 16 | 1627.5 MB |
| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch 24 | 2400.2 MB |
| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch 32 | 3185.0 MB |
| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch 48 | 4705.2 MB |
| Batch chọn | 24 |
| Giây/bước train, gồm đọc đĩa + crop (batch 24) | 0.264 |
| Giây/batch suy luận dev | 0.121 |
| Ước tính giây/epoch (train 4311 + dev 1462 cửa sổ) | 55 |
| embedding_fp16_vs_fp32_max_abs | 0.0378 |
| embedding_fp16_vs_fp32_min_cosine | 1 |

## Head AudioSet-strong của chính checkpoint trên một event dev mỗi lớp

Kiểm đường ống frontend + mạng có "nghe" đúng không; không phải metric.

| Lớp DataSED | Recording @ s | Nhãn trong cửa sổ | Top-3 AudioSet |
|---|---|---|---|
| bells | S-0022 @ 0 | bells, birds, vehicle_pass_by | Bird vocalization, bird call, bird song 0.24; Chirp, tweet 0.20; Background noise 0.18 |
| birds | S-0009 @ 0 | birds, thunder_fireworks_gunshot | Thunderstorm 0.47; Thunder 0.37; Wind 0.33 |
| cat_fights_and_moans | S-0133 @ 0 | cat_fights_and_moans | Mechanisms 0.52; Background noise 0.42; Cat 0.32 |
| chicken_coop | S-0060 @ 0 | birds, chicken_coop, lawn_mower_brush_cutter_olive_shaker | Wind 0.41; Bird vocalization, bird call, bird song 0.33; Crowing, cock-a-doodle-doo 0.31 |
| cicadas_and_crickets | S-0173 @ 0 | cicadas_and_crickets, dog_barkings_and_howlings | Mechanisms 0.54; Bark 0.54; Wind 0.30 |
| crows_seagulls_magpies | S-0012 @ 0 | birds, crows_seagulls_magpies, thunder_fireworks_gunshot | Wind 0.59; Wind noise (microphone) 0.59; Bleat 0.34 |
| dog_barkings_and_howlings | S-0074 @ 20 | dog_barkings_and_howlings, lawn_mower_brush_cutter_olive_shaker, voices | Mechanisms 0.45; Male speech, man speaking 0.41; Female speech, woman speaking 0.35 |
| glass_breaking | S-0088 @ 0 | glass_breaking | Mechanisms 0.90; Surface contact 0.79; Generic impact sounds 0.62 |
| horn | S-0021 @ 0 | horn, vehicle_pass_by | Wind 0.39; Vehicle horn, car horn, honking, toot 0.23; Mechanisms 0.18 |
| jet_aircrafts | S-0009 @ 20 | birds, jet_aircrafts, thunder_fireworks_gunshot | Wind 0.52; Bird vocalization, bird call, bird song 0.36; Chirp, tweet 0.27 |
| lawn_mower_brush_cutter_olive_shaker | S-0060 @ 0 | birds, chicken_coop, lawn_mower_brush_cutter_olive_shaker | Wind 0.41; Bird vocalization, bird call, bird song 0.33; Crowing, cock-a-doodle-doo 0.31 |
| music | S-0025 @ 0 | music | Mechanisms 0.61; Music 0.54; Generic impact sounds 0.39 |
| propeller_aircrafts | S-0096 @ 100 | propeller_aircrafts, vehicle_idling, vehicle_pass_by | Wind 0.37; Aircraft 0.20; Car passing by 0.18 |
| sirens_and_alarms | S-0033 @ 60 | birds, crows_seagulls_magpies, horn, sirens_and_alarms, train, vehicle_pass_by | Wind 0.33; Mechanisms 0.26; Generic impact sounds 0.17 |
| thunder_fireworks_gunshot | S-0009 @ 0 | birds, thunder_fireworks_gunshot | Thunderstorm 0.47; Thunder 0.37; Wind 0.33 |
| train | S-0033 @ 0 | crows_seagulls_magpies, train | Mechanisms 0.43; Background noise 0.32; Motor vehicle (road) 0.21 |
| vacuum_cleaner_fan_hairdryer | S-0061 @ 10 | bells, birds, horn, vacuum_cleaner_fan_hairdryer | Church bell 0.41; Motor vehicle (road) 0.38; Wind 0.35 |
| vehicle_idling | S-0021 @ 60 | horn, vehicle_idling, vehicle_pass_by | Wind 0.42; Mechanisms 0.19; Generic impact sounds 0.15 |
| vehicle_pass_by | S-0009 @ 30 | birds, jet_aircrafts, thunder_fireworks_gunshot, vehicle_pass_by | Wind 0.32; Mechanisms 0.30; Bird vocalization, bird call, bird song 0.29 |
| voices | S-0024 @ 10 | voices | Mechanisms 0.59; Generic impact sounds 0.44; Background noise 0.23 |
| workshop | S-0024 @ 30 | voices, workshop | Mechanisms 0.63; Electric toothbrush 0.48; Male speech, man speaking 0.21 |
