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
| [docs/STATUS.md](docs/STATUS.md) | Snapshot đã đối soát, bằng chứng, giới hạn | Khi cần số liệu hiện hành |
| [docs/TRAINING_OPS_PLAN.md](docs/TRAINING_OPS_PLAN.md) | Tracking, kiểm tra, phân tích lỗi | Trước lần train mới |
| [docs/RELATED_WORK.md](docs/RELATED_WORK.md) | Văn liệu và mức xác minh | Khi viết Chương 2 |
| [docs/data_inventory.md](docs/data_inventory.md) | Số file/giờ theo class | Khi lo về dữ liệu |
| [docs/decisions/](docs/decisions/) | Vì sao chọn thế này | Khi định thay đổi kiến trúc |
| [docs/measurements/](docs/measurements/) | Số đo sinh tự động | Khi cần bằng chứng cho một claim |

---

## 3. Trạng thái hiện tại

**Cập nhật:** 22/09/2026, sau Phase 1 (xác minh archive + git baseline).

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
| DataSED dedup T1 | 8 nhóm exact duplicate |
| Log-mel v1 | 717/717 file, 16 kHz, 64 mel, 50 fps |
| SED baseline (dò đường) | frame macro-F1 test 0.359448 |
| Test suite | 18 test pass, ruff sạch |

### Đang làm / chưa nghiệm thu ◐

| Hạng mục | Còn thiếu |
|---|---|
| Split DataSED | Candidate 435/142/140, **chưa freeze** — chờ D3 |
| DataSEC | Archive verify xong, **chưa giải nén**, chưa inventory |
| Tài liệu | SYSTEM/taxonomy/DATA_PLAN/evaluation_protocol đã viết lại; còn PLAN, STATUS, ADR, contracts |

### Chưa có ○

DataSEC classifier · transfer DataSEC→DataSED · post-processing hiệu chuẩn ·
event-based F1 / PSDS · grounded caption · RAG / retrieval · API / inference /
frontend · CI.

### Việc tiếp theo — theo thứ tự

1. **`scripts.find_duplicates`** — dedup T1/T2/T3, nội bộ và xuyên dataset. Mở cổng D3.
2. **`scripts.check_leakage`** — 5 kiểm của [DATA_PLAN §8.4](docs/DATA_PLAN.md).
3. Giải nén + inventory DataSEC (D1).
4. Freeze split sau D3 (D4).
5. Train DataSEC classifier (E1), rồi transfer (E3).

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
# scripts.find_duplicates, scripts.check_leakage: CHƯA triển khai — ưu tiên cao nhất
.venv/Scripts/python.exe -m scripts.create_splits datased

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
