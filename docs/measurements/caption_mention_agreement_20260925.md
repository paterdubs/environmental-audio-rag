# Bộ trích mention vs người đọc — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.caption_mention_worksheet score`. Lexicon `6f5634bb…`; 60 caption unconstrained đã điền (0 dòng chưa điền, bỏ qua); người đọc mù (không timeline, không output lexicon, không nghe audio).

| Mức | Precision | Recall | TP | FP | FN | Caption khớp hoàn toàn |
|---|---:|---:|---:|---:|---:|---:|
| Mention (lớp) | 0.896 | 0.936 | 147 | 17 | 10 | 42/60 |
| Gọi tên quá mức | 1.000 | 0.568 | | | | |

Gọi tên quá mức người đánh dấu mà lexicon không: 16, trong đó 8 là nhắc lại đúng tên lớp (vd "cicadas and crickets") — lexicon coi là mức lớp theo thiết kế.

## C2 trên cùng mẫu: lexicon đọc vs người đọc

| Metric | Lexicon | Người | Lexicon − người [CI 95%] |
|---|---:|---:|---:|
| hallucination_rate | 0.0111 | 0.0333 | -0.0222 [-0.0778, +0.0167] |
| omission_rate | 0.0492 | 0.0805 | -0.0312 [-0.0833, +0.0042] |

## Cờ "caption có bịa" (so với timeline)

| | Người: có | Người: không |
|---|---:|---:|
| Lexicon: có | 0 | 2 |
| Lexicon: không | 2 | 56 |

## Caption lệch

- `m-006` lexicon ['workshop'] · người [] — A rhythmic series of hammer strikes echoes through a workshop, punctuating the quiet air with sharp, metallic impacts.
- `m-008` lexicon ['sirens_and_alarms', 'vehicle_idling|vehicle_pass_by'] · người ['sirens_and_alarms', 'vehicle_pass_by'] — A vehicle passes by before the scene is dominated by the wailing of sirens and alarms that persist for the majority of the recording.
- `m-010` lexicon ['workshop'] · người [] — A rhythmic series of hammer strikes echoes through a workshop, marking the steady progress of a crafting project.
- `m-014` lexicon ['jet_aircrafts', 'vehicle_idling|vehicle_pass_by'] · người ['jet_aircrafts', 'vehicle_pass_by'] — A vehicle passes by briefly before the sound of jet aircrafts dominates the recording for over twenty seconds.
- `m-015` lexicon ['birds', 'dog_barkings_and_howlings', 'vehicle_idling|vehicle_pass_by', 'voices'] · người ['birds', 'dog_barkings_and_howlings', 'vehicle_pass_by', 'voices'] — A brief vehicle passes by to reveal a lively soundscape of chirping birds, human voices, and barking dogs in a natural setting.
- `m-020` lexicon ['cicadas_and_crickets', 'music'] · người ['cicadas_and_crickets'] — A rhythmic chorus of cicadas and crickets fills the air in this two-minute environmental recording, punctuating the quiet with repeated bursts of insect song.
- `m-021` lexicon ['horn', 'vehicle_idling', 'vehicle_idling|vehicle_pass_by', 'vehicle_pass_by', 'voices'] · người ['horn', 'vehicle_idling', 'vehicle_pass_by', 'voices'] — A continuous stream of urban traffic noise, featuring multiple vehicles passing by and idling, punctuated by brief moments of human voices and honking horns.
- `m-023` lexicon ['vehicle_pass_by', 'workshop'] · người ['vehicle_pass_by', 'voices'] — In a bustling workshop filled with early chatter, the steady rhythm of passing vehicles gradually takes over the soundscape.
- `m-026` lexicon ['lawn_mower_brush_cutter_olive_shaker|vacuum_cleaner_fan_hairdryer|workshop', 'workshop'] · người ['workshop'] — A 39.7-second environmental recording captures intermittent bursts of workshop activity, with distinct periods of machinery noise occurring at the beginning, middle, and end of the clip.
- `m-031` lexicon ['music', 'vehicle_idling|vehicle_pass_by', 'voices'] · người ['music', 'vehicle_pass_by', 'voices'] — A 159-second environmental recording captures a continuous background music track punctuated by intermittent human voices and the passing sounds of vehicles.
- `m-032` lexicon ['dog_barkings_and_howlings', 'horn', 'lawn_mower_brush_cutter_olive_shaker', 'thunder_fireworks_gunshot', 'train', 'vehicle_idling', 'vehicle_idling|vehicle_pass_by', 'vehicle_pass_by', 'voices'] · người ['dog_barkings_and_howlings', 'horn', 'lawn_mower_brush_cutter_olive_shaker', 'thunder_fireworks_gunshot', 'train', 'vehicle_idling', 'vehicle_pass_by', 'voices'] — A continuous stream of traffic noise, including passing vehicles, idling engines, and a distant train, is punctuated by brief moments of human voices, a lawn mower, a dog barking, a car horn, and a final loud gunshot.
- `m-033` lexicon ['lawn_mower_brush_cutter_olive_shaker', 'lawn_mower_brush_cutter_olive_shaker|vacuum_cleaner_fan_hairdryer|workshop', 'vehicle_pass_by', 'workshop'] · người ['lawn_mower_brush_cutter_olive_shaker', 'vehicle_pass_by', 'workshop'] — A brief soundscape captures the rhythmic hum of a workshop, punctuated by the roar of passing vehicles and the distinct whir of a lawn mower before settling back into mechanical noise.
- `m-037` lexicon ['birds', 'thunder_fireworks_gunshot', 'train', 'vehicle_idling|vehicle_pass_by'] · người ['birds', 'thunder_fireworks_gunshot', 'train', 'vehicle_pass_by'] — A brief moment of nature and urban noise unfolds as birds sing and a vehicle passes, interrupted by a sudden gunshot, before the steady rumble of a train dominates the final twenty seconds.
- `m-038` lexicon ['birds', 'vehicle_idling', 'vehicle_idling|vehicle_pass_by'] · người ['birds', 'vehicle_idling', 'vehicle_pass_by'] — A vehicle passes by and idles briefly before the recording concludes with the chirping of birds.
- `m-042` lexicon ['birds', 'thunder_fireworks_gunshot', 'train', 'vehicle_idling|vehicle_pass_by'] · người ['birds', 'thunder_fireworks_gunshot', 'train', 'vehicle_pass_by'] — A vehicle passes by briefly before a train rumbles through the scene, punctuated by chirping birds and ending with a sudden thunder or gunshot.
- `m-050` lexicon ['horn', 'train', 'vehicle_idling|vehicle_pass_by'] · người ['horn', 'train', 'vehicle_pass_by'] — A vehicle passes by while a horn blares, followed by the rumble of a train arriving.
- `m-055` lexicon ['birds', 'dog_barkings_and_howlings', 'jet_aircrafts', 'sirens_and_alarms', 'train', 'vehicle_pass_by'] · người ['birds', 'dog_barkings_and_howlings', 'jet_aircrafts', 'propeller_aircrafts', 'sirens_and_alarms', 'train', 'vehicle_pass_by'] — A 3-minute environmental recording captures a dynamic urban soundscape where the rhythmic chirping of birds and distant train rumble are punctuated by the roar of passing vehicles, propeller and jet aircraft, and intermittent sirens and dog barks.
- `m-060` lexicon ['birds', 'cicadas_and_crickets', 'music|voices'] · người ['birds', 'cicadas_and_crickets'] — A serene natural soundscape features a long, continuous chorus of birds singing from 4.7 to 53.5 seconds and again from 60.0 to the end, punctuated by intermittent bursts of cicada and cricket chirping throughout the 93-second recording.
