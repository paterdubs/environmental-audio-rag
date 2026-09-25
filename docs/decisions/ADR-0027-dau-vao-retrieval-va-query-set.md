# ADR-0027 — W6: đầu vào retrieval, document và query set v2

**Status:** Proposed — agent tự quyết trong chế độ tự động (26/09 đêm), **chờ người dùng duyệt**;
mọi lựa chọn dưới đây đảo được mà không phải sinh lại dữ liệu khác
**Date:** 2026-09-26

## Context

W6 (RQ3) cần: corpus để index, nguồn event, nội dung document, mô hình embedding, nơi lưu,
và query set. Nền tảng có sẵn: migration `001_event_store.sql`, `document_builder`, bốn vị từ
thời gian (SQL + Python, cùng ngữ nghĩa), relevance từ ground truth (nợ #16/#17 đã sửa). Nợ
#18: query set hiện chỉ có câu temporal ghép cặp máy móc — 25/100 câu có relevant trên test.

## Decision

### 1. Hai corpus, không có tham số chỉnh trên test

Index **dev** (137 recording) và **test** (142) thành hai corpus riêng. Hybrid theo SYSTEM §7.2
(lọc cứng → xếp hạng vector trong tập đã lọc) **không có tham số tự do**; top-k cố định 10.
Nếu về sau cần chọn gì (vd ngưỡng) thì chọn trên dev, test chạy một lần.

### 2. Event: dự đoán run B `054531Z` + `postproc.json` đóng băng (E5)

Cùng đầu vào với RQ2 (W5), nên caption, event và retrieval kể cùng một câu chuyện. Hệ thống
SED tối ưu (ensemble C, ADR-0024) chạy sau như phân tích độ nhạy trên test.

### 3. Document = caption template EN + VI + tóm tắt event

`build_document` với caption template tiếng Anh và tiếng Việt (ADR-0025): tất định, grounded
theo cấu tạo, có cho mọi timeline, không phụ thuộc LLM lúc suy luận (W7). Tóm tắt event giữ
số liệu mà caption tự nhiên hay bỏ (SYSTEM §7.1).

### 4. Embedding BGE-M3 dense qua `sentence-transformers`

ADR-0004 đã chọn BGE-M3; thư viện chọn `sentence-transformers` (dense 1024 chiều, chuẩn hoá,
cosine) — đủ cho `VECTOR(1024)`; FlagEmbedding (sparse/ColBERT) không cần cho RQ3.
`embedding_version` ghi tên model + phiên bản document.

### 5. Lưu trữ: PostgreSQL 16 + pgvector (Docker, ADR-0005)

Migration SQL áp bằng script nhỏ; Alembic hoãn (PLAN 6.1 ghi Alembic — lệch có chủ đích, file
migration đã viết để Alembic chạy được sau).

### 6. Query set v2 — chọn câu hỏi theo ground truth **train**

Bốn nhóm theo SYSTEM §8.5, mỗi câu có văn bản EN và VI, relevance = luật trên annotation:
lớp có mặt · hai lớp cùng có mặt · vị từ thời gian giữa hai lớp · lớp có event dài hơn T giây.
Câu hỏi chọn theo tần suất trên **train** (không nhìn dev/test). Phân bố **21/27/30/22** thay vì
mục tiêu 30/25/25/20: nhóm một lớp chỉ có 21 lớp polyphonic, lặp lại cùng lớp không thêm thông
tin. Câu không có relevant trong một corpus bị loại khỏi trung bình và được đếm riêng.

### 7. Metric

Recall@{1,5,10}, MRR, nDCG@10 (relevance nhị phân), filter exactness (so với event đã index —
bắt vi phạm kiến trúc). Sinh câu trả lời (6.8) hoãn — cut-list #9.

## Consequences

### Tích cực

- RQ3 so được ba cấu hình mà không tinh chỉnh trên test.
- Query set không phụ thuộc dev/test, không phụ thuộc output hệ thống.

### Đánh đổi

- Document dùng caption template (đơn điệu) — embedding có thể dựa chủ yếu vào tên lớp; caption
  LLM là ablation có thể làm sau.
- Phân bố nhóm lệch mục tiêu PLAN/HANDOFF.

## Alternatives considered

| Phương án | Vì sao không chọn (lúc này) |
|---|---|
| Index hệ thống SED tối ưu làm chính | W5 dùng run B; để làm độ nhạy |
| Caption LLM (constrained/cover) trong document | Chỉ có cho run B dev/test; W7 sẽ cần GPU + LLM lúc suy luận |
| Chọn câu hỏi để mọi câu có relevant trên test | Nhìn nhãn test khi dựng benchmark |
| FlagEmbedding (dense+sparse) | Thêm phụ thuộc, không cần cho RQ3 |
