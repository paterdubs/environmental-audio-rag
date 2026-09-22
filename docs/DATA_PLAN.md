# DATA_PLAN.md — Kế hoạch chuẩn bị dữ liệu

> Tài liệu này nói **làm thế nào** để đi từ DOI công bố tới split đóng băng dùng
> được cho benchmark. Định nghĩa lớp: [taxonomy.md](taxonomy.md). Quy ước nhãn:
> [annotation_guideline.md](annotation_guideline.md). Hiện trạng có bằng chứng:
> [STATUS.md](STATUS.md).

---

## 0. Ba nguyên tắc bất khả xâm phạm

### N1 — Nhãn nguồn là bất biến

Raw annotation từ archive **không bao giờ** bị sửa. Canonical annotation được
*sinh* từ raw bằng script có version, và cả hai cùng tồn tại trong mọi bảng.

> **Vì sao:** đề tài dùng annotation công bố. Sửa nhãn để kết quả đẹp hơn là gian
> lận; sửa nhãn vì "nghe thấy sai" cũng không hợp lệ vì không có quy trình gán
> nhãn có kiểm soát để bảo chứng. Nghi ngờ nhãn thì ghi vào phân tích lỗi, không
> sửa dữ liệu.

### N2 — Chia tập theo nguồn gốc, không theo file

Đơn vị split là **duplicate/content group**, không phải file, không phải segment.
Hai file cùng nguồn phải nằm cùng một split, kể cả khi tên khác nhau.

> **Vì sao:** một recording bị cắt thành 5 đoạn rồi rải qua train/test làm test
> score cao giả tạo. Đây là dạng leakage phổ biến nhất và khó phát hiện nhất.

### N3 — Mọi file bị loại đều phải ghi lý do

Không có thao tác "bỏ bớt cho gọn". Mỗi exclusion ghi đủ:

```text
file_id, stage, reason_code, detail, decided_by, decided_at
```

> **Vì sao:** không có reason code thì không tái lập được dataset, và không trả
> lời được câu hỏi hội đồng "vì sao 5,048 file còn 4,900?".

---

## 1. Hai dataset, hai cơ chế nhãn khác nhau

| | DataSEC | DataSED |
|---|---|---|
| Record DOI | `10.5281/zenodo.17033970` | `10.5281/zenodo.15346092` |
| License | `cc-by-nc-sa-4.0` | `cc-by-nc-sa-4.0` |
| Archive bytes | 6,414,663,316 | 4,510,378,259 |
| MD5 | `29fa9b8cc84cfa69aa4e5e674e780383` | `44e093f675fc44cfb8a11b68456b72d7` |
| Audio | 5,048 WAV | 717 WAV |
| Giải nén | 7.01 GiB | 5.55 GiB |
| **Nhãn nằm ở** | **Cây thư mục** | **2 file CSV** |
| Loại nhãn | Clip-level, 2 cấp | Strong label onset/offset |
| Vai trò | Pretraining, classification, subclass | **Benchmark SED chính** |

Nguồn: [measurements/archive_audit_20260922.md](measurements/archive_audit_20260922.md).

### Ba sự thật phải biết trước khi viết bất kỳ script nào

**1. Không archive nào chứa LICENSE hoặc README.** Audit đếm 0 file documentation
trong cả hai ZIP. Hệ quả:

- License chỉ lấy được từ `data/reference/zenodo_<dataset>_<record>.json`.
- `copy_reference_files()` sẽ không tìm thấy gì để copy.
- Mọi quy trình giả định "đọc LICENSE trong archive" đều sai và phải bỏ.

**2. DataSEC mã hóa nhãn bằng đường dẫn:**

```text
DATASEC/<coarse label>/<file>.wav              # 12 lớp không subclass
DATASEC/<coarse label>/<subclass>/<file>.wav   # 10 lớp có subclass
```

Nên `ml/dataops/archive_audit.py` dùng `label_depth=1`. Không có bảng annotation
nào để đối chiếu — **cây thư mục chính là ground truth**.

**3. DataSED mã hóa nhãn bằng CSV**, nên `label_depth=None`:

```text
SED_wav/S-####.wav
SED_ground_truth/Polyphonic_sound_detection.csv
SED_ground_truth/Monophonic_sound_detection.csv
```

Schema:

```text
sound_name,class_name,start_perc,end_perc,start_time,end_time,event_length
S-0001.wav,Birds,0.00,0.30,0.00,17.60,17.60
```

> ⚠️ **Dùng `start_time`/`end_time` (giây) làm nguồn chân lý.** `start_perc` làm
> tròn 2 chữ số; trên recording 93.8 s sai số có thể tới 0.94 s — đủ để phá
> event-based F1 với collar 200 ms.

---

## 2. Provenance phải lưu

Mỗi archive cần đủ 8 trường trước khi được xử lý:

| # | Trường | Nguồn | Trạng thái |
|---:|---|---|---|
| 1 | Record DOI | Zenodo API | ✅ |
| 2 | Concept DOI | Zenodo API | ✅ |
| 3 | URL tải chính thức | `ml/configs/sources.yaml` | ✅ |
| 4 | Ngày tải | Thời điểm chạy `data_sources download` | ◐ |
| 5 | Size + MD5 archive | `sources.yaml` + verify thật | ✅ |
| 6 | **License + hash** | **Zenodo record JSON** (không phải archive) | ✅ |
| 7 | README | Không tồn tại — ghi `absent` | ✅ |
| 8 | File count, duration, schema version sau giải nén | Inventory | ✅ DataSED · ○ DataSEC |

**Không suy license từ tên repository.** License phải đọc từ record metadata đã
lưu, và hash của file metadata đó phải được ghi lại.

---

## 3. Ràng buộc license CC-BY-NC-SA-4.0

| Thành phần | Hệ quả cụ thể |
|---|---|
| **BY** | Trích dẫn cả hai DOI trong báo cáo, README và `data/reference/` |
| **NC** | Khóa luận học thuật hợp lệ. Không dùng artifact cho mục đích thương mại |
| **SA** | **Derivative phải cùng license** |

### SA áp lên cái gì

| Artifact | SA áp? | Xử lý |
|---|:---:|---|
| Log-mel feature | Có | Không công bố, hoặc công bố dưới CC-BY-NC-SA-4.0 |
| Checkpoint train trên dữ liệu này | Có | Nếu công bố thì dưới CC-BY-NC-SA-4.0, **không** MIT/Apache |
| Caption sinh từ dữ liệu | Có | Cùng license |
| Manifest, split, hash | Có | Đã commit; nêu license trong `data/README.md` |
| **Code pipeline** | Không | Tác phẩm độc lập, license riêng được |

> Đây là điều dễ sai nhất khi công bố kèm khóa luận: đưa checkpoint lên GitHub
> dưới MIT là vi phạm SA.

---

## 4. Layout thư mục

```text
data/
├── raw/                          # KHÔNG commit
│   ├── datasec/
│   │   ├── archives/DATASEC.zip
│   │   └── extracted/
│   └── datased/
│       ├── archives/DataSED….zip
│       └── extracted/
├── interim/                      # KHÔNG commit — audio/label chuẩn hóa
├── features/                     # KHÔNG commit — tensor
├── manifests/                    # COMMIT
│   ├── <ds>_archive_audit.json       # cổng D0/D1 trước giải nén
│   ├── <ds>_inventory.csv            # một dòng / file audio
│   ├── <ds>_inventory_summary.json
│   ├── <ds>_recordings.csv
│   ├── <ds>_preparation_audit.json
│   ├── <ds>_logmel_v1.{csv,json}
│   ├── duplicate_groups.csv          # ○ cổng D3
│   └── exclusions.csv                # ○ N3
├── annotations/                  # COMMIT
│   ├── datased_polyphonic_events.csv
│   └── datased_monophonic_events.csv
├── reference/                    # COMMIT — Zenodo metadata, license
└── splits/                       # COMMIT — ID đóng băng + hash
```

**Quy tắc:** mọi thứ không commit phải **tái tạo được bằng một lệnh**. Danh sách
lệnh: [CLAUDE.md](../CLAUDE.md) §7.

---

## 5. Schema manifest

### 5.1 `<ds>_inventory.csv` — một dòng cho mỗi file audio

Sinh bởi `ml/dataops/inventory.py::build_inventory`.

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `dataset` | str | `datasec` \| `datased` |
| `file_id` | str | `<dataset>:<relative_path>` — khóa chính toàn hệ thống |
| `relative_path` | str | POSIX, tương đối so với `extracted/` |
| `bytes` | int | |
| `sha256` | str | **Tầng T1 của dedup** |
| `sample_rate` | int | |
| `channels` | int | |
| `frames` | int | |
| `duration_s` | float | |
| `format`, `subtype` | str | Từ `soundfile.info` |

### 5.2 `duplicate_groups.csv` — cổng D3 ○

| Cột | Ghi chú |
|---|---|
| `group_id` | `DUP-<tier>-<nnnn>` |
| `file_id` | Thành viên |
| `tier` | `T1` \| `T2` \| `T3` |
| `similarity` | 1.0 cho T1/T2; điểm fingerprint cho T3 |
| `representative` | bool — đúng một `true` mỗi group |
| `cross_dataset` | bool — **cờ quan trọng nhất của file này** |

### 5.3 `exclusions.csv` — N3

| Cột | Ghi chú |
|---|---|
| `file_id` | |
| `stage` | `inventory` \| `annotation` \| `dedup` \| `split` |
| `reason_code` | Xem §9 |
| `detail` | Mô tả ngắn, máy sinh |
| `decided_by` | `script:<tên>` hoặc `human:<tên>` |
| `decided_at` | ISO-8601 UTC |

---

## 6. Quy trình thu nhận

```text
D0  fetch metadata  →  verify size + MD5  →  archive audit (chưa giải nén)
D1  extract         →  inventory          →  validate từng file
D2  parse annotation →  canonicalize      →  annotation contract
D3  dedup T1/T2/T3  →  duplicate_groups.csv
D4  split           →  leakage check      →  freeze + SHA-256
D5  loader tests    →  frame alignment
```

### D0 — Metadata và toàn vẹn archive ✅

```bash
.venv/Scripts/python.exe -m scripts.data_sources metadata datasec datased
.venv/Scripts/python.exe -m scripts.audit_archive datasec
.venv/Scripts/python.exe -m scripts.audit_archive datased --labels-in-annotations
```

| Điều kiện pass | DataSEC | DataSED |
|---|:---:|:---:|
| Size khớp `sources.yaml` | ✅ | ✅ |
| MD5 khớp | ✅ | ✅ |
| Zenodo metadata đã lưu | ✅ | ✅ |
| Mọi nhãn trong layout ánh xạ được taxonomy | ✅ 22+28 | n/a (nhãn trong CSV) |
| Verdict | `pass` | `pass` |

**Archive audit chạy trước giải nén là có chủ ý:** phát hiện archive hỏng hoặc
nhãn lạ mà không tốn 7 GiB I/O và vài phút giải nén.

### D1 — Giải nén và inventory

```bash
.venv/Scripts/python.exe -m scripts.data_sources extract datasec
.venv/Scripts/python.exe -m scripts.build_inventory datasec
```

Kiểm mỗi file audio:

| # | Kiểm | Fail thì |
|---:|---|---|
| 1 | Đọc được toàn bộ, không lỗi decode | `exclude_corrupt` |
| 2 | `frames > 0`, không zero-byte | `exclude_corrupt` |
| 3 | Không toàn NaN hoặc toàn zero | `exclude_silent` |
| 4 | `sample_rate`, `channels`, `duration_s` hữu hạn | `exclude_corrupt` |
| 5 | Hash SHA-256 tính được | `exclude_corrupt` |

**Không ép số file theo paper.** Nếu archive có 5,048 file mà paper nói khác, ghi
cả hai và nêu chênh lệch. Archive đã tải là sự thật kiểm chứng được; paper thì không.

### D2 — Annotation contract ✅ (DataSED)

| # | Ràng buộc | Fail thì |
|---:|---|---|
| 1 | `0 <= onset_s < offset_s` | `exclude_invalid_time` |
| 2 | `offset_s <= duration_s + tolerance` | `exclude_invalid_time` |
| 3 | `class_name` ánh xạ được vào taxonomy | **Pipeline fail** — không tự ánh xạ mềm |
| 4 | `sound_name` tồn tại trong inventory | `exclude_orphan_annotation` |
| 5 | Polyphonic và monophonic không trộn trong cùng run | Lỗi cấu hình |

Kết quả đã đo: 4,034 polyphonic event / 21 class / 703 recording;
4,309 monophonic event / 22 class / 717 recording.

**14 recording không có polyphonic event được GIỮ** làm recording âm tính. Loại
chúng sẽ làm false-positive rate trông tốt hơn thực tế.

---

## 7. Khử trùng lặp và chống rò rỉ — cổng D3 ◐

**Đây là cổng đang chặn và là rủi ro lớn nhất của RQ1.**

### 7.1 Vì sao rủi ro cao hơn bình thường

| Bằng chứng | Hệ quả |
|---|---|
| Cùng 6 tác giả: Fredianelli, Artuso, Pompei, Licitra, Iannace, Akbaba | Nhiều khả năng cùng chiến dịch đo |
| Cùng miền: tiếng ồn môi trường ngoài trời | Cùng loại nguồn, cùng loại thiết bị |
| Công bố cách nhau 4 tháng (2025-05-05 → 2025-09-02) | Có thể tái sử dụng bản ghi |
| Cùng ontology 22 lớp | Thiết kế liên quan nhau |

**Giả định mặc định phải là "có khả năng trùng nguồn"** cho tới khi đo được ngược
lại. Không phải ngược lại.

### 7.2 Ba tầng phát hiện

| Tầng | Bắt được | Phương pháp | Ngưỡng | Trạng thái |
|---|---|---|---|---|
| **T1** | File byte-identical | SHA-256 trên bytes | Khớp tuyệt đối | ✅ DataSED: 8 nhóm × 2 |
| **T2** | Cùng nội dung, khác container/encode | SHA-256 trên **PCM đã decode + resample 16 kHz mono** | Khớp tuyệt đối | ○ |
| **T3** | Cùng nguồn, khác đoạn cắt hoặc xử lý | Fingerprint phổ + so khớp | Xem 7.3 | ○ |

**T2 tồn tại vì T1 không đủ:** cùng một bản ghi lưu WAV 16-bit và WAV 24-bit có
SHA-256 khác nhau nhưng nội dung âm thanh giống hệt. DataSEC 16 kHz và DataSED
44.1 kHz càng làm T1 vô dụng cho so sánh xuyên dataset.

### 7.3 T3 — fingerprint âm học

```text
1. Chuẩn hóa: 16 kHz mono, peak-normalize
2. Chia frame 1 s, hop 0.5 s
3. Với mỗi frame: MFCC 20 chiều + delta → vector 40 chiều
4. Fingerprint file = chuỗi vector đã chuẩn hóa L2
5. So khớp hai file: trượt cửa sổ, tính cosine similarity trung bình
   trên đoạn chồng lấp dài nhất
```

| Quyết định | Điều kiện |
|---|---|
| `duplicate` | similarity ≥ 0.95 **và** đoạn chồng lấp ≥ 3 s |
| `review` | 0.85 ≤ similarity < 0.95 **và** đoạn chồng lấp ≥ 3 s |
| `distinct` | Còn lại |

> ⚠️ Ngưỡng 0.95/0.85 là **điểm khởi đầu cần hiệu chuẩn**, không phải hằng số có
> cơ sở. Cách hiệu chuẩn: lấy 8 nhóm T1 đã biết của DataSED làm positive, lấy
> cặp ngẫu nhiên khác lớp làm negative, chọn ngưỡng tách hai phân bố. Kết quả
> hiệu chuẩn phải ghi vào `docs/measurements/`.

`review` **không** được tự động xử lý. Người xem, quyết định, ghi vào
`exclusions.csv` với `decided_by: human:<tên>`.

### 7.4 Ba kiểm tra phải chạy

| # | Kiểm tra | Mục đích | Trạng thái |
|---:|---|---|---|
| 1 | Duplicate trong DataSEC | Tránh cùng clip ở train và test của classification | ○ |
| 2 | Duplicate trong DataSED | Tránh cùng recording xuyên split SED | ✅ T1 |
| 3 | **Duplicate xuyên DataSEC–DataSED** | **Tránh pretraining trên test của SED** | ○ |

### 7.5 Luật xử lý

```text
Với mỗi duplicate group G:

  Nếu G chỉ nằm trong một dataset:
      → Giữ một representative, các bản còn lại: exclude_duplicate
      → CẢ GROUP phải cùng một split

  Nếu G có thành viên ở CẢ HAI dataset (cross_dataset = true):
      Gọi R = tập recording DataSED trong G
      Nếu R giao với (dev ∪ test) của DataSED:
          → LOẠI toàn bộ clip DataSEC trong G khỏi pretraining
          → reason_code: exclude_cross_dataset_leak
      Ngược lại (R chỉ nằm trong train):
          → GIỮ, nhưng ghi group vào duplicate_groups.csv
          → Nêu trong báo cáo: có N clip trùng với train
```

### 7.6 Ngưỡng báo động

| Tỷ lệ clip DataSEC trùng với dev/test DataSED | Hành động |
|---|---|
| 0% | RQ1 hợp lệ như thiết kế |
| < 1% | Loại, ghi số vào báo cáo, RQ1 vẫn hợp lệ |
| 1–5% | Loại, **chạy lại nhánh C**, nêu rõ trong Hạn chế |
| > 5% | **Δ transfer không còn diễn giải được như transfer.** Báo cáo trung thực là leakage; RQ1 chuyển thành kết quả âm tính |

> Kết quả âm tính ở đây **là một kết quả hợp lệ của khóa luận**, không phải thất
> bại. Nó chứng minh một điều có giá trị: đo transfer giữa hai dataset cùng nhóm
> tác giả mà không audit là không đáng tin.

---

## 8. Split — cổng D4 ○

### 8.1 Nguyên tắc chung

| | DataSEC | DataSED |
|---|---|---|
| Đơn vị split | Duplicate/content group | **Recording group** |
| Tỉ lệ | 70/15/15 | 70/15/15 |
| Phương pháp | Stratify coarse (+subclass nếu đủ mẫu) | Iterative multilabel stratification |
| Seed | 20260922 | 20260922 |
| Hiện trạng | ○ | ◐ candidate 435/142/140 |

Cài đặt: `ml/dataops/splits.py::grouped_multilabel_split`. Hàm **ép** mỗi item
thuộc đúng một group và raise nếu vi phạm — đó là hàng rào chống N2 ở mức code.

### 8.2 DataSED

- Đơn vị: **recording**, không phải event, không phải window.
- Iterative multilabel stratification theo event presence (21 nhãn nhị phân).
- Giữ phân bố class, duration và polyphony gần nhau giữa ba split.
- Candidate SHA-256:
  `656c1851de7c22a5eb6b2c2dc2b20397ad1bce98b136c591b7fe68b88cd130b1`.

**Split hiện tại CHƯA freeze.** Phải chạy lại sau D3 vì duplicate group có thể
buộc recording đổi split.

### 8.3 DataSEC — vấn đề low-support

Split 70/15/15 trên 4 subclass nhỏ nhất:

| Subclass | Files | train / dev / test |
|---|---:|---|
| `Crickets` | 20 | 14 / 3 / 3 |
| `Olive shaker` | 20 | 14 / 3 / 3 |
| `Magpies` | 21 | 14 / 3 / 4 |
| `Lawn mower` | 21 | 14 / 3 / 4 |

Ba lựa chọn, và lý do chọn phương án 1:

| # | Phương án | Đánh giá |
|---:|---|---|
| **1** | **Giữ 70/15/15, báo low-support riêng bằng số tuyệt đối** | ✅ Chọn. Giữ được một quy tắc split duy nhất; trung thực về giới hạn |
| 2 | Tỉ lệ riêng cho subclass nhỏ (50/25/25) | ❌ Hai quy tắc split trong một dataset, khó giải thích và khó tái lập |
| 3 | Gộp 4 subclass nhỏ vào "other" | ❌ Làm hỏng cấu trúc hierarchy, ảnh hưởng RQ4 |

Chi tiết cách báo cáo: [evaluation_protocol.md](evaluation_protocol.md) §4.

### 8.4 Leakage check bắt buộc trước freeze

| # | Kiểm | Pass khi |
|---:|---|---|
| 1 | Không group nào xuất hiện ở hai split | 0 vi phạm |
| 2 | Không `sha256` nào xuất hiện ở hai split | 0 vi phạm |
| 3 | Không cặp T2/T3 duplicate nào xuyên split | 0 vi phạm |
| 4 | Mọi class có ≥ 1 mẫu ở mỗi split | 0 class rỗng, hoặc ghi rõ ngoại lệ |
| 5 | Clip DataSEC trùng dev/test DataSED đã bị loại | Đếm = 0 sau khi lọc |

**Tỉ lệ chỉ được đổi bằng ADR, và chỉ trước khi xem test metrics.**

---

## 9. Bảng mã lý do loại trừ

| `reason_code` | Giai đoạn | Nghĩa |
|---|---|---|
| `exclude_corrupt` | inventory | Không đọc được, zero-byte, decode lỗi |
| `exclude_silent` | inventory | Toàn zero hoặc toàn NaN |
| `exclude_invalid_time` | annotation | Timestamp không sửa được bằng quy tắc xác định |
| `exclude_orphan_annotation` | annotation | Annotation trỏ tới file không tồn tại |
| `exclude_unmapped_label` | annotation | Nhãn ngoài taxonomy — **pipeline fail, không tự ánh xạ** |
| `exclude_duplicate` | dedup | Bản sao trong cùng dataset; giữ representative |
| `exclude_cross_dataset_leak` | dedup | Clip DataSEC trùng dev/test DataSED |
| `quarantine_review` | dedup | T3 rơi vào vùng 0.85–0.95, chờ người quyết |

---

## 10. QA thay cho relabeling

**Không nghe và gán lại toàn bộ dataset.** Đề tài chấp nhận annotation công bố.
QA giới hạn ở bốn việc, và **không việc nào sửa nhãn**:

| # | Phạm vi | Mục đích | Kết quả dùng để |
|---:|---|---|---|
| 1 | 1–2% sample ngẫu nhiên theo class | Ước lượng chất lượng dataset | Viết vào Hạn chế |
| 2 | Toàn bộ annotation invalid theo D2 | Xác nhận luật loại đúng | Điều chỉnh luật, không sửa nhãn |
| 3 | Candidate duplicate vùng `review` | Quyết định T3 | `exclusions.csv` |
| 4 | Duration outlier (ngoài 1.5×IQR) | Phát hiện lỗi parse | Sửa parser, không sửa nhãn |

**Ràng buộc cho người nghe:** không được xem prediction của model trước khi nghe.
Kết quả QA **không** được dùng để chọn model hay threshold.

> Không có verdict "nhãn nghe không đúng" trong pipeline tự động. Nghi ngờ được
> ghi vào phân tích lỗi, không sửa test tùy ý.

---

## 11. Segmentation và frame alignment — cổng D5 ◐

| # | Quy tắc | Vì sao |
|---:|---|---|
| 1 | Raw recording giữ nguyên, không cắt sẵn ra đĩa | Cắt sẵn khóa cứng window size vào dữ liệu |
| 2 | Training window tạo động hoặc qua manifest tái lập được | Đổi window không phải sinh lại dataset |
| 3 | Window overlap **không** được làm cùng recording xuyên split | N2 |
| 4 | Target frame tạo từ onset/offset bằng **một hàm duy nhất** dùng chung train và eval | Hai hàm khác nhau lệch 1 frame là đủ sai metric |
| 5 | Hàm đó phải có test biên | Lỗi off-by-one ở biên là lỗi im lặng |
| 6 | Padding mask **không** được tính vào loss hoặc metric | Padding làm loãng cả loss lẫn F1 |

Cấu hình baseline hiện tại: window 500 frame = 10 s, hop 500 frame (không chồng
lấp), 50 frame/s.

**Test biên bắt buộc:**

```text
onset đúng tại biên frame      → không lệch 1 frame
offset đúng tại biên frame     → không lệch 1 frame
event ngắn hơn 1 frame         → vẫn tạo ≥ 1 frame dương
event vượt quá cuối recording  → clip vào duration, không raise
event bắt đầu tại 0.0          → frame 0 dương
```

---

## 12. Cổng dữ liệu — bảng tổng

| Gate | Điều kiện pass | DataSEC | DataSED |
|---|---|:---:|:---:|
| **D0** | Metadata, license, size + MD5, archive audit `pass` | ✅ | ✅ |
| **D1** | Giải nén, inventory đầy đủ, mọi file hợp lệ hoặc có reason code | ○ | ✅ |
| **D2** | Annotation contract pass | n/a | ✅ |
| **D3** | Dedup T1+T2+T3, nội bộ và **xuyên dataset** | ○ | ◐ T1 |
| **D4** | Split freeze, 5 kiểm leakage pass, SHA-256 ghi lại | ○ | ◐ |
| **D5** | Loader và frame alignment tests pass | ○ | ◐ |

### Quy tắc chặn

> **Không huấn luyện benchmark chính trước D4.**
>
> Baseline `sed_polyphonic_20260922T115340Z` chạy trên split **candidate**, nên
> frame macro-F1 0.359448 là **số dò đường**, không phải số báo cáo. Mọi lần
> trích dẫn nó phải kèm câu này.

---

## 13. Định nghĩa "xong" — điều kiện đóng băng `data-v1.0`

### Tính đầy đủ

- [x] Hai archive tải xong, MD5 khớp
- [ ] Hai dataset giải nén, inventory đầy đủ
- [x] Annotation DataSED chuẩn hóa, giữ cả raw và canonical
- [ ] Mọi file có verdict: `pass`, `quarantine` hoặc `exclude_*` kèm reason code

### Tính đúng đắn

- [x] Mọi nhãn ánh xạ được vào taxonomy `0.1`, 0 unmapped
- [ ] Dedup T1+T2+T3 chạy trên cả hai dataset
- [ ] Audit xuyên dataset hoàn tất, có số liệu trong `docs/measurements/`
- [ ] 5 kiểm leakage của §8.4 pass
- [ ] Không duplicate group nào bị chia qua hai split

### Tính truy vết

- [x] Zenodo metadata + license đã lưu và hash
- [x] Archive audit manifest đã commit
- [ ] `duplicate_groups.csv` và `exclusions.csv` đã commit
- [ ] Split có SHA-256 và ghi trong run manifest
- [ ] Mọi manifest sinh bằng script, không sửa tay

### Đóng băng

- [ ] Tag `data-v1.0`
- [ ] `docs/data_inventory.md` sinh lại từ manifest thật
- [ ] `STATUS.md` cập nhật
- [ ] Thay đổi sau tag phải có ADR và lên `data-v1.1`

---

## 14. Danh sách script

| Script | Chức năng | Trạng thái |
|---|---|---|
| `scripts.data_sources metadata` | Lấy + lưu Zenodo record | ✅ |
| `scripts.data_sources download` | Tải có resume, verify MD5 | ✅ |
| `scripts.data_sources extract` | Giải nén + copy reference | ✅ |
| `scripts.audit_archive` | **Cổng D0/D1 trước giải nén** | ✅ |
| `scripts.report_archive_audit` | Sinh measurement từ audit | ✅ |
| `scripts.build_inventory` | Inventory + summary | ✅ |
| `scripts.prepare_datased` | Parse + canonicalize annotation | ✅ |
| `scripts.extract_features` | Log-mel v1 | ✅ |
| `scripts.create_splits` | Split theo group + hash | ✅ |
| `scripts.find_duplicates` | **Dedup T1/T2/T3** | ○ **ưu tiên cao nhất** |
| `scripts.check_leakage` | 5 kiểm của §8.4 | ○ |
| `scripts.build_exclusions` | Gom reason code | ○ |
| `scripts.report_data_inventory` | Sinh `data_inventory.md` | ○ |

**Thứ tự ưu tiên viết tiếp: `find_duplicates` → `check_leakage` → `build_exclusions`.**
Ba script này mở cổng D3/D4, và mọi thí nghiệm đều chờ sau nó.
