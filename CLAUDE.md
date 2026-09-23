# CLAUDE.md

> **ĐỌC FILE NÀY ĐẦU TIÊN trong mỗi phiên làm việc mới.**
> **CẬP NHẬT Ở CUỐI MỖI BLOCK CÔNG VIỆC** (xem [§9](#9-giao-thức-cập-nhật)).
>
> Đây là **living context + progress tracker**. Nó trả lời *"đang ở đâu, làm gì
> tiếp"*. Nó **không** chứa đặc tả (→ [docs/SYSTEM.md](docs/SYSTEM.md)) và
> **không** chứa kế hoạch dài hạn (→ [docs/PLAN.md](docs/PLAN.md)).

---

## 1. Dự án là gì

**Grounded Environmental Audio Monitoring and RAG-based Event Retrieval**
Khóa luận tốt nghiệp — Khoa học dữ liệu — IUH K18.

Hệ thống nhận recording môi trường liên tục → phát hiện sự kiện có định vị thời
gian (polyphonic SED) → sinh mô tả **bị ràng buộc vào event timeline** → lưu
event có cấu trúc → truy vấn lịch sử bằng RAG có trích dẫn recording/time span.

**Đóng góp nghiên cứu chính:**

- **C1** Grounded captioner có contract kiểm được bằng máy.
- **C2** Bộ metric đo factual grounding của caption âm thanh.
- **C3** Đo transfer isolated → continuous **có kiểm soát leakage xuyên dataset**.
- **C4** RAG trên event timeline có temporal predicate.

**Deadline:** 09/11/2026, buffer 1 tuần tới 16/11/2026 (8 tuần từ 22/09/2026).

**Dự án này độc lập với `audio-security-rag`.** Không import artifact, không kế
thừa quyết định ngầm. Xem [ADR-0001](docs/decisions/ADR-0001-scope-and-datasets.md).

---

## 2. Bản đồ tài liệu

| File | Trả lời câu hỏi | Khi nào đọc |
|---|---|---|
| **CLAUDE.md** (file này) | *Đang ở đâu?* | **Mỗi phiên, đầu tiên** |
| [docs/PLAN.md](docs/PLAN.md) | *Làm gì, khi nào, nghiệm thu ra sao?* | Đầu mỗi tuần, khi chọn task |
| [docs/SYSTEM.md](docs/SYSTEM.md) | *Hệ thống là gì?* — đặc tả đầy đủ = khung báo cáo | Khi cần chi tiết kỹ thuật |
| [docs/DATA_PLAN.md](docs/DATA_PLAN.md) | *Chuẩn bị dữ liệu thế nào?* | **Suốt giai đoạn D1–D4** |
| [docs/taxonomy.md](docs/taxonomy.md) | 22 lớp nghĩa là gì, ranh giới ở đâu | Khi làm việc với nhãn hoặc caption |
| [docs/annotation_guideline.md](docs/annotation_guideline.md) | Quy ước xử lý nhãn | Khi viết parser nhãn |
| [docs/evaluation_protocol.md](docs/evaluation_protocol.md) | *Số nào có nghĩa, số đó KHÔNG nói gì* | **Trước khi báo cáo bất kỳ con số nào** |
| **[docs/AGENT_SYNC.md](docs/AGENT_SYNC.md)** | *Agent kia đang làm gì, đã đo được gì* | **Mỗi phiên có 2 agent, đọc TRƯỚC khi code** |
| [docs/STATUS.md](docs/STATUS.md) | Snapshot đã đối soát, bằng chứng, giới hạn | Khi cần số liệu hiện hành |
| [docs/TRAINING_OPS_PLAN.md](docs/TRAINING_OPS_PLAN.md) | Tracking, kiểm tra, phân tích lỗi | Trước lần train mới |
| [docs/RELATED_WORK.md](docs/RELATED_WORK.md) | Văn liệu và mức xác minh | Khi viết Chương 2 |
| [docs/data_inventory.md](docs/data_inventory.md) | Số file/giờ theo class | Khi lo về dữ liệu |
| [docs/decisions/](docs/decisions/) | Vì sao chọn thế này | Khi định thay đổi kiến trúc |
| [docs/measurements/](docs/measurements/) | Số đo sinh tự động | Khi cần bằng chứng cho một claim |

---

## 3. Trạng thái hiện tại

**Cập nhật:** 23/09/2026, sau các hạng mục W1 độc lập (contract, CI, tài liệu vận hành).

**Cổng đang chặn: D3 — audit duplicate.** DataSEC nội bộ và duplicate xuyên
DataSEC–DataSED phải xong trước khi freeze split và trước mọi thí nghiệm transfer.

### Đã có ✅

| Hạng mục | Bằng chứng |
|---|---|
| Git baseline | `c9ccbc6` scaffold, `3c80110` archive audit |
| DataSEC archive verify | 6,414,663,316 B, MD5 `29fa9b8c…`, verdict `pass` |
| DataSED archive verify | 4,510,378,259 B, MD5 `44e093f6…`, verdict `pass` |
| **Taxonomy xác minh từ archive** | 22/22 coarse + 10/10 nhóm subclass khớp, 0 unmapped |
| Archive audit tái lập được | `scripts/audit_archive.py`, 7 test |
| License | `cc-by-nc-sa-4.0` cả hai, từ Zenodo record |
| DataSED inventory | 717 WAV, 18.6847 h, 44.1 kHz, mono 716 / stereo 1 |
| DataSED annotation | 4,034 poly event / 21 class; 4,309 mono / 22 class |
| DataSEC inventory | 5,048 WAV, 23.7082 h, 44.1 kHz, mono 5,048/5,048 | `data/manifests/datasec_inventory_summary.json` |
| DataSED dedup T1 | 8 nhóm exact duplicate |
| Log-mel v1 | 717/717 file, 16 kHz, 64 mel, 50 fps |
| SED baseline (dò đường) | frame macro-F1 test 0.359448 |
| Test suite | 18 test pass, ruff sạch |
| Dedup T1/T2/T3 | `ml/dataops/fingerprint.py` + `duplicates.py` + `dedup_run.py`; 44 test |
| Hiệu chuẩn ngưỡng T3 | Giữ 0.95/0.85; positive min 1.0000, negative max 0.9205, 0/5,000 vượt 0.95 |
| Leakage check D4 | `ml/dataops/leakage.py`; 5 kiểm §8.4; chặn chạy trước D3 |
| **Cổng D3 chạy xong** | 84 nhóm / 219 file; **3 nhóm xuyên dataset**; `docs/measurements/dedup_20260923.md` |
| Trùng xuyên dataset | `Sirens-0046`↔`S-0233` sim **1.000000**/35 s · `Sirens-0067`↔`S-0211` **1.000000**/13 s · `Train-0012`↔`S-0213` 0.9548/31 s |
| Mắt nối D3→D4 | `scripts/apply_cross_exclusions.py` + 10 test |
| Split DataSED **đã sinh lại sau D3** | 438/137/142; 687 nhóm rò rỉ, cụm lớn nhất 4; sha256 `d2924a5e45c2b271…` |
| Cổng D4 | 5/5 kiểm PASS, **đã chứng minh không rỗng**: bỏ exclusion → kiểm 5 FAIL đúng `Sirens-0046` |
| Rò rỉ xuyên dataset | **1 clip** `Sirens-0046.wav` (trùng `S-0233` ở validation, sim 1.000000) → dải `minor` 0.0198% |
| Phiếu duyệt tay | `data/manifests/review_worksheet.csv` + `docs/measurements/review_worksheet_20260923.md` |
| **Duyệt tay 35 cặp** | Xong: 10 `duplicate` · 1 `unsure` · 24 `distinct`, `human:patphh` |
| Rò rỉ cuối | **11 clip** / 5,048 = **0.2179%** → dải `minor`, **RQ1 vẫn hợp lệ** |
| Độ nhất quán chú giải | 8 cặp byte-identical gán nhãn 2 lần: **67/94** biên trong collar 0.2 s; **2/8** bất đồng lớp |
| Test suite | 218 test pass, ruff sạch |
| JSON Schema contracts | 6 schema Draft 2020-12; 13 test contract pass |
| CI baseline | `.github/workflows/ci.yml`; guard `services/api` không import torch pass |
| Tài liệu vận hành + annotation | `TRAINING_OPS_PLAN.md` và `annotation_guideline.md` đã cập nhật 23/09 |
| W4–W6 nền tảng | Metric/bootstrap/error harness, grounded caption, event-store/retrieval fixtures; 11 test pass |
| W3 nền tảng | Raw prediction NPZ contract, post-processing calibration guards và run manifest v2 đã có code/test |

### Đang làm / chưa nghiệm thu ◐

| Hạng mục | Còn thiếu |
|---|---|
| Split DataSED | **Đã đóng băng** 438/137/142, sha256 `d2924a5e45c2b271…` |
| Cổng D3/D4 | **Xong, split đã đóng băng.** |
| Tài liệu | `RELATED_WORK.md` và `data_inventory.md` còn chờ; contracts đã có |
| W2 nền tảng | Loader/sampler DataSEC, CNN14-compatible PANNs, `logmel_panns_v1` đã có code/test; chưa train |
| W4–W6 nền tảng | Đã có code/test fixture; chưa chạy metric thật, PostgreSQL, embedding hay prediction thật |
| W3 nền tảng | Chưa có logits/checkpoint thật; threshold và duration prior chưa được hiệu chuẩn trên split freeze |

### Chưa có ○

DataSEC classifier · transfer DataSEC→DataSED · post-processing hiệu chuẩn ·
event-based F1 / PSDS · grounded caption · RAG / retrieval · API / inference /
frontend.

### Việc tiếp theo — theo thứ tự

1. **Đọc kết quả `detect`** — `duplicate_groups.csv`, đối chiếu ngưỡng báo động
   [DATA_PLAN §7.6](docs/DATA_PLAN.md). Nếu trùng dev/test > 5% thì RQ1 chuyển
   thành kết quả âm tính, phải xử lý **ngay tuần này**.
2. **Xử lý nhóm `review` bằng người** — ghi `decided_by: human:<tên>` vào
   `exclusions.csv`. Cấm tự động hoá bước này.
3. Sinh lại split sau D3 (duplicate group có thể buộc recording đổi split),
   tỉ lệ 60/20/20 theo [ADR-0008](docs/decisions/ADR-0008-ti-le-split-datased.md).
4. `scripts.check_leakage datased` — 5 kiểm phải pass **thật**, không pass rỗng.
5. Áp `cross_dataset_exclusions` sau khi có split, rồi freeze + tag `data-v1.0`.
6. Train DataSEC classifier (E1), rồi transfer (E3).

---

## 4. Quyết định đã khóa

Không thảo luận lại trừ khi có lý do mới. Mỗi thay đổi phải kèm một ADR.

| Quyết định | Chọn | ADR | Lý do ngắn |
|---|---|---|---|
| Dataset | DataSEC + DataSED | [0001](docs/decisions/ADR-0001-scope-and-datasets.md) | Có audio + nhãn công bố, DOI rõ, bỏ được công gán nhãn thủ công |
| Miền tuyên bố | Environmental acoustic monitoring | 0001 | **Không** tuyên bố tội phạm, khẩn cấp, an ninh trường học |
| Benchmark chính | DataSED polyphonic, 21 class | 0001 | `wind_turbine` ngoài polyphonic label set |
| Encoder | Baseline CNN+BiGRU · Đề xuất PANNs CNN14 | [0002](docs/decisions/ADR-0002-encoder-va-nhanh-transfer.md) | 3 nhánh A/B/C; **RQ1 = C − B**, không phải C − A |
| Cân bằng lớp khi pretrain | Class-balanced sampling | 0002 | `voices`+`music` = 57.5% DataSEC |
| Threshold | Per-class θ quét **trên dev** | [0003](docs/decisions/ADR-0003-threshold-va-post-processing.md) | Duration prior suy từ **train**, không từ dev |
| Embedding | BGE-M3, 1024-dim | [0004](docs/decisions/ADR-0004-embedding-cho-retrieval.md) | Đa ngữ VI/EN cùng không gian |
| Database | PostgreSQL 16 + pgvector | [0005](docs/decisions/ADR-0005-database-va-vector-store.md) | Temporal predicate + filter + vector trong **một** câu SQL |
| Fingerprint T3 | Bỏ C0, delta trị tuyệt đối, `fmax` 7000, chuẩn hoá z-score corpus | [0007](docs/decisions/ADR-0007-fingerprint-va-luat-dedup.md) | Không chuẩn hoá thì 52.6% cặp ngẫu nhiên vượt ngưỡng review |
| Tỉ lệ split DataSED | **60/20/20**, không phải 70/15/15 | [0008](docs/decisions/ADR-0008-ti-le-split-datased.md) | ADR-0003 lập luận trên dev 142 = 60/20/20; code và candidate đều vậy |
| Ngưỡng T3 theo overlap | 0.95/0.85 khi overlap ≥ 3 s; **0.99, không review** khi ngắn hơn | [0009](docs/decisions/ADR-0009-nguong-phu-thuoc-overlap.md) | 95.5% cặp có overlap đúng 1 s — nhiễu của phép so 16.6M cặp |
| Subclass trên continuous | Chỉ báo trên DataSEC | [0006](docs/decisions/ADR-0006-danh-gia-subclass.md) | DataSED không có subclass ground truth |
| Caption song ngữ | EN benchmark, VI giao diện, embed cả hai | 0004 | So được với văn liệu AAC, truy vấn được tiếng Việt |
| Không có risk score | Bỏ hoàn toàn | 0001 | Không có cơ sở gán mức nguy hiểm cho nguồn âm |

---

## 5. Thỏa thuận làm việc với AI

### Luôn làm

- **Đọc `CLAUDE.md` → `docs/PLAN.md` (tuần hiện tại) trước khi code.** Không tự
  chọn task ngoài kế hoạch.
- Task nào cũng bám vào một dòng trong `PLAN.md`. Không có dòng khớp → hỏi trước.
- **Dùng `.venv/Scripts/python.exe`**, không dùng `python` trên PATH (thiếu dependency).
- Chạy script validate trước khi tuyên bố xong. **"Code chạy" ≠ "nghiệm thu"**.
- Viết ADR vào `docs/decisions/` cho mỗi thay đổi kiến trúc.
- Cập nhật `CLAUDE.md` ở cuối mỗi block (§9).
- **Báo cáo trung thực:** test trượt thì nói trượt kèm output; bỏ bước nào thì nói rõ.
- **Số trong docs phải sinh từ script**, không chép tay. Mọi số phải truy được về
  artifact trong `data/manifests/` hoặc `ml/runs/`.
- Sau khi sửa `ml/configs/taxonomy.yaml`: **grep toàn repo tìm tên lớp cũ TRƯỚC
  khi coi là xong.** `class_id` xuất hiện trong manifest, split, checkpoint và
  caption lexicon; đổi taxonomy mà không quét lại để lại dòng mồ côi mang lớp đã mất.

### Không bao giờ làm

- ❌ **Bịa số liệu, bịa tên dataset, bịa trích dẫn paper.** Không chắc → đánh dấu
  `⚠️ CẦN XÁC MINH` và ghi vào "Nợ kỹ thuật" của `PLAN.md`.
- ❌ Chạm test set để tuning bất cứ thứ gì. θ chọn trên **dev**, khóa lại, test
  chạy **một lần**.
- ❌ Suy duration prior từ dev hoặc test — chỉ từ train ([evaluation_protocol §2.2](docs/evaluation_protocol.md)).
- ❌ Tự viết lại metric đã có thư viện chuẩn (`sed_eval`, `psds_eval`).
- ❌ Dùng `taxonomy.class_ids` cho SED head — phải là `polyphonic_class_ids` (21).
- ❌ Tự tách lớp gộp `sirens_and_alarms` hay `thunder_fireworks_gunshot` bằng suy đoán.
- ❌ Sửa raw annotation. Nghi ngờ → ghi phân tích lỗi, không sửa dữ liệu.
- ❌ Commit audio, feature tensor, checkpoint hoặc vector index.
- ❌ Để `services/api` import torch hoặc load checkpoint.
- ❌ Mở rộng scope. Ý tưởng hay → ghi vào §8, không làm ngay.
- ❌ Viết caption suy diễn nguyên nhân/ý định/mức nguy hiểm (ràng buộc G3).

### Ưu tiên khi phải đánh đổi

1. **Tính đúng đắn của phương pháp** (không rò rỉ, không tuning trên test) — không bao giờ hy sinh
2. Nghiệm thu của tuần hiện tại
3. Đóng góp nghiên cứu C1/C2/C3
4. Độ hoàn thiện kỹ thuật
5. Độ đẹp của giao diện

### Ngôn ngữ

- Tài liệu, comment giải thích *vì sao*, giao diện, caption VI: **tiếng Việt**
- Code, tên biến, docstring, `class_id`, caption EN: **tiếng Anh**
- **Không dịch `class_id`** — luôn `glass_breaking`, không phải `kinh_vo`

---

## 6. Quy ước

| Hạng mục | Quy ước |
|---|---|
| Kích thước file | Code 200–400 dòng thường, 800 tối đa |
| Kích thước hàm | < 50 dòng |
| `file_id` | `<dataset>:<relative_path>` |
| `recording_id` | `datased:S-0001` hoặc `upload:<uuid>` |
| `class_id` | snake_case tiếng Anh, đúng 22 giá trị trong `ml/configs/taxonomy.yaml` |
| SED class list | **21** class từ `taxonomy.polyphonic_class_ids` |
| Run ID | `<task>_<YYYYMMDDTHHMMSSZ>` |
| Model version | `<component>-v<major>.<minor>`, ví dụ `sed-v1.0` |
| Commit | `<type>: <mô tả>` — feat, fix, refactor, docs, test, chore, exp |
| Nhánh | Hiện tại `master` |
| Config | YAML trong `ml/configs/`, **không hardcode** hyperparameter |
| Seed | 20260922 cho split và training |
| API response | Envelope `{success, data, error, meta}` |
| ADR | `ADR-NNNN-short-title.md`, 6 mục cố định |
| Measurement | `<chủ đề>_<YYYYMMDD>.md` hoặc `<run_id>.md`, **sinh tự động** |
| Số trong artifact | Giữ đầy đủ; làm tròn chỉ ở tầng trình bày |

---

## 7. Lệnh hay dùng

```bash
# ==== Chất lượng ====
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .

# ==== Dữ liệu: D0 — metadata và toàn vẹn archive ====
.venv/Scripts/python.exe -m scripts.data_sources metadata datasec datased
.venv/Scripts/python.exe -m scripts.data_sources download datasec --workers 8
.venv/Scripts/python.exe -m scripts.audit_archive datasec
.venv/Scripts/python.exe -m scripts.audit_archive datased --labels-in-annotations
.venv/Scripts/python.exe -m scripts.report_archive_audit datasec datased

# ==== Dữ liệu: D1–D2 ====
.venv/Scripts/python.exe -m scripts.data_sources extract datasec
.venv/Scripts/python.exe -m scripts.build_inventory datased
.venv/Scripts/python.exe -m scripts.prepare_datased
.venv/Scripts/python.exe -m scripts.extract_features datased

# ==== Dữ liệu: D3–D4 ====
.venv/Scripts/python.exe -m scripts.find_duplicates signatures --workers 8
.venv/Scripts/python.exe -m scripts.find_duplicates calibrate
.venv/Scripts/python.exe -m scripts.find_duplicates detect
.venv/Scripts/python.exe -m scripts.find_duplicates regroup   # đổi ngưỡng, không so lại
.venv/Scripts/python.exe -m scripts.report_duplicates
.venv/Scripts/python.exe -m scripts.create_splits datased
.venv/Scripts/python.exe -m scripts.apply_cross_exclusions datased
.venv/Scripts/python.exe -m scripts.build_review_worksheet     # sinh phiếu duyệt tay
.venv/Scripts/python.exe -m scripts.apply_review_decisions     # sau khi điền phiếu
.venv/Scripts/python.exe -m scripts.check_leakage datased

# ==== Huấn luyện ====
.venv/Scripts/python.exe -m scripts.train_classifier --epochs 30 --device cuda
.venv/Scripts/python.exe -m scripts.train_sed --epochs 8 --batch-size 8 --device cuda --evaluate-test
.venv/Scripts/python.exe -m scripts.report_run ml/runs/<run_id>

# ==== Chưa triển khai ====
# scripts.evaluate_run      — event-based F1, PSDS
# scripts.sweep_threshold   — quét θ trên dev
# scripts.build_retrieval_index
# scripts.serve_demo
```

---

## 8. Ý tưởng để dành

Không làm bây giờ. Ghi ở đây để khỏi mở rộng scope giữa chừng.

- Hop nhỏ hơn 320 cho class impulsive (`Gunshot` chỉ ~5 frame ở 50 fps).
- `logmel_v2` với ref cố định, để giữ mức áp suất âm tuyệt đối.
- Multi-task: SED + subclass cùng lúc thay vì hai giai đoạn.
- Spatial SED nếu tìm được dataset multi-channel cùng miền.
- Gán nhãn subclass cho một tập con DataSED để RQ4 trả lời đầy đủ.
- Streaming thật với overlap-add và event stitching.
- Đối chiếu với dataset của nhóm tác giả khác để kiểm tính suy rộng.

---

## 9. Giao thức cập nhật

Cuối mỗi block công việc:

1. Cập nhật §3 nếu trạng thái đổi.
2. Thêm dòng vào §10 nhật ký, có ngày.
3. Cập nhật [docs/STATUS.md](docs/STATUS.md) nếu có artifact mới.
4. Viết ADR nếu có quyết định kiến trúc.
5. Sinh measurement bằng script nếu có số mới.

**Không ghi "đã hoàn thành" nếu chưa có command và artifact kiểm chứng.**

---

## 10. Nhật ký tiến độ

### 2026-09-23 — W3: prediction, post-processing và reproducibility

Thêm contract NPZ nguyên tử cho logits/targets/mask/recording/time metadata với
SHA-256 và kiểm đúng 21 `polyphonic_class_ids`; thêm chuyển frame→event, median
filter, duration prior train-only, threshold sweep dev-only và schema
`postproc.json`; nâng run manifest lên v2 với seed evidence, git revision,
data/split/taxonomy/feature/postproc hash và policy chặn final measurement khi
run dirty/provisional/incomplete. Targeted tests từng nhánh pass và Ruff pass.
Chưa tạo logits, threshold, prior hay metric thật trước khi D3/D4 freeze.

### 2026-09-23 — W2: nền tảng DataSEC và PANNs

Triển khai các phần W2 không cần kết quả D4: loader phân cấp DataSEC (22 coarse,
28 subclass) và class-balanced sampler; encoder/classifier CNN14-compatible với
chính sách batch an toàn cho 8 GB VRAM; cùng `logmel_panns_v1` (32 kHz, 64 mel,
50 fps) theo config. Test model và log-mel pass; test loader bị chặn bởi lỗi
khởi tạo PyTorch cấp hệ điều hành `0x8007000e` trong môi trường hiện tại. Chưa
train, chưa sinh checkpoint hay metric trước khi D3/D4 freeze.

### 2026-09-23 — W4–W6: nền tảng đánh giá, caption và retrieval

Thêm adapter chuẩn cho `sed_eval`/`psds_eval`, bootstrap CI theo recording và
phân tích lỗi SED; timeline canonicalizer, lexicon 22 lớp + lexicon cấm,
template captioner và grounding metrics G1–G3; migration PostgreSQL/pgvector,
document builder, bốn temporal predicate và query set deterministic 100 câu.
Fixture tests ba nhánh pass 11 test. Dependency metric tùy chọn và database
chưa chạy trong môi trường này; không tạo số liệu nghiên cứu.

### 2026-09-23 — W1: contract, CI và tài liệu độc lập

Hoàn tất song song ba hạng mục không phụ thuộc D3: sáu JSON Schema trung lập
framework trong `contracts/` (recording, event, timeline, inference response,
retrieval result, run manifest), kèm 13 test bằng Draft 2020-12; CI GitHub
Actions chạy Ruff, pytest và guard AST/grep cấm `services/api` import `torch`;
và cập nhật `TRAINING_OPS_PLAN.md` cùng `annotation_guideline.md` về preflight,
ranh giới test, lineage và bất biến annotation. Xác minh độc lập: 14 test
(contracts + API boundary) pass và Ruff trên phạm vi mới pass. Full suite chưa
nghiệm thu trong block này vì fingerprint D3 đang được Claude Code sửa song song
và môi trường hiện không tạo được thư mục `%TEMP%` của pytest.

### 2026-09-22 — Viết lại hệ thống tài liệu

Tài liệu bản đầu (1,133 dòng) bị đánh giá là mơ hồ. Viết lại theo mức chi tiết
của dự án tiền nhiệm, nhưng **không copy scope**: bỏ toàn bộ bộ máy gán nhãn thủ
công (Scaper, gold set gán mù, kappa, ngân sách công người) vì DataSEC/DataSED có
annotation công bố; bỏ risk scoring và alert service vì ADR-0001 cấm tuyên bố
khẩn cấp.

Đã viết lại: `SYSTEM.md` 180→1,584, `taxonomy.md` 103→554, `DATA_PLAN.md`
141→578, `evaluation_protocol.md` 114→389, và `CLAUDE.md` (mới).

### 2026-09-22 — Phase 1: xác minh archive và git baseline

**Git.** Repo trước đó chưa có commit nào. Tạo `c9ccbc6` (scaffold, 98 file) và
`3c80110` (archive audit). Trước đó mọi run manifest ghi `git.revision: "HEAD"`
với `dirty: true`, tức không tái lập được.

**DataSEC đã tải xong** — trái với STATUS cũ ghi "đang chạy". Archive
6,414,663,316 byte khớp đúng byte, MD5 `29fa9b8cc84cfa69aa4e5e674e780383` khớp,
verify hết 10.3 s.

**Viết `ml/dataops/archive_audit.py`** thay vì chạy lệnh rời rồi chép số. Audit
đọc central directory của ZIP nên rẻ, chạy được *trước* giải nén — đúng vai trò
cổng D0/D1. Hỗ trợ hai kiểu layout nhãn: cây thư mục (DataSEC) và bảng annotation
(DataSED).

**Cổng taxonomy PASS.** `docs/taxonomy.md` §3 tự đặt điều kiện phải xác minh
subclass từ archive. Kết quả: **22/22 coarse class ánh xạ được, 10/10 nhóm
subclass khớp chính xác (28 subclass), 0 nhãn ngoài taxonomy.** Bảng subclass
trong docs là đúng.

**Ba phát hiện làm đổi thiết kế:**

1. **Imbalance 38:1.** `voices` 1,900 (37.6%) + `music` 1,001 (19.8%) = 57.5%
   DataSEC. Pretraining không cân bằng sẽ học chủ yếu phân biệt nói với nhạc →
   ADR-0002 yêu cầu class-balanced sampling.
2. **4 subclass dưới 25 file** (`Crickets` 20, `Olive shaker` 20, `Magpies` 21,
   `Lawn mower` 21). Với 70/15/15 thì test chỉ 3–4 mẫu → metric per-subclass vô
   nghĩa. `evaluation_protocol.md` §4 quy định báo số tuyệt đối thay vì tỷ lệ.
3. **Không archive nào chứa LICENSE/README.** License `cc-by-nc-sa-4.0` chỉ lấy
   được từ Zenodo record. `SA` nghĩa là checkpoint nếu công bố phải cùng license,
   không được MIT/Apache. Đã sửa `DATA_PLAN.md` §2–§3 vốn giả định sai.

**Rủi ro R1 nâng mức lên CAO:** hai dataset cùng 6 tác giả, cùng miền, công bố
cách nhau 4 tháng. Cổng D3 không phải thủ tục mà là rủi ro leakage thật của toàn
bộ RQ1.

**Một lỗi test bắt được.** `--skip-md5` làm verdict **luôn** trả `fail_checksum`
vì `md5_actual` bị gán `"(skipped)"` rồi so với giá trị mong đợi. Sửa thành
`str | None` và thêm verdict riêng `pass_unverified_md5`, để một lần bỏ qua
checksum không bao giờ đọc thành `pass`.

### 2026-09-23 — Cổng D3 chạy xong; ba lỗi phương pháp bị đo ra

**Kết quả chính: DataSEC và DataSED **có** chung bản ghi nguồn.** Ba cặp đạt
`duplicate`, hai trong đó similarity **1.000000** trên 35 s và 13 s chồng lấp:
`Sirens-0046`↔`S-0233`, `Sirens-0067`↔`S-0211`, và `Train-0012`↔`S-0213` (0.9548/31 s).
Similarity tuyệt đối trên 35 giây không phải trùng hợp — clip DataSEC là trích
đoạn của recording DataSED. Rủi ro R1 được xác nhận bằng đo, không còn là giả định.

Dải báo động hiện là `clean` (0/5,048) nhưng **chưa kết luận được**: luật loại
trừ xuyên dataset cần split, mà split phải sinh sau D3. Còn 35 quyết định của
người đang treo.

**Ba lỗi phương pháp, cả ba đều chỉ lộ ra khi chạy trên dữ liệu thật:**

1. **Fingerprint như đặc tả không phân biệt được gì.** Hiệu chuẩn lần đầu: 52.6%
   cặp ngẫu nhiên khác nhãn vượt ngưỡng review, negative max 0.983 còn cao hơn
   positive min. Hai nguyên nhân: `C0` phụ thuộc gain chi phối cosine, và thiếu
   chuẩn hoá theo thống kê corpus. Sau khi sửa: positive min 1.0000, negative max
   0.9205, 0/5,000 vượt 0.95. Ngưỡng 0.95/0.85 của DATA_PLAN là đúng; cách đo
   khoảng cách mới là chỗ sai. → ADR-0007.

2. **Gom cạnh `review` vào nhóm tạo một thành phần 2,310 file** (2,200 DataSEC +
   110 DataSED) nối bằng đúng ngưỡng yếu nhất 0.850. Chaining của single-linkage.
   Và gom cạnh review chính là "xử lý tự động" mà DATA_PLAN §7.3 cấm — cài đúng
   chữ nhưng vi phạm tinh thần ở một tầng khác. Giờ chỉ union cạnh `duplicate`.

3. **44,915 cặp `review` là cổng không chạy được.** Nguyên nhân là bài toán so
   sánh bội: FPR 0.22% mỗi cặp × 16.6 triệu cặp ≈ 36,000 dương tính giả. Cột
   `overlap` tách hai quần thể dứt khoát — mọi dải dưới 0.95 có median overlap
   **đúng 1.0 giây**, trong khi ba cặp thật có 35/13/31 giây. Ngưỡng giờ phụ
   thuộc overlap, và review nội bộ thành ràng buộc "cùng split" thay vì quyết
   định xoá. Hàng đợi người: **44,915 → 35**. → ADR-0009.

**Một lỗi thiết kế tự bắt được:** `regroup` ban đầu tin vào `verdict` đã lưu
trong cache, nên đổi ngưỡng xong vẫn ra kết quả cũ. Cache giờ chỉ giữ số đo;
verdict tính lại mỗi lần.

**Sửa sự thật trong tài liệu:** DataSEC là **44.1 kHz** chứ không phải 16 kHz như
DATA_PLAN §7.2 ghi. T2 **không** bắt được đổi bit-depth (49.5% mẫu lệch 1 LSB,
hệ thống ở tầng libsndfile) — chính là ví dụ DATA_PLAN dùng để biện minh cho T2.
Trên hai dataset này T2 tìm được đúng 24 cặp, bằng hệt T1, tức là một tầng rỗng.

**Chốt tỉ lệ split 60/20/20** (ADR-0008): code, split candidate và lập luận
"dev 142" của ADR-0003 đều đã là 60/20/20; chỉ một bảng trong DATA_PLAN ghi
70/15/15 mà không có ADR nào đứng sau.

### 2026-09-23 (tiếp) — D4 chạy xong; hai lỗi lệch namespace suýt cho kết quả sai

**Split sinh lại sau D3: 438/137/142**, sha256 `d2924a5e45c2b271…`. Khoá nhóm giờ
hợp nhất ba nguồn — `content_sha256`, `duplicate_groups.csv`, và
`split_cohesion_pairs.csv` — nên vi phạm kiểm 3 **không thể xảy ra** thay vì bị
phát hiện sau. 687 nhóm, cụm lớn nhất 4 recording (0.6%).

**Hai lỗi lệch namespace `file_id`, cùng một gốc, suýt cho kết quả sai:**

Split lưu `recording_id` (`S-0233`), cổng D3 lưu `file_id`
(`datased:<đường dẫn>.wav`). Ghép `f"datased:{recording_id}"` cho ra khoá không
khớp gì. Hậu quả không phải crash — mà là **mọi phép giao thành rỗng, và cổng
giao rỗng thì luôn báo pass**:

1. `create_splits` bỏ qua toàn bộ ràng buộc D3, vẫn ra split trông hợp lý
   (largest group = 2 thay vì 4).
2. `apply_cross_exclusions` báo **"0 clip rò rỉ"** trong khi `S-0233` nằm ở
   validation và trùng similarity **1.000000** với `Sirens-0046.wav`. Đúng thứ
   rò rỉ mà cả cổng D3 tồn tại để chặn.

Phát hiện được là nhờ đối chiếu tay `S-0233 -> validation` với báo cáo "0 rò rỉ".
Đã thêm guard raise ở cả `build_leakage_groups` và `apply_cross_exclusions`: nếu
một dataset có ràng buộc nhưng **không khớp được item nào**, đó là lỗi tên chứ
không phải dữ liệu sạch.

**Kết quả cuối sau khi sửa:** 1 clip pretraining bị loại
(`DATASEC/Sirens and alarms/Sirens/Sirens-0046.wav`), tỷ lệ 0.0198% → dải
**`minor`**: loại, ghi số vào báo cáo, **RQ1 vẫn hợp lệ**.

**Cổng D4: 5/5 PASS, và đã chứng minh không rỗng** — bỏ exclusion ra thì kiểm 5
FAIL, gọi đúng tên `Sirens-0046.wav` và `dup-0063` chạm validation. Sau hai lần
bị pass rỗng lừa, một cổng báo PASS mà không chứng minh được nó chạm dữ liệu thì
không đáng tin.

**Việc còn lại của người:** 35 cặp xuyên dataset ở dải review. Đã sinh phiếu
`data/manifests/review_worksheet.csv` kèm hướng dẫn nghe và lệnh `ffplay` sẵn cho
từng cặp. `unsure` được xử lý thận trọng như `duplicate`.

### 2026-09-23 (tiếp) — Duyệt tay xong; quan sát của người mở ra phát hiện lớn hơn

**Duyệt 35 cặp:** 10 `duplicate`, 1 `unsure`, 24 `distinct` (`human:patphh`).
Rò rỉ cuối: **11 clip DataSEC / 5,048 = 0.2179%** → dải **`minor`**: loại, ghi số
vào báo cáo, **RQ1 vẫn hợp lệ**. D4 pass 5/5.

**Quan sát của người duyệt dẫn tới phát hiện quan trọng nhất trong ngày.** Báo
rằng phần lớn cặp sai có audio 1 là nhạc, audio 2 là tiếng trực thăng *có một
giọng nói lặp đi lặp lại*. Truy ra:

- **20/24 cặp sai (83%) chỉ dính hai recording `S-0606` và `S-0622`** — mà hai
  file này byte-identical với nhau.
- Chú giải của nó: `propeller_aircrafts` 0.32-25.23 s phủ gần hết, cộng **4 event
  `voices` cách nhau đều 6.6-7.0 s**, mỗi event khoảng 1 s. Đó là một giọng lặp
  tuần hoàn, không phải hội thoại. Cấu trúc tuần hoàn trên nền băng rộng chính là
  thứ làm fingerprint nhầm với nhạc.

**Từ đó phát hiện DataSED có 8 cặp recording byte-identical được chú giải độc lập
hai lần** - một phép đo agreement có sẵn, không tốn công gán nhãn:

| | |
|---|---:|
| Biên nằm trong collar 0.2 s | **67 / 94** |
| Lệch biên lớn nhất | **12.72 s** (`S-0289`/`S-0500`, một event `jet_aircrafts`) |
| Cặp bất đồng lớp hoặc số event | **2 / 8** |

Hai ca bất đồng lớp là bằng chứng trực tiếp về cặp dễ nhầm, lấy từ **ground
truth** chứ không từ ma trận nhầm của model:
`lawn_mower_brush_cutter_olive_shaker` và `propeller_aircrafts` (S-0397/S-0585,
lệch cả ba lần xuất hiện), và `vacuum_cleaner_fan_hairdryer` với
`lawn_mower_brush_cutter_olive_shaker` (S-0062/S-0198).

**Hệ quả đã ghi vào `evaluation_protocol.md`:** collar 0.2 s **chặt hơn độ chính
xác của chính nhãn**. Cải thiện nhỏ hơn mức bất đồng này không phân biệt được với
nhiễu nhãn và không được tuyên bố. Cỡ mẫu 8 cặp - là tín hiệu cảnh báo, không
phải nghiên cứu agreement, và phải báo cáo đúng như vậy.

**Một lỗi công cụ:** Excel trên Windows tiếng Việt lưu lại phiếu duyệt bằng
cp1252, gây `UnicodeDecodeError` và **mất dấu 29/35 ghi chú**. Trình đọc giờ thử
lần lượt utf-8-sig, utf-8, cp1252, latin-1 và cảnh báo số ô mất ký tự. Quyết định
không bị ảnh hưởng (toàn ASCII), nhưng ghi chú đi vào phụ lục thì nên viết lại.

### 2026-09-23 (tiếp) — Nhật ký duyệt hoàn chỉnh, đối chứng được với ground truth

Phiếu duyệt đã lưu lại bằng UTF-8, **0 ghi chú mất dấu**. Quyết định không đổi
(10 `duplicate` / 1 `unsure` / 24 `distinct`), nên mọi số phía sau giữ nguyên:
rò rỉ 11 clip = 0.2179%, dải `minor`, D4 pass 5/5.

`scripts.report_duplicates` giờ đọc thẳng phiếu và xuất **nhật ký quyết định**
đầy đủ 35 dòng kèm ghi chú — vật liệu phụ lục. Trước đó báo cáo vẫn in "35 cặp
chưa có quyết định" vì nó đọc số từ hàng đợi chứ không đọc phiếu.

**Ghi chú của người duyệt khớp ground truth ở mọi ca kiểm được**, nên phần duyệt
tay này có thể dẫn trong báo cáo như một bước có kiểm chứng, không phải một khâu
tin vào lời khai:

| Ghi chú | Chú giải DataSED |
|---|---|
| `S-0323` "siren" | `sirens_and_alarms` 1.06-56.38 |
| `S-0089` "tiếng người nói chuyện và noise quạt" | `voices` 0-38.63 + `vacuum_cleaner_fan_hairdryer` 5.68-17.76 |
| `S-0594` (2 cặp `duplicate` với Helicopters) | 3 event `propeller_aircrafts` |

7 cặp `duplicate` còn để trống ghi chú (`rev-003`, `004`, `006`, `011`, `022`,
`029`, `035`). Không chặn gì; nêu ra để phụ lục biết chỗ còn thiếu lý do.

**Một số báo cáo sai đã sửa:** trình đọc báo encoding là `utf-8-sig` cho file
**không có BOM**, vì `utf-8-sig` giải mã được cả hai. Giờ kiểm BOM tường minh nên
tên encoding trong artifact đúng với thứ nằm trên đĩa. Thêm `tests/test_textio.py`.

### 2026-09-23 (chốt) — Đóng băng split, rà soát toàn bộ

**Rà soát một lượt:** 218 test pass, ruff sạch, D4 pass 5/5, và **mọi artifact
nhất quán chéo** — số file trong audit khớp inventory, tổng split khớp 717, hash
split khớp metadata, số exclusion cross khớp alarm, 132 loại trừ nội bộ khớp đúng
số nhóm nội bộ, 0 file_id trùng trong `exclusions.csv`.

**Ba thứ rác đã dọn:**

- `data/manifests/1.csv` — bản xuất Excel hỏng của phiếu duyệt, **cắt cụt** ghi
  chú giữa chừng ("độ l", "audio thứ") và mất `decided_by` ở 3 dòng. Không chứa
  thông tin nào phiếu thật không có. Đã xoá.
- `.test-tmp-prediction-{artifacts,final,integration}/` — rác từ lần chạy
  `pytest --basetemp=` trỏ vào repo. Đã xoá và thêm `.test-tmp-*/` vào `.gitignore`.
- Quét secret trên toàn bộ code: 0 hit. File lớn nhất sẽ commit là
  `datasec_inventory.csv` 1.0 MB — manifest hợp lệ.

**Đóng băng split.** `scripts/freeze_split.py` chỉ cho đóng băng khi D4 pass,
báo cáo D4 **không** phải pass rỗng, loại trừ xuyên dataset đã áp, và **không còn
cặp nào chờ người quyết định**. Ghi `datased_polyphonic.frozen.json`.

Kèm guard ở `check_leakage`: split đã đóng băng mà file đổi thì cổng **từ chối
chạy**. Đã kiểm chứng bằng cách sửa split thật — cổng dừng và in cả hai hash.
Sinh lại split rồi quên chạy lại cổng là cách im lặng nhất để làm hỏng mọi kết
quả phía sau, vì mọi số đã báo cáo đều gắn với đúng một split.
