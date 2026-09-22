# data_inventory.md — Inventory dữ liệu

> **Sinh tự động** bởi `python -m scripts.report_data_inventory` từ
> `data/manifests/` và `data/reference/`. **Không sửa số bằng tay.**

- Sinh lúc: `2026-09-22T13:22:49Z`
- Taxonomy: `0.1` / `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`

## 1. Archive

### `datasec` — archive

| Trường | Giá trị |
|---|---:|
| Record DOI | `10.5281/zenodo.17033970` |
| License | `cc-by-nc-sa-4.0` |
| Archive | `DATASEC.zip` |
| Bytes | 6,414,663,316 |
| MD5 | `29fa9b8cc84cfa69aa4e5e674e780383` |
| MD5 khớp contract | True |
| ZIP entries | 5,099 |
| File audio | 5,048 |
| Giải nén (GiB) | 7.01 |
| Bảng annotation | 0 |
| LICENSE/README trong archive | 0 |
| Coarse label trong layout | 22 |
| Subclass label trong layout | 28 |
| Nhãn ngoài taxonomy | 0 |
| **Verdict** | **pass** |

### `datased` — archive

| Trường | Giá trị |
|---|---:|
| Record DOI | `10.5281/zenodo.15346092` |
| License | `cc-by-nc-sa-4.0` |
| Archive | `DataSED - Dataset for Sound Event Detection of environmental noise.zip` |
| Bytes | 4,510,378,259 |
| MD5 | `44e093f675fc44cfb8a11b68456b72d7` |
| MD5 khớp contract | True |
| ZIP entries | 722 |
| File audio | 717 |
| Giải nén (GiB) | 5.55 |
| Bảng annotation | 2 |
| LICENSE/README trong archive | 0 |
| Coarse label trong layout | 0 |
| Subclass label trong layout | 0 |
| Nhãn ngoài taxonomy | 0 |
| **Verdict** | **pass** |

## 2. Phân bố lớp

### `datasec` — phân bố lớp

| Coarse class | Files | Share | Subclass (files) |
|---|---:|---:|---|
| `voices` | 1,900 | 37.6% | — |
| `music` | 1,001 | 19.8% | — |
| `thunder_fireworks_gunshot` | 235 | 4.7% | `Fireworks` 68, `Gunshot` 141, `Thunder` 26 |
| `workshop` | 218 | 4.3% | `air compressor` 30, `drill` 45, `grinder` 38, `jackhammer` 63, `saw` 42 |
| `vehicle_pass_by` | 217 | 4.3% | `car pass-by` 110, `motorbike pass-by` 57, `truck pass-by` 50 |
| `lawn_mower_brush_cutter_olive_shaker` | 127 | 2.5% | `Brush cutter` 86, `Lawn mower` 21, `Olive shaker` 20 |
| `vehicle_idling` | 112 | 2.2% | `car truck idling` 81, `motorbike idling` 31 |
| `glass_breaking` | 109 | 2.2% | — |
| `propeller_aircrafts` | 108 | 2.1% | `Airplanes` 50, `Helicopters` 58 |
| `crows_seagulls_magpies` | 106 | 2.1% | `Crows` 50, `Magpies` 21, `Seagulls` 35 |
| `sirens_and_alarms` | 105 | 2.1% | `Alarms` 37, `Sirens` 68 |
| `jet_aircrafts` | 103 | 2.0% | — |
| `wind_turbine` | 100 | 2.0% | — |
| `vacuum_cleaner_fan_hairdryer` | 95 | 1.9% | `fan` 32, `hairdryer` 32, `vacuum cleaner` 31 |
| `cicadas_and_crickets` | 74 | 1.5% | `Cicadas` 54, `Crickets` 20 |
| `dog_barkings_and_howlings` | 70 | 1.4% | — |
| `birds` | 69 | 1.4% | — |
| `bells` | 67 | 1.3% | — |
| `train` | 67 | 1.3% | — |
| `chicken_coop` | 58 | 1.1% | — |
| `horn` | 57 | 1.1% | — |
| `cat_fights_and_moans` | 50 | 1.0% | — |
| **Tổng** | **5,048** | 100% | |

**Chỉ số lệch lớp:**

- Lớn nhất: `voices` 1,900 (37.6%)
- Nhỏ nhất: `cat_fights_and_moans` 50 (1.0%)
- Tỉ lệ lệch coarse: **38.0 : 1**
- Hai lớp lớn nhất chiếm: **57.5%**
- Subclass: 28 node, nhỏ nhất 20 file
- **Subclass dưới 25 file (4):** `cicadas_and_crickets/Crickets`, `lawn_mower_brush_cutter_olive_shaker/Olive shaker`, `crows_seagulls_magpies/Magpies`, `lawn_mower_brush_cutter_olive_shaker/Lawn mower`

## 3. Inventory audio

### `datasec` — inventory audio

○ Chưa giải nén, nên chưa có duration, sample rate hay hash từng file.

### `datased` — inventory audio

| Trường | Giá trị |
|---|---:|
| File | 717 |
| Tổng thời lượng (giờ) | 18.6847 |
| Bytes | 5,961,792,358 |
| Sample rate | {'44100': 717} |
| Channels | {'1': 716, '2': 1} |
| Nhóm exact duplicate (T1) | 8 |

## 4. Ranh giới

Archive audit chỉ đọc central directory của ZIP: nó xác nhận toàn vẹn,
số file audio và độ phủ tên nhãn. Nó **không** mở file audio nào, nên
không nói gì về sample rate, duration, khả năng decode, tính hợp lệ của
annotation hay duplicate. Những mục đó thuộc cổng D1–D3.
