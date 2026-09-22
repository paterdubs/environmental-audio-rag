# DATA_PLAN.md — Kế hoạch dữ liệu

## 1. Vai trò dataset

| Dataset | Vai trò chính | Không dùng để |
|---|---|---|
| DataSEC | Classification, encoder pretraining, subclass refinement | Đánh giá SED trong soundscape liên tục |
| DataSED polyphonic | Huấn luyện và đánh giá SED chính | Đánh giá subclass bị gộp |
| DataSED monophonic | Benchmark phụ và ablation label policy | Thay thế benchmark polyphonic chính |

## 2. Provenance phải lưu

Mỗi archive cần:

- Record DOI và version DOI.
- URL tải chính thức.
- Ngày tải.
- SHA-256 archive.
- License file nguyên bản và hash.
- README nguyên bản và hash.
- File count, total duration và schema version sau giải nén.

Không suy license từ tên repository. License trong archive là nguồn kiểm tra bắt buộc.

## 3. Layout

```text
data/
├── raw/
│   ├── datasec/
│   └── datased/
├── interim/       # normalized audio/labels; tái tạo được
├── features/      # tensors; tái tạo được
├── manifests/     # provenance, inventory, exclusions, duplicate groups
├── annotations/   # canonical labels và mapping có version
├── reference/     # taxonomy/source documentation nhỏ
└── splits/        # frozen IDs cùng hash
```

## 4. Acquisition

1. Tải metadata, LICENSE và README.
2. Ghi record version vào `source_manifest`.
3. Tải archive; kiểm checksum trước giải nén.
4. Giải nén vào thư mục versioned.
5. Không đổi tên raw file.
6. Tạo inventory bằng script; không chỉnh CSV bằng tay.

## 5. Validation

Mỗi audio file phải kiểm:

- Đọc được toàn bộ.
- Sample rate, channels, sample count và duration hữu hạn.
- Không zero-byte hoặc toàn NaN.
- Annotation onset ≥ 0, offset > onset, offset ≤ duration + tolerance.
- Class tồn tại trong taxonomy đúng label mode.

Chênh lệch giữa paper và archive hiện hành phải được ghi, không tự ép số file theo paper.

## 6. Canonicalization

Mỗi annotation giữ đồng thời:

```text
source_label
canonical_class_id
taxonomy_version
label_mode
```

Không tách `sirens_and_alarms` hoặc `thunder_fireworks_and_gunshot` trong DataSED bằng suy đoán. Subclass prediction là output model riêng, không phải ground truth SED.

## 7. Deduplication và leakage

Tạo:

- Cryptographic hash cho exact duplicate.
- Duration/sample-rate signature.
- Acoustic fingerprint cho near duplicate.
- Duplicate group ID sau review rule-based.

Chạy ba kiểm tra:

1. Duplicate bên trong DataSEC.
2. Duplicate bên trong DataSED.
3. Duplicate xuyên DataSEC–DataSED.

Nếu một source xuất hiện ở cả hai dataset, toàn bộ group phải nằm cùng evaluation boundary hoặc bị loại khỏi pretraining khi counterpart thuộc DataSED test.

## 8. Split

### 8.1 DataSEC

- Đơn vị split: duplicate/content group.
- Mục tiêu ban đầu: 70/15/15 train/dev/test.
- Stratify theo coarse class và subclass nếu khả thi.
- Không để phiên bản xử lý khác của cùng source xuyên split.

### 8.2 DataSED

- Đơn vị split: recording group, không phải event hoặc segment.
- Mục tiêu ban đầu: 60/20/20 train/dev/test.
- Iterative multilabel stratification theo event presence.
- Giữ distribution class, duration và polyphony gần nhau.
- Split seed và danh sách ID phải đóng băng trước training.

Tỉ lệ chỉ được đổi bằng ADR trước khi xem test metrics.

## 9. Segmentation

- Raw recording giữ nguyên.
- Training window tạo động hoặc qua manifest tái lập được.
- Window overlap không được làm cùng recording xuyên split.
- Target frame tạo từ onset/offset bằng một quy tắc rounding duy nhất có test biên.
- Padding mask không được tính vào loss hoặc metric.

## 10. QA thay cho relabeling

Không nghe và gán lại toàn bộ dataset. QA giới hạn:

- 1–2% sample ngẫu nhiên theo class.
- Toàn bộ corrupt/invalid annotations.
- Candidate duplicate và duration outlier.
- Failure case sau baseline chỉ dùng phân tích, không sửa test label tùy ý.

Mọi exclusion gồm `file_id`, `stage`, `reason_code`, `detail`, `decided_by`, `decided_at`.

## 11. Data gates

| Gate | Điều kiện |
|---|---|
| D0 | Metadata/license/checksum đã lưu |
| D1 | Archive giải nén và inventory hoàn tất |
| D2 | Annotation contract pass |
| D3 | Exact/near duplicate audit hoàn tất |
| D4 | Split freeze và leakage check pass |
| D5 | Loader/frame alignment tests pass |

Không huấn luyện benchmark chính trước D4.

