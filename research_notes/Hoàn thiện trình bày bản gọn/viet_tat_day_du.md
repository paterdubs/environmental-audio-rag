# Từ viết tắt và tên riêng trong bản gọn: dạng đầy đủ đã kiểm từ nguồn gốc

Phạm vi: `report/gon_src/01_gioi_thieu.md` … `07_ket_luan.md`, `90_phan_cuoi.md`, cùng các bảng được chèn qua `@@INCLUDE@@` (đã áp phép đổi tên trong `display.yaml` trước khi quét). Danh sách ứng viên được trích bằng regex (token có ≥ 2 chữ hoa, hoặc chữ hoa + số, cộng một danh sách tên riêng), rồi lọc tay. Số dòng là dòng trong tệp `.md` nguồn; với bảng chèn, ghi "tệp:dòng-của-marker [bảng]". Bản PDF đã tải nằm ở `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\acronym_sources\` (coi là dữ liệu không tin cậy; chỉ trích chữ bằng pdftotext).

Nhãn trạng thái: **VERIFIED** = đã đọc nguồn gốc trong phiên này, có URL. **NOT AN ACRONYM** = tên riêng, không phải từ viết tắt, hoặc nguồn không đưa ra dạng đầy đủ. **THESIS-OWN** = từ viết tắt do chính khóa luận đặt (kiểm trong repo). **UNVERIFIED** = chưa kiểm được nguồn gốc trong phiên này; dạng ghi là dạng thông dụng, phải kiểm trước khi đưa vào.

## Bảng chính theo thứ tự xuất hiện đầu tiên (từ Chương 1)

### Takeaway
Gợi ý "DataSEC (Data Sound Event Classification)" của sinh viên **không đúng chữ của tác giả**. Bản ghi Zenodo đặt tên "DataSEC - Dataset for Sound Event Classification of environmental noise"; bài *Scientific Data* mở rộng "Sound Event Classification (SEC)" nhưng không viết "DataSEC (…)" như một từ viết tắt. Vì vậy nên giới thiệu DataSEC/DataSED là **tên riêng kèm tên chính thức của bộ dữ liệu**, không phải một dạng đầy đủ tự ghép. Phần lớn từ viết tắt kỹ thuật trong bảng hiện có là đúng. Có một số chỗ lệch nhỏ: ADR, nDCG, DESED, TAC. Một số tên riêng cũng không có dạng đầy đủ chính thức: BRACE, Qwen, GGML/GGUF, FilterAugment, AudioSet.

### Cited Findings

Cột: **Token** | **Lần đầu** | **Dạng đầy đủ đã kiểm (đúng chữ nguồn)** | **Trạng thái + nguồn** | **Gợi ý tiếng Việt**

| # | Token | Lần đầu | Dạng đầy đủ đã kiểm | Trạng thái, nguồn | Gợi ý tiếng Việt |
|---|---|---|---|---|---|
| 1 | SED | 01:9 (đã mở rộng tại chỗ "Sound Event Detection – SED") | "Sound Event Detection (SED)" | VERIFIED: [Fredianelli et al. 2025, Sci Data, qua Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41597-025-05991-w&format=json&resultType=core); [Zenodo DataSED](https://zenodo.org/records/15346092) | Phát hiện sự kiện âm thanh |
| 2 | DataSEC | 01:11 (chưa giới thiệu tên đầy đủ) | Tên bản ghi: "DataSEC - Dataset for Sound Event Classification of environmental noise"; mô tả: "DataSEC is an open-access dataset specifically designed for Sound Event Classification of environmental noise"; "Sound Event Classification (SEC) has attracted considerable attention…" | VERIFIED (tên chính thức): [Zenodo 23097290, v4, 02/10/2026](https://zenodo.org/records/23097290). Bài báo: "Sound Event Classification (SEC) and Sound Event Detection (SED) are gaining momentum…"; "This work introduces two open-access datasets, DataSEC and DataSED" ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41597-025-05991-w&format=json&resultType=core)). **"Data Sound Event Classification" không xuất hiện ở nguồn nào.** | Bộ dữ liệu phân loại sự kiện âm thanh tiếng ồn môi trường |
| 3 | DataSED | 01:11 | "DataSED - Dataset for Sound Event Detection of environmental noise"; "DataSED is an open-access dataset specifically designed for Sound Event Detection of environmental noise" | VERIFIED: [Zenodo 15346092, v1, 05/05/2025](https://zenodo.org/records/15346092) | Bộ dữ liệu phát hiện sự kiện âm thanh tiếng ồn môi trường |
| 4 | RAG | 01:13 (đã mở rộng tại chỗ) | "Retrieval-Augmented Generation" (tên bài: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks") | VERIFIED: tên bài trong bib `lewis2020rag`, [arXiv 2005.11401](https://arxiv.org/abs/2005.11401). Trang arXiv không được mở trong phiên này; dạng đầy đủ lấy từ tên bài. Cũng được xác nhận gián tiếp qua LA-RAG (dòng 13). | Sinh tăng cường truy hồi |
| 5 | QCVN | 01:35 (chưa mở rộng) | Bìa văn bản: "QCVN 26:2025/BNNMT — QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ TIẾNG ỒN — National Technical Regulation on Noise" | VERIFIED: [PDF QCVN 26:2025/BNNMT](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf). Lời nói đầu ghi Bộ trưởng Bộ Nông nghiệp và Môi trường ban hành theo Thông tư số 01/2025/TT-BNNMT ngày 15/5/2025, và văn bản "thay thế QCVN 26:2010/BTNMT". Chữ trích từ PDF bị lỗi dấu (phông VnArial); dòng tiếng Anh trên bìa thì trích sạch. | Quy chuẩn kỹ thuật quốc gia |
| 6 | BNNMT | 01:35 | Bộ Nông nghiệp và Môi trường | VERIFIED: cùng PDF trên (lời nói đầu); bib `qcvn262025` author = "Bộ Nông nghiệp và Môi trường" | Bộ Nông nghiệp và Môi trường |
| 7 | BTNMT | 01:35 | Bộ Tài nguyên và Môi trường | UNVERIFIED: PDF chỉ ghi "QCVN 26:2010/BTNMT", không ghi tên bộ | Bộ Tài nguyên và Môi trường (cũ) |
| 8 | dBA | 01:35 | QCVN định nghĩa "Mức áp suất âm theo trọng số tần số A (LA)… được tính theo đơn vị decibel (dBA)" (mục 1.3.7; phục dựng từ chữ trích lỗi dấu) | VERIFIED (đơn vị và cách viết "dBA"): [PDF QCVN](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf). Dạng tiếng Anh "A-weighted decibel" trong bảng là cách diễn đạt thông dụng; QCVN không viết chữ đó. | Đề-xi-ben theo đặc tuyến A |
| 9 | RQ | 01:67 (đã mở rộng "Research Question – RQ") | Research Question | THESIS-OWN (định nghĩa tại 01:67) | Câu hỏi nghiên cứu |
| 10 | AudioSet | 01:73 | Tên bộ dữ liệu, không phải từ viết tắt | NOT AN ACRONYM. Nguồn gốc (Gemmeke và cs. 2017) **chưa được trích và chưa kiểm** trong phiên này. Bài PANNs viết "trained on the large-scale AudioSet dataset" ([arXiv 1912.10211](https://arxiv.org/abs/1912.10211)). | Bộ dữ liệu âm thanh AudioSet của Google (cần trích nguồn nếu giới thiệu) |
| 11 | nDCG | 01:75 (bảng RQ, chưa mở rộng; 02:71 cũng chưa mở rộng) | Bài gốc dùng "cumulated": "cumulated gain with discount by document rank (DCG)", mục "Normalized (D)CG Measure", ký hiệu "nDCG"; tóm tắt bài lại viết "cumulative gain" | VERIFIED: [Järvelin & Kekäläinen 2002, ACM TOIS 20(4)](https://doi.org/10.1145/582415.582418), đọc qua [bản sao PDF](https://www.fi.muni.cz/~xkohout7/Research/clanky_cizi/evaluation/p422-jarvelin.pdf). Bảng hiện ghi "normalized Discounted Cumulative Gain": chấp nhận được và thông dụng, nhưng tên bài gốc là "Cumulated Gain-Based Evaluation". | Lợi ích tích lũy có chiết khấu, chuẩn hóa |
| 12 | C1–C6 | 01:87 trở đi | Mã đóng góp nội bộ | THESIS-OWN (bảng đóng góp ở Ch.1) | Đóng góp 1…6 |
| 13 | ECHO | 01:96 (chưa mở rộng; 02:61 cũng chưa) | "ECHO, which is Evaluation of Caption Hallucination in audiO" (Mục 2.3; hai biến thể ECHO_I và ECHO_S) | VERIFIED: [Kuan, Huang, Lee 2024, arXiv HTML v1](https://arxiv.org/html/2406.08402v1). Tóm tắt **không** nhắc ECHO; dạng đầy đủ chỉ có trong thân bài. Lưu ý cách viết hoa lạ "audiO". | Chỉ số đánh giá ảo giác của mô tả âm thanh |
| 14 | TAC | 01:96 | Tóm tắt: "We introduce Timestamped Audio Captioner (TAC)". Tên bài: "TAC: Timestamped Audio Captioning" | VERIFIED: [arXiv 2602.15766](https://arxiv.org/abs/2602.15766). TAC là **tên mô hình**, nên dạng "Captioner" mới khớp chữ viết tắt; tên bài dùng "Captioning". | Mô hình mô tả âm thanh có mốc thời gian |
| 15 | SQL | 01:98 | "Structured Query Language" (dạng thông dụng) | UNVERIFIED: chưa mở nguồn chuẩn (ISO/IEC 9075) trong phiên này | Ngôn ngữ truy vấn có cấu trúc |
| 16 | LA-RAG | 01:98 | "LA-RAG (Long Audio Retrieval-Augmented Generation)" | VERIFIED: [Hegde et al. 2026, arXiv 2602.14612](https://arxiv.org/abs/2602.14612); tên bài: "Event-Grounded Question Answering over Long Audio via Structured Retrieval" | Sinh tăng cường truy hồi cho âm thanh dài |
| 17 | LBR | 01:99 (đã mở rộng "Tinh chỉnh biên học được (LBR)") | Repo: `docs/SYSTEM.md:1735` "Learned Boundary Refinement + rescoring"; docstring `ml/postprocessing/boundary_refine.py:1` "learned boundary refinement and box rescoring" | THESIS-OWN (kiểm trong repo; ADR-0045 không ghi dạng tiếng Anh). LBR gồm cả **chấm lại hộp (rescoring)**. Nếu viết chỉ "Learned Boundary Refinement" thì thiếu nửa phương pháp; nên thêm "(kèm chấm lại hộp)". Không phải thuật ngữ của văn liệu: theo `docs/RELATED_WORK.md:745`, tìm "learned boundary refinement" chỉ ra nguồn cũ không liên quan. | Tinh chỉnh biên học được |
| 18 | PSDS (PSDS-1, PSDS-2) | 01:99 ("PSDS-2" trong bảng C5, **trước** chỗ mở rộng ở 02:35) | "polyphonic sound detection score (PSDS)" (tóm tắt viết thường) | VERIFIED: [Bilen et al., arXiv 1910.08440, ICASSP 2020](https://arxiv.org/abs/1910.08440). Lần dùng đầu ở 01:99 chưa mở rộng. | Điểm phát hiện âm thanh đa âm |
| 19 | F1 / Event-F1 / macro-F1 | 01:99 | Không phải từ viết tắt (độ đo F với β = 1) | NOT AN ACRONYM. Chưa trích nguồn gốc (van Rijsbergen) trong phiên này. | Điểm F1 theo sự kiện |
| 20 | CPU | 01:104 | Central Processing Unit | UNVERIFIED (thuật ngữ tin học chuẩn, chưa mở nguồn) | Bộ xử lý trung tâm |
| 21 | CRNN | 02:11 (mở rộng chỉ bằng tiếng Việt) | "Convolutional Recurrent Neural Network (CRNN)" | VERIFIED: [Çakır et al. 2017, arXiv 1702.06286](https://arxiv.org/abs/1702.06286) (IEEE TASLP, DOI 10.1109/TASLP.2017.2690575) | Mạng nơ-ron tích chập hồi quy |
| 22 | CNN | 02:11 | convolutional neural network ("a variety of convolutional neural networks") | VERIFIED: [PANNs, arXiv 1912.10211](https://arxiv.org/abs/1912.10211) | Mạng nơ-ron tích chập |
| 23 | BiGRU | 02:11 (chưa mở rộng) | GRU = "gated recurrent unit (GRU)"; "Bi" = bidirectional | Một phần VERIFIED: GRU theo [Chung et al. 2014, arXiv 1412.3555](https://arxiv.org/abs/1412.3555). Phần "Bidirectional" chưa trích nguồn (UNVERIFIED về nguồn, nghĩa thì rõ). | Mạng hồi quy có cổng hai chiều |
| 24 | TP / FP / FN | 02:21 (đã giải nghĩa tại chỗ bằng tiếng Việt) | True Positive / False Positive / False Negative | UNVERIFIED (thuật ngữ thống kê chuẩn, chưa mở nguồn) | Phát hiện đúng / báo nhầm / bỏ sót |
| 25 | DCASE | 02:37 (đã mở rộng tại chỗ) | "Detection and Classification of Acoustic Scenes and Events" | VERIFIED: [dcase.community](https://dcase.community/) | Thử thách phát hiện và phân loại cảnh, sự kiện âm thanh |
| 26 | SEBB | 02:43 ("hộp bao sự kiện (SEBB)") | "sound event bounding boxes (SEBBs)" (tên bài viết hoa: "Sound Event Bounding Boxes") | VERIFIED: [Ebbers et al., arXiv 2406.04212, Interspeech 2024](https://arxiv.org/abs/2406.04212) (đọc PDF toàn văn) | Hộp bao sự kiện âm thanh |
| 27 | cSEBB | 02:43 (giải nghĩa: "tìm biên tại điểm xác suất đổi hướng") | Đề mục trong bài: "Change-detection-based SEBBs"; chú thích Hình 3: "Proposed change-detection-based SEBB prediction". Hai biến thể còn lại là tSEBB (threshold-based) và hSEBB ("Hybrid SEBBs") | VERIFIED: cùng PDF arXiv 2406.04212 (Mục 3). "c" = **change-detection-based**. Bài không đặt "cSEBB (change-detection-based SEBB)" trong một ngoặc duy nhất; nghĩa suy từ đề mục và bộ ba t/c/h. Dạng trong bảng hiện có khớp. | Hộp bao sự kiện dựa trên phát hiện điểm thay đổi |
| 28 | AudioSet-Strong / AudioSet Strong | 02:45 ("AudioSet-Strong"), 02:51 ("AudioSet Strong") | Tập nhãn mạnh (theo khung) của AudioSet | NOT AN ACRONYM; chưa trích nguồn gốc (Hershey et al. 2021). **Hai cách viết không thống nhất** giữa 02:45 và 02:51. | Phần nhãn theo thời gian của AudioSet |
| 29 | PSDS1 | 02:43, 02:45, 02:51 | Cùng nghĩa PSDS-1 | Ghi chú nhất quán: thân bài dùng cả "PSDS1" lẫn "PSDS-1" (02:35, 06:*) | — |
| 30 | PANNs | 02:49 (chưa mở rộng) | "pretrained audio neural networks (PANNs)"; tên bài: "PANNs: Large-Scale Pretrained Audio Neural Networks for Audio Pattern Recognition" | VERIFIED: [arXiv 1912.10211](https://arxiv.org/abs/1912.10211) (IEEE/ACM TASLP 2020) | Mạng nơ-ron âm thanh tiền huấn luyện |
| 31 | CNN14 | 02:49 | Mạng CNN 14 lớp của PANNs: "We investigate 6-, 10- and 14-layer CNNs"; bài viết là "CNN14" | VERIFIED: PDF arXiv 1912.10211 (Mục II-A). Là tên mô hình, không cần mở rộng; chỉ cần câu giới thiệu "mạng tích chập 14 lớp". | Mạng tích chập 14 lớp (PANNs) |
| 32 | DESED | 02:51 (chưa mở rộng) | "Domestic Environment Sound Event Detection Dataset" | VERIFIED: [project.inria.fr/desed](https://project.inria.fr/desed/). Bảng ghi thiếu chữ "Dataset"; chấp nhận được, nhưng chữ nguồn có "Dataset". | Bộ dữ liệu SED trong môi trường gia đình |
| 33 | BEATs | 02:51 (chưa mở rộng) | "Bidirectional Encoder representation from Audio Transformers" ("representation" viết thường, số ít) | VERIFIED: [Chen et al., arXiv 2212.09058](https://arxiv.org/abs/2212.09058). Trang arXiv không ghi hội nghị (ICML 2023: UNVERIFIED). **BEATs chưa có trong bảng viết tắt.** | Bộ mã hóa hai chiều học biểu diễn từ Transformer âm thanh |
| 34 | Frame-MobileNet (8 lần) | 02:51 (trích dẫn `[@schmid2025effective]`) | Tác giả gọi là "frame-wise MobileNet (fmn)", với các cỡ fmn04/fmn06/fmn10/fmn20/fmn30, dựa trên MobileNetV3. Repo PretrainedSED gọi là "Customized MobileNet", checkpoint `frame_mn06`, `frame_mn10`, ghi "NEW", không gắn bài báo | VERIFIED: tên "frame-wise MobileNet (fmn)" theo [Morocutti et al., arXiv 2503.11373v2, EUSIPCO 2025](https://arxiv.org/html/2503.11373v2); [repo PretrainedSED](https://github.com/fschmid56/PretrainedSED). **"Frame-MobileNet" không phải tên tác giả dùng.** Tóm tắt bài được trích là [schmid2025effective (arXiv 2409.09546)](https://arxiv.org/abs/2409.09546), và tóm tắt đó **không nhắc MobileNet nào** (xem Gaps). | MobileNet theo khung (frame-wise MobileNet, fmn) |
| 35 | FilterAugment, Mixup | 02:53 | Tên phương pháp | NOT AN ACRONYM (bib `nam2022filteraugment`, `zhang2018mixup`) | Tăng cường dữ liệu |
| 36 | AAC | 02:61 ("mô tả âm thanh tự động (AAC)") | "Automated Audio Captioning" (dùng "Automated", không dùng "Automatic") | VERIFIED: [DCASE 2020 Task 6](https://dcase.community/challenge2020/task-automatic-audio-captioning) ("Automated audio captioning is the task of general audio content description using free text"); [Drossos et al. 2017, arXiv 1706.10006](https://arxiv.org/abs/1706.10006). Cả hai trang đều không viết dạng ngoặc "(AAC)". | Mô tả âm thanh tự động |
| 37 | BGE-M3 | 02:67 (chưa mở rộng) | BGE: "BGE (BAAI General Embedding)", "`bge` is short for `BAAI general embedding`". M3: "Multi-Linguality, Multi-Functionality, Multi-Granularity" (tên bài; model card xếp thứ tự khác). "more than 100 working languages" | VERIFIED: [FlagEmbedding README](https://github.com/FlagOpen/FlagEmbedding); [arXiv 2402.03216](https://arxiv.org/abs/2402.03216) (tên bài "M3-Embedding: …"); [model card BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3). Dạng "Beijing Academy of Artificial Intelligence" cho BAAI: UNVERIFIED (README không ghi). | Mô hình nhúng văn bản đa ngữ, đa chức năng, đa độ dài |
| 38 | llama.cpp | 02:81 | Tên phần mềm | NOT AN ACRONYM (tên dự án ggml-org/llama.cpp) | Phần mềm chạy mô hình ngôn ngữ trên máy |
| 39 | GBNF | 02:81 (chưa mở rộng) | "GBNF (GGML BNF) is a format for defining formal grammars to constrain model outputs in llama.cpp"; "Backus-Naur Form (BNF) is a notation for describing the syntax of formal languages" | VERIFIED: [llama.cpp grammars/README.md](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md). Dạng trong bảng "GGML Backus–Naur Form" khớp. **GGML không có dạng đầy đủ chính thức**: [ggml docs/gguf.md](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md) không mở rộng GGML lẫn GGUF, nên không tự ghép. | Dạng ngữ pháp BNF của GGML |
| 40 | scikit-learn | 02:83 | Tên thư viện | NOT AN ACRONYM | Thư viện học máy Python |
| 41 | KTC | 02:91 ("khoảng tin cậy 95% (KTC 95%)") | Khoảng tin cậy | THESIS-OWN (từ viết tắt tiếng Việt, định nghĩa tại 02:91) | Khoảng tin cậy |
| 42 | Zenodo | 03:7 | Tên kho dữ liệu | NOT AN ACRONYM | Kho lưu trữ dữ liệu mở |
| 43 | CC-BY-NC-SA-4.0 | 03:7 | "Creative Commons Attribution Non Commercial Share Alike 4.0 International" | VERIFIED: trường License của [Zenodo 23097290](https://zenodo.org/records/23097290) và [Zenodo 15346092](https://zenodo.org/records/15346092) | Giấy phép Creative Commons: ghi công, phi thương mại, chia sẻ tương tự 4.0 |
| 44 | MD5 | 03:9 | "The MD5 Message-Digest Algorithm" (tên RFC); "This document describes the MD5 message-digest algorithm." | VERIFIED: [RFC 1321](https://www.rfc-editor.org/rfc/rfc1321). RFC không mở rộng riêng con số "5"; nên viết "thuật toán tóm lược thông điệp MD5". | Mã tóm lược MD5 |
| 45 | WAV | 03:11 | Waveform Audio File Format (dạng thông dụng) | UNVERIFIED | Định dạng tệp âm thanh WAV |
| 46 | D0–D4 | 03:42 (đã định nghĩa "ký hiệu D0 đến D4") | Mã cổng dữ liệu | THESIS-OWN | Cổng kiểm tra dữ liệu 0…4 |
| 47 | SHA-256 | 03:50 (chưa mở rộng) | FIPS 180-4 "Secure Hash Standard (SHS)" quy định "secure hash algorithms - SHA-1, SHA-224, SHA-256, …"; độ dài tóm lược của SHA-256 là 256 bit | VERIFIED: [NIST FIPS 180-4 (PDF)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf); [trang CSRC](https://csrc.nist.gov/pubs/fips/180-4/upd1/final). Dạng trong bảng "Secure Hash Algorithm, 256 bit" khớp ý nguồn. | Hàm băm an toàn SHA-256 |
| 48 | MFCC | 03:56 (chưa mở rộng) | "Mel-Frequency Cepstral Coefficients" | VERIFIED (nguồn thứ cấp có trong bib): [Artuso et al. 2025, PDF FA2025](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf) ("the classic features Mel-Frequency Cepstral Coefficients"). Nguồn gốc Davis & Mermelstein 1980: UNVERIFIED. | Hệ số cepstral thang mel |
| 49 | T1/T2/T3 | 03:62 [bảng `02_leakage_d3_d4.md`] | Tầng kiểm trùng 1–3 | THESIS-OWN (văn bản gọi "Tầng 1/2/3") | Tầng 1…3 |
| 50 | PostgreSQL | 04:7 | Tên hệ quản trị CSDL | NOT AN ACRONYM (theo nghĩa cần mở rộng) | Hệ quản trị cơ sở dữ liệu PostgreSQL |
| 51 | G1–G3 | 04:80 (đã định nghĩa tại chỗ) | Ba ràng buộc bám sát | THESIS-OWN | Ràng buộc 1…3 |
| 52 | Qwen3.5-9B | 04:89 | "Qwen3.5-9B", "Number of Parameters: 9B", giấy phép apache-2.0, trích dẫn ghi 02/2026. "Qwen" không được mở rộng ở thẻ mô hình; repo QwenLM viết "Qwen (通义千问) … proposed by Alibaba Cloud" | NOT AN ACRONYM. VERIFIED (tên mô hình có tồn tại): [HF Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B); [github.com/QwenLM/Qwen](https://github.com/QwenLM/Qwen). Không có nguồn nào ghi "Qwen" là viết tắt của "Tongyi Qianwen"; chỉ ghi tên Trung "通义千问". | Mô hình ngôn ngữ 9 tỉ tham số của nhóm Qwen (Alibaba Cloud) |
| 53 | pgvector | 04:107 | Tên phần mở rộng | NOT AN ACRONYM | Phần mở rộng vector cho PostgreSQL |
| 54 | Python | 04:118 | Tên ngôn ngữ | NOT AN ACRONYM | — |
| 55 | JSON | 04:131 (chưa mở rộng) | "JavaScript Object Notation (JSON) is a lightweight, text-based, language-independent data interchange format." | VERIFIED: [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) | Định dạng dữ liệu có cấu trúc JSON |
| 56 | F1–F5, N1–N3 | 05:17–24 [bảng yêu cầu] | Mã yêu cầu chức năng / phi chức năng | THESIS-OWN. **Mã "F1" trùng chữ với điểm F1** (cùng chương, cùng bảng có "Event-F1"). | Yêu cầu chức năng 1…5; phi chức năng 1…3 |
| 57 | FLAC | 05:17 | "Free Lossless Audio Codec" | VERIFIED: [xiph.org/flac](https://xiph.org/flac/) | Mã hóa âm thanh không mất dữ liệu |
| 58 | OGG | 05:17 | Ogg là tên định dạng chứa của Xiph | UNVERIFIED (thường được coi là không phải từ viết tắt; chưa mở nguồn) | Định dạng Ogg |
| 59 | MP3 | 05:17 | MPEG-1/MPEG-2 Audio Layer III (dạng thông dụng) | UNVERIFIED | Định dạng âm thanh nén MP3 |
| 60 | MB | 05:17 | megabyte | UNVERIFIED (đơn vị chuẩn) | Mê-ga-bai |
| 61 | Docker Compose | 05:22 | Tên công cụ | NOT AN ACRONYM | Công cụ chạy nhiều container |
| 62 | ADR | 05:38 [bảng `f15_tech_stack.md`, tiêu đề cột]; 90:44; bảng `f08_freeze` | adr.github.io: "An Architectural Decision Record (ADR) captures a single AD and its rationale". Bài blog 2011 của Michael Nygard có tên "Documenting Architecture Decisions" | VERIFIED: [adr.github.io](https://adr.github.io/). **Bảng ghi "Architecture Decision Record", còn adr.github.io chỉ dùng "Architectural Decision Record".** Cả hai đều lưu hành (tên bài Nygard dùng "Architecture"); nếu dẫn adr.github.io thì nên đổi thành "Architectural". | Bản ghi quyết định kiến trúc |
| 63 | PyTorch, sed_eval, psds_eval, pytest, ruff, psycopg, FastAPI, Uvicorn, React, TypeScript, Vite, TanStack Query, Vitest, Playwright | 05:38 [bảng `f15_tech_stack.md`] | Tên thư viện, công cụ | NOT AN ACRONYM (tên riêng; chưa mở trang chính thức từng cái) | Giữ nguyên tên |
| 64 | CI | 05:38 [bảng `f15_tech_stack.md`: "kiểm tra mã trong CI"] | Continuous Integration (repo có `.github/workflows/ci.yml`) | UNVERIFIED (chưa mở nguồn). **Trùng chữ với "CI" = confidence interval**: `display.yaml` đổi "CI 95%" thành "KTC 95%", nhưng chữ "CI" trong f15 vẫn còn và mang nghĩa khác. | Tích hợp liên tục |
| 65 | GGUF / Q4_K_M | 05:38 [f15: `Qwen_Qwen3.5-9B-Q4_K_M.gguf`] | "GGUF is a file format for storing models for inference with GGML…"; không mở rộng | NOT AN ACRONYM (không có dạng đầy đủ chính thức): [ggml docs/gguf.md](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md). Q4_K_M là tên kiểu lượng tử hóa, tài liệu không giải nghĩa. | Tệp trọng số GGUF, lượng tử hóa 4 bit |
| 66 | API | 05:38 [f15]; thân bài 05:44 | Application Programming Interface | UNVERIFIED (thuật ngữ chuẩn) | Giao diện lập trình ứng dụng |
| 67 | HTTP | 05:38 [f15]; thân bài 05:48 | "The Hypertext Transfer Protocol (HTTP) is a stateless application-level protocol…" | VERIFIED: [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110). **HTTP chưa có trong bảng viết tắt.** | Giao thức truyền siêu văn bản |
| 68 | GPU | 05:44 | Graphics Processing Unit | UNVERIFIED (thuật ngữ chuẩn) | Bộ xử lý đồ họa |
| 69 | TRAIN | 05:126 [bảng `f13_latency.md`, tiêu đề "bản ghi TRAIN"] | Tên tập trong mã (train split), không phải từ viết tắt | NOT AN ACRONYM. Tiêu đề f13 chưa được `display.yaml` đổi (chỉ có quy tắc cho "CPU, 10 bản ghi TRAIN"). | Tập huấn luyện |
| 70 | B0, V2, V3, f2 | 06:16 [bảng `f00_key_results.md`] và Phụ lục B | Mã hệ thống nội bộ | THESIS-OWN (bảng tra ở 90:33–42). Sau khi đổi tên, còn sót trong `f08_freeze`, `f09_per_class`, `m05_f2_per_class` | Hệ cơ sở, LBR chính, LBR ứng dụng, hệ mốc |
| 71 | ECE | 06:20 ("sai số hiệu chuẩn ECE") | "Expected Calibration Error (Naeini et al., 2015) – or ECE" | VERIFIED: [Guo et al. 2017, ICML, arXiv 1706.04599](https://arxiv.org/abs/1706.04599) (đọc PDF, Mục 2). Bài Naeini et al. 2015: không mở được (PMC và AAAI chặn bot), UNVERIFIED. | Sai số hiệu chuẩn kỳ vọng |
| 72 | CLAP | 06:34 [bảng so sánh, hàng Artuso]; 06:37 | Artuso et al.: "the Contrastive Language-Audio Pretraining (CLAP) [9, 10] model". [9] = Elizalde, Deshmukh, Ismail, Wang, "CLAP Learning Audio Concepts from Natural Language Supervision", ICASSP 2023 (tức **CLAP của Microsoft**); [10] = Elizalde et al. arXiv 2309.05767. Bộ mã hóa âm thanh là HTS-AT. Bài Elizalde viết: "Contrastive Language-Audio Pretraining (CLAP)" | VERIFIED: [PDF Artuso FA2025](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf); [Elizalde et al., arXiv 2206.04769](https://arxiv.org/abs/2206.04769). Hàng CLAP thứ hai (06:37, dự án GitHub goyumsamuditha): chưa kiểm là CLAP nào (UNVERIFIED). | Tiền huấn luyện đối sánh âm thanh–văn bản |
| 73 | GitHub, README | 06:36, 06:39 | Tên nền tảng; README là tên tệp | NOT AN ACRONYM | — |
| 74 | MAESTRO (Real) | 06:132 (chưa mở rộng) | "MAESTRO Real - Multi-Annotator Estimated Strong Labels" (tác giả Martín-Morató, Harju, Mesaros) | VERIFIED: [Zenodo 7244360](https://zenodo.org/records/7244360). Chữ in hoa trong "MAESTRO" ghép từ "Multi-Annotator Estimated STROng labels" (cách viết hoa này chỉ thấy trong kết quả tìm kiếm, chưa đọc nguồn; phần tên bản ghi đã VERIFIED). | Bộ dữ liệu nhãn mạnh ước lượng từ nhiều người gán nhãn |
| 75 | BLEU (BLEU-4) | 06:153 (chưa mở rộng) | Chú thích chân trang: "So we call our method the bilingual evaluation understudy, BLEU." | VERIFIED: [Papineni et al. 2002, ACL, PDF](https://aclanthology.org/P02-1040.pdf). Nguồn viết thường; viết hoa chữ đầu như trong bảng là chấp nhận được. | Chỉ số trùng n-gram so với câu tham chiếu |
| 76 | CIDEr | 06:153 (chưa mở rộng) | "CIDEr: Consensus-based Image Description Evaluation" | VERIFIED: [Vedantam et al., arXiv 1411.5726](https://arxiv.org/abs/1411.5726) | Chỉ số đồng thuận n-gram |
| 77 | BRACE | 06:167 | "BRACE: A Benchmark for Robust Audio Caption Quality Evaluation"; tóm tắt: "we introduce BRACE, a new benchmark…"; **không có dạng đầy đủ** | NOT AN ACRONYM (nguồn không mở rộng): [arXiv 2512.10403](https://arxiv.org/abs/2512.10403). Không được viết "BRACE (Benchmark for Robust Audio Caption Evaluation)". | Bộ đánh giá chất lượng mô tả âm thanh |
| 78 | L2 | 06:217 [tiêu đề bảng `10_parser_l2.md`: "Bảng đánh giá parser L2"] | Mã công việc nội bộ (PLAN) | THESIS-OWN, còn sót (tiêu đề bảng chưa được đổi tên) | Bộ phân tích câu hỏi |
| 79 | T2a, T2b, S13, S11, C-v2, OOF, ADR-00xx | 90:37–50 [Phụ lục B, bảng `f08_freeze`] | Mã nội bộ. "OOF" = out-of-fold (DANH MỤC THUẬT NGỮ, 00_phan_dau: "Dự đoán ngoài mẫu — out-of-fold prediction") | THESIS-OWN. "OOF" còn ở 3 dòng `f08_freeze.md` (18, 19, 26) mà không có trong bảng viết tắt | Dự đoán ngoài mẫu |
| 80 | TS/TSX | 90:76 [bảng `f12_workload.md`]; 90:165 | TypeScript / TypeScript JSX (tệp `.ts`/`.tsx`) | UNVERIFIED | Mã TypeScript của giao diện |
| 81 | AP (macro AP) | 90:78 (chưa mở rộng) | "Average precision (AP)"; "mean average precision (mAP)" | VERIFIED: PDF [PANNs arXiv 1912.10211](https://arxiv.org/abs/1912.10211) (Mục IV). **AP chưa có trong bảng viết tắt.** Chữ "mAP" chỉ có trong tên tệp `Cnn14_mAP=0.431.pth` (bảng f08). | Độ chính xác trung bình |
| 82 | CV, SD, CI | 90:90 [tiêu đề bảng `06_s13_ranking_test.md`] | cross-validation, standard deviation, confidence interval | Có thể đã mất sau khi lọc `cols=` và đổi tên: quy tắc đầu của `display.yaml` thay đúng tiêu đề (đã bỏ cột "Model"). Cần kiểm bản DOCX đã dựng. | — |
| 83 | H1–H3 | 90:102 [bảng `f06_psds.md`] | Mã giả thuyết PSDS nội bộ | THESIS-OWN, còn sót | Giả thuyết 1…3 |
| 84 | GET, POST | 90:110 [bảng `f16_api.md`] | Phương thức HTTP (RFC 9110) | NOT AN ACRONYM | — |
| 85 | EN / VI | 90:110 [f16]; 90:161 | Mã ngôn ngữ tiếng Anh / tiếng Việt | UNVERIFIED (mã ISO 639-1, chưa mở nguồn) | Tiếng Anh / tiếng Việt |
| 86 | TT | 90:138 [tiêu đề bảng phân công] | Thứ tự | THESIS-OWN (quy ước văn bản tiếng Việt) | Thứ tự |
| 87 | Claude, Anthropic, Codex, OpenAI | 90:152 | Tên sản phẩm và công ty | NOT AN ACRONYM | — |
| 88 | GVHD | 90:171 [nhật ký] | Giáo viên hướng dẫn (00_phan_dau: "NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN") | THESIS-OWN (quy ước tiếng Việt) | Giáo viên hướng dẫn |

### Inferences
- DataSEC/DataSED nên được giới thiệu lần đầu (01:11) như tên riêng kèm tên chính thức, ví dụ "DataSEC (Dataset for Sound Event Classification of environmental noise)" và "DataSED (Dataset for Sound Event Detection of environmental noise)". Hai tên này lấy nguyên văn từ tiêu đề bản ghi Zenodo, nên an toàn hơn mọi dạng "Data + SEC" tự ghép.
- "Frame-MobileNet" là tên tự đặt của nhóm. Nên đổi thành "frame-wise MobileNet (fmn)" và trích Morocutti et al. 2025 (arXiv 2503.11373). Cách khác là giữ tên nhưng ghi rõ checkpoint `frame_mn10` của repo PretrainedSED. Hiện câu 02:51 trích `schmid2025effective` cho mô hình này, trong khi tóm tắt bài đó không nói tới MobileNet.
- Nhiều từ được dùng ở Ch.1 trước chỗ mở rộng ở Ch.2: PSDS (01:99 so với 02:35), nDCG (01:75, không mở rộng ở đâu), SQL (01:98). Nếu quy tắc là "mở rộng ở lần đầu từ Ch.1" thì cần thêm ngoặc ở các dòng Ch.1 này, kể cả trong các ô bảng đóng góp và RQ.

### Gaps
- Chưa mở được bài Naeini et al. 2015 (ECE gốc; PMC và AAAI chặn bot); chỉ có trích dẫn lại trong Guo et al. 2017.
- Chưa mở nguồn chuẩn cho các thuật ngữ tin học chung: SQL, API, CPU, GPU, CI, MB, WAV, OGG, MP3, TS/TSX, EN/VI, TP/FP/FN, và tên bộ BTNMT. Tất cả đã đánh dấu UNVERIFIED.
- Chưa kiểm hàng CLAP thứ hai (06:37, dự án GitHub) dùng CLAP nào.
- Chưa mở được bài *Scientific Data* trực tiếp: nature.com chuyển hướng sang trang đăng nhập. Phần trích DataSEC/DataSED lấy từ tóm tắt qua Europe PMC (PMC12572321) và từ bản ghi Zenodo.
- BEATs: arXiv không ghi hội nghị, nên "ICML 2023" chưa kiểm.
- Bản tóm tắt arXiv 2409.09546 không nói tới MobileNet. Chưa đọc toàn văn bản v2, nên chưa loại trừ được khả năng toàn văn có nhắc.

## Từ viết tắt có trong bảng (00_phan_dau.md dòng 75–113) nhưng không xuất hiện trong thân bài

### Takeaway
Có năm mục trong bảng không có lần dùng nào trong Ch.1–7 và phụ lục, kể cả trong bảng chèn sau khi đổi tên: **HNSW, LLM, RRF, TCVN** (0 lần), và **SEBB** chỉ xuất hiện đúng một lần (02:43). Dạng đầy đủ của HNSW, RRF đều đúng nguồn, nhưng vì không dùng nên có thể bỏ khỏi bảng.

### Cited Findings
- HNSW: 0 lần trong thân bài. Dạng trong bảng khớp nguồn: tên bài "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs"; tóm tắt viết "(Hierarchical NSW, HNSW)" — [Malkov & Yashunin, arXiv 1603.09320](https://arxiv.org/abs/1603.09320)
- RRF: 0 lần. Dạng khớp nguồn: "Reciprocal Rank Fusion (RRF), a simple method for combining the document rankings from multiple IR systems" — [Cormack, Clarke, Büttcher, SIGIR 2009 (PDF)](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- LLM: 0 lần. Thân bài chỉ viết bằng tiếng Việt "mô hình ngôn ngữ lớn" (90:152); `display.yaml` cũng xóa "LLM" khỏi nhãn hình ("LLM ràng buộc" → "Ràng buộc"). Dạng "Large Language Model" chưa trích nguồn trong phiên này (UNVERIFIED, thuật ngữ thông dụng).
- TCVN: 0 lần trong thân bài; chưa kiểm nguồn cho "Tiêu chuẩn quốc gia".
- Các mục còn lại trong bảng đều có trong thân bài: AAC, ADR, API, BGE-M3, BiGRU, BLEU (dạng BLEU-4), CIDEr, CLAP, CNN, CPU, CRNN, cSEBB, dBA, DCASE, DESED, ECE, FN/FP/TP, GBNF, GPU, JSON, KTC, LBR, MFCC, nDCG, PANNs, PSDS, QCVN, RAG, RQ, SED, SHA-256, SQL.

### Inferences
- Nên bỏ HNSW, RRF, LLM, TCVN khỏi bảng, hoặc dùng chúng trong thân bài; giữ trong bảng một từ không xuất hiện dễ bị hội đồng hỏi.

### Gaps
- Chưa kiểm bản DOCX đã dựng. Hình (PNG) có thể còn chữ "LLM" hay "CI" nếu `figure_names` không phủ hết; chưa đọc chữ trong hình.

## Từ viết tắt dùng trong thân bài nhưng thiếu trong bảng, và các mục bảng cần sửa

### Takeaway
Bảng thiếu khoảng 20 từ viết tắt hoặc tên viết hoa có trong thân bài. Quan trọng nhất là: **BEATs, CNN14, HTTP, MD5, AP, OOF, CI (tích hợp liên tục), ECHO, TAC, LA-RAG, BRACE (tên), MAESTRO, BNNMT/BTNMT, WAV/FLAC/OGG/MP3, CC-BY-NC-SA, GVHD, TT**. Trong các mục đang có, hai mục nên sửa chữ: ADR (Architectural) và nDCG (nguồn gốc dùng "cumulated"). Hai mục nên bổ sung: DESED (thêm "Dataset") và LBR (thêm "box rescoring"). Ngoài ra, đề xuất "DataSEC (Data Sound Event Classification)" không được dùng.

### Cited Findings
- **ADR**: adr.github.io viết "Architectural Decision Record (ADR)", còn bảng ghi "Architecture Decision Record" — [adr.github.io](https://adr.github.io/)
- **nDCG**: bài gốc gọi "cumulated gain"; "nDCG" là vector DCG chuẩn hóa — [Järvelin & Kekäläinen 2002](https://doi.org/10.1145/582415.582418). Dạng "Cumulative" trong bảng là biến thể thông dụng, không sai về nghĩa.
- **DESED**: nguồn viết "Domestic Environment Sound Event Detection Dataset" — [project.inria.fr/desed](https://project.inria.fr/desed/)
- **TAC**: là mô hình "Timestamped Audio Captioner (TAC)", tên bài dùng "Timestamped Audio Captioning" — [arXiv 2602.15766](https://arxiv.org/abs/2602.15766)
- **PANNs**: chữ trong bài viết thường "pretrained audio neural networks (PANNs)"; dạng trong bảng khớp — [arXiv 1912.10211](https://arxiv.org/abs/1912.10211)
- **PSDS**: tóm tắt viết thường "polyphonic sound detection score (PSDS)"; dạng trong bảng khớp — [arXiv 1910.08440](https://arxiv.org/abs/1910.08440)
- **CLAP**: nguồn mà khóa luận so sánh (Artuso 2025) dùng CLAP của Elizalde et al. (Microsoft), không phải LAION-CLAP. Dạng "Contrastive Language-Audio Pretraining" khớp cả hai bài — [PDF Artuso](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf), [arXiv 2206.04769](https://arxiv.org/abs/2206.04769)
- **BGE-M3**: dạng "BAAI General Embedding, Multi-Linguality, Multi-Functionality, Multi-Granularity" trong bảng khớp nguồn — [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding), [arXiv 2402.03216](https://arxiv.org/abs/2402.03216)
- **GBNF**: dạng "GGML Backus–Naur Form" khớp "GBNF (GGML BNF)" — [llama.cpp grammars README](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
- **cSEBB**: dạng "change-detection-based Sound Event Bounding Boxes" khớp đề mục "Change-detection-based SEBBs" — [arXiv 2406.04212](https://arxiv.org/abs/2406.04212)
- **SHA-256**: khớp FIPS 180-4 ("secure hash algorithms - … SHA-256") — [NIST FIPS 180-4](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- **BLEU**: "the bilingual evaluation understudy, BLEU" — [ACL P02-1040](https://aclanthology.org/P02-1040.pdf); **CIDEr** khớp — [arXiv 1411.5726](https://arxiv.org/abs/1411.5726); **CRNN** khớp — [arXiv 1702.06286](https://arxiv.org/abs/1702.06286); **AAC** "Automated Audio Captioning" khớp — [DCASE 2020 Task 6](https://dcase.community/challenge2020/task-automatic-audio-captioning); **DCASE** khớp — [dcase.community](https://dcase.community/); **ECE** khớp — [Guo et al. 2017](https://arxiv.org/abs/1706.04599); **QCVN** "Quy chuẩn kỹ thuật quốc gia" khớp bìa văn bản — [PDF QCVN 26:2025/BNNMT](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf)

### Inferences
- **Cần thêm vào bảng, với dạng đầy đủ đã kiểm:**
  - BEATs (Bidirectional Encoder representation from Audio Transformers)
  - ECHO (Evaluation of Caption Hallucination in audiO)
  - TAC (Timestamped Audio Captioner)
  - LA-RAG (Long Audio Retrieval-Augmented Generation)
  - HTTP (Hypertext Transfer Protocol)
  - MD5 (MD5 Message-Digest Algorithm)
  - AP (Average Precision)
  - FLAC (Free Lossless Audio Codec)
  - JSON: đã có
  - MAESTRO Real (Multi-Annotator Estimated Strong Labels)
  - CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International)
  - BNNMT (Bộ Nông nghiệp và Môi trường)
- **Cần thêm, là từ của chính khóa luận:**
  - OOF (out-of-fold, "dự đoán ngoài mẫu")
  - GVHD (giáo viên hướng dẫn)
  - TT (thứ tự)
- **Cần thêm nhưng dạng đầy đủ còn UNVERIFIED:** CI (Continuous Integration), WAV, MP3, OGG, MB, TS/TSX, BTNMT.
- **Tên riêng chỉ cần một câu giới thiệu, không ghép dạng đầy đủ:**
  - BRACE
  - Qwen3.5-9B: ghi "của nhóm Qwen, Alibaba Cloud".
  - GGUF/GGML: không có dạng đầy đủ chính thức.
  - CNN14: "mạng tích chập 14 lớp của PANNs".
  - Frame-MobileNet / fmn
  - AudioSet, AudioSet Strong
  - FilterAugment, mixup
  - llama.cpp, pgvector, PostgreSQL
  - DataSEC, DataSED: kèm tên Zenodo.
- **Nên sửa trong bảng:**
  - ADR → "Architectural Decision Record" (theo adr.github.io).
  - DESED → thêm "Dataset".
  - LBR → "Learned Boundary Refinement (kèm chấm lại hộp)", theo `docs/SYSTEM.md:1735`.
  - nDCG: tùy chọn ghi "normalized Discounted Cumulated Gain" theo bài gốc.
- **Nhất quán chính tả trong thân bài:**
  - "AudioSet-Strong" (02:45) với "AudioSet Strong" (02:51).
  - "PSDS1" (02:43–51) với "PSDS-1" (02:35, Ch.6).
  - Mã yêu cầu "F1" (05:17) trùng chữ với điểm F1.
  - "CI" trong f15 (tích hợp liên tục) khác "CI" mà `display.yaml` đổi thành KTC.
- **Mã nội bộ còn sót sau khi đổi tên** (nếu mục tiêu là bỏ mã khỏi thân bài):
  - "parser L2" (tiêu đề bảng 06:217).
  - "TRAIN" (tiêu đề f13).
  - H1–H3 (f06_psds).
  - S11, S13, C-v2, OOF, B0, f2, V2, V3, ADR-00xx trong `f08_freeze` (Phụ lục B). Phụ lục B có bảng tra nên mức chấp nhận ở đây cao hơn.

### Gaps
- Chưa dựng lại DOCX để kiểm chữ cuối cùng sau `display.yaml`. Việc quét ở đây áp `names` lên bảng chèn nhưng không mô phỏng `cols=`/`keep=`.
- Phần front matter (Tóm tắt/Abstract) nằm ngoài phạm vi "từ Ch.1"; ở đó QCVN, SED, RAG, LBR, PSDS-2, KTC đã xuất hiện trước Ch.1.
