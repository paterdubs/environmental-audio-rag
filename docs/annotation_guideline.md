# annotation_guideline.md — Quy ước xử lý nhãn

> **Dự án không tổ chức gán nhãn mới.** DataSEC và DataSED có annotation công bố.
> Tài liệu này quy định cách **nhập, chuẩn hóa, kiểm lỗi và bảo toàn** nhãn nguồn
> — không phải hướng dẫn cho người gán nhãn.
>
> Ý nghĩa từng lớp: [taxonomy.md](taxonomy.md). Quy trình dữ liệu:
> [DATA_PLAN.md](DATA_PLAN.md).

---

## 1. Nguồn chân lý

| Cấp | Nguồn | Tính chất |
|---|---|---|
| 1 | Raw annotation trong archive | **Bất biến** |
| 2 | Canonical annotation | Sinh bằng script từ cấp 1 + taxonomy có version |
| 3 | Prediction của model | Không bao giờ ghi đè cấp 1 hoặc 2 |

**Không sửa raw CSV, filename hoặc timestamp bằng tay.** Nếu cần sửa, sửa script
sinh cấp 2 và chạy lại, để thao tác tái lập được.

---

## 2. Hai cơ chế nhãn khác nhau

### 2.1 DataSEC — nhãn nằm trong đường dẫn

```text
DATASEC/<coarse label>/<file>.wav              # 12 lớp không subclass
DATASEC/<coarse label>/<subclass>/<file>.wav   # 10 lớp có subclass
```

Không có bảng annotation nào. **Cây thư mục chính là ground truth.**

Hệ quả cho parser:

| # | Quy tắc |
|---:|---|
| 1 | Độ sâu đường dẫn quyết định có subclass hay không — không dựa vào danh sách cứng |
| 2 | Tên thư mục lẫn Title Case và lowercase (`Brush cutter` nhưng `fan`) — phải chuẩn hóa |
| 3 | Chuẩn hóa bằng `normalize_text()`, không tự viết lại |
| 4 | Nhãn không ánh xạ được → **pipeline fail**, không ánh xạ mềm |

### 2.2 DataSED — nhãn nằm trong CSV

```text
SED_ground_truth/Polyphonic_sound_detection.csv
SED_ground_truth/Monophonic_sound_detection.csv
```

Schema:

```text
sound_name,class_name,start_perc,end_perc,start_time,end_time,event_length
S-0001.wav,Birds,0.00,0.30,0.00,17.60,17.60
```

> ⚠️ **Dùng `start_time`/`end_time` (giây) làm nguồn chân lý.**
>
> `start_perc`/`end_perc` làm tròn 2 chữ số thập phân. Trên recording dài 93.8 s,
> sai số tối đa là `0.005 × 93.8 ≈ 0.47 s` mỗi biên, tức gần 1 s cho cả event —
> lớn hơn collar 0.2 s của event-based F1. Dùng phần trăm sẽ phá metric một cách
> im lặng.
>
> `event_length` là trường dẫn xuất. Kiểm chéo với `end_time − start_time`; lệch
> quá tolerance thì ghi cảnh báo, **không** tự sửa.

---

## 3. Canonical contracts theo dataset

DataSEC là bài toán clip classification: archive không cung cấp onset/offset.
Không được bịa event timeline cho DataSEC chỉ để dùng chung một schema với
DataSED. Hai output canonical dùng chung provenance và taxonomy, nhưng có đơn vị
nhãn khác nhau.

### 3.1 DataSEC clip-label contract

Mỗi audio DataSEC sau canonicalize phải giữ tối thiểu:

```text
file_id              datasec:<relative_path>
source_dataset       datasec
source_path          <relative_path trong archive>
source_coarse_label  <tên thư mục nguyên văn>
canonical_class_id   <class_id từ taxonomy>
source_subclass_label <tên thư mục nguyên văn | null>
canonical_subclass_id <subclass_id | null>
taxonomy_version     0.1
```

`source_path` cùng hai trường `source_*_label` là lineage để audit lại cây thư
mục. `canonical_subclass_id = null` là hợp lệ với lớp không có subclass; nó
không có nghĩa là model dự đoán "không xác định".

### 3.2 DataSED event contract

Mỗi annotation canonical phải có đủ 8 trường:

```text
recording_id        datased:S-0001
source_dataset      datased
source_label        Birds              ← NGUYÊN VĂN, không chuẩn hóa
canonical_class_id  birds
onset_s             0.0
offset_s            17.6
label_mode          polyphonic | monophonic
taxonomy_version    0.1
```

**`source_label` và `canonical_class_id` cùng tồn tại.** Mất `source_label` là
mất khả năng kiểm tra lại mapping và mất khả năng phát hiện lỗi taxonomy. Một
event canonical phải truy ngược được về dòng CSV nguồn; nếu implementation cần
một định danh, nó phải sinh xác định từ file CSV, số dòng nguồn và taxonomy hash,
không dựa vào thứ tự đọc ngẫu nhiên.

### Ràng buộc

| # | Ràng buộc | Vi phạm thì |
|---:|---|---|
| 1 | `0 <= onset_s < offset_s` | `exclude_invalid_time` |
| 2 | `offset_s <= duration_s + tolerance` | `exclude_invalid_time` |
| 3 | `canonical_class_id` thuộc taxonomy | **Pipeline fail** |
| 4 | `recording_id` tồn tại trong inventory | `exclude_orphan_annotation` |
| 5 | Overlap hợp lệ ở polyphonic mode | — |
| 6 | Monophonic và polyphonic **không trộn** trong cùng evaluation run | Lỗi cấu hình |

Ràng buộc 6 đáng nhấn: hai label mode có số lớp khác nhau (21 vs 22) và định
nghĩa nhãn khác nhau. Trộn chúng cho ra một con số không diễn giải được.

Mọi canonical output đều phải kèm `taxonomy_version` và hash của taxonomy ở
manifest/provenance của lần sinh. Thay taxonomy, parser hoặc raw input là tạo
artifact mới; không sửa đè artifact cũ.

---

## 4. Hai label mode

### Polyphonic — benchmark chính

Giữ **mọi** target event được annotate, kể cả chồng lấp. 4,034 event / 21 class /
703 recording.

`wind_turbine` không thuộc label set này — SED head phải dùng
`taxonomy.polyphonic_class_ids` (21), không dùng `taxonomy.class_ids` (22).

### Monophonic — benchmark phụ

Chỉ giữ nguồn chiếm ưu thế theo annotation công bố. 4,309 event / 22 class /
717 recording.

> **Không diễn giải monophonic là ground truth đầy đủ của soundscape.** Nó là một
> *chính sách gán nhãn* (giữ nguồn trội), không phải mô tả đầy đủ những gì nghe
> được. Recording có 3 nguồn chồng lấp vẫn chỉ có 1 nhãn monophonic.

### 14 recording không có polyphonic event

703/717 recording có polyphonic label. **14 recording còn lại được GIỮ** làm
recording âm tính, không bị loại.

Loại chúng sẽ làm false-positive rate trông tốt hơn thực tế — một hệ thống SED
phải đúng cả khi không có gì xảy ra.

---

## 5. Lớp gộp — không tự tách

Không nghe rồi tách thủ công:

- `sirens_and_alarms`
- `thunder_fireworks_gunshot`
- Các lớp máy móc/giao thông gộp khác

DataSEC subclass label có thể huấn luyện classifier riêng, nhưng **prediction
không thay thế DataSED ground truth**. Xem
[ADR-0006](decisions/ADR-0006-danh-gia-subclass.md).

---

## 6. Rasterize onset/offset thành frame

Đây là nơi lỗi off-by-one gây sai metric mà không có triệu chứng.

### Quy tắc

| # | Quy tắc | Vì sao |
|---:|---|---|
| 1 | **Một hàm duy nhất** dùng chung cho train và evaluation | Hai hàm lệch 1 frame là đủ sai metric |
| 2 | Hàm đó phải có test biên | Lỗi biên là lỗi im lặng |
| 3 | Giữ onset/offset nguồn với độ chính xác ban đầu; chỉ rasterize khi tạo target | Rasterize sớm là mất thông tin vĩnh viễn |
| 4 | Event cắt qua window được clip vào window nhưng **giữ source event ID** | Để stitch lại được |
| 5 | Event chạm ranh giới **không** được nhân đôi khi stitch prediction | Nhân đôi làm insertion rate tăng giả |
| 6 | Padding mask **không** tính vào loss hoặc metric | Padding làm loãng cả loss lẫn F1 |

### Công thức

Với `frame_rate = sample_rate / hop_length = 16000 / 320 = 50` fps:

```text
frame_start = floor(onset_s  × frame_rate)
frame_end   = ceil (offset_s × frame_rate)
target[frame_start : frame_end, class_index] = 1
```

`floor` cho onset và `ceil` cho offset là lựa chọn có chủ ý: nó **không bao giờ
bỏ sót** phần event, thà thừa nửa frame còn hơn thiếu. Với event ngắn như
`glass_breaking` hoặc `Gunshot`, thiếu một frame là mất tỷ lệ lớn của event.

### Test biên bắt buộc

```text
onset đúng tại biên frame        → không lệch 1 frame
offset đúng tại biên frame       → không lệch 1 frame
event ngắn hơn 1 frame (< 20 ms) → vẫn tạo >= 1 frame dương
event vượt quá cuối recording    → clip vào duration, không raise
event bắt đầu tại 0.0            → frame 0 dương
event kết thúc đúng tại duration → frame cuối dương, không tràn
hai event cùng lớp liền kề       → không gộp ở bước rasterize
```

> ⚠️ Với 50 fps, mỗi frame là 20 ms. `Gunshot` dài ~100 ms chỉ có **5 frame**.
> Đây là rủi ro A5 trong [SYSTEM §11.2](SYSTEM.md).

---

## 7. QA verdict

| Verdict | Nghĩa | Hành động |
|---|---|---|
| `pass` | File và annotation hợp contract | Giữ |
| `quarantine_review` | Cần xem thêm, chưa dùng train/eval | Tách khỏi split |
| `exclude_corrupt` | Audio/CSV không đọc được | Loại, ghi reason |
| `exclude_silent` | Toàn zero hoặc toàn NaN | Loại |
| `exclude_invalid_time` | Timestamp không sửa được bằng quy tắc xác định | Loại event/file theo policy |
| `exclude_orphan_annotation` | Annotation trỏ tới file không tồn tại | Loại |
| `exclude_duplicate` | Bản sao thuộc group khác | Giữ một representative |
| `exclude_cross_dataset_leak` | Clip DataSEC trùng dev/test DataSED | Loại khỏi pretraining |

**Không có verdict "nhãn nghe không đúng" trong pipeline tự động.** Trường hợp
nghi ngờ được ghi vào phân tích lỗi, không sửa test tùy ý.

Mỗi exclusion ghi đủ: `file_id`, `stage`, `reason_code`, `detail`, `decided_by`,
`decided_at`.

---

## 8. Manual audit nhỏ

Nếu cần audit chất lượng dataset:

| # | Quy tắc |
|---:|---|
| 1 | Sample theo class, label mode và duration quantile — không sample ngẫu nhiên thuần |
| 2 | Người nghe **không được xem prediction của model** trước khi nghe |
| 3 | Chỉ đánh giá chất lượng dataset; **không** dùng kết quả để chọn model hay threshold |
| 4 | Báo tỷ lệ kèm cỡ mẫu và uncertainty, không suy rộng quá sample |
| 5 | Kết quả vào `docs/measurements/` và mục Hạn chế của báo cáo |

Quy tắc 2 chống confirmation bias: nếu đã thấy model nói `siren`, tai người sẽ
nghiêng về nghe ra `siren`.

---

## 9. Caption reference

Reference caption được **sinh xác định** từ ground-truth timeline để sanity check
harness đánh giá.

| Nó là | Nó không phải |
|---|---|
| Kiểm tra pipeline caption chạy đúng | Caption tự nhiên do người viết |
| Sàn so sánh cho grounding (hallucination = 0) | Chuẩn vàng về chất lượng ngôn ngữ |

**Không dùng metric n-gram so với reference này làm kết luận chính.** Không có một
cách diễn đạt duy nhất đúng cho một timeline, và điểm BLEU cao với một reference
nhân tạo không nói lên điều gì về chất lượng caption.

---

## 10. Checklist trước khi coi annotation là xong

- [x] Raw annotation giữ nguyên, có hash
- [x] Canonical annotation sinh bằng script
- [x] `source_label` và `canonical_class_id` cùng tồn tại
- [x] Mọi nhãn ánh xạ được vào taxonomy `0.1`, 0 unmapped
- [x] 6 ràng buộc event contract đã kiểm
- [x] 14 recording không có polyphonic event được giữ
- [ ] Hàm rasterize có test biên đầy đủ (8 case của §6)
- [ ] Padding mask được xác nhận không vào loss và metric
- [ ] `exclusions.csv` đã sinh và commit
