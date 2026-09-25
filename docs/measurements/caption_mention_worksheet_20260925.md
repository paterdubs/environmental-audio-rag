# Phiếu đối chiếu bộ trích mention (C2) — hướng dẫn điền

> Sinh bởi `scripts.caption_mention_worksheet build`. Phiếu:
> `data/manifests/caption_mention_worksheet.csv` (60 caption unconstrained, tập test;
> 30 mức oracle + 30 mức e2e, chọn bằng thứ tự băm có seed).

**Mục đích.** Metric C2 (hallucination, omission, gọi tên quá mức) dựa vào lexicon tự động
đọc caption. Phiếu này đo lexicon đọc đúng đến đâu. Bạn đọc caption và ghi nguồn âm caption
**khẳng định nghe thấy**. Đọc **mù**: không xem timeline, không xem kết quả lexicon, và
**không nghe audio** — phiếu đo cách đọc câu chữ; audio chứa gì đã có nhãn DataSED trả lời.

Mở được bằng Excel; khi lưu chọn **CSV UTF-8** (lưu kiểu khác sẽ mất dấu).

Các cột cần điền:

- `classes_mentioned` — `class_id` của mọi nguồn âm caption nói là nghe thấy, cách nhau
  bằng `;`. Từ mơ hồ phủ nhiều lớp ghi `lớp_a|lớp_b` (vd `jet_aircrafts|propeller_aircrafts`
  cho "aircraft"). Không có nguồn nào: ghi `none` — không để trống.
  Ví dụ: `birds; jet_aircrafts|propeller_aircrafts`.
- `other_sources` — nguồn âm **ngoài** 22 lớp (gió, mưa, bước chân, đám đông…), cách nhau
  bằng dấu phẩy; trống nếu không có. Ví dụ: `wind, footsteps`.
- `over_specific` — `class_id` của lớp mà caption gọi tên một loại con như sự thật
  ("a gunshot" → `thunder_fireworks_gunshot`, "sirens" → `sirens_and_alarms`,
  "a vacuum cleaner" → `vacuum_cleaner_fan_hairdryer`); cách nhau bằng `;`; trống nếu không có.
  Liệt kê loại con bằng "or" vẫn tính ("a fan or hairdryer" → `vacuum_cleaner_fan_hairdryer`)
  — đúng định nghĩa metric C2, vốn đếm mọi tên loại con.
- `notes` — tuỳ chọn.

**Quy tắc.** (1) Từ bối cảnh ("urban", "park", "street") không phải nguồn âm — không ghi.
(2) Một lớp nhắc nhiều lần chỉ ghi một lần. (3) Cách gọi khác vẫn tính ("chirping" →
`birds`, "people talking" → `voices`, "engine idling" → `vehicle_idling`). (4) Không sửa cột
`caption` — script kiểm nguyên văn. (5) Xong thì chạy
`scripts.caption_mention_worksheet score ml/runs/<run>`.

## 22 lớp

| `class_id` | Nhãn gốc |
|---|---|
| `bells` | Bells |
| `birds` | Birds |
| `cat_fights_and_moans` | Cat fight and moans |
| `chicken_coop` | Chicken coop |
| `cicadas_and_crickets` | Cicadas and crickets |
| `crows_seagulls_magpies` | Crows seagulls and magpies |
| `dog_barkings_and_howlings` | Dog barkings and howlings |
| `glass_breaking` | Glass breaking |
| `horn` | Horn |
| `jet_aircrafts` | Jet aircrafts |
| `lawn_mower_brush_cutter_olive_shaker` | Lawn mower brush cutter and olive shaker |
| `music` | Music |
| `propeller_aircrafts` | Propeller aircrafts |
| `sirens_and_alarms` | Sirens and alarms |
| `thunder_fireworks_gunshot` | Thunder fireworks and gunshot |
| `train` | Train |
| `vacuum_cleaner_fan_hairdryer` | Vacuum cleaner fan and hairdryer |
| `vehicle_idling` | Vehicle idling |
| `vehicle_pass_by` | Vehicle pass-by |
| `voices` | Voices |
| `wind_turbine` | Wind turbine |
| `workshop` | Workshop |
