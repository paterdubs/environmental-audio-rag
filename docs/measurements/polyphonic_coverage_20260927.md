# Độ phủ ground truth polyphonic DataSED và đối chiếu bài báo — 2026-09-27

Sinh bởi `scripts/report_polyphonic_coverage.py`. Chỉ đọc; không mở test, không đổi split hay annotation.

## 1. Độ phủ ground truth gốc

- `Polyphonic_sound_detection.csv` phủ **703** recording; `Monophonic_sound_detection.csv` phủ 717; archive có 717 WAV.
- Recording có trong split polyphonic nhưng **không có dòng nào** trong ground truth polyphonic: 14 (S-0704…S-0717).
- Tập này trùng đúng tập recording có nhãn monophonic `wind_turbine`: True.

| Split | Recording | Giờ | Nhãn monophonic thuộc 21 lớp polyphonic |
|---|---|---:|---:|
| train | S-0704, S-0705, S-0707, S-0709, S-0710, S-0712, S-0713, S-0715 | 0.989 | 49 |
| validation | S-0706, S-0708, S-0714 | 0.392 | 30 |
| test | S-0711, S-0716, S-0717 | 0.280 | 23 |

Trong benchmark hiện tại, các recording này được coi là **không có sự kiện nào**: dự đoán ở đó tính là FP, sự kiện thật không tính là FN, và khi train chúng là mẫu âm.

## 2. Bài báo và archive

| | Bài báo (văn bản) | Archive đo được |
|---|---:|---:|
| files | 712 | 717 |
| last_id | S-0712 | S-0717 |
| min_s | 2.29 | 2.29 |
| max_s | 285.0 | 818.32 |
| mean_s | 87.18 | 93.81 |
| total_h | 17.02 | 18.68 |
| polyphonic_labels | 4034 | 4034 |
| monophonic_labels | 4309 | 4309 |

Bảng 3 của bài (monophonic): tổng 4323 nhãn, trong khi văn bản bài ghi 4309.

| Lớp (tên trong bài) | Nhãn bài | Nhãn archive | Tổng s bài | Tổng s archive |
|---|---:|---:|---:|---:|
| Bells | 123 | 123 | 1377.7 | 1377.7 |
| Birds | 225 | 225 | 1590.7 | 1590.7 |
| Cat fights and moans | 138 | 138 | 636.2 | 636.2 |
| Chicken coop | 169 | 169 | 559.4 | 559.4 |
| Cicadas and crickets | 422 | 421 | 2695.7 | 2695.4 |
| Crows seagulls and magpies | 166 | 166 | 802.2 | 802.2 |
| Dog barkings and howlings | 243 | 240 | 1214.1 | 1212.9 |
| Glass breaking | 121 | 121 | 395.1 | 395.0 |
| Horn | 135 | 133 | 353.5 | 352.9 |
| Jet aircrafts | 100 | 99 | 2709.6 | 2709.5 |
| Lawn mower brush cutter and olive shaker | 140 | 140 | 3182.8 | 3182.8 |
| Music | 160 | 160 | 3433.3 | 3433.3 |
| Propeller aircrafts | 218 | 217 | 5219.6 | 5219.1 |
| Sirens and alarms | 148 | 148 | 2790.9 | 2790.8 |
| Thunder fireworks and gunshot | 145 | 145 | 1475.6 | 1475.6 |
| Train | 161 | 156 | 4801.5 | 4800.5 |
| Vacuum cleaner fan and hairdryer | 136 | 136 | 2369.0 | 2369.0 |
| Vehicle idling | 159 | 159 | 2511.9 | 2511.9 |
| Vehicle pass-by | 318 | 318 | 3283.2 | 3283.1 |
| Voices | 344 | 343 | 2011.1 | 2011.0 |
| Wind turbine | 113 | 113 | 3833.8 | 3833.8 |
| Workshop | 439 | 439 | 4818.4 | 4818.3 |

## 3. Cỡ ảnh hưởng trên dev (in-sample, hậu xử lý `postproc_cv.json`)

| Ứng viên | Event-F1 micro dev, 137 recording | Bỏ recording thiếu GT | Dự đoán rơi vào recording thiếu GT / tổng |
|---|---:|---:|---:|
| (c) v2 ×3 | 0.2120 | 0.2139 | 12 / 510 |
| (d) C-v2 ×3 | 0.2241 | 0.2262 | 13 / 533 |
| (f1) T2a ×3 | 0.2171 | 0.2194 | 15 / 533 |
