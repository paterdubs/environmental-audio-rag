# Rà soát danh mục tài liệu tham khảo của báo cáo khóa luận (references audit)

Phạm vi: nguồn Markdown `report/final_src/*.md` (gồm cả bảng chèn qua `@@INCLUDE@@`), danh mục `docs/thesis/bibliography.bib`, nhật ký xác minh `docs/RELATED_WORK.md`, mẫu khoa `report/Mau bao cao KLTN_DS.docx`. Không sửa tệp nào trong repo. Script phụ trợ (chỉ đọc) ở scratchpad: `cite_audit.py` (đếm trích dẫn theo file:line), `term_audit.py` (dò thuật ngữ/công cụ có hoặc không có trích dẫn), `template_refs.py` (trích phần hướng dẫn TLTK của mẫu khoa).

## Câu hỏi 1 — Từng tài liệu trong danh mục được dùng ở đâu, đóng góp gì, nên giữ hay bỏ?

### Takeaway
Danh mục có 28 mục, 27 mục được trích bằng `[@key]` (tổng 59 lượt: Ch.1 9, Ch.2 35, Ch.3 2, Ch.4 6, Ch.6 7; Ch.5 và Ch.7 không có trích dẫn nào). Không có mục nào là "rác" thật sự: 14 mục là đóng góp trực tiếp (dữ liệu, phương pháp, chỉ số, công cụ, kết quả đối chiếu), 14 mục là bối cảnh cần thiết (định nghĩa khái niệm, định cỡ kết quả, khoanh vùng đóng góp C2/C3/C4, bối cảnh Việt Nam). Mục duy nhất không được trích là `dcase2023task4b`, nhưng nó **đang chống lưng một hàng của bảng** nên nên thêm trích dẫn chứ không bỏ. Đề xuất bỏ: **không có mục nào** bắt buộc phải bỏ; chỉ có sửa định dạng/thay bản arXiv bằng bản đã bình duyệt.

### Cited Findings

**Cách build xử lý danh mục**
- Đường dẫn bib do build dùng là `docs/thesis/bibliography.bib` (hằng `BIBLIOGRAPHY`), không phải tệp trong `report/` — [scripts/build_midterm_report.py:29](../../scripts/build_midterm_report.py)
- Build **in toàn bộ** các mục trong bib vào danh mục (không tự bỏ mục không được trích); mục không được trích chỉ sinh cảnh báo `stderr` "tài liệu trong danh mục nhưng không được trích" — [scripts/build_midterm_report.py:73-100](../../scripts/build_midterm_report.py); [scripts/report_docx/package.py:324-340](../../scripts/report_docx/package.py)
- Khóa trích dẫn không có trong bib làm build dừng (`KeyError`), nên hiện **không có khóa nào trong văn bản thiếu trong bib** (script xác nhận: danh sách rỗng) — [scripts/report_docx/markdown.py:52-60](../../scripts/report_docx/markdown.py)
- Danh mục được nhóm Việt trước, Anh sau; tác giả Việt xếp theo tên, nước ngoài theo họ, không tác giả thì theo tên cơ quan; số `[n]` theo thứ tự danh mục — [scripts/report_docx/bib.py:1-7, 83-114](../../scripts/report_docx/bib.py)
- Header của bib và RELATED_WORK đặt luật nội bộ: "Chỉ gồm nguồn đạt V3 trở lên", "Chỉ V3 và V4 được trích dẫn trong báo cáo" — [docs/thesis/bibliography.bib:1](../../docs/thesis/bibliography.bib); [docs/RELATED_WORK.md:25](../../docs/RELATED_WORK.md)

**Bảng rà soát từng mục** (số lượt = số lần `[@key]` xuất hiện; vị trí theo `file:line` của `report/final_src/`; V = mức xác minh trong RELATED_WORK)

| # | Khóa | Trích dẫn ngắn | Lượt / vị trí | Luận điểm được chống lưng | V | Loại | Đề xuất |
|---|---|---|---|---|---|---|---|
| 1 | `fredianelli2025environmental` | Fredianelli, Artuso, Pompei, Licitra, Iannace, Akbaba (2025), "Environmental Noise Dataset for Sound Event Classification and Detection", *Scientific Data* 12, 1712, DOI 10.1038/s41597-025-05991-w | 7: 01:11; 02:9; 02:57; 02:99 (×2); 03:7; 03:80 | Mô tả DataSEC/DataSED, nhãn mạnh/yếu, nguồn Freesound+AudioSet (rủi ro trùng), bài không có baseline, giấy phép | V3 | **Trực tiếp — dữ liệu dùng** | **KEEP (direct)** |
| 2 | `ebbers2024sound` | Ebbers, Germain, Wichern, Le Roux (2024), "Sound Event Bounding Boxes", Interspeech 2024, pp. 562–566 | 4: 02:45 (×2); 02:99; 04:97 | cSEBB; nhóm tự cài theo bài và dùng trong hệ cuối B0 | V3 | **Trực tiếp — phương pháp dùng** | **KEEP (direct)** |
| 3 | `schmid2025effective` | Schmid, Morocutti, Foscarin, Schlüter, Primus, Widmer (2025), "Effective Pre-Training of Audio Transformers for SED", ICASSP 2025 | 3: 02:53; 02:99; 04:52 | Lý do thử bộ mã hóa đóng băng; nguồn checkpoint PretrainedSED (BEATs_strong, frame_mn10) dùng cho T2a/T2b → B0 | V3 | **Trực tiếp — phương pháp/checkpoint dùng** | **KEEP (direct)**; nên thêm trích ở 04:55 và 04:57 (xem Câu hỏi 2) |
| 4 | `dcase2016task3` | DCASE Community (2016), "DCASE 2016 Task 3: SED in Real Life Audio", trang web | 2: 02:39; 06:184 (và hàng bảng 06:192) | Định cỡ độ khó: event-F1 onset 1,5–8,1% | V3 | Bối cảnh — định cỡ kết quả | **KEEP (context, needed)** |
| 5 | `kong2020panns` | Kong, Cao, Iqbal, Wang, Wang, Plumbley (2020), "PANNs…", *IEEE/ACM TASLP* 28, 2880–2894 | 3: 01:71; 02:51; 02:99 | Trọng số CNN14 AudioSet cho nhánh B/C và mô hình phân loại DataSEC | V3 | **Trực tiếp — mô hình/trọng số dùng** | **KEEP (direct)** |
| 6 | `mesaros2016metrics` | Mesaros, Heittola, Virtanen (2016), "Metrics for Polyphonic SED", *Applied Sciences* 6(6), 162 | 3: 02:15; 02:29; 02:99 | Event-F1, collar, micro/macro — chỉ số chính | V3 | **Trực tiếp — chỉ số dùng** | **KEEP (direct)**; nên thêm ở 06:5 (`sed_eval`) |
| 7 | `mesaros2021tutorial` | Mesaros, Heittola, Virtanen, Plumbley (2021), "Sound Event Detection: A Tutorial", *IEEE SPM* 38(5), 67–83 | 6: 01:7; 01:9 (×2); 02:7; 02:9; 02:11 | Định nghĩa SED, đa âm, nhãn mạnh/yếu, CRNN | V3 | Bối cảnh — định nghĩa nền | **KEEP (context, needed)** — nguồn tổng quan duy nhất neo các định nghĩa Ch.1–2 |
| 8 | `bilen2020psds` | Bilen, Ferroni, Tuveri, Azcarreta, Krstulović (2020), "A Framework for the Robust Evaluation of SED", ICASSP 2020, pp. 61–65 | 2: 02:37; 02:99 | PSDS — chỉ số chính | V3 | **Trực tiếp — chỉ số dùng** | **KEEP (direct)**; nên thêm ở 04:179 (`psds_eval`) |
| 9 | `zhang2018mixup` | Zhang, Cisse, Dauphin, Lopez-Paz (2018), "mixup…", ICLR 2018 | 2: 02:55; 04:50 | Tăng cường dữ liệu trong công thức v2 | V3 | **Trực tiếp — kỹ thuật dùng** | **KEEP (direct)**; sửa định dạng (thiếu định vị, xem Câu hỏi 3) |
| 10 | `nam2022filteraugment` | Nam, Kim, Park (2022), "FilterAugment…", ICASSP 2022, pp. 4308–4312 | 2: 02:55; 04:50 | Tăng cường dữ liệu trong v2 | V3 | **Trực tiếp — kỹ thuật dùng** | **KEEP (direct)** |
| 11 | `chen2022beats` | Chen, Wu, Wang, Liu, Tompkins, Chen, Wei (2022), "BEATs…", arXiv:2212.09058v1 | 2: 02:53; 04:54 | Bộ mã hóa T2a (ứng viên f1/f3) | V3 | **Trực tiếp — mô hình thử nghiệm** | **KEEP (direct)**; MERGE/REPLACE bản arXiv bằng bản hội nghị (⚠️ cần xác minh venue) |
| 12 | `lewis2020rag` | Lewis và cs. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", arXiv:2005.11401v4 | 3: 01:13; 02:67; 02:99 | Khái niệm RAG — có trong tên đề tài | V3 | Bối cảnh — khái niệm cốt lõi | **KEEP (context, needed)**; REPLACE arXiv → NeurIPS 2020 |
| 13 | `chen2024m3` | Chen, Xiao, Zhang, Luo, Lian, Liu (2024), "M3-Embedding…", Findings of ACL 2024, pp. 2318–2335 | 2: 02:69; 04:134 | BGE-M3 làm embedding truy hồi | V3 | **Trực tiếp — công cụ/mô hình dùng** | **KEEP (direct)** |
| 14 | `ji2023hallucination` | Ji và cs. (2023), "Survey of Hallucination in NLG", *ACM Computing Surveys* 55(12), 1–38 | 3: 01:9; 02:61; 02:99 | Định nghĩa ảo giác nội tại/ngoại tại → cấu tạo chỉ số RQ2 | V3 | Bối cảnh — định nghĩa khái niệm đo | **KEEP (context, needed)** |
| 15 | `hegde2026larag` | Hegde, Sridhar, Vakada, Guo, Visser (2026), "Event-Grounded QA over Long Audio via Structured Retrieval" (LA-RAG), arXiv:2602.14612v4 | 1: 02:71 | Hệ gần nhất; khoanh đóng góp C4 (predicate giữa hai sự kiện) | V3 | Công trình liên quan — khoanh vùng đóng góp | **KEEP (context, needed)** — bỏ thì mất căn cứ cho việc không viết "lần đầu" |
| 16 | `kumar2026tac` | Kumar và cs. (2026), "TAC: Timestamped Audio Captioning", arXiv:2602.15766v2 | 1: 02:63 | Chỉ số ảo giác có mốc thời gian gần với C2 | V3 | Công trình liên quan — khoanh C2 | **KEEP (context, needed)** |
| 17 | `kuan2024echo` | Kuan, Huang, Lee (2024), "Understanding Sounds, Missing the Questions…" (ECHO), arXiv:2406.08402v1 | 1: 02:63 | Chỉ số ảo giác đối tượng gần C2 | V3 | Công trình liên quan — khoanh C2 | **KEEP (context, needed)**; REPLACE arXiv → Interspeech 2024 |
| 18 | `weck2023leakage` | Weck, Serra (2023), "Data Leakage in Cross-Modal Retrieval Training: A Case Study", arXiv:2302.12258v1 | 1: 02:101 | Rò rỉ dữ liệu bằng fingerprint — khoanh C3 | V3 | Công trình liên quan — khoanh C3 | **KEEP (context, needed)**; REPLACE arXiv → ICASSP 2023 |
| 19 | `wijngaard2025survey` | Wijngaard, Formisano, Esposito, Dumontier (2025), "Audio-Language Datasets of Scenes and Events: A Survey", arXiv:2407.06947v2 | 1: 02:101 | Đo chồng lấn giữa các bộ dữ liệu — khoanh C3 | V3 | Công trình liên quan — khoanh C3 | **KEEP (context, needed)**; REPLACE arXiv → *IEEE Access* 13 |
| 20 | `schmid2026boundary` | Schmid và cs. (2026), "SED with Boundary-Aware Optimization and Inference", arXiv:2601.04178v2 | 2: 02:47 (×2) | Hướng sửa biên khi huấn luyện, đối chiếu với LBR; nhóm đã thử một biến thể RED | V3 | Liên quan + phương pháp đã thử một phần | **KEEP (context, needed)**; cập nhật venue (IEEE SPL) |
| 21 | `dcase2022task4` | DCASE Community (2022), "DCASE 2022 Task 4 … results", trang web | 1: 06:184 (và hàng bảng 06:193) | Mốc PSDS hệ cơ sở DESED | V3 | Bối cảnh — định cỡ | **KEEP (context, needed)** |
| 22 | `dcase2023task4a` | DCASE Community (2023), "DCASE 2023 Task 4A … results", trang web | 1: 06:184 (và hàng bảng 06:194) | Mốc PSDS 2023 (kể cả hệ có BEATs) | V3 | Bối cảnh — định cỡ | **KEEP (context, needed)** |
| 23 | `dcase2023task4b` | DCASE Community (2023), "DCASE 2023 Task 4B … results", trang web | **0** lượt `[@]`; nhưng hàng bảng 06:195 và dòng nguồn 06:198 dùng số của nó | Mốc F1 MAESTRO Real | V3 | Bối cảnh — định cỡ (yếu nhất: khác chỉ số) | **KEEP + thêm `[@dcase2023task4b]`** vào hàng 06:195 hoặc NOTE 06:198. Chỉ bỏ nếu bỏ luôn hàng bảng đó |
| 24 | `qcvn262025` | Bộ Nông nghiệp và Môi trường (2025), *QCVN 26:2025/BNNMT: Quy chuẩn kỹ thuật quốc gia về tiếng ồn* | 2: 01:35; 01:37 | Bối cảnh ứng dụng tại VN; giới hạn đề tài (máy đo loại 1, không đo dBA) | **không có dòng nào trong RELATED_WORK** | Bối cảnh — ứng dụng VN | **KEEP (context, needed)** — tài liệu tiếng Việt duy nhất; sửa nguồn URL (xem Câu hỏi 3) |
| 25 | `artuso2025clap` | Artuso và cs. (2025), "Enhanced Environmental Sound Event Classification through Transfer Learning with CLAP Model", Forum Acusticum Euronoise 2025, pp. 2289–2294 | 1: 06:26 (và bảng 06:34–35) | Kết quả phân loại đã công bố trên dữ liệu tiền thân DataSEC | V3 | **Trực tiếp — kết quả đối chiếu** | **KEEP (direct)** |
| 26 | `goyumsamuditha2026datasec` | goyumsamuditha (2026), "Uncertainty-Aware and Explainable NN Classification of Environmental Sounds Using DataSEC", dự án GitHub, không bình duyệt | 1: 06:26 (và bảng 06:37–40) | Kết quả duy nhất tìm được trên DataSEC bản 4 | V3 (README) | **Trực tiếp — kết quả đối chiếu (không bình duyệt)** | **KEEP (direct)** — người dùng đã yêu cầu giữ so sánh này (CLAUDE.md §10, 23/11); giữ nhãn "không qua bình duyệt" |
| 27 | `bruch2023fusion` | Bruch, Gai, Ingber (2023), "An Analysis of Fusion Functions for Hybrid Retrieval", *ACM TOIS*, DOI 10.1145/3596512 | 1: 06:299 | Cách trộn hai nguồn xếp hạng tốt nhất phụ thuộc miền → bối cảnh cho backfill | **V2** | Bối cảnh — giải thích kết quả | **KEEP (context)** với điều kiện nâng lên V3 (đọc toàn văn) để khớp luật nội bộ; bổ sung tập/số |
| 28 | `guo2025brace` | Guo và cs. (2025), "BRACE: A Benchmark for Robust Audio Caption Quality Evaluation", arXiv:2512.10403v1 | 1: 06:230 | Nguồn ý tưởng của phép đo độ nhạy bộ chấm (thay một danh từ) | **V2** | **Trực tiếp — ghi công ý tưởng phương pháp đã dùng** | **KEEP (direct)** — bỏ là mất ghi công; nâng lên V3 |

Nguồn của từng dòng: số lượt và vị trí sinh bằng `cite_audit.py` trên [report/final_src/](../../report/final_src/); metadata từ [docs/thesis/bibliography.bib](../../docs/thesis/bibliography.bib); mức V từ [docs/RELATED_WORK.md:669-692](../../docs/RELATED_WORK.md) (bảng §8), [:458-473](../../docs/RELATED_WORK.md) (Artuso, goyumsamuditha), [:736](../../docs/RELATED_WORK.md) (bốn trang DCASE lên V3 ngày 23/11), [:750](../../docs/RELATED_WORK.md) (Bruch, BRACE "Mức V2 (đọc abstract/HTML, chưa đọc toàn văn PDF)").

**Bằng chứng cho các điểm đặc biệt**
- Hàng DCASE 2023 4B có trong bảng và dòng nguồn ghi "2023 T4A và T4B" nhưng không có `[@dcase2023task4b]` — [report/final_src/06_ket_qua.md:195, 198](../../report/final_src/06_ket_qua.md)
- `goyumsamuditha2026datasec` được giữ theo yêu cầu người dùng ("Người dùng yêu cầu giữ so sánh phân loại và thêm kết quả trên phiên bản DataSEC mới nhất") — [docs/RELATED_WORK.md:737](../../docs/RELATED_WORK.md)
- Bruch và BRACE chỉ đọc abstract/HTML ("Mức V2") — trái luật "Chỉ V3 và V4 được trích dẫn" — [docs/RELATED_WORK.md:25, 750](../../docs/RELATED_WORK.md)
- QCVN 26:2025 không xuất hiện ở bất kỳ dòng nào của RELATED_WORK (grep "QCVN" không khớp), dù bib ghi URL và ngày truy cập 23/11 — [docs/RELATED_WORK.md](../../docs/RELATED_WORK.md); [docs/thesis/bibliography.bib:235-243](../../docs/thesis/bibliography.bib)
- Bộ mã hóa của hệ cuối B0 là `frame_mn10` (công thức T2b), lấy từ PretrainedSED — đoạn này không có trích dẫn — [report/final_src/04_phuong_phap.md:55-57, 61](../../report/final_src/04_phuong_phap.md); checkpoint `frame_mn10_strong_1` và BEATs_strong là của Schmid và cs. 2025 — [docs/RELATED_WORK.md:226-235](../../docs/RELATED_WORK.md)
- Câu mở Chương 2 "Nhóm chỉ trích các nguồn đã đọc trực tiếp toàn văn" — [report/final_src/02_co_so_ly_thuyet.md:3](../../report/final_src/02_co_so_ly_thuyet.md) — đúng cho Ch.2 (mọi nguồn ở Ch.2 đều V3), nhưng Bruch/BRACE ở Ch.6 là V2.
- Bản đã bình duyệt của các mục arXiv (metadata arXiv API): Lewis 2005.11401 "Accepted at NeurIPS 2020"; Weck 2302.12258 "Accepted at ICASSP2023", DOI 10.1109/ICASSP49357.2023.10094617; Wijngaard 2407.06947 journal_ref "IEEE Access 13 (2025) 20328-20360", DOI 10.1109/ACCESS.2025.3534621; Kuan 2406.08402 "Accepted to Interspeech 2024"; Schmid 2601.04178 "Accepted for publication in IEEE Signal Processing Letters, 2026"; LA-RAG 2602.14612 nay đã v7, "Submitted to NAACL 2027 Industry Track"; BEATs, TAC, BRACE không có journal_ref — [arXiv API](http://export.arxiv.org/api/query?id_list=2005.11401,2212.09058,2406.08402,2407.06947,2601.04178,2302.12258,2210.11934,2512.10403,2602.14612,2602.15766,1710.09412&max_results=20)

### Inferences
- Danh mục 28 mục đã gọn: mỗi mục gắn với một luận điểm cụ thể, và 13 mục được trích đúng một lần đều chống lưng một câu khoanh vùng đóng góp hoặc một con số đối chiếu. Bỏ bất kỳ mục "chỉ một lần" nào (LA-RAG, TAC, ECHO, Weck, Wijngaard) sẽ làm hở các câu "áp dụng và mở rộng"/"không viết lần đầu" — đây là chỗ hội đồng hay hỏi về tính mới. Không nên bỏ.
- Ứng viên "có thể bỏ" duy nhất là `dcase2023task4b` cùng hàng bảng MAESTRO (F1 khác loại chỉ số với event-F1 của đề tài, nên giá trị định cỡ yếu nhất). Nếu muốn giữ bảng nguyên thì chỉ cần thêm trích dẫn; cách này ít rủi ro hơn.
- Nếu cần gộp, có thể gộp ba trang DCASE 2022/2023 thành một mục "DCASE Challenge results" — nhưng các trang có URL riêng và chống lưng số khác nhau, nên tách riêng là đúng chuẩn hơn; không khuyến nghị gộp.
- Việc thay sáu bản arXiv bằng bản đã bình duyệt (NeurIPS, ICASSP, Interspeech, IEEE Access, IEEE SPL, và có thể ICML cho BEATs) nâng tỉ lệ nguồn bình duyệt từ 13/28 lên 18/28 (19/28 nếu xác minh được BEATs) mà không thêm hay bớt mục nào.

### Gaps
- Chưa xác minh được venue/trang của BEATs (dblp chặn truy cập tự động; arXiv không ghi journal_ref). Theo trí nhớ là ICML 2023 (PMLR 202) — ⚠️ CẦN XÁC MINH qua Crossref/PMLR trước khi sửa bib.
- Chưa xác minh số trang/DOI của bản Interspeech 2024 (ECHO), tập/số của Bruch trong *TOIS* và bản SPL của Schmid 2026 — cần tra Crossref.

## Câu hỏi 2 — Có mục nào không được trích, khóa nào thiếu, và luận điểm nào cần trích dẫn mà đang thiếu?

### Takeaway
Không có khóa thiếu trong bib; chỉ `dcase2023task4b` không được trích (nhưng đang dùng trong bảng). Các chỗ thiếu trích dẫn quan trọng nhất có thể sửa **không cần thêm mục mới**: B0/T2b (`frame_mn10`, PretrainedSED) → `schmid2025effective`; `sed_eval` → `mesaros2016metrics`; `psds_eval` → `bilen2020psds`. Thiếu thật sự (cần mục mới): nDCG (chỉ số chính của RQ3, có công thức), mô hình Qwen3.5-9B, llama.cpp/GBNF, cây tăng cường gradient/scikit-learn (lõi của LBR), HNSW/pgvector; mức thấp hơn: BLEU/CIDEr, ECE/temperature scaling, bootstrap, focal loss, chưng cất tri thức, RRF, AudioSet, bản ghi Zenodo của hai bộ dữ liệu.

### Cited Findings
- Script cho kết quả: "KEYS IN TEXT NOT IN BIB: []", "UNCITED BIB ENTRIES: ['dcase2023task4b']" — `cite_audit.py` trên [report/final_src/](../../report/final_src/)
- Chương 5 (triển khai) và Chương 7 (kết luận) không có trích dẫn nào, dù Ch.5 nêu PostgreSQL + pgvector, llama.cpp + GBNF, FastAPI, PyTorch, React, Docker, BGE-M3, HNSW — [report/final_src/05_trien_khai.md:41, 63-72, 86, 114](../../report/final_src/05_trien_khai.md)

**Thuật ngữ được dùng nhưng dòng không có trích dẫn** (`term_audit.py`; `*` = dòng có trích dẫn):

| Mục | Vị trí (không trích) | Vai trò trong đề tài | Mức ưu tiên | Cách sửa đề xuất |
|---|---|---|---|---|
| Frame-MobileNet `frame_mn10` / PretrainedSED (T2b → B0, hệ cuối) | [04_phuong_phap.md:55, 57](../../report/final_src/04_phuong_phap.md) | Bộ mã hóa của hệ cuối | **Cao** | Thêm `[@schmid2025effective]` (đã có trong bib) |
| `sed_eval` | [06_ket_qua.md:5](../../report/final_src/06_ket_qua.md) | Thư viện tính event-F1 | Cao | Thêm `[@mesaros2016metrics]` (bài này đi kèm công cụ) |
| `psds_eval` | [04_phuong_phap.md:179](../../report/final_src/04_phuong_phap.md) | Thư viện tính PSDS | Cao | Thêm `[@bilen2020psds]` |
| nDCG@10 (có công thức) | [02_co_so_ly_thuyet.md:73](../../report/final_src/02_co_so_ly_thuyet.md); [04_phuong_phap.md:173](../../report/final_src/04_phuong_phap.md); 18 dòng, 1 dòng có trích | Chỉ số chính RQ3 | **Cao** | Mục mới: Järvelin & Kekäläinen (2002), *ACM TOIS* — ⚠️ cần xác minh metadata |
| Qwen3.5-9B | [04_phuong_phap.md:114](../../report/final_src/04_phuong_phap.md); [05_trien_khai.md:66](../../report/final_src/05_trien_khai.md) | LLM sinh mô tả (RQ2) và phân tích câu hỏi | **Cao** | Mục mới: báo cáo kỹ thuật hoặc model card của Qwen — ⚠️ cần xác minh tài liệu chính thức cho Qwen3.5 |
| llama.cpp, ngữ pháp GBNF | [02_co_so_ly_thuyet.md:85](../../report/final_src/02_co_so_ly_thuyet.md); [05_trien_khai.md:41](../../report/final_src/05_trien_khai.md) (10 dòng, 0 trích) | Cơ chế giải mã có ràng buộc (C1) | Trung bình–cao | Mục mới: kho GitHub llama.cpp, ghi bản build đã dùng |
| Cây tăng cường gradient (HistGradientBoosting, scikit-learn), có công thức | [02_co_so_ly_thuyet.md:87](../../report/final_src/02_co_so_ly_thuyet.md) | Lõi của LBR (đóng góp mới) | Trung bình–cao | Mục mới: Friedman (2001) và/hoặc Pedregosa và cs. (2011, JMLR) — ⚠️ cần xác minh |
| HNSW, pgvector | [05_trien_khai.md:86, 96](../../report/final_src/05_trien_khai.md); [00_phan_dau.md:98](../../report/final_src/00_phan_dau.md) | Chỉ mục vector | Trung bình | Malkov & Yashunin (HNSW); kho GitHub pgvector — tùy chọn |
| Bootstrap ghép cặp (có công thức) | [02_co_so_ly_thuyet.md:89](../../report/final_src/02_co_so_ly_thuyet.md) (10 dòng, 0 trích) | Kiểm định mọi so sánh | Trung bình | Efron & Tibshirani (sách) — tùy chọn; có thể coi là kiến thức phổ biến |
| BLEU-4, CIDEr | [04_phuong_phap.md:118](../../report/final_src/04_phuong_phap.md); [06_ket_qua.md:226](../../report/final_src/06_ket_qua.md) | Báo "để tham khảo" | Trung bình | Papineni và cs. (2002); Vedantam và cs. (2015) |
| ECE / hiệu chuẩn nhiệt độ | [06_ket_qua.md:44](../../report/final_src/06_ket_qua.md) | Kết quả âm tính phụ | Thấp–TB | Guo và cs. (2017) — tùy chọn |
| Focal loss | [04_phuong_phap.md:29, 57](../../report/final_src/04_phuong_phap.md) | Ứng viên g1/g2 (không thắng) | Thấp | Lin và cs. (2017) — tùy chọn |
| Chưng cất tri thức (KD, P2) | [04_phuong_phap.md:61](../../report/final_src/04_phuong_phap.md) | Ứng viên âm tính | Thấp | Hinton và cs. (2015) — tùy chọn |
| RRF (k = 60) | [06_ket_qua.md:307](../../report/final_src/06_ket_qua.md) | Phương án so sánh với backfill | Thấp | Cormack và cs. (2009), hoặc trỏ `[@bruch2023fusion]` |
| Kiểm định t Welch | [04_phuong_phap.md:181](../../report/final_src/04_phuong_phap.md) | Phân tích RQ1 | Thấp | Kiến thức thống kê phổ biến — không bắt buộc |
| AudioSet | 16 dòng, 7 có trích (qua PANNs/Schmid) | Dữ liệu tiền huấn luyện | Thấp–TB | Gemmeke và cs. (2017) — tùy chọn |
| Bản ghi Zenodo DataSEC 17033970 / DataSED 15346092; checkpoint PANNs Zenodo | [03_du_lieu.md:11, 13](../../report/final_src/03_du_lieu.md); [04_phuong_phap.md:57](../../report/final_src/04_phuong_phap.md) | Dữ liệu thật sự tải và dùng (bản 3 khác bài báo) | Trung bình | Thêm 2 mục dataset có DOI Zenodo — vì đề tài dùng bản 3, khác số liệu trong bài báo |
| FastAPI, React, Docker, PyTorch, MFCC, log-mel | Ch.5, Ch.3 | Công cụ/khái niệm phổ thông | Không cần | Bỏ qua theo nguyên tắc "không trích kiến thức phổ biến" |

- CHAIR (02:63) được nêu qua ECHO, đúng cách trích gián tiếp: không liệt kê bài gốc khi chưa đọc bài gốc — phù hợp quy định "tài liệu gốc đó không được phép liệt kê" — [hướng dẫn UIT](https://sdh.uit.edu.vn/sites/default/files/201506/hd-tieuluan-khoaluan-phuluc.pdf)
- TCVN 12527-1:2018 (01:37) chỉ được nêu như nội dung của QCVN và trích qua `[@qcvn262025]` — [report/final_src/01_gioi_thieu.md:37](../../report/final_src/01_gioi_thieu.md)

### Inferences
- Ba sửa đổi "không thêm mục" (frame_mn10, sed_eval, psds_eval) nên làm trước vì rẻ và che đúng các chỗ hội đồng dễ hỏi: hệ cuối dựa trên mô hình của ai, chỉ số tính bằng công cụ nào.
- Nếu muốn giữ danh mục gọn, bộ tối thiểu nên thêm là 3–4 mục: nDCG (Järvelin & Kekäläinen), Qwen (tài liệu chính thức), llama.cpp (GitHub), và gradient boosting/scikit-learn. Thêm các mục này đưa tổng lên khoảng 31–32, vẫn trong dải điển hình của khóa luận đại học (Câu hỏi 3).
- Chương 5 không có trích dẫn là bình thường với chương triển khai, nhưng một trích dẫn cho llama.cpp/Qwen ở bảng thành phần 05:63–66 giúp người đọc biết phiên bản mô hình dùng.

### Gaps
- Chưa tra metadata chính xác cho các mục mới đề xuất (nDCG, Qwen3.5, Friedman, scikit-learn, HNSW, BLEU, CIDEr, Guo 2017, Lin 2017, Hinton 2015, Cormack 2009, Gemmeke 2017). Theo luật dự án, phải đọc nguồn (V3) rồi mới đưa vào bib; tôi chỉ nêu tên từ hiểu biết chung, chưa xác minh.
- Không rõ tài liệu chính thức nào nên trích cho Qwen3.5-9B (báo cáo kỹ thuật hay model card Hugging Face) — chưa tra.

## Câu hỏi 3 — Hướng dẫn của Việt Nam và thông lệ học thuật nói gì về một danh mục tài liệu tham khảo tốt?

### Takeaway
Mẫu IUH (và hướng dẫn của Bộ/ĐHQG có nội dung gần như trùng) chỉ quy định **hình thức**: nhóm theo ngôn ngữ (Việt trước), xếp alphabet theo họ (nước ngoài) hoặc tên (Việt), định dạng bài báo/sách/web. Các hướng dẫn khác bổ sung: mọi tài liệu trích phải có trong danh mục và ngược lại, không trích kiến thức phổ biến, không liệt kê tài liệu gốc chưa tiếp cận. Không có quy định số lượng; thông lệ quốc tế cho khóa luận đại học là khoảng 15–50 mục (TU Berlin gợi ý khoảng 20). Danh mục 28 mục hiện tại nằm trong dải này; không cần cắt.

### Cited Findings

**Mẫu khoa IUH (đọc trực tiếp tệp mẫu)**
- "Tài liệu tham khảo được xếp theo nhóm ngôn ngữ với thứ tự tiếng: Việt, Anh, Pháp, Đức, Nga, Trung, Nhật; giữ nguyên văn tiếng nước ngoài, không phiên dịch" — [report/Mau bao cao KLTN_DS.docx](../../report/Mau%20bao%20cao%20KLTN_DS.docx) (đoạn 325)
- Xếp alphabet: tác giả nước ngoài theo họ; tác giả Việt "theo tên, không đảo tên trước họ"; không có tác giả thì theo từ đầu của tên cơ quan ban hành — [mẫu khoa](../../report/Mau%20bao%20cao%20KLTN_DS.docx) (đoạn 326–329)
- Bài báo: tác giả, (năm), "tên bài" (ngoặc kép, không nghiêng), tên tạp chí, tập (số), trang; sách/báo cáo: tác giả hoặc cơ quan ban hành, (năm), *tên* (nghiêng), NXB, nơi XB; web: "tên trang web, (tháng-năm xuất bản), địa chỉ trang web"; dòng sau lùi 1 cm — [mẫu khoa](../../report/Mau%20bao%20cao%20KLTN_DS.docx) (đoạn 330–348)
- Phần quy trình chỉ dặn: "Lên danh mục tài liệu tham khảo và trình bày … theo đúng hướng dẫn của Khoa, chú ý trích dẫn và tránh copy/đạo văn" — mẫu không có câu nào về số lượng, arXiv, dữ liệu, phần mềm hay quy chuẩn — [mẫu khoa](../../report/Mau%20bao%20cao%20KLTN_DS.docx) (đoạn 268–269)
- Tệp `report/Mau bao cao KLTN_DS (1).docx` chưa track trong git trùng SHA-256 với mẫu đã dùng (cùng 408.103 byte), tức không có phiên bản mẫu mới — kiểm bằng `sha256sum` trên hai tệp trong [report/](../../report/)

**Hướng dẫn các trường khác (cùng gốc quy định của Bộ)**
- Hướng dẫn UIT (ĐHQG-HCM) có phần TLTK gần như trùng mẫu IUH, và thêm: "Nguồn được trích dẫn phải liệt kê chính xác trong danh mục tài liệu tham khảo"; "Không nên trích dẫn những kiến thức phổ biến mà mọi người đều biết vì chỉ làm nặng nề phần trình bày"; "Nếu không tiếp cận được tài liệu gốc mà phải trích dẫn … thông qua tài liệu trung gian thì phải nêu rõ cách trích dẫn này, tài liệu gốc đó không được phép liệt kê trong danh mục"; trích dẫn theo số trong ngoặc vuông, nhiều tài liệu thì tăng dần, ví dụ [5, 12, 34] — [UIT, Phụ lục hướng dẫn trình bày](https://sdh.uit.edu.vn/sites/default/files/201506/hd-tieuluan-khoaluan-phuluc.pdf)
- Hướng dẫn HCMUAF/Văn Lang yêu cầu tài liệu dẫn trong luận văn phải có trong danh mục và ngược lại; UEL mô tả danh mục là nơi đặt tài liệu "được dẫn, sử dụng hoặc nhắc tới" (theo tóm tắt kết quả tìm kiếm, chưa mở toàn văn) — [HCMUAF/Văn Lang](https://www2.hcmuaf.edu.vn/data/pvhien/Huong%20dan%20viet%20%20LV-DH%20Van%20Lang.pdf); [UEL](https://psdh.uel.edu.vn/Resources/Docs/SubDomain/psdh/THAM%20KHAO%20HUONG%20DAN%20TRINH%20BAY%20LUAN%20AN%20TOM%20TAT%20LUAN%20AN%20TS.pdf)
- Bài "Một số lưu ý khi làm phần tài liệu tham khảo" của UIT: tách nhóm Việt/Anh, trình bày thẳng hàng và thống nhất, ghi rõ loại tài liệu (khóa luận, luận văn) và trường khi trích luận văn; bài không nói gì về DOI, Wikipedia/blog, độ mới hay số lượng — [UIT](https://www.uit.edu.vn/bai-viet/mot-so-luu-y-khi-lam-phan-tai-lieu-tham-khao)

**Số lượng tài liệu**
- TU Berlin: "a rough number is 20 references for a bachelor thesis and 30-40 for a master's thesis" — [TU Berlin TKN](https://www.tkn.tu-berlin.de/theses/info.shtml) (qua tóm tắt tìm kiếm)
- Heidelberg (nhóm kỹ nghệ phần mềm): khoảng 15–20 bài học thuật cho khóa luận cử nhân, tùy đề tài — [Uni Heidelberg SE](https://se.ifi.uni-heidelberg.de/theses/q+a-thesis) (qua tóm tắt tìm kiếm)
- Một blog hướng dẫn viết luận (không chuyên CS) nêu 25–50 nguồn — [acurio.ch](https://acurio.ch/en/blog/how-many-sources-for-a-bachelor-thesis) (nguồn thứ cấp, độ tin cậy thấp)

**arXiv và bản đã bình duyệt**
- Thông lệ: nếu bài đã đăng thì trích bản chính thức; nếu trích preprint thì ghi rõ phiên bản (v1, v2…) và đánh dấu là preprint — [Springer Nature Communities](https://communities.springernature.com/posts/citing-a-preprint); [Mount Sinai Library](https://libguides.mssm.edu/preprints/citing)
- Với khóa luận, preprint chấp nhận được khi chưa có bản bình duyệt và luận điểm thuộc về "hiện trạng nghiên cứu" — [acurio.ch](https://acurio.ch/en/blog/citing-preprints) (blog, độ tin cậy trung bình)

**Trích dữ liệu, phần mềm, GitHub, quy chuẩn**
- IEEE theo nguyên tắc FORCE11 cho dữ liệu và phần mềm; dữ liệu nên có tác giả, tên, nơi lưu, ngày phát hành và DOI nếu có — [Penn State IEEE guide: datasets](https://guides.libraries.psu.edu/ieeequickguide/datasets); [Murdoch IEEE: dataset](https://libguides.murdoch.edu.au/IEEE/dataset)
- GitHub: tác giả/chủ kho, tên kho, phiên bản, ngày sửa cuối, "GitHub", URL — [Santa Clara University: citing code](https://libguides.scu.edu/citationguides/code); phần mềm: tên, phiên bản/năm, nhà phát hành, ngày truy cập, URL — [JCU Library IEEE: software](https://libguides.jcu.edu.au/IEEE/software)
- QCVN 26:2025/BNNMT: Lời nói đầu ghi "do Cục Môi trường biên soạn, Vụ Khoa học và Công nghệ trình duyệt; Bộ Khoa học và Công nghệ thẩm định, Bộ trưởng Bộ Nông nghiệp và Môi trường ban hành theo Thông tư số 0…1./2025/TT-BNNMT ngày 1…5. tháng 5 năm 2025. QCVN 26:2025/BNNMT thay thế QCVN 26:2010/BTNMT" (số và ngày điền tay trên bản quét) — [bản PDF trên thuvienphapluat](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf) (trích văn bản bằng pdftotext)
- Thông tư 01/2025/TT-BNNMT ban hành QCVN 26:2025, 27:2025, 43:2025; ngày ban hành 15/5/2025, hiệu lực 14/11/2025 — [LuatVietnam](https://luatvietnam.vn/tai-nguyen/thong-tu-01-2025-tt-bnnmt-quy-chuan-ky-thuat-quoc-gia-ve-chat-luong-moi-truong-400872-d1.html); [LuatVietnam tin văn bản mới](https://luatvietnam.vn/tin-van-ban-moi/3-quy-chuan-ky-thuat-quoc-gia-ve-chat-luong-moi-truong-xung-quanh-ap-dung-tu-14-11-2025-186-102239-article.html); bản chính thức đặt trên cổng Bộ — [mae.gov.vn](https://www.mae.gov.vn/noidung/Lists/VBQPPL/Attachments/567/QCVN%2026_2025_BNNMT.pdf) (tôi không mở được: kết nối bị từ chối)

**Định dạng hiện tại so với mẫu (đọc từ bib và bộ định dạng)**
- Mục `inproceedings` không in `eprint`, nên `zhang2018mixup` (không có trang/DOI) ra danh mục chỉ với tên hội nghị, không có cách nào tìm lại bài — [scripts/report_docx/bib.py:154-158](../../scripts/report_docx/bib.py); [docs/thesis/bibliography.bib:92-99](../../docs/thesis/bibliography.bib)
- `bruch2023fusion` thiếu tập/số/trang — [docs/thesis/bibliography.bib:265-273](../../docs/thesis/bibliography.bib)
- Mục web in năm và "truy cập dd/mm/yyyy", trong khi mẫu đòi "(tháng-năm xuất bản)" — khác nhỏ, chấp nhận được — [scripts/report_docx/bib.py:128-142](../../scripts/report_docx/bib.py)
- URL của QCVN trỏ CDN của thuvienphapluat (trang tổng hợp thương mại), không phải cổng Bộ; mục không ghi số Thông tư ban hành — [docs/thesis/bibliography.bib:235-243](../../docs/thesis/bibliography.bib)

**Cơ cấu hiện tại** (đếm từ bib): 1 tài liệu tiếng Việt, 27 tiếng Anh; 13 mục là bài tạp chí/hội nghị đã bình duyệt, 9 mục arXiv (5 trong đó đã có bản bình duyệt theo metadata arXiv, BEATs có thể là thứ sáu — chưa xác minh), 4 trang kết quả DCASE, 1 kho GitHub, 1 quy chuẩn; 13/28 mục từ 2024 trở đi — [docs/thesis/bibliography.bib](../../docs/thesis/bibliography.bib)

### Inferences
- **Nguyên tắc tinh gọn đề xuất** (rút từ các nguồn trên và luật nội bộ của dự án):
  1. Mỗi mục trong danh mục phải được trích ít nhất một lần trong thân bài, và mỗi trích dẫn phải có mục — hiện đạt 27/28; sửa nốt `dcase2023task4b` bằng cách thêm trích ở bảng.
  2. Giữ mọi nguồn của dữ liệu, mô hình/trọng số, chỉ số, công cụ, phương pháp đã dùng, kết quả được so — không cắt.
  3. Giữ nguồn bối cảnh khi nó chống lưng một câu cụ thể (định nghĩa, con số định cỡ, ranh giới đóng góp). Bỏ chỉ khi câu đó cũng bị bỏ.
  4. Không trích kiến thức phổ biến (Docker, React, FastAPI, MFCC) — đây là lý do hợp lệ để không thêm mục, không phải để bỏ mục đang có.
  5. Không liệt kê bài gốc chưa đọc (ví dụ CHAIR); trích qua nguồn trung gian và nói rõ — cách Ch.2 đang làm là đúng.
  6. Ưu tiên bản đã bình duyệt; nếu trích preprint thì ghi phiên bản đã đọc và đánh dấu preprint/không bình duyệt (bib đang ghi đúng phiên bản `vN`; GitHub đã ghi "không qua bình duyệt").
  7. Dữ liệu, phần mềm, quy chuẩn được trích như một tài liệu: dữ liệu ghi DOI Zenodo và phiên bản; GitHub ghi chủ kho, tên, phiên bản/commit, ngày, URL; quy chuẩn ghi cơ quan ban hành, số hiệu, văn bản ban hành (Thông tư 01/2025/TT-BNNMT ngày 15/5/2025), nguồn chính thức.
  8. Xếp danh mục: Việt trước, Anh sau; alphabet theo họ (nước ngoài), tên (Việt), tên cơ quan (không có tác giả) — bộ build đã làm đúng; không cần đổi sang thứ tự xuất hiện kiểu IEEE vì mẫu IUH dùng alphabet.
- **Những điều hội đồng hay chê và tình trạng hiện tại:** mục không được trích (còn 1, dễ sửa); nguồn Wikipedia/blog (không có); định dạng không thống nhất (nhỏ: mixup thiếu định vị, Bruch thiếu tập/số); thiếu DOI (các bài bình duyệt đều có DOI, trừ mixup và các trang web — bình thường); ít nguồn mới (không phải vấn đề: 13/28 từ 2024); quá ít tài liệu tiếng Việt (chỉ 1 — có thể bị hỏi, nhưng đề tài không có văn liệu tiếng Việt cùng chủ đề trong nhật ký tra cứu; không nên thêm nguồn tiếng Việt chỉ để đủ số).
- **Danh sách "chỉ bỏ nếu thật cần"** (thứ tự từ dễ bỏ nhất): `dcase2023task4b` (chỉ khi bỏ luôn hàng MAESTRO trong bảng dcase); sau đó không còn mục nào bỏ được mà không mất một luận điểm.
- **Danh sách việc làm đề xuất, không tăng số mục:** thêm 4 trích dẫn (04:55/57, 06:5, 04:179, 06:195); thay 5–6 bản arXiv bằng bản bình duyệt; bổ sung số Thông tư và URL cổng Bộ cho QCVN; thêm URL/arXiv cho mixup; bổ sung tập/số cho Bruch; nâng Bruch và BRACE lên V3 (đọc toàn văn) và ghi QCVN vào RELATED_WORK §10.

### Gaps
- Không tìm được hướng dẫn chính thức của Bộ GD&ĐT riêng cho khóa luận **đại học** (các văn bản tìm thấy là quy chế thạc sĩ/tiến sĩ hoặc hướng dẫn của từng trường); mẫu IUH và hướng dẫn UIT có phần TLTK trùng nhau, gợi ý cùng một gốc, nhưng tôi không xác minh được văn bản gốc.
- Không tìm được nguồn đáng tin liệt kê các lỗi danh mục mà hội đồng Việt Nam thường nêu; phần "hội đồng hay chê" ở trên là suy luận từ các quy định, không phải từ biên bản hội đồng.
- Không có quy định số lượng tối thiểu/tối đa trong mẫu IUH; các con số 15–50 là của trường nước ngoài, lấy qua tóm tắt tìm kiếm.
- Không mở được bản QCVN trên cổng mae.gov.vn (kết nối bị từ chối); số Thông tư lấy từ bản quét trên thuvienphapluat (số điền tay) và LuatVietnam.
