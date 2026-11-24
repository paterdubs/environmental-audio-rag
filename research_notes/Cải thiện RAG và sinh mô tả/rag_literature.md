# Cải thiện RAG trên timeline sự kiện âm thanh có dấu thời gian (2022–2026)

Phạm vi: các kỹ thuật cải thiện truy vấn và sinh câu trả lời trên event store (class, onset, offset, score, recording) trong PostgreSQL + pgvector, truy vấn bằng câu hỏi EN/VI có temporal predicate. Ràng buộc: còn 4 ngày, không train lại, LLM local Qwen ~9B (llama.cpp), embedding BGE-M3. Tra ngày 24/11/2026. Mức xác minh: "đã đọc" = đã mở trang abstract/HTML; "qua tóm tắt" = chỉ đọc snippet của công cụ tìm kiếm hoặc trang thứ cấp.

## Hybrid fusion: khi nào thêm vector similarity trên filter chính xác lại làm xếp hạng tệ hơn

### Takeaway
Văn liệu không có quy luật "hybrid luôn tốt hơn". Convex combination (CC) có một tham số α, tinh chỉnh trên một tập validation nhỏ, thắng RRF cả trong miền lẫn ngoài miền, còn RRF nhạy với tham số của nó. Hệ quả cho dự án: hybrid thua vector_only ở một corpus nhưng thắng ở corpus khác là hành vi đã được dự báo khi trọng số fusion cố định. Cách sửa rẻ nhất là chọn α (hoặc chọn chế độ) trên validation, không dùng một trọng số cố định.

### Cited Findings
- Bruch, Gai, Ingber, "An Analysis of Fusion Functions for Hybrid Retrieval" (ACM TOIS 2023, arXiv 2210.11934): CC vượt RRF cả trong miền và ngoài miền. RRF nhạy với tham số, trái với các nghiên cứu trước. Chọn cách chuẩn hóa điểm gần như không ảnh hưởng tới việc học CC. CC hiệu quả về mẫu: chỉ cần một tập nhỏ ví dụ để chỉnh α cho miền đích (abstract không nêu số query cụ thể). Đã đọc trang abstract. — [arXiv 2210.11934](https://arxiv.org/abs/2210.11934)
- Bruch et al. bác lại Chen et al. (2022), vốn cho rằng CC nhạy với tham số và chuẩn hóa nên RRF, vì không có tham số, phù hợp hơn. Bruch et al. kết luận RRF đã tinh chỉnh tổng quát hóa kém ra ngoài miền. Qua tóm tắt. — [Pinecone research mirror](https://www.pinecone.io/research/an-analysis-of-fusion-functions-for-hybrid-retrieval/md/); [arXiv](https://arxiv.org/abs/2210.11934)
- Elastic quảng bá RRF vì dễ dùng: không giám sát, không cần hiệu chuẩn điểm. Nguồn thứ cấp của nhà cung cấp, không phải bằng chứng hiệu năng. — [Elastic Search Labs](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)
- BGE-M3 (Chen et al., arXiv 2402.03216, v5 12/2025) có ba chế độ: dense ([CLS]), sparse (trọng số từ vựng) và multi-vector (ColBERT-style), cùng một lần forward. MIRACL dev nDCG@10 trung bình: Dense 69.2, Sparse 53.9, Multi-vec 70.5, Dense+Sparse 70.4, All 71.5. MLDR (tài liệu dài) test nDCG@10: Dense 52.5, Sparse 62.2, Multi-vec 57.6, Dense+Sparse 64.8, All 65.0. Đã đọc bản HTML. — [arXiv 2402.03216v4](https://arxiv.org/html/2402.03216v4)
- Trọng số kết hợp BGE-M3 (w_dense, w_sparse, w_multi) khác hẳn giữa các tác vụ: MIRACL Dense+Sparse 1/0.3/0, All 1/0.3/1 (multi-vector chỉ rerank top-200 dense); MLDR Dense+Sparse 0.2/0.8/0, All 0.15/0.5/0.35. Bài báo nói rõ trọng số "phụ thuộc kịch bản downstream". — [arXiv 2402.03216v4](https://arxiv.org/html/2402.03216v4)
- pgvector: HNSW mặc định áp filter sau một lượt index, nên filter chọn lọc trả về ít hàng hơn yêu cầu. Ví dụ: với `hnsw.ef_search`=40 và filter khớp 10% hàng, trung bình chỉ còn khoảng 4 hàng. Bản 0.8.0 thêm `hnsw.iterative_scan` (`off` mặc định / `strict_order` / `relaxed_order`), dừng theo `hnsw.max_scan_tuples` (mặc định 20,000) và `hnsw.scan_mem_multiplier`. Qua tóm tắt + tài liệu phân phối lại. — [pgEdge pgvector docs v0.8.5](https://docs.pgedge.com/pgvector/v0-8-5/iterative-index-scans/); [PostgreSQL news 0.8.0](https://www.postgresql.org/about/news/pgvector-0.8.0-released-2952/); [AWS blog](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql)
- Crunchy Data mô tả mẫu hybrid trong Postgres (full-text + pgvector, fusion bằng SQL). Thứ cấp. — [Crunchy Data](https://crunchydata.com/blog/hybrid-vector-search)

### Inferences
- **Vì sao hybrid có thể thua vector_only, rồi lại thắng ở corpus khác.** Khi structured filter đã định nghĩa gần như chính xác tập liên quan (relevance lấy từ cùng ngữ nghĩa predicate), cosine giữa câu hỏi và document template trong tập đã lọc chủ yếu đo độ trùng văn phong template, không đo relevance. Thứ tự trong tập đó gần như nhiễu. Ngược lại, khi filter do parser sinh ra bị sai hoặc quá rộng, vector giúp kéo lên đầu những document khớp ngữ nghĩa. Trọng số fusion cố định không thể tối ưu cho cả hai chế độ, đúng như Bruch et al. dự báo (tham số phụ thuộc miền).
- **Rẻ nhất, khoảng 0.5 ngày:** quét α ∈ {0, 0.1, …, 1} của CC (min-max hoặc z-score theo query) trên validation, chọn một α rồi khóa trước test. Báo cả đường nDCG@10 theo α như một hình. Vì CC hiệu quả về mẫu (Bruch), 96 câu validation là đủ để chọn α một cách có nghĩa.
- **Dùng tín hiệu có cấu trúc làm khóa xếp hạng thứ hai trong tập đã lọc:** detector score, thời lượng chồng lấn với cửa sổ truy vấn, số event khớp. Với tài liệu template, các tín hiệu này có lẽ mang thông tin hơn cosine. Không cần model mới; chỉ đổi `ORDER BY`.
- **BGE-M3 sparse/lexical mode** có thể giúp document template ngắn vì khớp tên lớp chính xác, nhưng trên MIRACL sparse một mình kém dense (53.9 vs 69.2). Lợi ích lớn của sparse chỉ thấy ở tài liệu dài (MLDR). Kỳ vọng thấp cho document event ngắn; chỉ thử nếu FlagEmbedding đã cài sẵn. Chi phí khoảng 1 ngày (cột mới, re-index).
- **Kiểm pgvector:** nếu lượt vector-in-filter dùng HNSW với filter chọn lọc, recall có thể sụt thầm lặng. Với corpus nhỏ (vài trăm tới vài nghìn event), chạy exact scan (không index hoặc `SET enable_indexscan=off`) loại bỏ hẳn rủi ro này. Nên xác minh `EXPLAIN` trước khi diễn giải bất kỳ chênh lệch hybrid nào.

### Gaps
- Không tìm được bài báo nào đo riêng "filter-then-rank vs rank-then-filter" trên event store có cấu trúc với relevance định nghĩa bằng predicate. Phần lý giải ở trên là suy luận, chưa có trích dẫn.
- Chưa đọc trực tiếp Chen et al. 2022 (bài ủng hộ RRF), chỉ biết qua Bruch et al.

## Reranker (bge-reranker-v2-m3, cross-encoder, LLM rerank) cho document template ngắn

### Takeaway
Không có bằng chứng sạch về mức tăng của bge-reranker-v2-m3 trên tài liệu ngắn dạng template. Bằng chứng gián tiếp cho thấy cross-encoder giúp khi thứ tự first-stage yếu và có thể làm hại khi thứ tự đã gần hoàn hảo. Với relevance định nghĩa bằng predicate thời gian, reranker văn bản không "hiểu" quan hệ onset/offset. Ưu tiên thấp.

### Cited Findings
- Model card chính thức: bge-reranker-v2-m3 là reranker đa ngữ nhẹ dựa trên bge-m3. Chưa đọc trực tiếp bảng số. — [Hugging Face BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- GeoGPT-RAG technical report: bge-reranker-v2-m3 đạt nDCG@10 trung bình khoảng 0.468 trên BEIR, so với 0.478 của GeoReranker. Không nêu baseline first-stage nên không suy ra được mức tăng. Qua tóm tắt. — [arXiv 2509.09686](https://arxiv.org/pdf/2509.09686)
- Querit-Reranker (arXiv 2606.19037): model của họ cải thiện first-stage +5.17 điểm (trung bình 59.28) và vượt bge-reranker-v2-m3 cùng Qwen3-Reranker-0.6B. Qua tóm tắt, không thấy số trung bình của bge-reranker-v2-m3. — [arXiv 2606.19037](https://arxiv.org/pdf/2606.19037)
- Báo cáo triển khai của nhà cung cấp (Mixpeek): reranker làm giảm nDCG từ 0.986 xuống 0.781 với các query mà thứ tự dense đã gần hoàn hảo, và chậm trên CPU khi nhiều ứng viên. Một đánh giá nội bộ, không phải benchmark. — [Mixpeek](https://mixpeek.com/models/bge-reranker-v2-m3)
- Bản thân BGE-M3 dùng chế độ multi-vector để rerank top-200 dense trên MIRACL (69.2 → 71.5 khi dùng "All"), tức khoảng +2.3 nDCG@10 mà không cần model riêng. — [arXiv 2402.03216v4](https://arxiv.org/html/2402.03216v4)

### Inferences
- Với relevance do temporal predicate quyết định, cross-encoder chỉ thấy văn bản. Nó có thể học thứ tự từ chữ "before/after" trong template nhưng không tính được onset/offset. Có lẽ chỉ giúp ở các query vector_only, nơi first-stage yếu.
- Nếu muốn thử: chi phí khoảng 0.5–1 ngày (tải model khoảng 2.3 GB, rerank top-50 trên validation, so nDCG@10 có ghép cặp). Cần ghi luật chọn trước khi chạy. Rủi ro: bổ sung một thành phần mới ở tuần cuối mà không có tác dụng lên đúng nhóm câu hỏi có predicate.
- LLM rerank bằng Qwen ~9B local quá chậm cho benchmark 96–100 câu × top-k nếu không cache; không khuyến nghị.

### Gaps
- Không tìm được số liệu chính thức (bài báo/model card) về mức tăng của bge-reranker-v2-m3 so với first-stage. Chưa tra RankGPT/LLM listwise rerank (không đủ ngân sách lượt tra).

## Biểu diễn tài liệu cho dữ liệu sự kiện

### Takeaway
Bằng chứng gần nhất là LongAudio-RAG (LA-RAG, 2026). Họ lưu detection vào SQL và chỉ đưa các event liên quan cho LLM; cách này thắng "mỗi event thành một bản ghi văn bản + vector top-k" rất xa. Điều đó ủng hộ việc để SQL làm phần lọc, còn văn bản chỉ để LLM đọc. Không tìm được nghiên cứu đối chứng về câu quan hệ thời gian hay tóm tắt theo recording.

### Cited Findings
- LA-RAG (arXiv 2602.14612, v3 09/03/2026, Qualcomm): event của audio model lưu trong SQLite. Query thường dùng toàn bộ tập event; query cụ thể áp thêm bộ lọc embedding top-k (bài không nêu k). Baseline RAG biến mỗi event thành bản ghi văn bản (tag, timestamp, duration, loudness), truy vấn bằng all-MiniLM-L6-v2 với k=5. Đã đọc HTML. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- LA-RAG Bảng 1 (Simple-QA, n=800), độ chính xác tổng: Home IoT LA-RAG 76.88% vs RAG (AGM) 48.95% vs Text2SQL 41.77%; Industrial IoT 68.92% vs 49.88% vs 40.90%. Độ trễ 0.56 s vs 3.26 s vs 1.34 s. Theo loại câu hỏi (Home IoT): detection 90.67/67.93/47.13, counting 76.93/44.13/48.00, summary 56.10/27.70/24.40. Số tự báo cáo trên benchmark tổng hợp của chính tác giả. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- LA-RAG: bài mô tả rubric GPT-4o 1–5 nhưng không giải thích cách đổi thang đó thành phần trăm ở Bảng 1. Tương quan Pearson giữa GPT-4o và người là 0.57. Đây là điểm yếu phương pháp khi trích số. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- LA-RAG chỉ hỗ trợ ràng buộc before/after đối với cửa sổ thời gian, không mô tả lập luận về quan hệ giữa hai event. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- Trên MLDR, trộn dense+sparse giúp nhiều với tài liệu dài, sparse một mình 62.2 vs dense 52.5. Đây là gợi ý gián tiếp rằng tài liệu gộp theo recording (dài hơn) sẽ được lợi từ tín hiệu lexical. — [arXiv 2402.03216v4](https://arxiv.org/html/2402.03216v4)

### Inferences
- Thiết kế hiện tại của dự án (SQL predicate + vector trong cùng câu SQL) đã đúng hướng LA-RAG. Có thể trình bày LA-RAG như bằng chứng bên ngoài rằng "structured trước, vector sau". Lưu ý: số LA-RAG không so được trực tiếp vì khác benchmark và khác thước đo.
- Đánh chỉ mục đa mức (event / cửa sổ / recording) là một thay đổi thiết kế corpus. Nó sẽ đổi định nghĩa relevance và đòi đánh giá lại; với 4 ngày còn lại thì không nên làm. Ghi thành hướng tương lai.
- Thêm câu quan hệ thời gian ("A occurs 3 s before B") vào document chỉ giúp nhánh vector; nhánh structured đã tính chính xác predicate. Kỳ vọng thấp và đổi hash document; không khuyến nghị.

### Gaps
- Không tìm được nghiên cứu đối chứng caption template vs serialized JSON cho dense retrieval trên dữ liệu sự kiện.

## Phân tích câu hỏi thành filter (NL-to-filter / text-to-SQL)

### Takeaway
Ba đòn bẩy có bằng chứng và không cần train: (1) chọn few-shot theo độ tương tự (DAIL-SQL), (2) self-consistency/biểu quyết (mức tăng nhỏ, +0.4–0.5 điểm EX), (3) bộ giải thời gian lai rule + LLM (LA-RAG: 60–62% → 77.8%). Constrained JSON decoding hại tác vụ suy luận nhưng thường không hại, thậm chí giúp, tác vụ kiểu phân loại; parser filter của dự án gần với phân loại hơn.

### Cited Findings
- DAIL-SQL (Gao et al., VLDB 2024, arXiv 2308.15363): GPT-4 Spider test EX 86.2% → 86.6% với self-consistency; dev EX 83.1 → 83.6 nhưng dev exact match giảm 70.0 → 68.7. Theo README repo, chưa kiểm bảng trong bài. — [GitHub DAIL-SQL](https://github.com/beachwang/dail-sql); [arXiv 2308.15363](https://arxiv.org/pdf/2308.15363v4.pdf)
- DAIL-SQL chọn ví dụ bằng cách kết hợp độ tương tự câu hỏi (đã che tên schema) với độ tương tự khung SQL. Theo README: 3-shot GPT-4 với DAIL selection khoảng 81.7% EX vs khoảng 79.4% với chọn ngẫu nhiên. Bố cục cột README mơ hồ, cần kiểm lại trong bài. — [GitHub DAIL-SQL](https://github.com/beachwang/dail-sql)
- LA-RAG Bảng 3 (45 cặp QA), độ chính xác giải thời gian: regex 60.00%, chỉ LLM 62.22%, kết hợp 77.78% (dễ 93.3/86.7/100; trung bình 55/65/85; khó 20/20/30). Mẫu nhỏ. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- LA-RAG Bảng 2: ở cỡ khoảng 8B, độ chính xác tổng khác nhau rất lớn giữa các LLM trên cùng pipeline: Qwen3-8B 57.88%, Qwen2.5-7B 67.88%, Llama-3.1-8B 43.85%, Phi-3.5-MoE 71.10%. Chọn LLM quan trọng ngang chọn pipeline. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)
- Tam et al., "Let Me Speak Freely?" (EMNLP 2024 Industry, arXiv 2408.02442): format càng chặt thì suy luận (vd GSM8K) càng giảm; JSON mode thường kém nhất. Riêng tác vụ phân loại, JSON mode "cạnh tranh, có khi vượt": DDXPlus Gemini 1.5 Flash 41.6 → 60.3, Sports GPT-3.5 67.2 → 80.0. Nhưng Task 280 Llama-3-8B 65.3 → 39.5. Lỗi parse không phải nguyên nhân chính. NL-to-Format (trả lời tự do rồi chuyển sang format) gần bằng ngôn ngữ tự nhiên trên tác vụ suy luận. Đã đọc HTML. — [arXiv 2408.02442v3](https://arxiv.org/html/2408.02442v3)
- "Thinking Before Constraining" (01/2026): cho LLM suy luận tự do tới token kích hoạt rồi mới chuyển sang sinh có cấu trúc. Chỉ đọc qua tóm tắt. — [arXiv 2601.07525](https://www.arxiv.org/abs/2601.07525)
- MRAG (arXiv 2412.15540, không cần train): tách câu hỏi thành nội dung chính và ràng buộc thời gian, giới thiệu benchmark TempRAGEval. Abstract chỉ nói "vượt đáng kể" baseline, không có số. — [arXiv 2412.15540](https://arxiv.org/abs/2412.15540)

### Inferences
- **Rẻ, khoảng 0.5 ngày:** chọn few-shot động theo độ tương tự BGE-M3 giữa câu hỏi đầu vào và một pool ví dụ lấy từ **train/template**, không lấy từ paraphrase validation. Đo bằng exact match filter + predicate accuracy trên tập paraphrase đã khóa.
- **Rẻ, khoảng 0.5 ngày:** self-consistency k=3–5 (temperature > 0, seed cố định) rồi biểu quyết theo trường của JSON. Bằng chứng DAIL-SQL cho thấy mức tăng nhỏ, có thể không phân biệt được trên 40 paraphrase. Chi phí gấp k lần độ trễ.
- **Rẻ, khoảng 0.5–1 ngày:** tiền xử lý số học/khoảng thời gian bằng regex ("within N seconds", "trong vòng N giây", "từ phút X tới Y") trước LLM, giống thiết kế lai của LA-RAG.
- Grammar JSON hiện dùng có lẽ không phải nguồn lỗi chính, vì tác vụ gần phân loại. Nếu thấy lỗi ở câu hỏi cần suy luận (ví dụ đổi "phút" thành giây), có thể thử NL-to-Format (hai bước).
- Fallback: khi parser trả về filter rỗng hoặc lỗi, chuyển sang vector_only thay vì chặn. Cần đo riêng nhóm câu hỏi rơi vào fallback.

### Gaps
- Chưa đọc trực tiếp bảng DAIL-SQL. Không tìm được nghiên cứu text-to-SQL tiếng Việt có predicate thời gian.

## Văn liệu temporal RAG và time-aware retrieval

### Takeaway
Văn liệu temporal RAG 2024–2026 chủ yếu nhắm câu hỏi có ràng buộc thời gian lịch sử (năm, giai đoạn) trên văn bản hoặc temporal KG. Cách làm chung: tách ràng buộc thời gian ra khỏi nội dung, lọc hoặc chấm điểm theo thời gian, rồi rerank. Chưa thấy công trình nào làm predicate giữa hai sự kiện (A before/overlaps B) trên timeline âm thanh, khớp với ghi nhận trước đây của dự án về C4.

### Cited Findings
- TimeR⁴ (EMNLP 2024): pipeline Retrieve-Rewrite-Retrieve-Rerank trên temporal KG. Viết lại câu hỏi với ràng buộc thời gian tường minh, truy vấn fact khớp cả nghĩa lẫn thời gian, rerank theo ràng buộc; retriever được fine-tune bằng contrastive time-aware. Tăng tương đối 47.8% và 22.5% trên "hai dataset" (abstract không ghi tên). Cần train retriever, nên không áp dụng nguyên được. — [ACL Anthology 2024.emnlp-main.394](https://aclanthology.org/2024.emnlp-main.394)
- MRAG (2024): module tách câu hỏi thành nội dung chính + ràng buộc thời gian, không cần train. — [arXiv 2412.15540](https://arxiv.org/abs/2412.15540)
- TA-RAG (arXiv 2507.22917): RAG cho câu hỏi trải trên khoảng thời gian dài (diachronic). Qua tóm tắt. — [arXiv 2507.22917](https://arxiv.org/abs/2507.22917)
- TG-RAG (arXiv 2510.13590): Temporal GraphRAG mô hình corpus thành đồ thị thời gian hai mức, kèm dataset ECT-QA. Qua tóm tắt. — [arXiv 2510.13590](https://arxiv.org/pdf/2510.13590v1)
- TempRetriever (arXiv 2502.21024): dense retriever kết hợp thời gian cho câu hỏi nhạy thời gian. Qua tóm tắt. — [arXiv 2502.21024](https://arxiv.org/pdf/2502.21024)
- Benchmark lập luận thời gian cho LLM: TRAVELER (2505.01325, 3,300 câu về sự kiện trong nhà; câu tham chiếu mơ hồ có độ chính xác thấp nhất), TIME (2505.12891, 38,522 cặp QA, tập con TIME-LITE 938), ComplexTempQA (2406.04866). Qua tóm tắt; chưa xác nhận họ gán nhãn quan hệ kiểu Allen. — [TRAVELER](https://arxiv.org/pdf/2505.01325); [TIME](https://arxiv.org/html/2505.12891v4); [ComplexTempQA](https://arxiv.org/pdf/2406.04866v3)
- LA-RAG (2026) là analog gần nhất trong miền âm thanh. Chỉ hỗ trợ before/after với cửa sổ thời gian, không hỗ trợ quan hệ giữa hai event. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)

### Inferences
- Ý tưởng chung "tách ràng buộc thời gian → lọc chính xác → xếp hạng" chính là kiến trúc của dự án. Có thể trích MRAG/TimeR⁴ làm bối cảnh cho Chương 2. Cái khác của dự án là predicate giữa hai sự kiện được tính bằng SQL.
- Có thể dựng một tập con câu hỏi mơ hồ (kiểu TRAVELER, ví dụ "lúc gần cuối") làm phân tích lỗi; không cần làm ngay.

### Gaps
- Không tìm được "TimeRAG" như tên một bài báo; TempRALM chỉ xuất hiện dưới dạng trích dẫn. Không tra video moment retrieval (hết ngân sách lượt tra).

## Độ trung thực của câu trả lời: trích dẫn, abstention, bất định

### Takeaway
ALCE (citation recall/precision bằng NLI) và RAGAS faithfulness là hai thước chuẩn được trích nhiều. Với hệ thống mà mọi khẳng định trích dẫn một event có cấu trúc, có thể đo theo kiểu ALCE một cách tất định (kiểm span/lớp), không cần NLI. Như vậy "0 unsupported claim" sẽ trở thành một con số định nghĩa rõ thay vì một hệ quả của cấu tạo.

### Cited Findings
- ALCE (Gao, Yen, Yu, Chen, EMNLP 2023): benchmark đầu tiên đánh giá tự động trích dẫn của LLM, trên ba trục fluency, correctness, citation quality. Citation recall = output có được các đoạn trích dẫn hỗ trợ đầy đủ không; citation precision = có trích dẫn thừa/không liên quan không; cả hai chấm bằng NLI. NLI không nhận ra "hỗ trợ một phần" nên chấm precision thấp hơn người. Trên ELI5, model tốt nhất vẫn thiếu hỗ trợ trích dẫn đầy đủ khoảng 50% thời gian. Chất lượng retrieval là then chốt. Qua tóm tắt + trang ACL. — [ACL Anthology 2023.emnlp-main.398](https://aclanthology.org/2023.emnlp-main.398); [arXiv 2305.14627](https://arxiv.org/abs/2305.14627)
- RAGAS (Es, James, Espinosa-Anke, Schockaert; EACL 2024 demo, tr. 150–158): đánh giá RAG không cần tham chiếu, ba trục faithfulness (câu trả lời có dựa trên context truy vấn được không), answer relevance, context relevance. Tác giả báo dự đoán khớp với người, nhất là ở faithfulness và answer relevance. Qua tóm tắt. — [ACL Anthology 2024.eacl-demo.16](https://aclanthology.org/2024.eacl-demo.16); [arXiv 2309.15217](https://arxiv.org/abs/2309.15217)
- LA-RAG dùng GPT-4o làm giám khảo; tương quan với người chỉ 0.57. Đây là ví dụ cho thấy chấm bằng LLM-judge cần được kiểm định. — [arXiv 2602.14612v3](https://arxiv.org/html/2602.14612v3)

### Inferences
- **Khoảng 0.5 ngày, không cần model:** báo citation recall/precision kiểu ALCE nhưng tất định. Mỗi mệnh đề phải trỏ tới event_id có cùng lớp và span; precision là tỉ lệ event được trích thực sự cần cho câu trả lời. Như vậy "0 ảo giác" của RQ2/RQ3 có một định nghĩa đo được, có thể nêu cả mặt hạn chế ("do cấu tạo").
- **Abstention:** thêm một tập nhỏ câu hỏi không có đáp án (lớp không xuất hiện trong khoảng thời gian), đo tỉ lệ hệ thống trả lời "không tìm thấy" đúng. Rẻ và trả lời trực tiếp câu hỏi "thực tế".
- **Bất định từ detector:** kèm score/khoảng tin cậy của event trong câu trả lời; có thể kết hợp với kết quả định cỡ (calibration) đã có. Không tìm được bài báo đo lợi ích của việc này.
- Không khuyến nghị RAGAS với Qwen 9B làm giám khảo trong 4 ngày: cần kiểm định với người, tốn thời gian.

### Gaps
- Chưa tra các bài về abstention/selective answering trong RAG (không đủ ngân sách lượt tra).

## Độ chặt của đánh giá: kiểm định ghép cặp, thắng/hòa/thua theo query, phân loại lỗi

### Takeaway
Văn liệu IR về kiểm định thống kê khuyến nghị t-test ghép cặp hoặc permutation (randomization) test cho chênh lệch trung bình. Bootstrap mạnh nhưng có xu hướng cho p nhỏ, tức hơi dễ dãi, khi mẫu nhỏ. Với khoảng 96–100 query, nên báo kèm permutation test và bảng thắng/hòa/thua theo query bên cạnh CI bootstrap.

### Cited Findings
- Urbano, Lima, Hanjalic (SIGIR 2019, arXiv 1905.11096): mô phỏng với giả thuyết null biết trước. Bootstrap có tỉ lệ dương tính giả cao hơn danh nghĩa khi mẫu nhỏ; randomization tốt hơn bootstrap, Wilcoxon, sign; t-test đúng danh nghĩa kể cả mẫu nhỏ. Khuyến nghị t-test cho trung bình và randomization cho thống kê khác; không khuyến khích Wilcoxon/sign. Bootstrap thường mạnh nhất. Qua tóm tắt thứ cấp, chưa đọc bài. — [arXiv 1905.11096](https://arxiv.org/pdf/1905.11096)
- Urbano, Corsi, Hanjalic (SIGIR 2021): t-test và permutation giữ lỗi loại I gần α; bootstrap thiên về p nhỏ. Qua tóm tắt. — [TU Delft repository](https://repository.tudelft.nl/record/uuid:aff400ca-ecfe-40b0-aed6-79ef2ee56afe)
- Parapar et al. kết luận khác và khuyến nghị sign/Wilcoxon, nên vấn đề còn tranh luận. Qua tóm tắt. — [arXiv 1901.10696](https://arxiv.org/pdf/1901.10696)

### Inferences
- Khoảng 0.5 ngày: với mỗi cặp cấu hình (hybrid vs vector_only vs structured_only), báo Δ nDCG@10 + CI bootstrap ghép cặp (đã có) + p của permutation test ghép cặp + số query thắng/hòa/thua. Như vậy câu "hybrid thua vector_only" có hình dạng rõ (vài query thua nặng hay thua đều).
- Phân loại lỗi retrieval theo query: (a) parser sai filter, (b) filter đúng nhưng thứ tự trong tập lọc sai, (c) không có relevant trong corpus do SED bỏ sót, (d) giới hạn top-k/HNSW cắt mất. Mỗi loại ứng với một khắc phục khác nhau trong các mục trên.

### Gaps
- Chưa đọc trực tiếp hai bài của Urbano; khuyến nghị cụ thể lấy từ tóm tắt thứ cấp.

### Bảng xếp hạng đề xuất cho 4 ngày còn lại (suy luận, không phải số trích)
| # | Kỹ thuật | Lợi ích kỳ vọng | Chi phí | Đo bằng |
|---|---|---|---|---|
| 1 | Quét α của CC (hoặc chọn mode) trên validation, khóa trước test | Cao với mâu thuẫn hybrid/vector | ~0.5 ngày | nDCG@10 val theo α; test một lần |
| 2 | Thắng/hòa/thua theo query + permutation test + phân loại lỗi | Cao về độ tin của luận văn | ~0.5 ngày | không cần chạy model mới |
| 3 | Citation recall/precision tất định kiểu ALCE + tập câu hỏi abstention | Trung bình–cao (trả lời câu "0 ảo giác do cấu tạo") | ~0.5–1 ngày | tỉ lệ trên validation |
| 4 | Tín hiệu cấu trúc làm khóa xếp hạng trong tập lọc (score, overlap) | Trung bình | ~0.5 ngày | nDCG@10 val |
| 5 | Regex thời gian + few-shot động cho parser | Trung bình cho parsed mode | ~0.5–1 ngày | exact match/predicate acc trên paraphrase |
| 6 | Self-consistency parser | Thấp (+0.4–0.5 EX trong DAIL-SQL) | ~0.5 ngày, ×k độ trễ | như trên |
| 7 | BGE-M3 sparse/multi-vector | Thấp với tài liệu ngắn | ~1 ngày | nDCG@10 val |
| 8 | bge-reranker-v2-m3 | Không rõ, có thể hại | ~0.5–1 ngày | nDCG@10 val |
| 9 | Đánh chỉ mục đa mức / câu quan hệ thời gian trong document | Không rõ, đổi định nghĩa corpus | >1 ngày | — để làm hướng tương lai |
