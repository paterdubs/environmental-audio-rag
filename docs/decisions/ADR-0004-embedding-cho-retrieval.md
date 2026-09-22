# ADR-0004 — Embedding model và chính sách song ngữ cho retrieval

**Status:** Accepted
**Date:** 2026-09-22

## Context

RQ3 so sánh `structured_only`, `vector_only` và `hybrid`. Nhánh vector cần một
embedding model. Ràng buộc:

1. **Truy vấn bằng tiếng Việt.** Người dùng đích hỏi tiếng Việt; caption benchmark
   viết tiếng Anh để so với văn liệu AAC. Embedding phải bắc cầu hai ngôn ngữ.
2. **Document ngắn và nhiều số.** Document là caption cộng event summary dạng
   `birds 0.0-17.6s (0.88); bells 34.8-50.7s (0.91)` — không phải văn xuôi dài.
3. **Thuật ngữ âm học dễ dịch sai.** `horn` dịch máy thành "sừng"; `train` thành
   "huấn luyện". Lỗi loại này phá retrieval một cách khó chẩn đoán.
4. **Chạy local trên 8 GB VRAM**, dùng chung GPU với training.

## Decision

### 1. BGE-M3, 1024 chiều

### 2. Embed trực tiếp cả tiếng Việt và tiếng Anh vào cùng một không gian

**Không dịch câu hỏi sang tiếng Anh trước khi embed.** Dịch thêm một nguồn lỗi
vào critical path, và lỗi dịch thuật ngữ âm học (điểm 3 ở trên) tạo ra hỏng hóc
im lặng: hệ thống vẫn trả kết quả, chỉ là kết quả sai.

### 3. Document gồm hai phần

```text
[caption]            ← ngôn ngữ tự nhiên, phần con người đọc
[event summary]      ← class, thời gian, confidence, polyphony
```

Caption tự nhiên thường bỏ qua con số, nên truy vấn dạng "sự kiện dài hơn 30
giây" không có gì để khớp nếu chỉ embed caption. Phần summary bù chỗ đó.

### 4. Tách `retrieval_documents` khỏi `captions`

Bảng riêng, khóa `(recording_id, embedding_version)`. Đổi embedding model không
phải sinh lại caption, và nhiều `embedding_version` tồn tại song song để so sánh.

### 5. Hard filter không bao giờ chạy qua embedding

`class_ids`, `total_events`, `max_polyphony`, duration được denormalize thành cột
có index. Chúng lọc **trước**, vector chỉ xếp hạng trong tập đã lọc.

## Consequences

### Tích cực

- Truy vấn tiếng Việt không mất chất lượng so với tiếng Anh, không cần dịch.
- 1024 chiều vừa với `VECTOR(1024)` + HNSW index của pgvector.
- Tách bảng cho phép ablation embedding model mà không đụng tới caption.
- BGE-M3 chạy được local, không phụ thuộc API ngoài, không lộ dữ liệu.

### Đánh đổi

- BGE-M3 khoảng 568M tham số, chiếm VRAM khi index. Giảm thiểu: chạy index theo
  batch, hoặc trên CPU vì đây là thao tác offline một lần.
- Embedding đa ngữ thường kém hơn embedding đơn ngữ chuyên biệt trên từng ngôn
  ngữ riêng lẻ. Chấp nhận, vì lợi ích bắc cầu VI–EN lớn hơn.
- Phần `[event summary]` là văn bản nhân tạo, không giống phân bố huấn luyện của
  embedding model. Rủi ro: model xử lý số kém. Đây chính là lý do `structured
  filter` phải là hard filter chứ không phải tín hiệu ngữ nghĩa.
- Chưa đo được BGE-M3 có phù hợp document ngắn nhiều số không — cần thực nghiệm.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Dịch câu hỏi VI→EN rồi dùng embedding tiếng Anh** | Thêm nguồn lỗi; lỗi dịch thuật ngữ âm học gây hỏng im lặng |
| **multilingual-E5** | Ứng viên hợp lệ, chất lượng tương đương. Chọn BGE-M3 vì hỗ trợ cả dense và sparse trong một model, hữu ích nếu sau này muốn thêm lexical matching. Giữ làm phương án dự phòng |
| **Embedding qua API (OpenAI/Cohere)** | Phụ thuộc nhà cung cấp, tốn phí, và gửi dữ liệu ra ngoài |
| **Chỉ embed tiếng Anh, giao diện dịch kết quả** | Truy vấn tiếng Việt vẫn phải dịch — cùng vấn đề |
| **Không dùng vector, chỉ structured** | Chính là nhánh `structured_only` của RQ3; không thể là thiết kế duy nhất vì mất khả năng truy vấn mô tả tự do |
| **Qdrant / Weaviate riêng** | Xem [ADR-0005](ADR-0005-database-va-vector-store.md) |

## Evidence cần kiểm lại

- [ ] BGE-M3 có xử lý tốt document ngắn chứa nhiều số không.
- [ ] Recall tiếng Việt so với tiếng Anh trên cùng query set — chênh bao nhiêu.
- [ ] Thời gian index 717 document và VRAM tiêu thụ.
- [ ] HNSW với 717 document có đáng không, hay brute force đã đủ nhanh ở cỡ này.
