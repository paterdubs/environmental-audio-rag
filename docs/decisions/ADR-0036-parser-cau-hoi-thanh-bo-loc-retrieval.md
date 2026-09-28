# ADR-0036 — Parser câu hỏi thành bộ lọc retrieval

**Status:** Accepted — đặc tả được khóa trước khi viết parser và trước lần gọi parser đầu tiên.
**Date:** 2026-09-28

## Context

`POST /api/v1/retrieval/query` hiện bắt buộc client gửi `filters`. Vì vậy người dùng demo phải
biết trước mã lớp và predicate thời gian, trong khi câu hỏi tự nhiên đã có đủ thông tin để tạo bộ
lọc. Benchmark RQ3 trong ADR-0027 dùng trực tiếp filter gold của query set v2; các số đó giả định
parse hoàn hảo và là cận trên, không phải chất lượng đầu-cuối của giao diện hỏi đáp.

Qwen3.5-9B và llama.cpp đã được khóa cho caption trong ADR-0022/ADR-0023. L2 tái sử dụng đúng
model/runtime này qua HTTP, nhưng cần một contract riêng để không cho LLM tạo lớp ngoài taxonomy,
predicate tùy ý hoặc âm thầm đoán filter khi dịch vụ không chạy.

## Decision

### 1. Contract đầu ra là đúng `Filters` của API

Parser chỉ được trả một JSON object có ít nhất một trong ba field:

- `classes_all`: 1–5 mã lớp, dùng cho một hoặc nhiều lớp cùng xuất hiện;
- `temporal`: `{predicate, a, b, tolerance_s}`, với `tolerance_s` mặc định và gold đều là `0.0`;
- `duration`: `{class_id, min_s}` với `0 < min_s <= 600`.

Không thêm field giải thích vào object filter. Kết quả phải qua Pydantic `Filters`, rồi kiểm toàn bộ
mã lớp thuộc `taxonomy.polyphonic_class_ids`. Lớp lạ, JSON hỏng, field thừa hoặc object rỗng đều là
lỗi; parser không sửa gần đúng và không ánh xạ ngầm sau khi decode.

### 2. JSON Schema sinh từ nguồn chân lý

Mỗi request sinh JSON Schema từ:

- đúng 21 giá trị `taxonomy.polyphonic_class_ids` cho mọi vị trí mã lớp;
- đúng `PREDICATES.keys()` trong `ml/retrieval/temporal.py` cho `predicate`;
- giới hạn số và độ dài của Pydantic `Filters`.

Schema đặt `additionalProperties: false` ở mọi object và được gửi bằng constrained JSON decoding
của llama.cpp (`response_format.type=json_schema`). Danh sách enum không được chép thành hằng mới
trong parser. Đây là grammar phụ thuộc taxonomy; thay taxonomy/predicate sẽ đổi schema sinh ra.

### 3. Prompt và tham số sinh được đóng băng

System prompt nói rõ nhiệm vụ chỉ là chuyển câu hỏi môi trường EN/VI thành JSON filter, không trả
lời câu hỏi và không tạo lớp. Few-shot cố định gồm đủ bốn dạng: một lớp, nhiều lớp, quan hệ thời
gian và thời lượng; ví dụ dùng mã lớp hợp lệ nhưng không lấy từ mẫu đang chấm.

Giải mã greedy với `temperature=0`, `seed=20260922`, `enable_thinking=false`; model và timeout đọc
từ `ml/configs/caption_llm.yaml`. Endpoint mặc định là endpoint trong YAML, được ghi đè bởi
`EARAG_LLM_ENDPOINT`; profile Docker dùng `http://host.docker.internal:8081`.

### 4. API và provenance

Thêm `POST /api/v1/retrieval/parse` nhận `{question, language}` và trả `{filters, raw}` trong
envelope chung. `/retrieval/query` cho phép thiếu `filters`; khi đó gọi cùng parser rồi mới embed và
search. Kết quả query luôn trả `filters_applied` và `filters_source`, chỉ nhận hai giá trị `user` hoặc
`parsed`, để UI không che giấu nguồn bộ lọc.

Module `ml/retrieval/query_parser.py` chỉ dùng HTTP/JSON/Pydantic/YAML, không import `torch` và
không tải checkpoint trong process API.

### 5. Tập đánh giá được khóa trước lần parse đầu

Hai tập được báo riêng:

1. 100 mục query set v2 × hai ngôn ngữ = 200 câu. Câu hỏi được sinh từ template và filter gold đã
   có, nên kết quả này là **cận trên trên câu có cấu trúc**, không đại diện lời nói tự do.
2. `query_parse_paraphrase_v1.csv`: 40 câu viết tay, 20 EN + 20 VI, phủ bốn nhóm, có văn nói và lỗi
   chính tả nhẹ. File được commit cùng ADR này trước khi parser chạy lần đầu và không sửa sau khi
   thấy kết quả.

Không đọc/chấm split test: parse filter không cần audio hay relevance. RQ3 đầu-cuối chỉ chạy corpus
`validation` và dùng chính filter parser sinh ra thay filter gold.

### 6. Metric và luật so sánh

Trước khi chấm, JSON được chuẩn hóa bằng Pydantic: bỏ field `None`, sắp xếp `classes_all` (vì đây
là phép hội không có thứ tự), giữ nguyên vai trò `a`/`b` và giá trị số. Báo:

- exact match toàn bộ filter sau chuẩn hóa;
- precision/recall micro theo mã lớp xuất hiện trong tất cả vị trí filter;
- độ chính xác predicate trên các mẫu gold temporal; thiếu/sai temporal tính sai;
- tỷ lệ parse thành công và số lỗi theo loại.

RQ3 parsed giữ nguyên query text, relevance, embedding, top-k và corpus validation của benchmark
gold. Báo riêng từng mode/ngôn ngữ và chênh `nDCG@10(parsed − gold)` trên cùng câu có relevant;
không thay filter lỗi bằng gold. Mẫu parse lỗi nhận danh sách retrieval rỗng và metric bằng 0 để
không làm đẹp số bằng cách loại mẫu.

## Consequences

### Tích cực

- API nhận được câu hỏi tự nhiên mà vẫn giữ bộ lọc có schema, provenance và kiểm taxonomy.
- Có thể tách lỗi hiểu câu hỏi khỏi lỗi SED/retrieval và định lượng khoảng cách với cận trên gold.
- Grammar, prompt và seed tạo một benchmark tái lập được, không phát sinh lớp/predicate mới.

### Đánh đổi

- Query template dễ hơn paraphrase; hai tập phải luôn báo riêng.
- Greedy vẫn có thể chọn filter hợp schema nhưng sai nghĩa; constrained decoding chỉ bảo đảm hình
  thức, không bảo đảm semantic exact match.
- Demo phụ thuộc thêm llama.cpp khi người dùng không nhập filter thủ công.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Regex/từ điển VI/EN | Khó phủ paraphrase, lỗi chính tả và quan hệ diễn đạt đa dạng; không đúng L2 đã duyệt |
| Cho model trả JSON tự do rồi sửa gần đúng | Che giấu lỗi parse và có thể đưa lớp ngoài taxonomy vào truy vấn |
| Khi LLM tắt tự dùng filter rỗng hoặc vector-only | Thay đổi nghĩa câu hỏi âm thầm và phá contract evidence-bound |
| Dùng filter gold khi parser lỗi trong benchmark | Làm tăng giả tạo RQ3 parsed và không đo pipeline đầu-cuối |

## Verification

ADR và `query_parse_paraphrase_v1.csv` được commit ở `aafd8ec` trước code parser và trước lần gọi
LLM đầu tiên. Lượt đo đầu ở `dfcafa1` **không hợp lệ để báo như constrained**: llama.cpp b11158
chấp nhận wrapper `response_format.type=json_schema` nhưng âm thầm bỏ qua schema; `$ref` của
Pydantic cũng không giữ enum khi thử wrapper đúng. Pydantic hậu kiểm đã chặn output sai nhưng
không thay thế constrained decoding.

Phiên bản v1.1 chuyển sang extension top-level `json_schema` của llama.cpp và inline ba biến thể
filter; probe đối nghịch đã xác nhận enum ép `vehicle_pass_by` thay vì chuỗi ngoài taxonomy.
Lượt RQ3 dẫn xuất từ output không constrained đã bị xóa; không được dùng số của lượt đó.

Measurement v1.1 chạy lại trên tree sạch revision `38bcf53`; cả 240/240 output qua schema:

| Tập | Exact toàn filter | P/R lớp | Đúng predicate |
|---|---:|---:|---:|
| Template (cận trên) | 171/200 = 0.855 | 1.000 / 1.000 | 0.767 (60 câu temporal) |
| Paraphrase viết tay | 37/40 = 0.925 | 0.984 / 1.000 | 1.000 (10 câu temporal) |

Lỗi template tập trung ở đảo `a`/`b` của `after`, đổi `within` thành `overlaps`, và bỏ điều kiện
duration; grammar bảo đảm hình thức nhưng không bảo đảm đúng ngữ nghĩa. Nguồn:
[`query_parser_20260928.md`](../measurements/query_parser_20260928.md).

RQ3 với filter parse chạy **chỉ trên validation** (96/100 câu có relevant). Hybrid nDCG@10 là
0.491 EN và 0.490 VI; chênh so filter gold trên cùng câu lần lượt +0.012 và −0.002.
Structured-only là 0.507/0.502, chênh +0.009/+0.005. Filter sai có thể tình cờ làm thứ hạng tốt
hơn khi vẫn chấm bằng relevance gold; chênh dương **không** phải bằng chứng parser cải thiện
retrieval. Nguồn:
[`retrieval_benchmark_validation_parsed_20260928.md`](../measurements/retrieval_benchmark_validation_parsed_20260928.md).

Test transport HTTP giả, lớp lạ, JSON lỗi, API parse/query, fallback 503 và guard torch đều xanh.
Compose build healthy; `/retrieval/parse` và `/retrieval/query` thật qua cổng 8088 trả filter có
schema và `filters_source=parsed`. UI vẫn giữ bộ lọc thủ công; khi llama.cpp tắt API trả
`query_parser_unavailable`, không đoán filter. Không chạy test corpus.
