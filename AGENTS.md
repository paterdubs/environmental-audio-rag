# Hướng dẫn làm việc

> **Đọc [CLAUDE.md](CLAUDE.md) trước.** Nó chứa trạng thái hiện tại, bản đồ tài
> liệu, quyết định đã khóa, lệnh hay dùng và nhật ký tiến độ.
>
> File này chỉ là guardrail ngắn — bản đầy đủ ở [CLAUDE.md §5](CLAUDE.md).

## Trước khi sửa

1. Đọc [CLAUDE.md](CLAUDE.md) §3 (đang ở đâu) và [docs/STATUS.md](docs/STATUS.md).
2. Đọc tài liệu nguồn chân lý liên quan — bảng ở [README §6](README.md).
3. Phân biệt rõ **kiến trúc dự kiến** ([SYSTEM.md](docs/SYSTEM.md)) với **tính
   năng đã chạy được** ([STATUS.md](docs/STATUS.md)).
4. Task phải bám vào một dòng trong [docs/PLAN.md](docs/PLAN.md). Không khớp dòng
   nào thì hỏi trước.

## Môi trường

Dùng `.venv/Scripts/python.exe`. `python` trên PATH thiếu dependency.

```bash
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .
```

## Dữ liệu

- Không commit audio, feature, checkpoint hoặc vector database.
- Ghi version, DOI, checksum và license vào manifest trước khi xử lý. **License
  lấy từ Zenodo record, không phải từ archive** — archive không chứa LICENSE.
- Chia tập theo recording/content group sau khi deduplicate; không chia theo segment.
- Tìm duplicate cả trong từng dataset **và xuyên DataSEC–DataSED** trước split.
- Giữ label gốc; canonical label chỉ là lớp ánh xạ có version.
- Không sửa raw annotation. Nghi ngờ → ghi phân tích lỗi, không sửa dữ liệu.

## Code

- `ml/` chứa logic import được; `scripts/` chỉ điều phối CLI.
- `services/api` **không** tải model; inference nằm trong `services/inference`.
- Contract JSON không phụ thuộc framework và phải được test.
- Config quyết định class order; không hardcode class list rải rác.
- SED head dùng `taxonomy.polyphonic_class_ids` (**21**), không phải
  `class_ids` (22).
- Mọi run phải lưu config, seed, git revision, data manifest và metric.

## Đánh giá

- θ chọn trên **dev**; duration prior suy từ **train**; test chạy **một lần**.
- Không dùng test để chọn threshold, checkpoint hay encoder.
- Frame-F1 không so được với event-based F1.
- Class có `n_test < 10` báo bằng số tuyệt đối, không báo tỷ lệ.

Chi tiết: [docs/evaluation_protocol.md](docs/evaluation_protocol.md).

## Tài liệu

- Cập nhật [docs/STATUS.md](docs/STATUS.md) sau mỗi block có artifact mới.
- Cập nhật [CLAUDE.md](CLAUDE.md) §3 và §10 ở cuối mỗi block.
- Quyết định làm đổi scope, split, taxonomy hoặc metric phải có ADR.
- Báo cáo sinh tự động đặt trong `docs/measurements/`; **không sửa số bằng tay**.
- **Không bịa số, không bịa trích dẫn.** Chưa chắc → `⚠️ CẦN XÁC MINH`.
- Không ghi "đã hoàn thành" nếu chưa có command và artifact kiểm chứng.
