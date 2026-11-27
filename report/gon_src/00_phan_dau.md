@@TITLE:ABSTRACT@@

**Title:** Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval

Noise monitoring needs to know which sound sources occur, when, and for how long; Vietnam's noise regulation QCVN 26:2025/BNNMT makes this a practical need. This thesis builds a four-part system: sound event detection (SED) with start and end times, captions written only from the detected events, an event store in PostgreSQL with a vector index, and question answering with Retrieval-Augmented Generation (RAG) that cites recordings and time spans as evidence. It uses two public datasets, DataSEC (5,048 clips) and DataSED (717 recordings, 21 classes). A three-tier duplicate check found recordings shared by the two datasets, so 11 clips were removed and all data splits were frozen before training.

The main finding is that caption and answer quality depend mostly on SED. The constrained caption generator adds no sound source outside the detected events, and the hard filter returns only recordings whose stored events satisfy the query; useful improvements therefore lie in SED and in event coverage at retrieval time. Extra pre-training on DataSEC did not help (difference −0.003, 95% CI [−0.025, +0.020]). A learned boundary refinement stage (LBR) raised test event-based micro-F1 from 0.181 to 0.297 (+0.116 [+0.074, +0.159]), at the cost of lower segment-F1 and PSDS-2. Hybrid retrieval scored lower than semantic-only ranking on three of four event stores, while a backfill mode beat both on all four. The web application runs locally with a median of 3.9 s per recording. Future work: field recordings in Vietnam and a stronger detector.

**Keywords:** sound event detection, environmental noise, grounded captioning, hallucination, retrieval-augmented generation, transfer learning, data leakage.

@@PAGEBREAK@@

@@TITLE:TÓM TẮT@@

**Tên đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

Giám sát tiếng ồn cần biết nguồn âm nào xuất hiện, lúc nào và kéo dài bao lâu. Quy chuẩn QCVN 26:2025/BNNMT về tiếng ồn cho thấy nhu cầu này ở Việt Nam. Khóa luận xây dựng một hệ thống gồm bốn phần: phát hiện sự kiện âm thanh (SED) kèm thời điểm bắt đầu và kết thúc; sinh mô tả chỉ từ các sự kiện đã phát hiện; lưu sự kiện vào kho PostgreSQL có chỉ mục vector; và trả lời câu hỏi bằng sinh tăng cường truy hồi (RAG), có trích bản ghi và khoảng thời gian làm bằng chứng. Dữ liệu là DataSEC (5.048 đoạn) và DataSED (717 bản ghi, 21 lớp). Kiểm tra trùng lặp ba tầng cho thấy hai bộ có chung bản ghi gốc, nên 11 đoạn bị loại và các tập dữ liệu được khóa trước khi huấn luyện.

Kết quả chính là độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào bước SED. Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện, và bộ lọc cứng chỉ trả bản ghi có sự kiện đã lưu thỏa điều kiện; vì vậy cải tiến có tác dụng nằm ở SED và ở độ phủ sự kiện khi truy hồi. Huấn luyện thêm trên DataSEC không giúp (hiệu −0,003, KTC 95% [−0,025; +0,020]). Bước tinh chỉnh biên học được (LBR) nâng event-F1 micro trên tập kiểm tra từ 0,181 lên 0,297 (hiệu +0,116 [+0,074; +0,159]), đổi lại F1 theo đoạn và PSDS-2 thấp hơn. Truy hồi kết hợp thấp hơn truy hồi chỉ theo ngữ nghĩa ở ba trên bốn kho sự kiện, còn chế độ bổ sung cao hơn cả hai ở cả bốn kho. Ứng dụng web chạy trên máy cá nhân, trung vị 3,9 giây cho mỗi bản ghi. Hướng phát triển: thử trên bản ghi thu tại Việt Nam và cải thiện bộ phát hiện.

**Từ khóa:** phát hiện sự kiện âm thanh, tiếng ồn môi trường, mô tả có căn cứ, ảo giác, sinh tăng cường truy hồi, học chuyển giao, rò rỉ dữ liệu.

@@PAGEBREAK@@

@@TITLE:LỜI CẢM ƠN@@

Nhóm xin gửi lời cảm ơn chân thành đến TS. Huỳnh Công Bằng, người đã hướng dẫn, góp ý và định hướng cho nhóm trong suốt quá trình thực hiện khóa luận.

Nhóm cảm ơn quý thầy cô Khoa Công nghệ Thông tin, Trường Đại học Công nghiệp Thành phố Hồ Chí Minh đã truyền đạt kiến thức nền tảng để nhóm có thể thực hiện đề tài này.

Nhóm cũng cảm ơn các tác giả của hai bộ dữ liệu DataSEC và DataSED đã công bố dữ liệu mở, cùng cộng đồng nghiên cứu âm thanh đã chia sẻ mã nguồn và mô hình tiền huấn luyện mà nhóm sử dụng.

Cuối cùng, nhóm cảm ơn gia đình và bạn bè đã luôn động viên trong thời gian qua. Do thời gian có hạn, khóa luận khó tránh khỏi thiếu sót; nhóm rất mong nhận được góp ý của quý thầy cô để hoàn thiện khóa luận.

@@PAGEBREAK@@

@@TITLE:NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN@@

@@REVIEWPAGE@@

@@PAGEBREAK@@

@@TITLE:NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 1@@

@@REVIEWPAGE@@

@@PAGEBREAK@@

@@TITLE:NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 2@@

@@REVIEWPAGE@@

@@PAGEBREAK@@

@@TITLE:MỤC LỤC@@

@@TOC@@

@@PAGEBREAK@@

@@HEADING1N:DANH MỤC HÌNH ẢNH@@

@@TOF:Hình@@

@@PAGEBREAK@@

@@HEADING1N:DANH MỤC BẢNG BIỂU@@

@@TOF:Bảng@@

@@PAGEBREAK@@

@@HEADING1N:DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT@@

| Từ viết tắt | Từ đầy đủ | Nghĩa |
|---|---|---|
| AAC | Automated Audio Captioning | Mô tả âm thanh tự động |
| ADR | Architecture Decision Record | Bản ghi quyết định thiết kế (Phụ lục B) |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| BGE-M3 | BAAI General Embedding, Multi-Linguality, Multi-Functionality, Multi-Granularity | Mô hình nhúng văn bản đa ngữ dùng cho truy hồi |
| BiGRU | Bidirectional Gated Recurrent Unit | Mạng hồi quy có cổng hai chiều |
| BLEU | Bilingual Evaluation Understudy | Chỉ số trùng n-gram giữa câu sinh và câu tham chiếu |
| CIDEr | Consensus-based Image Description Evaluation | Chỉ số đồng thuận n-gram có trọng số TF-IDF |
| CLAP | Contrastive Language-Audio Pretraining | Tiền huấn luyện đối sánh âm thanh và văn bản |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CPU | Central Processing Unit | Bộ xử lý trung tâm |
| CRNN | Convolutional Recurrent Neural Network | Mạng nơ-ron tích chập hồi quy |
| cSEBB | change-detection-based Sound Event Bounding Boxes | Cách tách hộp sự kiện bằng điểm đổi hướng của xác suất |
| dBA | A-weighted decibel | Mức áp suất âm theo đặc tuyến A |
| DCASE | Detection and Classification of Acoustic Scenes and Events | Chuỗi thử thách phát hiện và phân loại cảnh, sự kiện âm thanh |
| DESED | Domestic Environment Sound Event Detection | Bộ dữ liệu SED trong nhà của DCASE |
| ECE | Expected Calibration Error | Sai số hiệu chuẩn kỳ vọng |
| FN, FP, TP | False Negative, False Positive, True Positive | Bỏ sót, báo nhầm, phát hiện đúng |
| GBNF | GGML Backus–Naur Form | Cú pháp ngữ pháp dùng để ràng buộc đầu ra của llama.cpp |
| GPU | Graphics Processing Unit | Bộ xử lý đồ họa |
| HNSW | Hierarchical Navigable Small World | Chỉ mục đồ thị cho tìm kiếm vector gần đúng |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc |
| KTC | Khoảng tin cậy | Khoảng tin cậy bootstrap 95% |
| LBR | Learned Boundary Refinement | Tinh chỉnh biên học được (Chương 4) |
| LLM | Large Language Model | Mô hình ngôn ngữ lớn |
| MFCC | Mel-Frequency Cepstral Coefficients | Hệ số cepstral thang mel |
| nDCG | normalized Discounted Cumulative Gain | Lợi ích tích lũy chiết khấu chuẩn hóa |
| PANNs | Pretrained Audio Neural Networks | Mạng nơ-ron âm thanh tiền huấn luyện |
| PSDS | Polyphonic Sound Detection Score | Điểm phát hiện âm thanh đa âm trên dải ngưỡng |
| QCVN | Quy chuẩn kỹ thuật quốc gia | Quy chuẩn kỹ thuật quốc gia Việt Nam |
| RAG | Retrieval-Augmented Generation | Sinh tăng cường truy hồi |
| RQ | Research Question | Câu hỏi nghiên cứu |
| RRF | Reciprocal Rank Fusion | Gộp xếp hạng theo hạng nghịch đảo |
| SEBB | Sound Event Bounding Boxes | Hộp bao sự kiện âm thanh |
| SED | Sound Event Detection | Phát hiện sự kiện âm thanh |
| SHA-256 | Secure Hash Algorithm, 256 bit | Hàm băm dùng để khóa dữ liệu |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |
| TCVN | Tiêu chuẩn quốc gia | Tiêu chuẩn quốc gia Việt Nam |

@@PAGEBREAK@@

@@HEADING1N:DANH MỤC THUẬT NGỮ@@

Mỗi khái niệm trong báo cáo chỉ dùng một tên. Bảng dưới nêu tên đó, thuật ngữ tiếng Anh tương ứng và nghĩa ngắn gọn.

@@COLWIDTHS:24,24,52@@

| Tên trong báo cáo | Tiếng Anh | Nghĩa |
|---|---|---|
| Tập huấn luyện, tập phát triển, tập kiểm tra | train, dev, test | Tập để học mô hình; tập để chọn cấu hình; tập chỉ dùng để đo cấu hình đã chọn |
| Dự đoán ngoài mẫu | out-of-fold prediction | Dự đoán cho một bản ghi bởi mô hình không được học trên bản ghi đó |
| Kiểm chứng chéo, fold | cross-validation, fold | Chia dữ liệu thành K phần (fold), lần lượt giữ một phần để kiểm |
| Gộp mô hình | ensemble | Lấy trung bình xác suất của nhiều mô hình |
| Seed | random seed | Giá trị khởi tạo ngẫu nhiên; chạy nhiều seed để đo độ dao động |
| Dung sai | collar | Độ lệch thời gian tối đa để một sự kiện dự đoán được tính là khớp |
| Event-F1 | event-based F1 | F1 tính theo từng sự kiện, có dung sai 0,2 s (Chương 2) |
| F1 theo đoạn | segment-based F1 | F1 tính theo từng đoạn 1 s |
| Hệ mốc | (hệ f2) | Hệ SED được khóa ở vòng chọn trước, giữ làm mốc so sánh |
| Hệ cơ sở | (hệ B0) | Hệ SED cuối cùng trước khi thêm LBR |
| LBR chính | (LBR V2) | Hệ cơ sở cộng LBR, cấu hình tối đa event-F1; là số chính |
| LBR ứng dụng | (LBR V3) | Hệ cơ sở cộng LBR, cấu hình ưu tiên phát hiện; dùng trong demo |
| Theo mẫu, tự do, ràng buộc, ràng buộc + phủ | template, unconstrained, constrained, constrained-cover | Bốn cách sinh mô tả (Chương 4) |
| Chỉ lọc, chỉ ngữ nghĩa, kết hợp, bổ sung | structured_only, vector_only, hybrid, backfill | Bốn chế độ truy hồi (Chương 4) |
| Ảo giác, bỏ sót | hallucination, omission | Nhắc nguồn âm không có trong danh sách sự kiện; không nhắc lớp có trong danh sách |
| Rào đón | hedge | Nhãn "độ tin cậy thấp" gắn cho lớp có điểm thấp |
| Độ đúng bộ lọc | filter exactness | Tỷ lệ kết quả trả về thỏa mọi điều kiện của câu hỏi |

@@SECTION:front@@
