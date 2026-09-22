# HANDOFF — Nhiệm vụ tiếp theo

> **File này là brief công việc cho agent tiếp nhận.** Nó không phải tài liệu
> khóa luận. Xóa hoặc thay khi Phase B xong.
>
> Trạng thái lúc giao: commit `5c80134`. Bộ tài liệu đã hoàn tất (5,564 dòng).
> Việc còn lại: **hoàn tất lý thuyết hệ thống (Phase A) trước, rồi mới viết code
> phân tích (Phase B)**.

---

## 0. Đọc trước khi làm bất cứ gì

Theo đúng thứ tự, không bỏ bước:

| # | File | Lấy gì ở đó |
|---:|---|---|
| 1 | [CLAUDE.md](CLAUDE.md) | Đang ở đâu, quyết định đã khóa, lệnh hay dùng, quy ước |
| 2 | [docs/STATUS.md](docs/STATUS.md) | Cái gì đã chạy được, kèm bằng chứng |
| 3 | [docs/PLAN.md](docs/PLAN.md) | Đường găng và cut-list |
| 4 | [docs/SYSTEM.md](docs/SYSTEM.md) | Đặc tả đích — §4.3 DDL, §6 contract caption, §7 RAG, §9 run layout |
| 5 | [docs/evaluation_protocol.md](docs/evaluation_protocol.md) | **Bắt buộc** trước khi viết bất kỳ code metric nào |
| 6 | [docs/decisions/](docs/decisions/) | 6 ADR — không quyết lại |

**Không viết lại tài liệu.** Chúng vừa được viết xong và đã được duyệt. Nếu phát
hiện tài liệu sai so với thực tế, sửa **đúng chỗ sai** và ghi vào
[CLAUDE.md](CLAUDE.md) §10, không viết lại cả file.

---

## 1. Môi trường

Windows. Shell: PowerShell hoặc Git Bash.

```bash
# LUÔN dùng interpreter này. `python` trên PATH thiếu dependency.
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m scripts.<name>
```

GPU: RTX 3070 Laptop, **8 GB VRAM**. torch 2.11.0+cu128. Đây là ràng buộc thật —
mọi thiết kế model phải vừa 8 GB.

Trạng thái sạch lúc giao: **18 test pass, ruff sạch, 0 link docs hỏng**. Giữ
nguyên trạng thái này sau mỗi commit.

---

## 2. Mười ràng buộc cứng — vi phạm là làm hỏng kết quả khoá luận

| # | Ràng buộc | Vì sao |
|---:|---|---|
| 1 | **Không dùng test set** để chọn threshold, checkpoint, encoder hay config | Test chạy **một lần**, config đóng băng |
| 2 | **Duration prior (`w_c`, `d_min_c`, `g_max_c`) suy từ TRAIN**, không từ dev | [ADR-0003](docs/decisions/ADR-0003-threshold-va-post-processing.md) — suy từ dev là rò rỉ, triệu chứng dễ bị chẩn đoán nhầm thành overfit model |
| 3 | SED head dùng `taxonomy.polyphonic_class_ids` (**21**), không phải `class_ids` (22) | `wind_turbine` ngoài polyphonic label set |
| 4 | **Không bịa số, không bịa trích dẫn.** Chưa chắc → `⚠️ CẦN XÁC MINH` | |
| 5 | Số trong docs phải **sinh từ script**, không gõ tay | Xem `scripts/report_*.py` làm mẫu |
| 6 | Không commit audio, feature, checkpoint, vector index | `.gitignore` đã chặn; đừng thêm ngoại lệ |
| 7 | Không sửa raw annotation. Nghi ngờ → ghi phân tích lỗi | |
| 8 | `services/api` **không** import torch, không load checkpoint | |
| 9 | Không tự viết lại metric đã có thư viện chuẩn (`sed_eval`, `psds_eval`) | |
| 10 | Không đổi `taxonomy.yaml` version `0.1` mà không có ADR | Checkpoint lưu `taxonomy_sha256` |

---

## 3. Sự thật đã xác minh — đừng khám phá lại

Tất cả đã có artifact. Nguồn:
[docs/measurements/archive_audit_20260922.md](docs/measurements/archive_audit_20260922.md),
[docs/data_inventory.md](docs/data_inventory.md).

| Sự thật | Giá trị |
|---|---|
| DataSEC | 5,048 WAV, 22 coarse + 28 subclass, nhãn trong **cây thư mục**, 7.01 GiB |
| DataSED | 717 WAV, 18.6847 h, 44.1 kHz, mono 716 / stereo 1, nhãn trong **2 CSV** |
| DataSED annotation | 4,034 poly event / 21 class / 703 rec · 4,309 mono / 22 class / 717 rec |
| Cả hai archive | MD5 khớp, verdict `pass`, **không chứa LICENSE/README** |
| License | `cc-by-nc-sa-4.0` cả hai — thành phần `SA` áp lên checkpoint |
| **Imbalance DataSEC** | **38:1**; `voices` 1,900 (37.6%) + `music` 1,001 (19.8%) = **57.5%** |
| **4 subclass < 25 file** | `Crickets` 20, `Olive shaker` 20, `Magpies` 21, `Lawn mower` 21 |
| Taxonomy | version `0.1`, SHA-256 `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a` |
| Split candidate | 435/142/140, SHA-256 `656c1851…` — **chưa freeze** |
| Baseline SED | frame macro-F1 test **0.359448** — số dò đường, 4 lý do ở [STATUS §5](docs/STATUS.md) |

**Rủi ro R1 — đọc kỹ.** Hai dataset do **cùng 6 tác giả** công bố (Fredianelli,
Artuso, Pompei, Licitra, Iannace, Akbaba), cùng miền đo ngoài trời, cách nhau 4
tháng. Nếu DataSEC cắt từ recording của DataSED thì transfer learning trở thành
train-trên-test. Giả định mặc định là **có khả năng trùng nguồn** cho tới khi đo
được ngược lại. Đây là lý do B1 là việc đầu tiên của Phase B.

---

# PHASE A — Hoàn tất lý thuyết hệ thống

Không train model nào ở phase này. Mục tiêu: biến mọi thiết kế trong
`SYSTEM.md` thành **artifact kiểm được bằng máy**, để Phase B không phải vừa
code vừa quyết thiết kế.

## A1 · Sáu JSON Schema contract ⭐ ưu tiên cao

Hiện `contracts/` chỉ có README liệt kê 6 file "dự kiến". **0/6 tồn tại.**

Tạo, dùng JSON Schema draft 2020-12:

```text
contracts/recording.schema.json
contracts/event.schema.json
contracts/timeline.schema.json
contracts/inference_response.schema.json
contracts/retrieval_result.schema.json
contracts/run_manifest.schema.json
```

**Nguồn suy schema — theo thứ tự ưu tiên:**

1. `run_manifest.schema.json` phải suy từ **manifest thật đang có**
   (`ml/runs/sed_polyphonic_20260922T115340Z/manifest.json`), cộng 8 trường bổ
   sung ở [TRAINING_OPS_PLAN §3.2](docs/TRAINING_OPS_PLAN.md). Đánh dấu 8 trường
   mới là optional cho tới khi `train_sed` ghi chúng.
2. `event.schema.json`, `recording.schema.json` từ DDL ở
   [SYSTEM §4.3](docs/SYSTEM.md).
3. `timeline.schema.json`, `inference_response.schema.json` từ
   [SYSTEM §6.1–6.2](docs/SYSTEM.md).
4. `retrieval_result.schema.json` từ [SYSTEM §7.4](docs/SYSTEM.md).

**Nghiệm thu:**

- [ ] `tests/test_contracts.py` validate **manifest thật hiện có** qua schema và pass
- [ ] Schema từ chối: `onset_s >= offset_s`; `score` ngoài `[0,1]`; `class_id`
      ngoài 22 giá trị của taxonomy; `evidence: []` trên answer có claim
- [ ] `retrieval_result` bắt buộc có `filters_applied` **và** `evidence` (kể cả rỗng)
- [ ] `contracts/README.md` cập nhật: bỏ chữ "dự kiến", thêm bảng version
- [ ] Không hardcode danh sách 22 class trong schema — sinh từ `taxonomy.yaml`
      lúc build test, hoặc dùng `pattern`; ràng buộc 10

> Điểm dễ sai: schema không được nới lỏng để manifest hiện tại pass. Nếu manifest
> thật thiếu trường **bắt buộc theo thiết kế**, để trường đó `required` và ghi
> test `xfail` kèm lý do, rồi thêm vào nợ kỹ thuật của `PLAN.md`.

## A2 · Caption lexicon và lexicon cấm ⭐ ưu tiên cao

Đây là điều kiện để lên taxonomy `1.0` ([taxonomy.md §11](docs/taxonomy.md), mục
5–6) và là nền của ràng buộc G1/G3.

Tạo `ml/configs/caption_lexicon.yaml`:

```yaml
version: "0.1"
# Mỗi coarse class → cụm từ hợp lệ khi CHỈ có coarse evidence
classes:
  glass_breaking:
    en: ["glass breaking", "breaking glass", "shattering glass"]
    vi: ["tiếng kính vỡ", "kính vỡ"]
  sirens_and_alarms:
    en: ["a siren- or alarm-like sound"]
    vi: ["âm thanh giống còi hú hoặc báo động"]
    # Lớp gộp: KHÔNG được dùng cụm chỉ một nguồn khi chỉ có coarse
    forbidden_when_coarse_only: ["ambulance", "fire alarm", "police car"]
# Cấm tuyệt đối — ràng buộc G3, hệ quả của ADR-0001
forbidden_terms:
  en: [emergency, crime, intruder, accident, danger, attack, break-in, threat]
  vi: [khẩn cấp, tội phạm, đột nhập, tai nạn, nguy hiểm, tấn công]
```

Viết đầy đủ **22 lớp**, lấy cụm từ hợp lệ từ cột `📌 Caption` trong
[taxonomy.md](docs/taxonomy.md) §2–§6, và chính sách lớp gộp từ §7.

**Nghiệm thu:**

- [ ] `ml/captioning/lexicon.py` load + checksum (theo mẫu `ml/taxonomy.py`)
- [ ] Hàm `extract_mentions(text) -> set[class_id]` — bản đồ ngược cụm từ → class
- [ ] Hàm `check_grounding(caption, timeline) -> GroundingReport` kiểm G1/G2/G3
- [ ] Test: mọi 22 class có ít nhất 1 cụm EN và 1 cụm VI
- [ ] Test: caption chứa `forbidden_terms` bị từ chối (G3)
- [ ] Test: caption nói `"a gunshot"` khi timeline chỉ có
      `thunder_fireworks_gunshot` bị từ chối
- [ ] Test: caption lớp gộp **thiếu** mệnh đề "no subclass ground truth" bị từ chối
      ([taxonomy.md §7](docs/taxonomy.md))
- [ ] Không có cụm từ nào trùng giữa hai class (giống `Ambiguous taxonomy alias`)

## A3 · Schema cơ sở dữ liệu thành migration thật

DDL hiện chỉ là code block trong [SYSTEM §4.3](docs/SYSTEM.md). Biến nó thành
artifact chạy được.

- `services/api/alembic/` + `alembic.ini`
- Migration `0001_initial_schema.py` khớp **đúng** DDL của SYSTEM §4.3
- 7 bảng: `recordings`, `events`, `event_subclass_predictions`, `captions`,
  `caption_evidence`, `retrieval_documents`, `runs`

**Nghiệm thu:**

- [ ] `alembic upgrade head` chạy được trên PostgreSQL 16 + pgvector
- [ ] Mọi CHECK constraint của SYSTEM §4.3 có trong migration
      (`offset_s > onset_s`, `score BETWEEN 0 AND 1`, …)
- [ ] Index HNSW và GIN có mặt
- [ ] Nếu không dựng được PostgreSQL: **vẫn viết migration**, ghi
      `⚠️ CẦN XÁC MINH` vào nợ kỹ thuật, không bỏ task

## A4 · Đặc tả query set cho retrieval benchmark

Viết `docs/retrieval_queryset.md` + `ml/configs/queryset.yaml`.

100 query, 4 nhóm theo [SYSTEM §8.5](docs/SYSTEM.md): single-class 30,
multi-class 25, temporal 25, duration/confidence 20.

**Ràng buộc quan trọng nhất:** relevance phải xác định được **bằng máy từ ground
truth**, không phán đoán thủ công.

```yaml
- id: Q001
  group: temporal
  text_vi: "Có tiếng kính vỡ nào trước tiếng còi báo động không?"
  text_en: "Is there glass breaking before a siren?"
  relevance_rule:
    type: temporal
    predicate: before
    class_a: glass_breaking
    class_b: sirens_and_alarms
    tolerance_s: 0
  hard_filters: {}
```

**Nghiệm thu:**

- [ ] 100 query, đúng phân bố 30/25/25/20
- [ ] Mỗi query có `relevance_rule` máy đánh giá được
- [ ] `ml/retrieval/relevance.py` tính relevant set từ ground truth
- [ ] Test: mọi query có ≥ 1 recording relevant trên DataSED (query không có
      relevant nào là query vô dụng — sửa hoặc bỏ)
- [ ] Query set **đóng băng trước** khi chạy retrieval lần đầu

## A5 · CI

`.github/workflows/ci.yml`:

| Job | Lệnh | Chặn |
|---|---|---|
| lint | `ruff check .` | ✅ |
| test | `pytest -q` | ✅ |
| guard-api | `grep -r "import torch" services/api/ && exit 1 \|\| exit 0` | ✅ |
| docs-links | script kiểm link nội bộ (đã có mẫu ở cuối §6 dưới) | ✅ |

**Nghiệm thu:** CI xanh trên `master`; 4 job đều chạy.

## A6 · Systematic search cho RELATED_WORK

[docs/RELATED_WORK.md](docs/RELATED_WORK.md) đang ở mức V2 cho 2 dataset, V0–V1
cho mọi thứ khác. Kế hoạch search đã có ở §7, thang xác minh ở §0.

**Chỉ làm nếu có truy cập web.** Nếu không, bỏ qua và ghi vào nợ kỹ thuật —
đừng bịa trích dẫn để lấp bảng §8.

Ưu tiên: tìm paper kèm DataSEC/DataSED (nâng V2 → V3), và tìm xem đã có baseline
công bố trên hai dataset này chưa (nếu có → V4, là baseline để so trực tiếp).

**Nghiệm thu:** mọi dòng trong bảng §8 hoặc đạt V3+ với DOI thật, hoặc giữ
nguyên `⚠️ CẦN XÁC MINH`. Ba claim khoảng trống ở §9 được chứng minh hoặc **rút
lại** — rút lại không làm khoá luận yếu đi, giữ claim sai thì có.

### Nghiệm thu Phase A

- [ ] 6 schema tồn tại, `tests/test_contracts.py` pass trên manifest thật
- [ ] Caption lexicon 22 lớp + lexicon cấm, G1/G2/G3 có test tự động
- [ ] Migration khớp SYSTEM §4.3
- [ ] Query set 100 câu, relevance máy đánh giá được, đã đóng băng
- [ ] CI xanh 4 job
- [ ] `pytest -q` và `ruff check .` sạch
- [ ] Cập nhật [CLAUDE.md](CLAUDE.md) §3 + §10 và [docs/STATUS.md](docs/STATUS.md)

---

# PHASE B — Code phân tích

Bắt đầu **sau khi** Phase A xong. Thứ tự dưới đây là **đường găng** — không làm
nhảy cóc.

## B1 · `scripts.find_duplicates` ⭐⭐ CHẶN MỌI THỨ

Cổng D3. Không có nó thì không freeze split được, và không thí nghiệm transfer
nào hợp lệ.

Đặc tả đầy đủ: [DATA_PLAN §7](docs/DATA_PLAN.md). Ba tầng:

| Tầng | Bắt được | Phương pháp |
|---|---|---|
| **T1** | Byte-identical | SHA-256 trên bytes — ✅ đã có trong `inventory.py` |
| **T2** | Cùng nội dung, khác container/encode | SHA-256 trên **PCM đã decode + resample 16 kHz mono** |
| **T3** | Cùng nguồn, khác đoạn cắt | MFCC 20 + delta → 40 chiều, frame 1 s hop 0.5 s, cosine trượt cửa sổ |

Ngưỡng T3 khởi đầu: `duplicate` ≥ 0.95, `review` 0.85–0.95, cả hai cần đoạn chồng
lấp ≥ 3 s.

> **Ngưỡng này PHẢI hiệu chuẩn, không dùng như hằng số.** Cách làm: lấy 8 nhóm T1
> đã biết của DataSED làm positive, cặp ngẫu nhiên khác lớp làm negative, chọn
> ngưỡng tách hai phân bố. Ghi kết quả hiệu chuẩn vào `docs/measurements/`.

**Ba kiểm tra phải chạy:** trong DataSEC · trong DataSED · **xuyên DataSEC–DataSED**.

Output: `data/manifests/duplicate_groups.csv` theo schema
[DATA_PLAN §5.2](docs/DATA_PLAN.md) — chú ý cột `cross_dataset`.

**Nghiệm thu:**

- [ ] Tái phát hiện đúng 8 nhóm T1 đã biết của DataSED
- [ ] Hiệu chuẩn ngưỡng T3 có báo cáo trong `docs/measurements/`
- [ ] `duplicate_groups.csv` sinh ra, có cột `cross_dataset`
- [ ] `quarantine_review` **không** tự động xử lý — chờ người quyết
- [ ] Báo cáo tỷ lệ clip DataSEC trùng dev/test DataSED
- [ ] Test trên fixture tổng hợp (theo mẫu `tests/test_archive_audit.py`, không
      cần dữ liệu thật)

> **Nếu trùng lặp > 5%:** dừng, báo ngay. Theo
> [DATA_PLAN §7.6](docs/DATA_PLAN.md), RQ1 phải đổi cách diễn giải thành kết quả
> âm tính về leakage. Đây là **kết quả hợp lệ**, không phải thất bại — nhưng phải
> đổi ngay ở tuần này, không đợi tới lúc train.

## B2 · `scripts.check_leakage`

Cổng D4. 5 kiểm của [DATA_PLAN §8.4](docs/DATA_PLAN.md). Exit code khác 0 khi fail.

## B3 · Giải nén + inventory DataSEC

```bash
.venv/Scripts/python.exe -m scripts.data_sources extract datasec
.venv/Scripts/python.exe -m scripts.build_inventory datasec
.venv/Scripts/python.exe -m scripts.report_data_inventory
```

7.01 GiB — kiểm dung lượng đĩa trước. Sau đó chạy lại B1 để có T1/T2/T3 trên
DataSEC.

**Nghiệm thu:** `datasec_inventory.csv` đầy đủ; `data_inventory.md` sinh lại có
số DataSEC thật (duration, sample rate, channels); mọi file có verdict hoặc
reason code.

## B4 · Freeze split

Chạy lại `scripts.create_splits` **sau** B1/B2, vì duplicate group có thể buộc
recording đổi split. Ghi SHA-256 mới, cập nhật STATUS, tag `data-v1.0` theo
[DATA_PLAN §13](docs/DATA_PLAN.md).

## B5 · `scripts.check_data_contract`

Pha 2 của [TRAINING_OPS_PLAN](docs/TRAINING_OPS_PLAN.md). Chặn train khi cổng D4
chưa pass. Cờ `--allow-unfrozen-split` làm manifest ghi `"provisional": true`.

## B6 · Hạ tầng đánh giá — bốn script

Không train gì mới ở bước này; chạy trên checkpoint đã có.

| Script | Việc | Đặc tả |
|---|---|---|
| `scripts.predict` | Lưu logit thô `predictions/<split>.npz` gồm `logits`, `targets`, `recording_ids`, `frame_offsets`, **`mask`** | TRAINING_OPS Pha 3 |
| `scripts.calibrate_postproc` | duration prior từ **train**, θ quét trên **dev**, ghi `postproc.json` | [ADR-0003](docs/decisions/ADR-0003-threshold-va-post-processing.md) |
| `scripts.evaluate_run` | event-based F1 (`sed_eval`), PSDS-1/PSDS-2 (`psds_eval`), bootstrap CI theo **recording** | [evaluation_protocol §3](docs/evaluation_protocol.md) |
| `scripts.compare_runs` | **Từ chối** so sánh khi 6 điều kiện không khớp | [evaluation_protocol §6](docs/evaluation_protocol.md) |

**Tham số metric đã đóng băng, dùng đúng, không tự chọn lại:**

- Event-based: `t_collar` 0.200 s, `percentage_of_length` 0.200, macro
- PSDS-1: DTC 0.7, GTC 0.7, `alpha_ct` 0, `alpha_st` 1, `max_efpr` 100
- PSDS-2: DTC 0.1, GTC 0.1, CTTC 0.3, `alpha_ct` 0.5, `alpha_st` 1, `max_efpr` 100

**Nghiệm thu:**

- [ ] `mask` có trong `.npz` và **được dùng** — padding không vào metric
- [ ] Quét lại θ **không** cần chạy lại inference
- [ ] `compare_runs` từ chối so frame-F1 với event-F1, và từ chối so polyphonic
      với monophonic
- [ ] Bootstrap theo recording, không theo frame (671,570 frame chỉ từ 140 recording)
- [ ] Class có `n_test < 10` báo bằng **số tuyệt đối**, không báo tỷ lệ

## B7 · Tám trường manifest bổ sung

[TRAINING_OPS_PLAN §3.2](docs/TRAINING_OPS_PLAN.md):
`data_manifest_sha256`, `feature_config_sha256`, `seeds`, `postproc`,
`checkpoint_selection_rule`, `primary_metric`, `branch`, `wall_clock_s`.

Cũng sửa: `git.revision` phải là commit thật (hiện ghi `"HEAD"` với
`dirty: true`), và `seeds` phải chứng minh đã seed python/numpy/torch/cuda.

## B8 · Ba nhánh SED

Chỉ bắt đầu sau B1–B7. [ADR-0002](docs/decisions/ADR-0002-encoder-va-nhanh-transfer.md).

| Nhánh | Encoder | Ghi chú |
|---|---|---|
| A | CNN+BiGRU random | Đã có, chạy lại trên split đã freeze |
| B | PANNs CNN14 (AudioSet) | Cần `logmel_panns_v1` theo cấu hình PANNs |
| C | PANNs → DataSEC → DataSED | **Class-balanced sampling** khi pretrain DataSEC |

**RQ1 = `C − B`.** Báo `C − A` được, nhưng dán nhãn rõ là "tổng lợi ích của mọi
pretraining", không phải lợi ích của DataSEC.

Kiểm trước: CNN14 (~81M tham số) có vừa 8 GB với window 10 s không. Nếu OOM:
giảm batch, gradient accumulation, hoặc window 5 s — ghi rõ vào manifest.

---

## 4. Quy ước commit

```text
<type>: <mô tả tiếng Việt>

<thân bài: làm gì, vì sao, kiểm chứng bằng gì>

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

Type: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `exp`.

Commit nhỏ, mỗi commit một việc hoàn chỉnh có test. Không commit khi
`pytest`/`ruff` đỏ.

---

## 5. Cuối mỗi block công việc

1. `pytest -q` và `ruff check .` sạch
2. Cập nhật [CLAUDE.md](CLAUDE.md) §3 (trạng thái) và §10 (nhật ký, có ngày)
3. Cập nhật [docs/STATUS.md](docs/STATUS.md) nếu có artifact mới
4. Sinh measurement **bằng script** nếu có số mới
5. Viết ADR nếu có quyết định kiến trúc
6. Cập nhật nợ kỹ thuật trong [docs/PLAN.md](docs/PLAN.md)

**Không ghi "đã hoàn thành" nếu chưa có command và artifact kiểm chứng.**

---

## 6. Script kiểm link docs (dùng cho CI job `docs-links`)

```python
import re, pathlib, sys
root = pathlib.Path('.')
bad = 0
files = list(root.glob('*.md')) + list(root.glob('docs/**/*.md')) + list(root.glob('*/README.md'))
for md in files:
    if '.venv' in str(md):
        continue
    for text, link in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', md.read_text(encoding='utf-8')):
        if link.startswith(('http', '#', 'mailto')):
            continue
        if not (md.parent / link.split('#')[0]).resolve().exists():
            print(f'BROKEN {md}: {text!r} -> {link}')
            bad += 1
print(f'broken_links = {bad}')
sys.exit(1 if bad else 0)
```

---

## 7. Nếu bế tắc

| Tình huống | Làm gì |
|---|---|
| Tài liệu mâu thuẫn với code | Code là sự thật về *hiện trạng*; tài liệu là sự thật về *thiết kế đích*. Sửa chỗ sai, ghi vào CLAUDE.md §10 |
| Không dựng được PostgreSQL / không có web | **Vẫn làm phần làm được**, ghi phần còn lại vào nợ kỹ thuật. Đừng bỏ cả task |
| Task vượt ngân sách thời gian | Dùng cut-list [PLAN.md](docs/PLAN.md). Cắt từ trên xuống, không nhảy cóc |
| Cần quyết định kiến trúc mới | Viết ADR, **hỏi trước khi triển khai** |
| D3 phát hiện trùng lặp lớn | **Dừng và báo.** Đây là kết quả khoa học, không phải bug |

**Không bao giờ cắt:** cổng D3/D4 và audit leakage · event-based F1 và PSDS ·
bộ metric hallucination · giao thức test một lần.
