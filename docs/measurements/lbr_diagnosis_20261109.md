# Chẩn đoán lỗi event — B0 OOF (ADR-0045 Context)

> OOF 564 recording annotated; λ cSEBB chọn chéo fold (tái lập micro của tầng C). Oracle chỉ đo khoảng cách, không dùng để chọn. Không đọc test.

Micro F1 B0: **0.2342** · TP 592 (khớp sed_eval).

| Loại FN | Số event |
|---|---:|
| miss_nothing | 995 |
| bnd_onset | 656 |
| miss_other_class_overlap | 482 |
| merged | 309 |
| bnd_offset | 116 |
| bnd_both | 100 |
| fragmented | 44 |

Posterior max trong span của event không có box cùng lớp:

| Khoảng | [0, 0.1) | [0.1, 0.3) | [0.3, 0.5) | [0.5, 0.7) | [0.7, 0.9) | [0.9, 1.0001) |
|---|---:|---:|---:|---:|---:|---:|
| Số event | 138 | 108 | 100 | 130 | 212 | 789 |

| Trần: sửa biên box 1-1 trong ± | Micro F1 |
|---|---:|
| 0.5 s | 0.3703 |
| 1 s | 0.4641 |
| 2 s | 0.5230 |

Lệch onset trung vị (dự đoán − nhãn, s) theo lớp, cặp 1-1:

| Lớp | Trung vị |
|---|---:|
| `bells` | -0.08 |
| `birds` | -0.47 |
| `cat_fights_and_moans` | -0.03 |
| `chicken_coop` | -0.15 |
| `cicadas_and_crickets` | -0.12 |
| `crows_seagulls_magpies` | -0.08 |
| `dog_barkings_and_howlings` | -0.09 |
| `glass_breaking` | -0.02 |
| `horn` | -0.06 |
| `jet_aircrafts` | -1.47 |
| `lawn_mower_brush_cutter_olive_shaker` | -0.63 |
| `music` | -0.22 |
| `propeller_aircrafts` | -0.61 |
| `sirens_and_alarms` | -0.18 |
| `thunder_fireworks_gunshot` | -0.05 |
| `train` | -1.47 |
| `vacuum_cleaner_fan_hairdryer` | -0.24 |
| `vehicle_idling` | -0.03 |
| `vehicle_pass_by` | -1.06 |
| `voices` | -0.07 |
| `workshop` | -0.14 |
