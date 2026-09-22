# ADR-0005 — Database và vector store

**Status:** Accepted
**Date:** 2026-09-22

## Context

Event store phải phục vụ bốn loại truy vấn, và loại thứ tư là đóng góp C4:

| # | Loại | Ví dụ |
|---|---|---|
| 1 | Lọc metadata | class, duration, confidence, split |
| 2 | Tìm kiếm ngữ nghĩa | "tiếng máy móc ồn kéo dài" |
| 3 | Kết hợp 1 và 2 | "sự kiện máy móc dài hơn 30 giây" |
| 4 | **Quan hệ thời gian** | **"kính vỡ trước còi báo động"** |

Loại 4 là phép **self-join trên timestamp trong cùng recording**:

```sql
SELECT DISTINCT a.recording_id
FROM events a
JOIN events b ON a.recording_id = b.recording_id
WHERE a.class_id = :class_a AND b.class_id = :class_b
  AND a.offset_s <= b.onset_s + :tolerance_s;
```

Đây là ràng buộc quyết định. Vector store thuần không biểu diễn được quan hệ
giữa hai bản ghi; và embedding không mã hóa đáng tin quan hệ "trước/sau".

Quy mô: 717 recording, khoảng 4,034 ground-truth event cộng lượng tương đương
prediction. Nhỏ — không phải bài toán scale.

## Decision

**PostgreSQL 16 + pgvector.**

### 1. Một hệ quản trị cho cả bốn loại truy vấn

Lọc metadata, temporal join và vector search nằm trong **một câu SQL**, một
transaction, một nguồn chân lý.

### 2. Thứ tự thực thi cố định, không đổi được

```text
1. Structured filter (hard)   →  GIN index trên class_ids, B-tree trên onset_s
2. Temporal predicate          →  self-join
3. Vector ranking              →  HNSW, chỉ trên tập đã lọc
```

Semantic score **không bao giờ** được ghi đè hard filter. Ràng buộc này kiểm được
bằng metric `filter exactness` phải bằng 1.000
([evaluation_protocol §9.2](../evaluation_protocol.md)).

### 3. Bốn vị từ thời gian

`before`, `after`, `overlaps`, `within` — quan hệ khoảng Allen rút gọn. Tolerance
`τ` mặc định 0 và phải khai tường minh trong query.

### 4. Cột `provenance` phân biệt ground truth với prediction

Cùng một bảng `events` chứa cả hai, nhưng bắt buộc có cột phân biệt. Không có nó
sẽ đánh giá model trên chính output của nó.

## Consequences

### Tích cực

- Temporal predicate là SQL chuẩn, không cần logic ở tầng ứng dụng.
- Hard filter chạy trên index, không phải lọc sau khi lấy vector — đảm bảo
  `filter exactness = 1.000` theo kiến trúc chứ không nhờ cẩn thận.
- Một hệ quản trị, một backup, một migration path. Phù hợp ngân sách vận hành
  của khóa luận.
- Ràng buộc khóa ngoại thật cho `caption_evidence` — biến "grounded" từ quy ước
  thành ràng buộc CSDL.
- pgvector hỗ trợ HNSW, đủ nhanh ở quy mô này.

### Đánh đổi

- pgvector chậm hơn vector DB chuyên dụng ở quy mô hàng triệu vector. **Không
  liên quan ở đây** — 717 document.
- Cần chạy một service PostgreSQL trong Docker Compose; nặng hơn SQLite.
- Phải quản lý migration (Alembic). Thêm một thành phần.
- `VECTOR(1024)` cố định chiều — đổi embedding model khác chiều cần migration.
  Giảm thiểu: khóa `(recording_id, embedding_version)` cho phép nhiều version
  song song nhưng **cùng chiều**. Đổi chiều thì phải migration thật.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Qdrant / Weaviate / Milvus** | Không làm được temporal self-join. Phải tải toàn bộ event về tầng ứng dụng rồi lọc — mất tính scale và làm `filter exactness` phụ thuộc vào code ứng dụng thay vì kiến trúc |
| **PostgreSQL + Qdrant riêng** | Hai nguồn chân lý, phải đồng bộ, và join giữa hai hệ phải làm ở tầng ứng dụng. Phức tạp không tương xứng với 717 document |
| **SQLite + sqlite-vec** | Nhẹ, đủ cho quy mô này, nhưng thiếu GIN index cho mảng, thiếu kiểu `int4range` cho `mention_span`, và không quen thuộc bằng cho người đọc khóa luận |
| **Elasticsearch** | Mạnh cho lexical + vector, nhưng temporal self-join vẫn khó và chi phí vận hành cao |
| **Chỉ file JSON + tìm kiếm trong bộ nhớ** | Đủ cho demo nhưng không chứng minh được kiến trúc C4, và không có ràng buộc toàn vẹn |

## Evidence cần kiểm lại

- [ ] pgvector phiên bản nào hỗ trợ HNSW với `vector_cosine_ops` trên PostgreSQL 16.
- [ ] Hiệu năng temporal self-join với khoảng 8,000 event — có cần index thêm không.
- [ ] `int4range` cho `mention_span` có phải kiểu phù hợp nhất không.
- [ ] Với 717 document, HNSW có nhanh hơn brute force không, hay chỉ thêm phức tạp.
