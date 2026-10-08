# DataSEC v4 — pool O-F và hồ sơ năng lượng

> Chỉ train ∩ v4 − exclusion, giữ 21 lớp polyphonic. Không tạo nhãn mạnh. RMS 20 ms không chồng lấn, mono 32 kHz; khung cuối dùng số mẫu thật. Hoạt động khi RMS > median(RMS) × 10^(6/20), tương đương median + 6 dB. Im lặng không có vùng hoạt động; tie vùng dài nhất lấy vùng đầu.

**Giới hạn:** ngưỡng tương đối có thể cho 0 khung ở âm thanh liên tục; tỷ lệ hoạt động thường ≤ 0,5 theo định nghĩa median. Đây là độ nổi bật năng lượng trong clip, không phải độ phủ của sự kiện hoặc độ tin cậy nhãn.

Pool: **2846 clip**, **10.7633 giờ**. SHA-256 CSV: `dd22705aaa7d5cfda1d5823b61bb7971d70f818b45625459e300726c36aaf908`.

| Lớp | Clip | Giờ | Median clip (s) | Median tỷ lệ RMS hoạt động | Median vùng dài nhất (s) | Clip không hoạt động | Event train ≤3s |
|---|---:|---:|---:|---:|---:|---:|:---:|
| `bells` | 46 | 0.3652 | 29.4933 | 0.1376 | 0.2800 | 2 | — |
| `birds` | 48 | 0.1808 | 5.0000 | 0.2342 | 0.1900 | 2 | — |
| `cat_fights_and_moans` | 34 | 0.2099 | 18.7290 | 0.2121 | 0.5500 | 0 | có |
| `chicken_coop` | 41 | 0.1356 | 11.4785 | 0.2437 | 0.3800 | 4 | có |
| `cicadas_and_crickets` | 48 | 0.2524 | 13.4557 | 0.0034 | 0.0200 | 20 | — |
| `crows_seagulls_magpies` | 66 | 0.4307 | 21.9822 | 0.1342 | 0.2500 | 1 | có |
| `dog_barkings_and_howlings` | 47 | 0.1309 | 7.4455 | 0.3538 | 0.2600 | 0 | có |
| `glass_breaking` | 54 | 0.3881 | 8.0955 | 0.2893 | 0.4100 | 0 | có |
| `horn` | 39 | 0.0578 | 1.8800 | 0.2564 | 0.1200 | 12 | có |
| `jet_aircrafts` | 72 | 0.5502 | 25.0646 | 0.0977 | 0.4000 | 0 | — |
| `lawn_mower_brush_cutter_olive_shaker` | 68 | 0.7227 | 32.4062 | 0.0056 | 0.0700 | 21 | — |
| `music` | 159 | 1.3250 | 30.0000 | 0.0227 | 0.0600 | 36 | — |
| `propeller_aircrafts` | 74 | 0.6154 | 20.9545 | 0.0445 | 0.1000 | 6 | — |
| `sirens_and_alarms` | 65 | 0.3358 | 9.6778 | 0.0440 | 0.0600 | 23 | — |
| `thunder_fireworks_gunshot` | 165 | 0.4156 | 2.0000 | 0.2893 | 0.3600 | 9 | — |
| `train` | 45 | 0.3670 | 19.3307 | 0.0898 | 0.1600 | 4 | — |
| `vacuum_cleaner_fan_hairdryer` | 66 | 0.6734 | 21.8443 | 0.0009 | 0.0200 | 31 | — |
| `vehicle_idling` | 79 | 0.8473 | 24.6767 | 0.0509 | 0.1200 | 18 | — |
| `vehicle_pass_by` | 151 | 0.4951 | 5.2685 | 0.2040 | 0.6600 | 20 | — |
| `voices` | 1330 | 1.1977 | 2.2970 | 0.2928 | 0.2000 | 19 | có |
| `workshop` | 149 | 1.0666 | 20.6051 | 0.0039 | 0.0200 | 65 | — |

Các cột `energy_*` trong CSV chỉ là mô tả năng lượng, không được đưa trực tiếp vào annotation. Onset/offset RMS là đầu khung/cuối khung (độ phân giải 20 ms); giá trị trống nghĩa là không có khung vượt ngưỡng. Clip được kiểm byte SHA-256 với inventory/v4 trước decode.
