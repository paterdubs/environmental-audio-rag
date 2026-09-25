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

### 8. Kết quả (26/09 đêm; query set đóng băng ở 4762f7f trước mọi lần chạy)

Index dựng lại trên tree sạch (`retrieval_index_20260925T202815Z`); dev chạy trước, test một
lần. Nguồn: `retrieval_benchmark_{validation,test}_20260925.md`. 96/100 (dev), 97/100 (test)
câu có relevant.

| Test | nDCG@10 EN [CI 95%] | nDCG@10 VI | R@10 EN | MRR EN | Filter exactness |
|---|---:|---:|---:|---:|---:|
| structured_only | **0.523** [0.460, 0.589] | 0.523 | 0.512 | 0.610 | 1.000 |
| hybrid | 0.481 [0.424, 0.539] | 0.472 | 0.486 | 0.588 | 1.000 |
| vector_only | 0.418 [0.361, 0.472] | 0.340 | 0.427 | 0.532 | 0.587 (VI 0.467) |

Hiệu số cặp nDCG@10 (theo câu hỏi): hybrid − vector_only +0.063 [+0.020, +0.109] (EN), +0.131
[+0.087, +0.181] (VI); hybrid − structured_only −0.042 [−0.085, −0.004] (EN), −0.052 [−0.096,
−0.007] (VI). Dev cùng chiều (hybrid − structured −0.019 / −0.005, CI chứa 0).

**Đọc đúng:** (1) lọc cứng là thành phần quyết định — hybrid và structured vượt vector_only,
và filter exactness 1.000 xác nhận điểm ngữ nghĩa không ghi đè bộ lọc; (2) xếp hạng vector
**trong** tập đã lọc không giúp, trên test còn kém thứ tự theo onset — document chỉ là caption
template nên vector ít thông tin phân biệt; (3) truy vấn tiếng Việt kém tiếng Anh ở vector_only
(0.340 vs 0.418) nhưng gần bằng ở hybrid (0.472 vs 0.481). Chưa làm: sinh câu trả lời (6.8),
index hệ thống SED tối ưu (độ nhạy), document dùng caption LLM (ablation).

**Câu trả lời (6.8, `retrieval_answers_{validation,test}_20260925.md`):** bộ sinh tất định
chỉ trích recording có event đã index thoả lọc; bộ kiểm độc lập đọc lại văn bản. Test,
structured_only và hybrid × EN/VI: unsupported-claim **0.000**, contract 97/97, evidence có thật
97/97, trích thoả lọc 97/97, 96/97 câu có trả lời (câu còn lại: evidence rỗng + filters_applied).
Recording được trích đúng theo ground truth 0.43–0.48 — giới hạn do SED + retrieval, không do
grounding.

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
