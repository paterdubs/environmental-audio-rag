# Kiểm toán nội bộ: truy hồi (RAG) và sinh mô tả có ràng buộc — hiện trạng, điểm hỏng, cải thiện rẻ trong 4 ngày

> Phạm vi: chỉ đọc repo tại HEAD `575f784` (24/11/2026). Không sửa file repo, không chạy Docker, không đánh giá test.
> Hai phép mô phỏng offline mới (mục 1 và 3) chạy **chỉ trên validation/dev** bằng `.venv/Scripts/python.exe`, từ
> danh sách `retrieved` và file caption JSONL đã lưu; relevance tính lại từ annotation dev bằng đúng
> `ml.retrieval.relevance`. Script nháp ở scratchpad (không trong repo):
> `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\sim_rq3.py`
> và `...\scratchpad\cap_vs_gt.py`. Các số "mô phỏng" dưới đây vì vậy **chưa có artifact trong repo** — muốn dùng
> trong báo cáo phải sinh lại bằng script repo (xem mục 5).
> Trên test chỉ đọc lại số đã lưu trong JSON đã khóa (đếm thắng/thua và độ dài danh sách từ `per_query`), không tính metric mới.

## 1. Truy hồi: tài liệu, chế độ hybrid, vị từ, parser, query set — và vì sao hybrid thua vector_only

### Takeaway
Hybrid **không có fusion hay trọng số**: nó là "lọc cứng SQL trên sự kiện *dự đoán* → xếp cosine BGE-M3 bên trong tập đã lọc", nên trên kho độ phủ thấp (f2/B0/V2) bộ lọc trả về rất ít bản ghi (trung vị **1** kết quả, **32–39/97** truy vấn test rỗng) và nDCG@10 bị chặn bởi recall SED; trên V3 (dày sự kiện) danh sách đủ dài nên hybrid thắng. Một sửa rẻ không cần train/test — **lọc cứng trước, nối thêm kết quả vector_only (backfill)** — trên validation B0 nâng nDCG@10 EN từ 0.428 (hybrid) lên 0.577, cao hơn vector_only +0.027 [+0.010, +0.047]; trên V3 +0.096 [+0.062, +0.133] so vector và +0.053 so hybrid.

### Cited Findings
**Cách dựng tài liệu**
- Document = `[caption]` + caption + `[canonical event summary]` mỗi event một dòng `class_id onset-offset s (score)` + dòng `duration …; events N; max polyphony M` + `classes …`; trả kèm `class_ids`, `total_events`, `max_polyphony` để lọc — [ml/retrieval/document_builder.py L6–43](../../ml/retrieval/document_builder.py)
- Caption dùng trong document là **template** EN + VI ("A {phrase} is audible from {onset} to {offset} seconds."), tất định — [ml/captioning/template.py L22–27](../../ml/captioning/template.py); [ADR-0027 §3](../../docs/decisions/ADR-0027-dau-vao-retrieval-va-query-set.md). `DOCUMENT_VERSION = "doc-v1-template-en-vi"` — [ml/retrieval/embedding.py L20](../../ml/retrieval/embedding.py)
- Embedding BGE-M3 dense 1024 chiều qua `sentence-transformers`, chuẩn hóa L2; sparse/ColBERT của BGE-M3 **không dùng** ("FlagEmbedding (sparse/ColBERT) không cần cho RQ3") — [ml/retrieval/embedding.py L17–41](../../ml/retrieval/embedding.py); [ADR-0027 §4](../../docs/decisions/ADR-0027-dau-vao-retrieval-va-query-set.md)
- ADR-0027 tự ghi đánh đổi: "Document dùng caption template (đơn điệu) — embedding có thể dựa chủ yếu vào tên lớp" — [ADR-0027 Consequences](../../docs/decisions/ADR-0027-dau-vao-retrieval-va-query-set.md)

**Ba chế độ, không có fusion**
- `structured_only`: lọc cứng, sắp theo onset sớm nhất của lớp đã lọc; `vector_only`: cosine trên mọi document, không lọc; `hybrid`: lọc cứng rồi `ORDER BY d.embedding <=> qv` trong tập đã lọc, `LIMIT k` — [ml/retrieval/store.py L3–12, L100–122](../../ml/retrieval/store.py). Không có RRF, không có trọng số, không có reranker; hybrid "không có tham số tự do; top-k cố định 10" — [ADR-0027 §1](../../docs/decisions/ADR-0027-dau-vao-retrieval-va-query-set.md); [scripts/evaluate_retrieval.py L9–10, L38](../../scripts/evaluate_retrieval.py)
- Bộ lọc: `classes_all` (`d.class_ids @> …`), `temporal` (EXISTS self-join events a/b), `duration` (`offset−onset > min_s`), đều chỉ trên `provenance = 'prediction'` — [ml/retrieval/store.py L65–89](../../ml/retrieval/store.py). Hợp đồng Pydantic `Filters` (classes_all 1–5 lớp, tolerance 0–60 s, cần ít nhất một bộ lọc) — [ml/retrieval/filters.py](../../ml/retrieval/filters.py)

**Bốn vị từ thời gian** (SQL và Python cùng một bảng) — [ml/retrieval/temporal.py L24–42](../../ml/retrieval/temporal.py)
- `before`: `a.offset_s <= b.onset_s + tol`; `after`: `a.onset_s >= b.offset_s − tol`; `overlaps`: `a.onset < b.offset AND b.onset < a.offset`; `within`: `a.onset ≥ b.onset AND a.offset ≤ b.offset`. Query set dùng `tolerance_s = 0.0` cho mọi câu temporal — [ml/retrieval/query_set.py L269](../../ml/retrieval/query_set.py)

**Query set v2 và relevance**
- 100 câu, 4 nhóm 21/27/30/22 (single_class/multi_class/temporal/duration), temporal 8/8/7/7 theo vị từ, duration ngưỡng 10 s và 30 s, chọn theo tần suất trên **train** (support ≥ 3), văn bản EN + VI từ mẫu — [ml/retrieval/query_set.py L22–25, L27–44](../../ml/retrieval/query_set.py)
- Relevance từ **annotation** bằng đúng ngữ nghĩa bộ lọc; nhị phân; nDCG@10, R@{1,5,10}, MRR; filter exactness đo trên sự kiện đã index — [ml/retrieval/relevance.py L1–14](../../ml/retrieval/relevance.py); [scripts/evaluate_retrieval.py L55–63](../../scripts/evaluate_retrieval.py). Validation 96/100, test 97/100 câu có relevant — [retrieval_benchmark_validation_s8lite_b0_gold_20261108.md](../../docs/measurements/retrieval_benchmark_validation_s8lite_b0_gold_20261108.md)

**Parser câu hỏi (ADR-0036)**
- Qwen3.5-9B qua llama.cpp, schema JSON sinh từ enum lớp/vị từ, prompt `query-filter-prompt-v1.1` có 4 few-shot (EN/VI), temperature 0, seed 20260922 — [ml/retrieval/query_parser.py L20–38](../../ml/retrieval/query_parser.py); [query_parser_20260928.md](../../docs/measurements/query_parser_20260928.md)
- Kết quả: paraphrase 40 câu exact **0.925 (37/40)**; template 200 câu exact **0.855 (171/200)**, đúng predicate chỉ **0.767** trên 60 câu temporal; 240/240 hợp lược đồ — [query_parser_20260928.md](../../docs/measurements/query_parser_20260928.md). Lỗi chính: đảo vai a/b, nhầm within↔overlaps, bỏ ràng buộc thời lượng — [report/final_src/06_ket_qua.md L265](../../report/final_src/06_ket_qua.md)
- Parsed − gold nDCG@10 hybrid/en trên test: f2 0.409, B0 0.377, V2 0.398, V3 0.655, thấp hơn gold 0.006–0.015 — [report/final_src/06_ket_qua.md L261](../../report/final_src/06_ket_qua.md)

**Số RQ3 đã khóa (test, gold, EN)**
- Hybrid − vector_only: f2 −0.111 [−0.166, −0.059], B0 −0.075 [−0.121, −0.028], V2 −0.087 [−0.136, −0.037], V3 +0.040 [+0.004, +0.079]; hybrid − structured |Δ| ≤ 0.013; exactness vector 0.274/0.271/0.273/0.493 so 1.000 — [rq3_modes_20261123.md](../../docs/measurements/rq3_modes_20261123.md)
- Theo nhóm (hybrid / vector): temporal f2 0.126/0.426, B0 0.134/0.330, V2 0.209/0.398, V3 0.501/0.501; multi_class f2 0.151/0.387, B0 0.090/0.264; duration hybrid cao hơn ở cả bốn kho (f2 0.762/0.621) — [rq3_modes_20261123.md](../../docs/measurements/rq3_modes_20261123.md)
- Lịch sử: trên corpus run B (v1, 25/09) hybrid **thắng** vector +0.063 [+0.020, +0.109] EN và +0.131 VI; structured 0.523 > hybrid 0.481 > vector 0.418 — [ADR-0027 §8](../../docs/decisions/ADR-0027-dau-vao-retrieval-va-query-set.md). Đổi sang f2: structured 0.523→0.416, hybrid 0.481→0.415, vector 0.418→0.526 — [PAPER_NOTES S43](../../docs/PAPER_NOTES.md)
- PAPER_NOTES S70 ghi rõ "Hướng chưa thử: lọc mềm, dung sai thời gian" và cơ chế "chưa kiểm bằng thí nghiệm kiểm soát" — [docs/PAPER_NOTES.md L115](../../docs/PAPER_NOTES.md); báo cáo Chương 6 cũng nói "dùng bộ lọc như điểm cộng thay cho điều kiện cứng" là hướng chưa thử — [report/final_src/06_ket_qua.md L259](../../report/final_src/06_ket_qua.md)

**Bằng chứng theo từng truy vấn (đếm từ `per_query` đã lưu, không tính metric mới)**
- Test f2: hybrid > vector **15**, < vector **49**, hòa **33**; danh sách hybrid < 10 kết quả ở **88/97**, rỗng **32/97**, trung vị độ dài **1** — [retrieval_benchmark_test_20261002.json](../../docs/measurements/retrieval_benchmark_test_20261002.json)
- Test B0: 15/39/43; < 10 ở 87/97, rỗng 39/97, trung vị 1 — [retrieval_benchmark_test_s8lite_b0_gold_20261108.json](../../docs/measurements/retrieval_benchmark_test_s8lite_b0_gold_20261108.json). Test V2: 16/41/40; rỗng 35/97 — [retrieval_benchmark_test_lbrv2_gold_20261110.json](../../docs/measurements/retrieval_benchmark_test_lbrv2_gold_20261110.json)
- Test V3: hybrid thắng 44, thua 18, hòa 35; < 10 ở 73/97, rỗng chỉ **2/97**, trung vị **5** — [retrieval_benchmark_test_lbrv3_gold_20261110.json](../../docs/measurements/retrieval_benchmark_test_lbrv3_gold_20261110.json)
- Validation B0: 13/48/35, < 10 ở 82/96, rỗng 35/96, trung vị 1.5; validation V3: 43/21/32, rỗng 3/96, trung vị 6 — [retrieval_benchmark_validation_s8lite_b0_gold_20261108.json](../../docs/measurements/retrieval_benchmark_validation_s8lite_b0_gold_20261108.json); [retrieval_benchmark_validation_lbrv3_gold_20261110.json](../../docs/measurements/retrieval_benchmark_validation_lbrv3_gold_20261110.json)

**Mô phỏng offline trên validation (mới, chưa có artifact repo)** — từ cùng danh sách `retrieved` đã lưu; kiểm: nDCG hybrid tính lại trùng giá trị lưu (assert < 1e-9). nDCG@10 EN:

| Kho validation | structured | vector | hybrid | **backfill** (hybrid + vector chưa có) | RRF(hybrid, vector) k=60 |
|---|---:|---:|---:|---:|---:|
| B0 (OOF dev) | 0.427 | 0.551 | 0.428 | **0.577** | 0.574 |
| f2 | 0.399 | 0.540 | 0.398 | **0.571** | 0.566 |
| V2 | 0.375 | 0.466 | 0.378 | **0.500** | 0.493 |
| V3 | 0.595 | 0.584 | 0.628 | **0.680** | 0.659 |

- Bootstrap theo truy vấn (10 000 mẫu, EN): B0 backfill − vector +0.027 [+0.010, +0.047], backfill − hybrid +0.149 [+0.113, +0.188]; V3 backfill − vector +0.096 [+0.062, +0.133], backfill − hybrid +0.053 [+0.028, +0.082] (script nháp `sim_rq3.py`, dữ liệu nguồn ở các JSON validation trên).
- Theo nhóm (B0, EN, backfill): temporal 0.478 (hybrid 0.196, vector 0.475), multi_class 0.338 (0.145 / 0.336), duration 0.743 (0.690 / 0.671), single_class 0.829 (0.803 / 0.787). Tiếng Việt B0: hybrid 0.427, vector 0.488, backfill 0.540.

### Inferences
- Cơ chế "lọc cứng bị chặn bởi recall SED" giờ có kiểm gián tiếp: hybrid gần như bằng structured vì tập lọc thường chỉ 0–2 bản ghi, nên xếp cosine không có gì để xếp; vector_only thắng ở multi_class/temporal vì nó vẫn đưa lên bản ghi mà SED chỉ dự đoán một trong hai lớp (relevance tính trên nhãn thật). Bằng chứng: trung vị độ dài hybrid 1 (f2/B0/V2) so với 5 (V3) khớp đúng chiều thắng/thua.
- Backfill là "lọc như ưu tiên" chứ không phải lọc mềm thật: phần đầu danh sách vẫn đúng ràng buộc 100%, phần nối thêm cần được đánh dấu "gần đúng, chưa thỏa bộ lọc" trong câu trả lời để giữ unsupported-claim = 0. Exactness của danh sách sẽ giảm, phải báo kèm (ví dụ exactness của k_filtered đầu = 1.000).
- Vì không có tham số tự do (RRF có k=60 nhưng backfill thì không), backfill có thể ghi trước trên validation, và nếu muốn đưa vào kết luận thì là **một lượt mở test mới, phải ghi ledger** — hoặc chỉ báo trên validation như phân tích cơ chế (an toàn hơn trong 4 ngày).
- Các đòn bẩy khác đều rẻ: (a) dung sai `tolerance_s` cho before/after (hiện 0.0), (b) nới `classes_all` thành "ít nhất k−1 lớp" làm tầng thứ hai, (c) dùng thêm `score` sự kiện (đã lưu trong bảng `events`) để có lọc "mềm", (d) document giàu hơn có câu quan hệ thời gian ("birds before horn") để vector bắt được temporal.

### Gaps
- Không có điểm cosine trong artifact (`documents[].score` chỉ là thứ hạng nghịch, [ml/retrieval/answer.py L83](../../ml/retrieval/answer.py)), nên chưa mô phỏng được fusion theo điểm hay ngưỡng cosine; cần DB (Docker) để chạy lại `store.search` với SQL mới.
- Dung sai thời gian, nới classes_all, lọc theo `score` cần sự kiện đã index (trong PostgreSQL hoặc `predictions/*.npz` + postproc); chưa mô phỏng trong phiên này.
- Chưa tìm thấy phân tích từng truy vấn được commit (mọi số thắng/thua trong báo cáo là từ hình f05c); không có ví dụ định tính "truy vấn nào vector cứu được".

## 2. Câu trả lời RAG: bộ sinh, metric unsupported-claim, hợp đồng

### Takeaway
Bộ sinh câu trả lời là **template tất định, không LLM**: đếm số bản ghi trong top-k thỏa bộ lọc trên sự kiện dự đoán, trích tối đa 3 bản ghi với lớp + khoảng thời gian; bộ kiểm độc lập đọc lại văn bản. Unsupported-claim = 0.000 ở mọi cấu hình là hệ quả cấu tạo; điểm yếu thật là **số câu có trả lời** (B0 61/96 validation, 58/97 test) và việc câu trả lời không có tổng hợp (đếm toàn kho, tổng thời lượng), không có "gợi ý gần đúng" khi bộ lọc rỗng.

### Cited Findings
- `answer()` chỉ trích bản ghi mà `supporting_events` thỏa bộ lọc; `MAX_CITED = 3`; câu mẫu EN "{n} of the top {k} results satisfy the filters." / "In {rid}, {name} at {on}–{off} s, then …"; rỗng → "No indexed recording satisfies the applied filters." — [ml/retrieval/answer.py L20–29, L61–84](../../ml/retrieval/answer.py)
- `unsupported_claims` tách theo "In/Trong <rid>," và gán mỗi khoảng thời gian cho lớp được nhắc gần nhất, cộng từ cấm G3 — [ml/retrieval/answer.py L87–110](../../ml/retrieval/answer.py)
- Validation B0: contract 96/96, unsupported-claim 0.000, có trả lời **61/96**, trích đúng GT 0.953 (structured) / 0.939 (hybrid) — [retrieval_answers_validation_s8lite_b0_gold_20261108.md](../../docs/measurements/retrieval_answers_validation_s8lite_b0_gold_20261108.md)
- Validation V3: có trả lời **93/96**, trích đúng GT 0.627 / 0.646 — [retrieval_answers_validation_lbrv3_gold_20261110.md](../../docs/measurements/retrieval_answers_validation_lbrv3_gold_20261110.md); test V3 95/97, 0.704/0.712 — [retrieval_answers_test_lbrv3_gold_20261110.md](../../docs/measurements/retrieval_answers_test_lbrv3_gold_20261110.md)
- Test B0 có trả lời 58/97, f2 65/97 — [PAPER_NOTES S59](../../docs/PAPER_NOTES.md)
- Báo cáo rà soát: "Khi phục vụ, caption là template, câu trả lời RAG là template tất định, và Qwen3.5-9B chỉ dùng để phân tích câu hỏi thành bộ lọc", trong khi SYSTEM.md L666 vẫn nói Qwen sinh câu trả lời — [reports/Đánh giá khóa luận audio RAG.md L27, L167](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- "Sinh câu trả lời" nằm trong cut-list (#9 "RAG answer generation, chỉ giữ retrieval") — [docs/PLAN.md, khối Giai đoạn F/cut-list](../../docs/PLAN.md)

### Inferences
- Đánh đổi độ phủ ↔ độ đúng rõ ràng: B0 trả lời ít (61/96) nhưng 95% trích đúng; V3 trả lời nhiều (93/96) nhưng ~63% đúng. Một câu trả lời hai tầng ("khớp chính xác: …; gần đúng (chưa thỏa bộ lọc): …") dùng chính backfill ở mục 1 tăng "có trả lời" mà không phá unsupported-claim, miễn bộ kiểm chỉ đòi evidence cho phần "khớp chính xác" và phần gần đúng không khẳng định lớp/thời gian.
- Tổng hợp rẻ: "N bản ghi trong kho thỏa bộ lọc" (đếm toàn kho, không chỉ top-k), tổng thời lượng lớp, khung onset sớm nhất/muộn nhất — tất cả tất định từ bảng `events`, kiểm được bằng cùng bộ kiểm.
- Diễn đạt độ chắc: `score` sự kiện đã có trong document và bảng `events` ([document_builder.py L26–29](../../ml/retrieval/document_builder.py)) nhưng câu trả lời và caption không dùng; có thể thêm từ rào đón theo ngưỡng điểm ("likely"/"có thể") — cần kiểm từ rào đón không bị lexicon G3 coi là suy diễn.

### Gaps
- Không có đánh giá người dùng hay độ tự nhiên của câu trả lời (báo cáo tự nhận là hạn chế — [reports/… L194](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)).
- Chưa thấy metric "câu trả lời đúng theo GT" ở mức sự kiện (chỉ mức bản ghi "trích đúng GT").

## 3. Sinh mô tả: template, constrained, cover, unconstrained; metric G1–G3; điểm yếu đo được

### Takeaway
Mọi metric RQ2 chấm caption **so với timeline SED mà nó nhận** (e2e) hoặc so với GT khi đưa GT vào (oracle) — nên "0 ảo giác" của template/constrained là theo cấu tạo. Mô phỏng mới trên dev chấm **caption e2e so với nhãn thật**: các caption bỏ sót **34–42%** số lớp có trong GT ở f2/B0/V2, và với V3 thì ảo giác so GT là **0.18–0.23** — tức độ đúng thực tế của mô tả do SED quyết định, không do bộ sinh. Điểm yếu riêng của bộ sinh: constrained bỏ sót khi timeline dày (V3 dev 0.145, test 0.081), caption rất dài (template V3 trung bình 400 ký tự, tối đa 2 361), không gộp sự kiện lặp, không đếm, không diễn đạt độ chắc.

### Cited Findings
**Cách hoạt động**
- Template: một câu mỗi sự kiện, evidence span cho từng câu, `assert_safe` chặn từ cấm — [ml/captioning/template.py L22–60](../../ml/captioning/template.py). Đây là caption **đang phục vụ** trong pipeline (EN + VI) — [ml/inference/pipeline.py L19, L56–57](../../ml/inference/pipeline.py)
- Constrained: ngữ pháp GBNF theo từng timeline cho phép **một câu** liệt kê một dãy con sự kiện theo onset, mỗi sự kiện tối đa một lần; G1, G3, bối cảnh, gọi tên quá mức, sai thời gian, sai thứ tự đều "impossible by construction"; "omission is the dimension left to measure" — [ml/captioning/constrained.py L1–11, L77–101](../../ml/captioning/constrained.py)
- Cover (ADR-0026): sự kiện đầu tiên của mỗi lớp bắt buộc → bỏ sót lớp không thể xảy ra — [ml/captioning/constrained.py L13–16, L83](../../ml/captioning/constrained.py)
- Ngân sách token theo **ký tự** của caption dài nhất +1 sau khi trần 256 token cắt 16/558 caption — [ml/captioning/constrained.py L18–26, L120–122](../../ml/captioning/constrained.py)
- Unconstrained: cùng prompt ("You write one short English caption…", timeline JSON không có score), không evidence → G2 coverage = 0 theo cấu tạo — [ml/captioning/llm.py L24–32, L88–98, L154–155](../../ml/captioning/llm.py). Prompt **bỏ score** có chủ đích nên không thể diễn đạt độ chắc.
- Metric: precision/recall mức lớp qua lexicon; hallucination = 1 − precision, omission = 1 − recall; mập mờ lexicon luôn được tính có lợi cho caption ("RQ2 delta … is therefore a lower bound"); thứ tự = tỷ lệ cặp đúng thứ tự (không phải Kendall τ) — [ml/evaluation/grounding.py L1–8, L45–76, L102–140](../../ml/evaluation/grounding.py); [ml/evaluation/caption_stats.py L7–16](../../ml/evaluation/caption_stats.py)

**Số đã khóa**
- Test annotated n=139 (e2e): omission constrained f2 0.012, B0 0.013, V2 0.007, **V3 0.081 [0.051, 0.112]**; cover 0 ở cả bốn; hallucination LLM ≤ 0.022 — [PAPER_NOTES S67](../../docs/PAPER_NOTES.md); [rq2_llm_systems_20261110_test_annotated.md](../../docs/measurements/rq2_llm_systems_20261110_test_annotated.md)
- Dev annotated n=134 (e2e): constrained omission V3 **0.145 [0.106, 0.184]**; unconstrained bối cảnh 0.299–0.440, gọi tên quá mức 0.071–0.093, thứ tự V3 0.811; unconstrained V3 omission 0.031 — [rq2_llm_systems_20261110_dev_annotated.md](../../docs/measurements/rq2_llm_systems_20261110_dev_annotated.md)
- Oracle dev (timeline = GT): constrained omission **0.084 [0.051, 0.119]**, unconstrained hallucination 0.009, omission 0.018, bối cảnh 0.216, thứ tự 0.848 — [rq2_llm_systems_20261110_dev_annotated.md](../../docs/measurements/rq2_llm_systems_20261110_dev_annotated.md)
- Ví dụ thật (dev oracle S-0009): GT có `birds` 0.0–124.91 s, caption constrained bắt đầu bằng "An impulsive sound … from 0.8 to 10.7 seconds and the sound of jet aircrafts …" — **bỏ hẳn sự kiện chim dài nhất** — [ml/runs/sed_ensemble_s13_f2_20260929T045053Z/captions/constrained_dev.jsonl](../../ml/runs/sed_ensemble_s13_f2_20260929T045053Z/captions/constrained_dev.jsonl) (dòng đầu)
- Phê bình đã ghi: "0 ảo giác ở RQ2 có được là do cấu tạo của ngữ pháp, và mô tả constrained gần như trùng template" (BLEU-4 0.3584, CIDEr 3.60 so với template; unconstrained 0.0147); κ ≈ −0.03 giữa cờ "caption có bịa" của bộ đo từ điển và người đọc (0/4 ca trùng) — [reports/Đánh giá khóa luận audio RAG.md L3, L39](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md); [caption_mention_agreement_20260925.md](../../docs/measurements/caption_mention_agreement_20260925.md)

**Mô phỏng mới trên dev (annotated n=134, chưa có artifact repo; `cap_vs_gt.py`)** — chấm caption **e2e** bằng `evaluate_grounding` với timeline **GT** (lấy từ dòng oracle của cùng file, đã kiểm trùng GT trong báo cáo gốc):

| Kho dev | sự kiện dự đoán/bản ghi (tổng) | timeline rỗng | template vs GT: ảo giác / bỏ sót | constrained vs GT | cover vs GT | unconstrained vs GT |
|---|---|---:|---|---|---|---|
| f2 | 2.94 (394) | 22 | 0.011 / 0.373 | 0.011 / 0.378 | 0.011 / 0.373 | 0.026 / 0.370 |
| B0 (OOF) | 3.47 (465) | 15 | 0.019 / 0.342 | 0.017 / 0.355 | 0.019 / 0.342 | 0.034 / 0.339 |
| V2 | 2.99 (400) | 34 | 0.022 / 0.415 | 0.019 / 0.419 | 0.022 / 0.415 | 0.035 / 0.412 |
| V3 | 7.05 (945) | 0 | 0.178 / 0.107 | 0.192 / 0.204 | 0.199 / 0.107 | 0.234 / 0.105 |

GT dev: trung bình 6.61 sự kiện, 2.03 lớp/bản ghi.
- Độ dài caption (ký tự, trung bình / tối đa): template f2 172 / 1 104, V3 400 / 2 361; constrained f2 213 / 1 406, V3 283 / 1 651; cover V3 405 / 2 530; unconstrained 131–150 / ≤ 225. Số mention trung bình: cover V3 6.1, constrained V3 4.1, unconstrained V3 2.5.

### Inferences
- "Ảo giác 0" và "ảo giác so với thực tế" là hai đại lượng khác nhau; báo cáo nên tách rõ "trung thành với timeline" (đóng góp bộ sinh) và "đúng với âm thanh" (bị chặn bởi SED). Bảng trên là cách rẻ để nói điều đó bằng số, và cho thấy bộ sinh **không làm tệ thêm** so với template (constrained ≈ template ở mọi kho, trừ bỏ sót thêm trên V3).
- Bỏ sót của constrained trên V3 đến từ việc ngữ pháp bắt liệt kê **từng sự kiện** trong một câu; với 7 sự kiện/bản ghi model dừng sớm. Nén timeline theo lớp trước khi sinh (gộp các đoạn cùng lớp: "birds, 5 segments between 0.0 and 124.9 s") giảm độ dài, giữ G1/G2 (evidence trỏ nhiều event), và có thể giảm bỏ sót mà không cần cover — làm được bằng một biến thể `build_grammar`/template, chạy trên dev.
- Hai khoảng trống tính năng rẻ, tất định: đếm/tổng hợp ("3 times", "for about 40 s in total") và rào đón theo `score` ("possibly" khi score thấp) — template hiện bỏ qua score hoàn toàn ([template.py L43–50](../../ml/captioning/template.py)); prompt LLM cũng bỏ score ([llm.py L88–98](../../ml/captioning/llm.py)).

### Gaps
- Không thấy metric độ tự nhiên/đọc được; chưa có người đọc thứ hai ngoài nhóm (T1-10 đề xuất chấm lại caption dev, tính κ — [reports/… L120](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)).
- Lexicon phát hiện bịa yếu so người (precision 0.896, recall 0.936, bỏ lọt kiểu "hammer strikes" sau "workshop" — [CLAUDE.md nhật ký 26/09](../../CLAUDE.md)); mọi số ảo giác của unconstrained là cận dưới.
- Chưa kiểm tác động của nén timeline lên bỏ sót bằng LLM thật (cần llama.cpp chạy; chỉ template variant là chạy được không cần GPU).

## 4. Mã có sẵn để tái sử dụng cho thí nghiệm nhanh dev/validation-only, và ước lượng công

### Takeaway
Hầu hết thí nghiệm cải thiện chỉ cần đọc artifact đã có và tái dùng `relevance`, `evaluate_grounding`, `caption_stats`; chỉ các biến thể lọc mềm/dung sai cần PostgreSQL (Docker) hoặc dựng lại sự kiện từ predictions. Backfill/RRF và "caption vs GT" làm được trong vài giờ, không GPU, không test.

### Cited Findings
- `run_queries` đã lưu `retrieved` cho mọi (truy vấn × chế độ × ngôn ngữ) trong `per_query` của mọi `retrieval_benchmark_*.json` — [scripts/evaluate_retrieval.py L76–100, L210](../../scripts/evaluate_retrieval.py); `rank_metrics`, `corpus_ground_truth`, bootstrap ghép cặp `recording_bootstrap` dùng lại được — [scripts/evaluate_retrieval.py L55–73, L103–128](../../scripts/evaluate_retrieval.py)
- `report_rq3_modes` là mẫu script "chỉ đọc artifact đã khóa → artifact mới có provenance" — [scripts/report_rq3_modes.py](../../scripts/report_rq3_modes.py)
- `score_sources` chấm mọi nhánh và template trên cùng timeline; có cổng test (`check_test_gate`) và `--eval-set annotated` — [scripts/score_captions.py L74–100, L161–187](../../scripts/score_captions.py); caption dev cho cả bốn kho có sẵn trong `ml/runs/<run>/captions/{constrained,constrained_cover,unconstrained}_dev.jsonl` (f2, `sed_filtered_B0_oof_dev_…`, hai run `sed_lbr_oofevents_…`)
- `filter_sql`/`temporal_query` là điểm chèn cho dung sai/lọc mềm; `PREDICATES` có cả SQL và Python cùng ngữ nghĩa nên một biến thể Python-only (trên sự kiện dựng lại) vẫn khớp SQL — [ml/retrieval/store.py L65–89](../../ml/retrieval/store.py); [ml/retrieval/temporal.py](../../ml/retrieval/temporal.py)
- `build_document` là hàm thuần, thêm dòng quan hệ thời gian không đụng schema; nhưng đổi document cần embed lại và nạp DB (`scripts.build_retrieval_index`) — [ml/retrieval/document_builder.py](../../ml/retrieval/document_builder.py); [CLAUDE.md §7](../../CLAUDE.md)

### Inferences — ước lượng công (một người, đã quen repo)

| Thí nghiệm (chỉ validation/dev) | Cần gì | Công | Kỳ vọng / rủi ro |
|---|---|---|---|
| R1. Backfill hybrid + vector, RRF(k=60) — script repo kiểu `report_rq3_modes` đọc `per_query` validation, bootstrap | Không DB, không GPU | 2–3 giờ (+1 giờ test) | Đã mô phỏng: +0.027…+0.096 so vector, +0.05…+0.15 so hybrid. Rủi ro thấp; nhớ báo exactness |
| R2. Dung sai thời gian (before/after tol 1–2 s) và nới classes_all ("≥ k−1 lớp") làm tầng 2 của backfill | Sự kiện đã index (DB) hoặc dựng lại từ `predictions/dev.npz` + postproc | 0.5–1 ngày | Chủ yếu giúp temporal/multi_class; phải ghi trước giá trị tol |
| R3. Document giàu quan hệ (câu "X before Y", đếm lớp) + embed lại | GPU/CPU cho BGE-M3, DB | ~1 ngày | Không chắc tăng; vector chỉ thấy tên lớp |
| R4. Trả lời hai tầng + đếm toàn kho | Sửa `answer.py`, bộ kiểm | 0.5 ngày | Tăng "có trả lời" 61/96 → ~96/96 mà vẫn 0 unsupported nếu phần gần đúng không khẳng định |
| C1. Bảng "caption e2e vs GT" bằng script repo | Không GPU | 2–3 giờ | Đã mô phỏng; số trung thực cho phê bình "0 do cấu tạo" |
| C2. Template nén theo lớp + đếm + rào đón theo score (EN/VI) | Không GPU; cần cụm từ VI được duyệt | 0.5–1 ngày | Caption ngắn hơn nhiều; G1–G3 vẫn kiểm được; VI cần người duyệt cụm từ |
| C3. Constrained trên timeline nén (LLM) | llama.cpp GPU; ~2 giờ chạy/kho dev | 1 ngày | Có thể giảm bỏ sót V3 0.145; phải giữ prompt/model như ADR-0023 hoặc ghi biến thể mới |

### Gaps
- Chưa đo thời gian chạy BGE-M3 embed lại toàn corpus dev trên máy này (artifact không ghi).
- Chưa kiểm xem `predictions/dev.npz` + postproc của từng kho có tái dựng đúng sự kiện đã index không (parity đã có cho phục vụ, chưa cho script mới).

## 5. PLAN "Giai đoạn F" và báo cáo rà soát nói gì về điểm yếu RAG/caption

### Takeaway
Giai đoạn F đã viết lại RQ3 (T0-04 ✅) và RQ2 (T0-08 ✅) theo hướng trung thực nhưng **không thêm thí nghiệm**; luật dự án cấm chọn trên test và mọi lượt đánh giá test mới phải ghi trước + ledger. Rủi ro hội đồng hàng đầu vẫn là "hybrid thua vector, lọc cứng làm hại?" và "RQ2 hiển nhiên theo cấu tạo, LLM để làm gì?"; hai thí nghiệm R1 và C1 ở trên trả lời thẳng hai câu này chỉ bằng dữ liệu validation/dev.

### Cited Findings
- T0-04: "Đoạn RQ3 nói thẳng hybrid < vector_only (Δ −0.111/−0.075/−0.087), cơ chế lọc cứng bị chặn bởi recall SED" — ✅ 23/11; T0-08: "Viết lại RQ2 trung thực: 0 vi phạm có được do cấu tạo, constrained ≈ template, κ ≈ −0.03, LLM thật sự có ích ở parser" — ✅ 23/11 — [docs/PLAN.md, Giai đoạn F, L432+](../../docs/PLAN.md)
- Đòn #1 (rất cao): hybrid thua vector trên 3/4 kho; nhóm temporal f2 hybrid 0.126 so vector 0.426 "đúng chỗ C4 tự nhận là mạnh" — [reports/Đánh giá khóa luận audio RAG.md L35](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- Đòn #5 (cao): "RQ2 hiển nhiên theo cấu tạo; template cũng bằng 0, LLM để làm gì?" — [reports/… L39](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- "Phần mô tả và RAG thì mỏng hơn vẻ ngoài" — [reports/… L27](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- Luật: "không chọn hay tinh chỉnh gì trên DataSED test… mọi lượt đánh giá mới trên test, kể cả 'chỉ tính thêm một metric' từ dự đoán đã đóng băng, phải ghi trước và vào ledger" — [reports/… L66](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- Văn liệu ngoài được trích trong báo cáo rà soát: HARP (SLT 2026) kết luận hybrid keyword + vector là cấu hình vững nhất; LA-RAG 2026 có event store SQL + cửa sổ thời gian tuyệt đối — [reports/… L60](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md) (chưa đọc lại nguồn gốc trong phiên này)
- Đề xuất T1-09 baseline CLAP cho RQ3 (~1 ngày, phải mở test có ghi trước) và T1-10 người đọc thứ hai chấm caption dev — [reports/… L119–120](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)
- Chương 6 hiện viết "Một hướng chưa thử là dùng bộ lọc như điểm cộng thay cho điều kiện cứng; nhóm nêu hướng này ở Chương 7 và không khẳng định nó tốt hơn" — [report/final_src/06_ket_qua.md L259](../../report/final_src/06_ket_qua.md)

### Inferences
- R1 (backfill) biến câu "hướng chưa thử" thành một phép đo validation có CI, trả lời đòn #1 mà không mở test: "lọc trước, ngữ nghĩa bù sau" giữ được ưu thế ràng buộc và vượt vector_only trên cả bốn kho validation.
- C1 (caption vs GT) trả lời đòn #5 bằng cách tách hai đại lượng, và đúng với luận điểm trung tâm của báo cáo rà soát ("lỗi định vị lan xuống mô tả và truy hồi").
- Nếu muốn đưa backfill vào kết luận chính trên test: ghi trước (ADR mới, không tham số), một lượt test, ghi ledger — khả thi trong 4 ngày nhưng cần Docker và người dùng duyệt lượt mở test.

### Gaps
- Chưa rõ người dùng có chấp nhận thêm thí nghiệm mới ở giai đoạn F (kế hoạch đã duyệt ghi "không train lại, không mở test, không 'lần đầu'", nhưng không cấm phân tích validation).
- Số validation của kho B0 là OOF dev (134 bản ghi) còn f2 dev gần in-sample (hậu xử lý chọn trên dev), nên so giữa kho trên validation cần ghi chú — [PAPER_NOTES S59](../../docs/PAPER_NOTES.md).
