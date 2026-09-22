# taxonomy.md — 22 lớp âm thanh môi trường

> **Nguồn chân lý máy đọc được là `ml/configs/taxonomy.yaml`**, không phải file này.
> Taxonomy version hiện tại `0.1`, SHA-256
> `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`.
> File này giải thích *ý nghĩa* của từng lớp để đọc nhãn, viết caption lexicon và
> phân tích lỗi cho đúng.

---

## 0. Cách đọc tài liệu này — và nó KHÔNG phải cái gì

Đề tài **không tổ chức gán nhãn mới**. DataSEC và DataSED đã có nhãn công bố, và
nhãn đó là bất biến (xem [annotation_guideline.md](annotation_guideline.md) §2).

Vì vậy phần ❌ **Không bao gồm** ở đây **không phải** luật cho người gán nhãn. Nó
phục vụ ba việc khác, cả ba đều ảnh hưởng trực tiếp tới kết quả:

| Mục đích | Dùng ở đâu | Hậu quả nếu sai |
|---|---|---|
| **Đọc nhãn cho đúng** | Khi diễn giải kết quả và viết báo cáo | Kết luận sai về cái model học được |
| **Caption lexicon** | `ml/captioning/`, ràng buộc G1/G3 ([SYSTEM.md](SYSTEM.md) §6.3) | Caption bịa hoặc suy diễn ngoài bằng chứng |
| **Phân tích lỗi** | `confusable_with` khi đọc ma trận nhầm lẫn | Quy tội sai cho model |

Mỗi lớp có bốn phần:

- ✅ **Bao gồm** — nguồn âm nhãn này bao phủ theo ontology công bố.
- ❌ **Không bao gồm** — nguồn âm nghe *giống* nhưng thuộc lớp khác. Đây là phần
  quan trọng nhất: định nghĩa một lớp chủ yếu là nói nó *không* phải cái gì.
- 🔍 **Dấu hiệu phân biệt** — tiêu chí âm học tách nó khỏi cặp dễ nhầm nhất.
- 📌 **Caption hợp lệ / không hợp lệ** — ràng buộc ngôn ngữ cho C1.

### Hai nguyên tắc bao trùm

**N1 — Mô tả nguồn âm, không mô tả tình huống.** Hệ quả trực tiếp của
[ADR-0001](decisions/ADR-0001-scope-and-datasets.md). "Có tiếng kính vỡ" hợp lệ;
"có đột nhập" không, dù cùng một tín hiệu.

**N2 — Caption không được sắc nét hơn bằng chứng.** Nếu SED chỉ cho
`thunder_fireworks_gunshot` thì caption phải giữ nguyên mức mơ hồ đó. Làm sắc
hơn là hallucination, kể cả khi đoán đúng.

---

## 1. Cấu trúc taxonomy

```text
22 coarse class   ← nhãn của DataSEC (cây thư mục) và DataSED (CSV)
 └── 28 subclass  ← CHỈ có trong DataSEC, thuộc 10 coarse class
```

| Label set | Số lớp | Dùng cho |
|---|---:|---|
| DataSEC classification | 22 coarse + 28 subclass | Encoder pretraining, RQ4 |
| **DataSED polyphonic** | **21** | **Benchmark SED chính** |
| DataSED monophonic | 22 | Benchmark phụ |

**Vì sao polyphonic chỉ có 21:** `wind_turbine` không thuộc polyphonic label set
của DataSED. Kiểm bằng `taxonomy.polyphonic_class_ids`; `tests/test_taxonomy.py`
pin con số này.

`background`, `silence`, `unknown` là **trạng thái**, không phải event head.

### Bảng tra nhanh 22 lớp

Cột "DataSEC" là số file trong archive, nguồn
[measurements/archive_audit_20260922.md](measurements/archive_audit_20260922.md).

| # | `class_id` | Nhóm | DataSEC | Poly | Subclass |
|---:|---|---|---:|:---:|---:|
| 1 | `bells` | Tín hiệu | 67 | ✅ | — |
| 2 | `birds` | Sinh vật | 69 | ✅ | — |
| 3 | `cat_fights_and_moans` | Sinh vật | 50 | ✅ | — |
| 4 | `chicken_coop` | Sinh vật | 58 | ✅ | — |
| 5 | `cicadas_and_crickets` | Sinh vật | 74 | ✅ | 2 |
| 6 | `crows_seagulls_magpies` | Sinh vật | 106 | ✅ | 3 |
| 7 | `dog_barkings_and_howlings` | Sinh vật | 70 | ✅ | — |
| 8 | `glass_breaking` | Xung | 109 | ✅ | — |
| 9 | `horn` | Giao thông | 57 | ✅ | — |
| 10 | `jet_aircrafts` | Giao thông | 103 | ✅ | — |
| 11 | `lawn_mower_brush_cutter_olive_shaker` | Máy móc | 127 | ✅ | 3 |
| 12 | `music` | Người/media | 1,001 | ✅ | — |
| 13 | `propeller_aircrafts` | Giao thông | 108 | ✅ | 2 |
| 14 | `sirens_and_alarms` | Tín hiệu | 105 | ✅ | 2 |
| 15 | `thunder_fireworks_gunshot` | Xung | 235 | ✅ | 3 |
| 16 | `train` | Giao thông | 67 | ✅ | — |
| 17 | `vacuum_cleaner_fan_hairdryer` | Máy móc | 95 | ✅ | 3 |
| 18 | `vehicle_idling` | Giao thông | 112 | ✅ | 2 |
| 19 | `vehicle_pass_by` | Giao thông | 217 | ✅ | 3 |
| 20 | `voices` | Người/media | 1,900 | ✅ | — |
| 21 | `wind_turbine` | Máy móc | 100 | ❌ | — |
| 22 | `workshop` | Máy móc | 218 | ✅ | 5 |
| | **Tổng** | | **5,048** | **21** | **28** |

---

## 2. Nhóm A — Sinh vật (6 lớp)

### A1. `birds` — Chim (chung)

Tiếng chim hót, kêu, ríu rít của các loài không thuộc nhóm `crows_seagulls_magpies`.

| | |
|---|---|
| ✅ **Bao gồm** | Chim hót có giai điệu · Ríu rít nhiều con · Tiếng gọi bầy · Chim nhỏ trong vườn, công viên |
| ❌ **Không bao gồm** | Quạ, mòng biển, chim ác là → `crows_seagulls_magpies` · Gà và tiếng chuồng gà → `chicken_coop` · Ve sầu, dế → `cicadas_and_crickets` |
| 🔍 **Dấu hiệu phân biệt** | **so với `crows_seagulls_magpies`:** quạ/mòng biển/ác là có tiếng **khàn, gắt, không giai điệu**, năng lượng dàn rộng. `birds` thường có **cấu trúc hài và cao độ rõ**. Nghe ra "tiếng kêu khàn lặp lại" → nhóm quạ. **so với `cicadas_and_crickets`:** côn trùng phát **liên tục gần như không nghỉ**, phổ hẹp; chim có khoảng lặng giữa các nốt |
| 📌 **Caption** | ✅ "Bird calls are audible." ❌ "A songbird sings in a garden" — `garden` là bối cảnh, vi phạm N1 |

---

### A2. `crows_seagulls_magpies` — Quạ, mòng biển, chim ác là

Lớp **gộp** ba nhóm chim có tiếng kêu khàn, gắt, thường sống gần khu dân cư.

| | |
|---|---|
| ✅ **Bao gồm** | Quạ kêu · Mòng biển kêu (thường gần biển/cảng) · Chim ác là |
| ❌ **Không bao gồm** | Chim hót có giai điệu → `birds` · Gà → `chicken_coop` |
| 🔍 **Dấu hiệu phân biệt** | Xem A1. Trong nội bộ lớp: mòng biển có tiếng **kéo dài, lên xuống**; quạ **ngắn, lặp, đều**; ác là có tiếng **lạch cạch như tiếng gõ**. Ba phân biệt này chỉ áp cho subclass DataSEC |
| 📌 **Caption** | ✅ "A harsh bird call, such as a crow, seagull or magpie, is audible." ❌ "Seagulls cry near the harbour" khi chỉ có coarse evidence |

**Subclass (DataSEC):** `Crows` (50), `Seagulls` (35), `Magpies` (21).

> ⚠️ `Magpies` chỉ có **21 file** → thuộc nhóm low-support, dev/test ~3 file.
> Xem [evaluation_protocol.md](evaluation_protocol.md) §4.

---

### A3. `chicken_coop` — Chuồng gà

| | |
|---|---|
| ✅ **Bao gồm** | Gà mái cục tác · Gà trống gáy · Tiếng ồn tổng của đàn gà trong chuồng |
| ❌ **Không bao gồm** | Chim hoang dã → `birds` hoặc `crows_seagulls_magpies` · Tiếng người cho gà ăn → thêm `voices` chồng lấp |
| 🔍 **Dấu hiệu phân biệt** | **so với `birds`:** gà có nhịp **cục tác lặp không đều**, phổ thấp hơn chim hót, và thường là **nền liên tục của nhiều con** chứ không phải tiếng đơn lẻ |
| 📌 **Caption** | ✅ "Poultry sounds from a chicken coop are audible." |

---

### A4. `dog_barkings_and_howlings` — Chó sủa, chó tru

| | |
|---|---|
| ✅ **Bao gồm** | Sủa đơn hoặc loạt · Tru kéo dài · Nhiều con sủa cùng lúc |
| ❌ **Không bao gồm** | Mèo → `cat_fights_and_moans` · Sủa phát qua loa/TV → vẫn là nhãn nguồn nếu dataset gán vậy; ghi vào phân tích lỗi, không tự sửa |
| 🔍 **Dấu hiệu phân biệt** | **so với `cat_fights_and_moans`:** chó sủa có **xung dốc, ngắn, lặp đều**; mèo có **tiếng kéo dài, cao độ trượt, sắc thái gào**. **so với `voices`:** chó không có cấu trúc formant của tiếng nói |
| 📌 **Caption** | ✅ "A dog barks." ✅ "Dog howling is audible." ❌ "A guard dog warns of an intruder" — vi phạm N1 |

---

### A5. `cat_fights_and_moans` — Mèo gào, mèo đánh nhau

| | |
|---|---|
| ✅ **Bao gồm** | Mèo gào khi đánh nhau · Tiếng rên kéo dài · Tiếng kêu gắt cao độ |
| ❌ **Không bao gồm** | Chó → `dog_barkings_and_howlings` · Tiếng người thét → `voices` |
| 🔍 **Dấu hiệu phân biệt** | Xem A4. **so với `voices`:** tiếng mèo gào có cao độ **trượt liên tục không theo cấu trúc âm tiết**; tiếng người dù gào vẫn có ngắt âm tiết |
| 📌 **Caption** | ✅ "Cat moans or fighting sounds are audible." |

> **Lớp nhỏ nhất của DataSEC: 50 file (1.0%).** Khi đọc per-class F1, nhớ rằng
> lớp này có ít dữ liệu nhất trong 22 lớp.

**Lưu ý nhãn nguồn:** DataSED ghi `Cat fight and moans` (số ít), DataSEC ghi
`Cat fights and moans` (số nhiều). `ml/configs/taxonomy.yaml` khai bản DataSED làm
`source_label` và bản DataSEC làm alias. Đây là bẫy im lặng nếu tự viết parser.

---

### A6. `cicadas_and_crickets` — Ve sầu và dế

| | |
|---|---|
| ✅ **Bao gồm** | Ve sầu kêu ban ngày · Dế gáy ban đêm · Nền côn trùng liên tục |
| ❌ **Không bao gồm** | Chim → `birds` · Tiếng máy móc rè đều → `vacuum_cleaner_fan_hairdryer` hoặc `workshop` |
| 🔍 **Dấu hiệu phân biệt** | **so với `birds`:** xem A1. **so với nền máy móc:** côn trùng có **điều biến biên độ theo nhịp sinh học** (nhấp nháy đều); máy móc có phổ hài ổn định và tần số cơ bản cố định |
| 📌 **Caption** | ✅ "Insect sounds, such as cicadas or crickets, are audible." |

**Subclass (DataSEC):** `Cicadas` (54), `Crickets` (20).

> ⚠️ `Crickets` **20 file** — subclass nhỏ nhất toàn dataset. Dev/test ~3 file.

---

## 3. Nhóm B — Giao thông (6 lớp)

### B1. `vehicle_pass_by` — Xe chạy ngang qua

Lớp **đông thứ ba** của DataSEC (217 file). Đặc trưng: cường độ **tăng rồi giảm**
theo đường cong Doppler khi nguồn di chuyển ngang micro.

| | |
|---|---|
| ✅ **Bao gồm** | Ô tô, xe máy, xe tải chạy qua · Tiếng lốp trên mặt đường · Đường bao cường độ hình chuông |
| ❌ **Không bao gồm** | Xe đứng nổ máy → `vehicle_idling` · Còi xe → `horn` · Tàu hỏa → `train` · Va chạm xe → không có lớp riêng; mô tả bằng các nguồn quan sát được |
| 🔍 **Dấu hiệu phân biệt** | **so với `vehicle_idling`:** pass-by có **đường bao tăng–đỉnh–giảm** rõ trong vài giây và thường có **dịch tần Doppler**; idling có mức **gần như phẳng, kéo dài**. Đây là tiêu chí chính, không phải âm lượng |
| 📌 **Caption** | ✅ "A vehicle passes by." ❌ "A car speeds past dangerously" — `dangerously` vi phạm N1 |

**Subclass (DataSEC):** `car pass-by` (110), `motorbike pass-by` (57), `truck pass-by` (50).

---

### B2. `vehicle_idling` — Xe nổ máy tại chỗ

| | |
|---|---|
| ✅ **Bao gồm** | Ô tô/xe tải nổ máy đứng yên · Xe máy nổ máy tại chỗ · Nền động cơ ổn định |
| ❌ **Không bao gồm** | Xe chạy qua → `vehicle_pass_by` · Máy phát điện, máy nén → `workshop` · Quạt, máy hút bụi → `vacuum_cleaner_fan_hairdryer` |
| 🔍 **Dấu hiệu phân biệt** | Xem B1. **so với `workshop`:** động cơ đốt trong có **chuỗi hài của tần số nổ** và rung không đều nhẹ; máy nén/khoan có phổ ổn định hơn hoặc có xung lặp |
| 📌 **Caption** | ✅ "A vehicle engine is idling." |

**Subclass (DataSEC):** `car truck idling` (81), `motorbike idling` (31).

---

### B3. `horn` — Còi xe

| | |
|---|---|
| ✅ **Bao gồm** | Còi ô tô, xe tải, xe máy · Bấm ngắn hoặc giữ dài · Nhiều xe bấm còi |
| ❌ **Không bao gồm** | Còi hú cứu hộ/báo động → `sirens_and_alarms` · Chuông → `bells` · Còi tàu hỏa → thường đi cùng `train`; theo nhãn dataset |
| 🔍 **Dấu hiệu phân biệt** | **so với `sirens_and_alarms`:** còi xe có **cao độ cố định** trong suốt thời gian phát; còi hú **trượt cao độ liên tục** hoặc nhảy hai mức. Đây là tiêu chí quyết định. **so với `bells`:** chuông có **đuôi ngân tắt dần**; còi tắt đột ngột |
| 📌 **Caption** | ✅ "A vehicle horn sounds." |

> **Lớp này đạt trần `pos_weight = 50` trong baseline** và có frame-F1 thấp nhất
> nhì (0.134842). Là ứng viên hàng đầu cho phân tích lỗi.

---

### B4. `train` — Tàu hỏa

| | |
|---|---|
| ✅ **Bao gồm** | Tàu chạy qua · Tiếng bánh trên ray, tiếng nối toa · Tiếng phanh rít · Còi tàu khi dataset gán vào lớp này |
| ❌ **Không bao gồm** | Xe đường bộ → `vehicle_pass_by` · Máy bay → `jet_aircrafts` / `propeller_aircrafts` |
| 🔍 **Dấu hiệu phân biệt** | **so với `vehicle_pass_by`:** tàu có **thời lượng dài hơn nhiều** (hàng chục giây), có **nhịp lặp đều của bánh trên mối ray**, và năng lượng tần số thấp mạnh hơn |
| 📌 **Caption** | ✅ "A train passes by." |

---

### B5. `jet_aircrafts` — Máy bay phản lực

| | |
|---|---|
| ✅ **Bao gồm** | Phản lực bay qua · Cất/hạ cánh · Tiếng rít turbine |
| ❌ **Không bao gồm** | Máy bay cánh quạt, trực thăng → `propeller_aircrafts` · Tuabin gió → `wind_turbine` |
| 🔍 **Dấu hiệu phân biệt** | **so với `propeller_aircrafts`:** phản lực cho **tiếng rít băng rộng, không có nhịp cánh**; cánh quạt/trực thăng có **điều biến tuần hoàn rõ theo vòng quay** (nghe "phựt-phựt"). Nghe thấy nhịp đập đều → `propeller_aircrafts` |
| 📌 **Caption** | ✅ "A jet aircraft passes overhead." |

---

### B6. `propeller_aircrafts` — Máy bay cánh quạt và trực thăng

| | |
|---|---|
| ✅ **Bao gồm** | Máy bay cánh quạt · Trực thăng · Tiếng đập cánh quạt |
| ❌ **Không bao gồm** | Phản lực → `jet_aircrafts` · Drone nhỏ → không có lớp riêng · Tuabin gió → `wind_turbine` |
| 🔍 **Dấu hiệu phân biệt** | Xem B5. **so với `wind_turbine`:** trực thăng có **tần số đập cao và biến thiên** theo khoảng cách; tuabin gió có nhịp **rất chậm, đều, gần như không đổi** |
| 📌 **Caption** | ✅ "A propeller aircraft or helicopter is audible." |

**Subclass (DataSEC):** `Airplanes` (50), `Helicopters` (58).

---

## 4. Nhóm C — Máy móc (4 lớp)

### C1. `workshop` — Xưởng, công trường

Lớp **gộp rộng nhất về nguồn âm** (5 subclass, 218 file).

| | |
|---|---|
| ✅ **Bao gồm** | Máy nén khí · Khoan · Máy mài · Máy khoan phá bê tông · Cưa |
| ❌ **Không bao gồm** | Máy cắt cỏ, máy tỉa → `lawn_mower_brush_cutter_olive_shaker` · Máy gia dụng → `vacuum_cleaner_fan_hairdryer` · Xe nổ máy → `vehicle_idling` |
| 🔍 **Dấu hiệu phân biệt** | **so với `lawn_mower…`:** thiết bị xưởng thường **cố định, có chu kỳ bật/tắt**; máy làm vườn có **động cơ 2 thì rú lên xuống theo tải**. **so với `vacuum_cleaner_fan_hairdryer`:** thiết bị xưởng **mạnh hơn, có va đập kim loại**; máy gia dụng là **nền khí ổn định** |
| 📌 **Caption** | ✅ "Workshop or construction machinery is operating." ❌ "Building work is disturbing the neighbourhood" — suy diễn tác động, vi phạm N1 |

**Subclass (DataSEC):** `jackhammer` (63), `drill` (45), `saw` (42), `grinder` (38),
`air compressor` (30).

---

### C2. `lawn_mower_brush_cutter_olive_shaker` — Máy cắt cỏ, máy tỉa, máy rung ô liu

| | |
|---|---|
| ✅ **Bao gồm** | Máy cắt cỏ · Máy tỉa cành/cắt cỏ cầm tay · Máy rung thu hoạch ô liu |
| ❌ **Không bao gồm** | Thiết bị xưởng → `workshop` · Quạt/máy hút bụi → `vacuum_cleaner_fan_hairdryer` |
| 🔍 **Dấu hiệu phân biệt** | Xem C1. Đặc trưng riêng: **động cơ hai thì rú lên khi gặp tải rồi hạ xuống**, chu kỳ vài giây, kèm nền băng rộng của lưỡi cắt |
| 📌 **Caption** | ✅ "Garden machinery such as a lawn mower or brush cutter is operating." |

**Subclass (DataSEC):** `Brush cutter` (86), `Lawn mower` (21), `Olive shaker` (20).

> ⚠️ **Hai subclass low-support trong cùng một node:** `Lawn mower` (21) và
> `Olive shaker` (20). Node này có 3 subclass nhưng 2 trong số đó không đánh giá
> được có ý nghĩa.

---

### C3. `vacuum_cleaner_fan_hairdryer` — Máy hút bụi, quạt, máy sấy tóc

| | |
|---|---|
| ✅ **Bao gồm** | Máy hút bụi · Quạt điện, quạt thông gió · Máy sấy tóc |
| ❌ **Không bao gồm** | Thiết bị xưởng → `workshop` · Điều hòa ngoài trời → theo nhãn dataset · Gió tự nhiên → nền, không phải target event |
| 🔍 **Dấu hiệu phân biệt** | **Nền khí băng rộng, ổn định, ít điều biến** — đây là dấu hiệu chính. So với `workshop`: không có va đập kim loại, không có chu kỳ tải |
| 📌 **Caption** | ✅ "A household appliance such as a vacuum cleaner, fan or hairdryer is running." |

**Subclass (DataSEC):** `fan` (32), `hairdryer` (32), `vacuum cleaner` (31).

> Đây là node **cân bằng nhất** của DataSEC: 32/32/31. Ứng viên tốt để đánh giá
> subclass classifier mà không bị nhiễu bởi imbalance.

---

### C4. `wind_turbine` — Tuabin gió

**Lớp duy nhất không thuộc polyphonic label set.**

| | |
|---|---|
| ✅ **Bao gồm** | Tiếng cánh tuabin gió quay · Nền hạ âm và tiếng lướt cánh tuần hoàn |
| ❌ **Không bao gồm** | Trực thăng → `propeller_aircrafts` · Quạt → `vacuum_cleaner_fan_hairdryer` · Gió qua cây → nền |
| 🔍 **Dấu hiệu phân biệt** | Xem B6. Đặc trưng: **nhịp lướt cánh rất chậm và đều** (bậc ~1 Hz), kéo dài liên tục, gần như không đổi theo thời gian |
| 📌 **Caption** | ✅ "Wind turbine blade noise is audible." |

> ⚠️ **Ràng buộc kỹ thuật quan trọng.** `wind_turbine` có `polyphonic: false`,
> nên head SED chính chỉ có 21 class. Mọi code lấy class list cho SED **phải**
> dùng `taxonomy.polyphonic_class_ids`, không dùng `taxonomy.class_ids`.
> Dùng nhầm sẽ làm lệch class order và checkpoint không khớp.

---

## 5. Nhóm D — Người và phương tiện truyền thông (2 lớp)

### D1. `voices` — Giọng nói

**Lớp lớn nhất DataSEC: 1,900 file = 37.6%.**

| | |
|---|---|
| ✅ **Bao gồm** | Nói chuyện · Gọi nhau · Trẻ em chơi · Đám đông nói · Nói qua loa |
| ❌ **Không bao gồm** | Hát và nhạc → `music` · Tiếng động vật → lớp sinh vật tương ứng |
| 🔍 **Dấu hiệu phân biệt** | **so với `music`:** giọng nói có **cấu trúc formant biến đổi nhanh, không theo cao độ nhạc**; hát có cao độ ổn định theo thang âm. Khi có cả hai → gán **cả hai** lớp chồng lấp |
| 📌 **Caption** | ✅ "People are talking." ❌ Bất kỳ trích dẫn nội dung lời nói nào — vi phạm phạm vi riêng tư ([SYSTEM.md](SYSTEM.md) §1.6) |

> 🔒 **Ràng buộc riêng tư cứng.** Hệ thống chỉ phát hiện *sự hiện diện* của giọng
> nói. Không nhận dạng lời, không nhận dạng người nói, không suy đoán nội dung.
> Caption không bao giờ được chứa lời thoại.

---

### D2. `music` — Âm nhạc

**Lớp lớn thứ hai: 1,001 file = 19.8%.**

| | |
|---|---|
| ✅ **Bao gồm** | Nhạc phát qua loa · Nhạc cụ sống · Hát · Nhạc từ xe, quán, sự kiện |
| ❌ **Không bao gồm** | Nói → `voices` · Chuông → `bells` · Tiếng gõ không có giai điệu → theo nguồn thật |
| 🔍 **Dấu hiệu phân biệt** | Xem D1. Dấu hiệu chính: **nhịp đều và cao độ theo thang âm**, duy trì qua nhiều giây |
| 📌 **Caption** | ✅ "Music is playing." |

> ⚠️ **`voices` + `music` = 57.5% DataSEC.** Đây là lý do
> [ADR-0002](decisions/ADR-0002-encoder-va-nhanh-transfer.md) yêu cầu
> class-balanced sampling khi pretrain: không cân bằng thì encoder học chủ yếu
> phân biệt nói với nhạc, chứ không học đặc trưng tiếng ồn môi trường.

---

## 6. Nhóm E — Tín hiệu và xung (4 lớp)

### E1. `bells` — Chuông

| | |
|---|---|
| ✅ **Bao gồm** | Chuông nhà thờ · Chuông tháp · Chuông gió · Chuông cửa |
| ❌ **Không bao gồm** | Báo động → `sirens_and_alarms` · Còi xe → `horn` · Nhạc có chuông → `music` |
| 🔍 **Dấu hiệu phân biệt** | **Đuôi ngân tắt dần dài với phổ hài không điều hòa** — dấu hiệu đặc trưng của vật thể kim loại rung tự do. **so với `sirens_and_alarms`:** chuông **không trượt cao độ**, mỗi tiếng là một xung có đuôi; báo động lặp hoặc trượt liên tục |
| 📌 **Caption** | ✅ "A bell is ringing." |

---

### E2. `sirens_and_alarms` — Còi hú và báo động ⚠️ LỚP GỘP

| | |
|---|---|
| ✅ **Bao gồm** | Còi hú xe cứu thương/cứu hỏa/cảnh sát · Báo động cháy · Báo động chống trộm · Báo động lùi xe |
| ❌ **Không bao gồm** | Còi xe thường → `horn` · Chuông → `bells` |
| 🔍 **Dấu hiệu phân biệt** | Xem B3 và E1. Dấu hiệu chính: **cao độ trượt liên tục hoặc nhảy hai mức lặp lại**, kéo dài nhiều giây |
| 📌 **Caption** | Xem §7 |

**Subclass (DataSEC):** `Sirens` (68), `Alarms` (37).

---

### E3. `thunder_fireworks_gunshot` — Sấm, pháo hoa, tiếng súng ⚠️ LỚP GỘP

Lớp gộp **ba nguồn có bản chất hoàn toàn khác nhau**, chung nhau ở tính chất xung.

| | |
|---|---|
| ✅ **Bao gồm** | Sấm · Pháo, pháo hoa · Tiếng súng |
| ❌ **Không bao gồm** | Kính vỡ → `glass_breaking` · Cửa đóng sầm, đồ rơi → không có lớp riêng · Máy khoan phá → `workshop` |
| 🔍 **Dấu hiệu phân biệt** | **so với `glass_breaking`:** kính vỡ có **đuôi lách tách tần số cao kéo dài**; xung của lớp này có đuôi **vọng băng rộng hoặc ầm tần số thấp**, không có tiếng mảnh vụn. Trong nội bộ lớp: sấm **ầm, đuôi dài > 1 s, tần số thấp**; pháo hoa **chuỗi nhiều tiếng rải rác, có tiếng rít bay lên**; súng **đơn, khô, dốc đứng** |
| 📌 **Caption** | Xem §7 |

**Subclass (DataSEC):** `Gunshot` (141), `Fireworks` (68), `Thunder` (26).

> **Mất thông tin không khôi phục được.** Ở mức SED, ba nguồn này không tách được.
> Đây là một trong những hạn chế phải ghi vào báo cáo
> ([SYSTEM.md](SYSTEM.md) §11.3, mục 3).

---

### E4. `glass_breaking` — Kính vỡ

| | |
|---|---|
| ✅ **Bao gồm** | Cửa kính vỡ · Chai lọ vỡ · Kính xe vỡ · Tiếng mảnh vụn rơi sau va đập |
| ❌ **Không bao gồm** | Sấm/pháo/súng → `thunder_fireworks_gunshot` · Đồ vật rơi không phải kính → không có lớp riêng |
| 🔍 **Dấu hiệu phân biệt** | Xem E3. Dấu hiệu quyết định: **đuôi lách tách tần số cao kéo dài > 0.5 s** do mảnh vụn |
| 📌 **Caption** | ✅ "Glass breaking is audible." ❌ "A window was smashed during a break-in" — vi phạm N1 |

---

## 7. Hai lớp gộp — chính sách caption bắt buộc

Đây là phần vận hành trực tiếp nguyên tắc N2 và ràng buộc G1/G3.

### 7.1 `sirens_and_alarms`

| Tình huống bằng chứng | Caption hợp lệ | Caption KHÔNG hợp lệ |
|---|---|---|
| Chỉ có coarse SED | "A siren- or alarm-like sound is audible." | "An ambulance drives past." · "A fire alarm goes off." |
| Có subclass prediction | "A siren- or alarm-like sound is audible. The classifier favors *sirens* (0.83), but DataSED provides no subclass ground truth for this interval." | "A siren sounds." (bỏ mất phần không kiểm chứng được) |

### 7.2 `thunder_fireworks_gunshot`

| Tình huống bằng chứng | Caption hợp lệ | Caption KHÔNG hợp lệ |
|---|---|---|
| Chỉ có coarse SED | "An impulsive sound resembling thunder, fireworks, or a gunshot is detected." | "A gunshot is heard." · "Fireworks are being set off." |
| Có subclass prediction | "An impulsive sound is detected. The classifier favors *fireworks* (0.71), but DataSED provides no subclass ground truth for this interval." | "Fireworks (71% confidence)." |

**Vì sao câu "nhưng DataSED không có subclass ground truth" là bắt buộc, không
phải tùy chọn:** không có nó, người đọc caption sẽ hiểu subclass đã được xác nhận.
Đó chính là loại hallucination mà C2 đo. Mệnh đề này là một phần của contract, và
phải có test kiểm.

---

## 8. Bảng tra nhanh cặp dễ nhầm

Dán bảng này cạnh màn hình khi phân tích ma trận nhầm lẫn.

| Cặp | Câu hỏi quyết định | Trả lời → lớp |
|---|---|---|
| `vehicle_pass_by` ↔ `vehicle_idling` | Đường bao có **tăng–đỉnh–giảm** trong vài giây không? | Có → `vehicle_pass_by` · Phẳng, kéo dài → `vehicle_idling` |
| `horn` ↔ `sirens_and_alarms` | Cao độ **cố định** hay **trượt/nhảy lặp**? | Cố định → `horn` · Trượt → `sirens_and_alarms` |
| `bells` ↔ `sirens_and_alarms` | Có **đuôi ngân tắt dần** sau mỗi tiếng? | Có → `bells` · Lặp/trượt liên tục → `sirens_and_alarms` |
| `glass_breaking` ↔ `thunder_fireworks_gunshot` | Có **đuôi lách tách tần số cao > 0.5 s**? | Có → `glass_breaking` · Đuôi vọng/ầm → `thunder_fireworks_gunshot` |
| `jet_aircrafts` ↔ `propeller_aircrafts` | Có **nhịp đập tuần hoàn** của cánh quạt? | Có → `propeller_aircrafts` · Rít băng rộng liên tục → `jet_aircrafts` |
| `propeller_aircrafts` ↔ `wind_turbine` | Nhịp **nhanh và biến thiên** hay **rất chậm, đều**? | Nhanh/biến thiên → `propeller_aircrafts` · Chậm, đều → `wind_turbine` |
| `voices` ↔ `music` | Cao độ theo **thang âm và nhịp đều** không? | Có → `music` · Formant biến đổi nhanh → `voices` |
| `birds` ↔ `crows_seagulls_magpies` | Tiếng **khàn, gắt, không giai điệu**? | Có → `crows_seagulls_magpies` · Có cấu trúc hài, cao độ rõ → `birds` |
| `birds` ↔ `cicadas_and_crickets` | Có **khoảng lặng giữa các nốt**? | Có → `birds` · Liên tục, phổ hẹp → `cicadas_and_crickets` |
| `chicken_coop` ↔ `birds` | Nhịp **cục tác lặp không đều**, nhiều con, phổ thấp? | Có → `chicken_coop` · Hót có giai điệu → `birds` |
| `dog_barkings_and_howlings` ↔ `cat_fights_and_moans` | Xung **dốc, ngắn, lặp** hay **kéo dài, trượt cao độ**? | Dốc, ngắn → chó · Kéo dài, trượt → mèo |
| `workshop` ↔ `lawn_mower…` | Có **va đập kim loại / chu kỳ bật-tắt**? | Có → `workshop` · Động cơ rú theo tải → `lawn_mower…` |
| `workshop` ↔ `vacuum_cleaner…` | Nền khí **ổn định, không va đập**? | Có → `vacuum_cleaner…` · Có va đập → `workshop` |
| `vehicle_idling` ↔ `workshop` | Có **chuỗi hài của tần số nổ** động cơ đốt trong? | Có → `vehicle_idling` · Phổ ổn định/xung lặp → `workshop` |
| `train` ↔ `vehicle_pass_by` | Kéo dài **hàng chục giây** với nhịp bánh trên ray? | Có → `train` · Vài giây → `vehicle_pass_by` |

> ⚠️ Bảng trên dựa trên **đặc trưng âm học**, chưa dựa trên ma trận nhầm lẫn đo
> được của model trên đề tài này. Sau khi có phân tích lỗi (E4), bảng phải được
> cập nhật bằng các cặp **thực sự** bị nhầm, kèm số lượt. Đó mới là nguồn chân lý
> cho `confusable_with`.

---

## 9. Quy ước xuyên suốt

1. **Sự kiện chồng nhau thì giữ tất cả.** Polyphonic cho phép chồng lấp — không
   chọn một. Một recording có thể đồng thời có `voices` + `music` + `vehicle_pass_by`.
2. **Không dịch `class_id`.** Chúng là định danh: luôn `glass_breaking`, không bao
   giờ `kinh_vo`.
3. **Giữ nhãn nguồn nguyên văn.** `source_label` và `canonical_class_id` cùng tồn
   tại trong mọi annotation ([annotation_guideline.md](annotation_guideline.md) §3).
4. **Không tự tách lớp gộp.** Xem §7.
5. **Nhãn ngoài taxonomy làm pipeline fail**, không được tự ánh xạ mềm.
   `scripts/audit_archive.py` trả verdict `fail_unmapped_label`.
6. **Class order chỉ đến từ config.** Không hardcode danh sách lớp ở bất kỳ đâu.

---

## 10. Mapping policy

```text
source label → canonical coarse ID → optional subclass ID
```

| # | Quy tắc |
|---:|---|
| 1 | `source_label` luôn được lưu nguyên văn, kể cả khi sai chính tả so với paper |
| 2 | Mapping là file config có version và checksum: `ml/configs/taxonomy.yaml` |
| 3 | Alias được chuẩn hóa bằng `normalize_text()`: NFKD → ASCII → lowercase → `[^a-z0-9]+` thành `_` |
| 4 | Alias trùng nhau giữa hai lớp làm `load_taxonomy()` raise `Ambiguous taxonomy alias` |
| 5 | Unknown source label làm pipeline fail ở bước validation |
| 6 | **Không đổi class order sau khi đã train checkpoint** — thay đổi tạo taxonomy version mới |
| 7 | Caption lexicon và frontend đọc cùng canonical config, không tự khai hằng số |

**Ví dụ chuẩn hóa alias — vì sao layout DataSEC không cần sửa tay:**

```text
"Vehicle pass-by"      → vehicle_pass_by       ✅ khớp class_id
"car pass-by"          → car_pass_by           ✅ khớp subclass
"Cat fights and moans" → cat_fights_and_moans  ✅ khớp alias (source là số ít)
"vacuum cleaner"       → vacuum_cleaner        ✅ khớp subclass
```

Archive dùng lẫn lộn Title Case và lowercase (`Brush cutter` nhưng `fan`,
`car truck idling`). `normalize_text()` xử lý được toàn bộ — đã xác minh
22/22 coarse và 10/10 nhóm subclass.

---

## 11. Versioning

```text
major.minor
```

| Phần | Thay đổi khi |
|---|---|
| **Major** | Đổi class set, hierarchy hoặc semantics của lớp |
| **Minor** | Thêm alias hoặc caption phrase mà **không** đổi target IDs |

Checkpoint lưu `taxonomy_sha256`. Load checkpoint với taxonomy khác hash phải
cảnh báo, và nếu khác major thì phải từ chối.

### Điều kiện lên version 1.0

| # | Điều kiện | Trạng thái |
|---:|---|---|
| 1 | 22 coarse class xác minh từ archive thật | ✅ |
| 2 | 28 subclass xác minh từ archive thật | ✅ |
| 3 | Mọi source label ánh xạ được, 0 unmapped | ✅ |
| 4 | `wind_turbine` xác nhận ngoài polyphonic label set | ✅ |
| 5 | Caption lexicon cho 22 lớp đã viết và có test | ○ |
| 6 | Lexicon cấm (ràng buộc G3) đã viết và có test | ○ |
| 7 | `confusable_with` cập nhật từ ma trận nhầm lẫn thật | ○ |

Điều kiện 1–4 pass tại `3c80110`. **Taxonomy giữ version `0.1`** cho đến khi
5–7 xong, vì caption lexicon là một phần của semantics lớp.
