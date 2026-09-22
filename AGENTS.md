# Hướng dẫn làm việc

## Trước khi sửa

1. Đọc `CONTEXT.md` và `docs/STATUS.md`.
2. Đọc tài liệu nguồn chân lý liên quan trong `README.md` §6.
3. Phân biệt rõ kiến trúc dự kiến với tính năng đã chạy được.

## Dữ liệu

- Không commit audio, features, checkpoints hoặc vector database.
- Ghi version, DOI, checksum và license vào manifest trước khi xử lý.
- Chia tập theo recording/content group sau khi deduplicate; không chia theo segment.
- Tìm duplicate cả trong từng dataset và xuyên DataSEC–DataSED trước split.
- Giữ label gốc; canonical label chỉ là lớp ánh xạ có version.

## Code

- `ml/` chứa logic import được; `scripts/` chỉ điều phối CLI.
- `services/api` không tải model; inference nằm trong `services/inference`.
- Contract JSON không phụ thuộc framework và phải được test.
- Config quyết định class order; không hardcode class list rải rác.
- Mọi run phải lưu config, seed, git revision, data manifest và metric.

## Tài liệu

- Cập nhật `docs/STATUS.md` sau mỗi block có artifact mới.
- Quyết định làm đổi scope, split, taxonomy hoặc metric phải có ADR.
- Báo cáo sinh tự động đặt trong `docs/measurements/`; không sửa số bằng tay.
- Không ghi “đã hoàn thành” nếu chưa có command và artifact kiểm chứng.

