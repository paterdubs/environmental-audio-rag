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

ADR và `query_parse_paraphrase_v1.csv` được commit trước code parser và trước lần gọi LLM đầu tiên.
Nghiệm thu sau triển khai phải có test transport HTTP giả, lớp ngoài taxonomy, API parse/query,
guard không import torch, lỗi LLM rõ ràng, measurement parse và RQ3 parsed trên validation. Các số
và artifact sẽ được bổ sung sau, không điền trước trong ADR này.
