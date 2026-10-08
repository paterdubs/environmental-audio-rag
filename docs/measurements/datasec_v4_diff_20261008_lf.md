# DataSEC v4 so với v3

Sinh bởi `scripts.compare_datasec_versions`.

Đã kiểm MD5 toàn archive trước khi đọc WAV; SHA-256 từng member đọc stream trong zip, không giải nén. 5 mẫu byte v3 được đối chiếu inventory trước scan.

Chuẩn hóa: đổi backslash thành slash, bỏ tiền tố trước DATASEC cuối cùng, chuẩn root thành DATASEC, giữ case phần còn lại, cấm '..' và path trùng. `in_v3` là thuộc tập hash v3, không phải cùng path. WAV duration từ header qua soundfile; hash gồm toàn bộ byte file. Không sửa inventory/split/exclusion.

Nguồn: [Zenodo record v4](https://zenodo.org/records/23097290), DOI 10.5281/zenodo.23097290, license `cc-by-nc-sa-4.0` lấy từ metadata record, không lấy từ zip.

MD5 archive: `11e0ae0098ecf3d982ab5f7375c56844`.

| Lớp | v3 file | v3 giờ | v4 file | v4 giờ |
|---|---:|---:|---:|---:|
| bells | 67 | 0.53209407 | 67 | 0.53209407 |
| birds | 69 | 0.25217591 | 69 | 0.25217591 |
| cat_fights_and_moans | 50 | 0.32508887 | 50 | 0.32508887 |
| chicken_coop | 58 | 0.19260540 | 58 | 0.19260540 |
| cicadas_and_crickets | 74 | 0.46997588 | 74 | 0.46997588 |
| crows_seagulls_magpies | 106 | 0.75151087 | 106 | 0.75151087 |
| dog_barkings_and_howlings | 70 | 0.18684577 | 70 | 0.18684577 |
| glass_breaking | 109 | 1.10932239 | 109 | 1.10932239 |
| horn | 57 | 0.07820974 | 57 | 0.07820974 |
| jet_aircrafts | 103 | 0.79620343 | 103 | 0.79620343 |
| lawn_mower_brush_cutter_olive_shaker | 127 | 1.51715967 | 127 | 1.51715967 |
| music | 1001 | 8.33562759 | 245 | 2.04166667 |
| propeller_aircrafts | 108 | 1.01404401 | 108 | 1.01404401 |
| sirens_and_alarms | 105 | 0.52925292 | 105 | 0.52925292 |
| thunder_fireworks_gunshot | 235 | 0.63587284 | 235 | 0.63587284 |
| train | 67 | 0.65460337 | 67 | 0.65460337 |
| vacuum_cleaner_fan_hairdryer | 95 | 1.01692479 | 95 | 1.01692479 |
| vehicle_idling | 112 | 1.14528590 | 112 | 1.14528590 |
| vehicle_pass_by | 217 | 0.64982450 | 217 | 0.64982450 |
| voices | 1900 | 1.68204895 | 1900 | 1.68204895 |
| wind_turbine | 100 | 0.31836530 | 100 | 0.31836530 |
| workshop | 218 | 1.51519454 | 218 | 1.51519454 |

Tổng v3: 5048 file, 23.70823670 giờ; v4: 4292 file, 17.41427578 giờ.

Path bị bỏ/thêm/cùng path khác hash: 756/0/0.

File v3 mất hash ở v4: 756; file v4 có hash mới: 0.

v4 ⊆ v3 theo hash: **True**.

## Giao file v3 bị bỏ theo hash với exclusion/split

Exclusions: 33 file.

- test: 108 file.
- train: 519 file.
- validation: 96 file.

## Đề xuất

Có thể lọc danh sách v3 theo member v4, giữ exclusion D3; Claude quyết cách tích hợp, script không đổi split/inventory.

Danh sách path/hash bị bỏ/thêm/thay đổi, giao theo path, SHA-256 bảng nguồn, 5 mẫu v3 và provenance đầy đủ ở JSON; member ở `datasec_v4_members.csv`.
