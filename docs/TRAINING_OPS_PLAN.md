# TRAINING_OPS_PLAN.md — Vận hành huấn luyện

> **Mục tiêu:** mọi experiment chạy được từ config, tạo run directory tự đủ bằng
> chứng, resume an toàn, và **so sánh được với nhau**.
>
> Metric và cách diễn giải: [evaluation_protocol.md](evaluation_protocol.md).
> File này nói về **hạ tầng** chạy và theo dõi.

---

## 0. Lý do tài liệu này tồn tại

Baseline `sed_polyphonic_20260922T115340Z` có manifest khá đầy đủ, nhưng vẫn
**không tái lập chính xác được**, vì ba lý do đo được:

| # | Vấn đề | Bằng chứng | Hậu quả |
|---:|---|---|---|
| 1 | `git.revision: "HEAD"`, `dirty: true` | manifest | Không biết code nào đã chạy |
| 2 | Không lưu logit thô | Không có `predictions/` | Đổi θ phải chạy lại toàn bộ inference |
| 3 | Thiếu `data_manifest_sha256` | manifest | Biết split nào nhưng không biết feature nào |

Ba vấn đề này rẻ để sửa **trước** khi chạy 3 nhánh × 3 seed, và rất đắt để sửa
sau.

---

## 1. Yêu cầu

| # | Yêu cầu | Vì sao |
|---:|---|---|
| Y1 | Mọi run ghi đủ provenance để tái lập | Không có thì số không dùng được cho báo cáo |
| Y2 | Hai run so được với nhau, hoặc biết rõ vì sao không | [evaluation_protocol §6](evaluation_protocol.md) |
| Y3 | Đổi θ không cần train lại, không cần inference lại | Quét ngưỡng là thao tác lặp nhiều lần |
| Y4 | Run bị ngắt không được ghi `complete = true` | Artifact dở dang lẫn vào báo cáo |
| Y5 | Resume kiểm được config và data hash khớp | Resume nhầm dữ liệu là lỗi im lặng |
| Y6 | Cổng dữ liệu chặn được việc train | Train trên split chưa freeze là không hợp lệ cho kết luận |
| Y7 | Test là ranh giới một chiều | Không dùng test để chọn checkpoint, encoder, threshold hoặc post-processing |

---

## 2. Run layout

### 2.1 Hiện tại ✅

```text
ml/runs/<run_id>/
├── manifest.json        config, hashes, git, environment, complete
├── metrics.json         best_validation, test, per_class_f1
├── checkpoints/
│   ├── best.pt
│   └── last.pt
└── logs/
    └── history.json
```

### 2.2 Đích — bốn thứ còn thiếu ○

```text
├── config.resolved.yaml     config sau khi merge mọi default
├── taxonomy.snapshot.yaml   bản chụp taxonomy tại thời điểm train
├── postproc.json            θ_c, w_c, d_min_c, g_max_c đã hiệu chuẩn
└── predictions/
    ├── dev.npz              logit thô
    └── test.npz             chỉ sinh SAU khi chọn model
```

**`predictions/` là thứ thiếu gây tốn nhất.** Kích thước phụ thuộc số window,
frame và class của run, nhưng nhỏ hơn đáng kể chi phí phải inference lại mỗi lần
quét θ. Chúng vẫn là artifact run, không commit vào Git.

`taxonomy.snapshot.yaml` tồn tại vì `taxonomy_sha256` cho biết taxonomy **đã đổi**
nhưng không cho biết **đổi gì**. Snapshot cho phép so sánh hai run qua ranh giới
taxonomy version.

---

## 3. Manifest bắt buộc

### 3.1 Đã có ✅

`command`, `config`, `class_ids`, `taxonomy_sha256`, `split_sha256`,
`pretrained_classifier`, `git`, `environment`, `dataset_windows`, `pos_weight`,
`complete`, `best_checkpoint`.

### 3.2 Phải thêm ○

| Trường | Kiểu | Vì sao |
|---|---|---|
| `data_manifest_sha256` | str | Biết feature version nào đã dùng |
| `feature_config_sha256` | str | `LogMelConfig.checksum` — đổi hop/mel là đổi bài toán |
| `seeds` | dict | `{python, numpy, torch, cuda}` — chứng minh đã seed đủ |
| `postproc` | dict \| null | θ và filter đã áp; null khi chưa hiệu chuẩn |
| `checkpoint_selection_rule` | str | `"best dev frame_macro_f1"` |
| `primary_metric` | str | Tên metric chính, tránh nhầm khi so run |
| `branch` | str | `"A"` \| `"B"` \| `"C"` — nhánh transfer |
| `wall_clock_s` | float | Ước lượng ngân sách cho lần sau |

### 3.3 Ràng buộc `git`

```json
{"revision": "29b9e85…", "dirty": false}
```

**`dirty: true` làm run không hợp lệ cho báo cáo.** Cảnh báo lúc train, và từ
chối khi sinh measurement cuối.

### 3.4 Preflight phải được lưu cùng run

Trước khi tạo checkpoint đầu tiên, launcher phải kiểm và ghi verdict của các
điều kiện sau vào manifest hoặc artifact preflight có hash:

| Điều kiện | Verdict fail |
|---|---|
| D3/D4 đã pass; split frozen và hash khớp | Chặn train chính thức |
| Taxonomy, feature config và data manifest có hash | Chặn vì không tái lập được |
| `class_ids` đúng task (`polyphonic_class_ids` cho SED) | Chặn vì class order sai làm checkpoint vô nghĩa |
| Branch, seed và training budget đã khai báo | Chặn so sánh liên-run, không chặn smoke test được đánh dấu `provisional` |
| Working tree sạch, revision là commit cụ thể | Không được dùng cho measurement cuối |

Không dùng `--allow-unfrozen-split` để lách một run báo cáo. Nếu cần dò đường,
run phải ghi `provisional: true`; mọi metric của nó chỉ phục vụ chẩn đoán.

---

## 4. Các pha

### ✅ Pha 1 — Run manifest cơ bản *(đã có)*

Manifest, metrics, checkpoint, history. Thiếu 8 trường ở §3.2.

### ○ Pha 2 — Cổng dữ liệu chặn train ⭐ *ưu tiên cao*

Trước khi train, kiểm và **fail nếu không pass**:

| # | Kiểm | Fail thì |
|---:|---|---|
| 1 | Split đã freeze (có trong `data/splits/`, hash khớp) | Chặn |
| 2 | Cổng D4 pass | Chặn |
| 3 | `taxonomy_sha256` khớp config đang dùng | Chặn |
| 4 | Feature manifest đầy đủ, không thiếu file | Chặn |
| 5 | Không group nào xuyên split | Chặn |

```bash
.venv/Scripts/python.exe -m scripts.check_data_contract datased
# Cờ bỏ qua CHỈ dùng khi cố ý dò đường:
.venv/Scripts/python.exe -m scripts.train_sed --allow-unfrozen-split
```

Baseline hiện tại lẽ ra phải chạy với `--allow-unfrozen-split`. Cờ này làm
manifest ghi `"provisional": true` để số đó không lẫn vào báo cáo.

### ○ Pha 3 — Lưu logit thô ⭐ *ưu tiên cao*

```bash
.venv/Scripts/python.exe -m scripts.predict --run ml/runs/<id> --split dev
.venv/Scripts/python.exe -m scripts.predict --run ml/runs/<id> --split test
```

Ghi `predictions/<split>.npz` gồm `logits`, `targets`, `recording_ids`,
`frame_offsets`, `mask`. **`mask` bắt buộc** — không có nó thì frame padding lẫn
vào metric.

### ○ Pha 4 — Hiệu chuẩn post-processing

```bash
.venv/Scripts/python.exe -m scripts.calibrate_postproc --run ml/runs/<id>
```

Theo [ADR-0003](decisions/ADR-0003-threshold-va-post-processing.md):
duration prior từ **train**, θ quét trên **dev**. Ghi `postproc.json` rồi
**đóng băng**.

### ○ Pha 5 — Metric thật

```bash
.venv/Scripts/python.exe -m scripts.evaluate_run --run ml/runs/<id> --split dev
```

Event-based F1 (`sed_eval`), PSDS-1 và PSDS-2 (`psds_eval`), bootstrap CI theo
**recording**. Không tự viết lại metric đã có thư viện chuẩn.

### ○ Pha 6 — Phân tích lỗi

Confusion matrix, insertion/deletion/fragmentation/merging, hiệu năng theo
duration/polyphony/confidence. Kết quả cập nhật `confusable_with` trong
[taxonomy.md §8](taxonomy.md).

### ○ Pha 7 — So sánh nhiều run

```bash
.venv/Scripts/python.exe -m scripts.compare_runs ml/runs/A ml/runs/B ml/runs/C
```

**Phải từ chối so sánh** khi 6 điều kiện của
[evaluation_protocol §6](evaluation_protocol.md) không khớp, thay vì im lặng in
bảng gây hiểu nhầm.

---

## 5. Các giai đoạn huấn luyện

| ID | Giai đoạn | Mục tiêu | Phụ thuộc |
|---|---|---|---|
| **T1** | DataSEC classifier | Baseline 22 coarse + subclass head | D4 |
| **T2** | SED nhánh A và B | Baseline dưới + AudioSet pretrained | D4 |
| **T3** | SED nhánh C | Transfer DataSEC → DataSED, **RQ1** | T1, T2 |
| **T4** | Hiệu chuẩn + metric | θ, filter, event-F1, PSDS | T2, T3 |
| **T5** | Đóng băng predictions | Đầu vào cố định cho caption và RAG | T4 |

**T5 tồn tại để RQ2 và RQ3 có nghĩa.** Nếu caption và retrieval chạy trên SED
prediction khác nhau mỗi lần, Δ của chúng trộn với Δ của SED.

---

## 6. Chính sách tài nguyên

| # | Quy tắc | Vì sao |
|---:|---|---|
| 1 | Smoke test trên subset trước full run | Bắt lỗi shape/config trong 2 phút thay vì 2 giờ |
| 2 | Ước lượng dung lượng trước, fail nếu vượt quota | 3 nhánh × 3 seed × checkpoint tích lũy nhanh |
| 3 | Chỉ giữ `best` và `last`, không giữ mỗi epoch | Dung lượng |
| 4 | `predictions/test.npz` chỉ sinh **sau** khi chọn model | Tránh cám dỗ nhìn test |
| 5 | Không sweep không có giả thuyết và budget cap | Sweep vô định hướng là tuning trá hình |
| 6 | Ghi `wall_clock_s` mọi run | Xếp lịch cho lần sau |

### Ngân sách ước lượng

| Hạng mục | Ước lượng | Cơ sở |
|---|---|---|
| SED nhánh A, 8 epoch | ~20 phút | Baseline đã chạy |
| SED nhánh B/C với CNN14 | ⚠️ CẦN XÁC MINH | Model lớn hơn nhiều |
| Predict + lưu logit | ~2 phút/split | |
| Quét θ per-class trên logit đã lưu | ~30 giây | CPU, không cần GPU |
| Event-F1 + PSDS | ~2 phút | CPU |
| 3 nhánh × 3 seed | ⚠️ CẦN XÁC MINH | Phụ thuộc nhánh B/C |

> Nếu 3 nhánh × 3 seed vượt ngân sách, cut-list
> ([PLAN.md](PLAN.md)) cho phép giảm xuống 1 seed — nhưng **phải ghi rõ và không
> tuyên bố Δ nhỏ có ý nghĩa**.

---

## 7. Resume và phục hồi

| # | Quy tắc |
|---:|---|
| 1 | Resume kiểm `config_sha256`, `split_sha256`, `taxonomy_sha256`, `feature_config_sha256` — khác bất kỳ cái nào thì **từ chối** |
| 2 | Khôi phục đầy đủ RNG state (python, numpy, torch, cuda) |
| 3 | Run bị ngắt **không** được ghi `complete = true` |
| 4 | Artifact thiếu manifest hoặc `complete != true` là **không hợp lệ** cho báo cáo |
| 5 | `dirty = true` làm run không hợp lệ cho báo cáo cuối |

---

## 8. Thứ tự thực thi

```bash
# 0. Cổng dữ liệu — CHẶN
.venv/Scripts/python.exe -m scripts.check_data_contract datased

# 1. Train
.venv/Scripts/python.exe -m scripts.train_sed --branch B --seed 20260922 --device cuda

# 2. Logit thô trên dev
.venv/Scripts/python.exe -m scripts.predict --run ml/runs/<id> --split dev

# 3. Hiệu chuẩn (duration prior từ train, θ từ dev) rồi ĐÓNG BĂNG
.venv/Scripts/python.exe -m scripts.calibrate_postproc --run ml/runs/<id>

# 4. Metric trên dev
.venv/Scripts/python.exe -m scripts.evaluate_run --run ml/runs/<id> --split dev

# 5. So sánh ba nhánh, chọn cấu hình cuối
.venv/Scripts/python.exe -m scripts.compare_runs ml/runs/A ml/runs/B ml/runs/C

# --- RANH GIỚI: từ đây trở đi chạm vào test ---

# 6. Logit thô trên test, áp postproc.json y nguyên, chạy MỘT lần
.venv/Scripts/python.exe -m scripts.predict --run ml/runs/<id> --split test
.venv/Scripts/python.exe -m scripts.evaluate_run --run ml/runs/<id> --split test

# 7. Sinh measurement
.venv/Scripts/python.exe -m scripts.report_run ml/runs/<id>
```

**Bước 5 là ranh giới.** Mọi lựa chọn phải xong trước nó. Sau bước 5 không quay
lại sửa θ.

---

## 9. Trạng thái triển khai

| Thành phần | Trạng thái |
|---|---|
| `train_sed`, `train_classifier` | ✅ |
| `report_run` | ✅ |
| Manifest cơ bản | ✅ |
| 8 trường manifest bổ sung | ○ |
| `check_data_contract` | ○ **ưu tiên cao** |
| `predict` (lưu logit) | ○ **ưu tiên cao** |
| `calibrate_postproc` | ○ |
| `evaluate_run` (event-F1, PSDS) | ○ |
| `compare_runs` | ○ |
| Resume với kiểm hash | ○ |
| Phân tích lỗi | ○ |
