# taxonomy.md — Taxonomy âm thanh môi trường

## 1. Nguyên tắc

- Canonical taxonomy bám ontology công bố của DataSEC/DataSED.
- Class mô tả nguồn âm nghe được, không suy nguyên nhân hoặc mức nguy hiểm.
- DataSED coarse class là ground truth SED.
- DataSEC subclass chỉ dùng cho classification/refinement.
- `background`, `silence` và `unknown` là trạng thái, không phải target event.

## 2. Coarse classes

| ID | Source label | Nhóm | Polyphonic SED |
|---|---|---|---:|
| `bells` | Bells | signal | Có |
| `birds` | Birds | biophony | Có |
| `cat_fights_and_moans` | Cat fights and moans | biophony | Có |
| `chicken_coop` | Chicken coop | biophony | Có |
| `cicadas_and_crickets` | Cicadas and crickets | biophony | Có |
| `crows_seagulls_magpies` | Crows, seagulls and magpies | biophony | Có |
| `dog_barkings_and_howlings` | Dog barkings and howlings | biophony | Có |
| `glass_breaking` | Glass breaking | impact | Có |
| `horn` | Horn | transport/signal | Có |
| `jet_aircrafts` | Jet aircrafts | transport | Có |
| `lawn_mower_brush_cutter_olive_shaker` | Lawn mower, brush cutter and olive shaker | machinery | Có |
| `music` | Music | human/media | Có |
| `propeller_aircrafts` | Propeller aircrafts | transport | Có |
| `sirens_and_alarms` | Sirens and alarms | signal | Có |
| `thunder_fireworks_gunshot` | Thunder, fireworks and gunshot | impulsive | Có |
| `train` | Train | transport | Có |
| `vacuum_cleaner_fan_hairdryer` | Vacuum cleaner, fan and hairdryer | machinery | Có |
| `vehicle_idling` | Vehicle idling | transport | Có |
| `vehicle_pass_by` | Vehicle pass-by | transport | Có |
| `voices` | Voices | human | Có |
| `wind_turbine` | Wind turbine | machinery | Không |
| `workshop` | Workshop | machinery | Có |

Primary polyphonic head có 21 class do `wind_turbine` chỉ thuộc monophonic label set.

## 3. DataSEC subclasses

Subclasses được giữ theo hierarchy, không nâng thành DataSED strong-label targets.

| Coarse class | Subclasses |
|---|---|
| `cicadas_and_crickets` | `cicadas`, `crickets` |
| `crows_seagulls_magpies` | `crows`, `seagulls`, `magpies` |
| `lawn_mower_brush_cutter_olive_shaker` | `lawn_mower`, `brush_cutter`, `olive_shaker` |
| `propeller_aircrafts` | `airplanes`, `helicopters` |
| `sirens_and_alarms` | `sirens`, `alarms` |
| `thunder_fireworks_gunshot` | `thunder`, `fireworks`, `gunshot` |
| `vacuum_cleaner_fan_hairdryer` | `vacuum_cleaner`, `fan`, `hairdryer` |
| `vehicle_idling` | `car_truck_idling`, `motorbike_idling` |
| `vehicle_pass_by` | `car_pass_by`, `motorbike_pass_by`, `truck_pass_by` |
| `workshop` | `air_compressor`, `drill`, `grinder`, `jackhammer`, `saw` |

Subclass list phải được xác nhận lại từ manifest của archive đã tải trước khi freeze taxonomy version 1.0.

## 4. Mapping policy

```text
source label → canonical coarse ID → optional subclass ID
```

Quy tắc:

1. Source label luôn được lưu nguyên văn.
2. Mapping là file config có version và checksum.
3. Unknown source label làm pipeline fail ở bước validation.
4. Không đổi class order sau khi train checkpoint; thay đổi tạo taxonomy version mới.
5. Caption lexicon và frontend đọc cùng canonical config.

## 5. Class gộp và cách diễn đạt

### `sirens_and_alarms`

Caption coarse hợp lệ:

> A siren- or alarm-like sound is audible.

Không được khẳng định `emergency vehicle` hoặc `fire alarm` nếu chỉ có coarse prediction.

### `thunder_fireworks_gunshot`

Caption coarse hợp lệ:

> An impulsive sound resembling thunder, fireworks, or a gunshot is detected.

Subclass classifier có thể thêm:

> The classifier favors fireworks (0.71), but DataSED provides no subclass ground truth for this interval.

## 6. Versioning

Taxonomy version gồm:

```text
major.minor
```

- Major: đổi class set, hierarchy hoặc semantics.
- Minor: thêm alias/caption phrase không đổi target IDs.

