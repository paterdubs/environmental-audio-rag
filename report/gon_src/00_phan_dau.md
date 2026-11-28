@@TITLE:ABSTRACT@@

**Title:** Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval

Noise monitoring needs to know which sound sources occur, when, and for how long; Vietnam's national technical regulation on noise (QCVN 26:2025/BNNMT) makes this a practical need. This thesis builds a four-part system: sound event detection (SED) with start and end times, captions written only from the detected events, an event store in PostgreSQL with a vector index, and question answering with Retrieval-Augmented Generation (RAG) that cites recordings and time spans as evidence. It uses two public datasets, DataSEC (5,048 clips) and DataSED (717 recordings, 21 classes). A three-tier duplicate check found recordings shared by the two datasets, so 11 clips were removed and all data splits were frozen before training.

The main finding is that caption and answer quality depend mostly on SED, and specifically on event coverage, the share of true events that are detected. The constrained caption generator adds no sound source outside the detected events, and the hard filter returns only recordings whose stored events satisfy the query, so whatever SED misses, captions and answers miss too. Extra pre-training on DataSEC did not help (difference −0.003, 95% confidence interval [−0.025, +0.020]). A learned boundary refinement stage (LBR) raised test event-based micro-F1 from 0.181 to 0.297 (+0.116 [+0.074, +0.159]), but it did not raise event coverage, and retrieval and captions did not improve with it. They improved where coverage rose: an LBR setting that favours detection (coverage 0.820) and a backfill retrieval mode, which beat both hybrid and semantic-only ranking on all four event stores, while hybrid retrieval alone scored below semantic-only ranking on three of them. The web application runs locally with a median of 3.9 s per recording. Future work: field recordings in Vietnam and a stronger detector.

**Keywords:** sound event detection, environmental noise, grounded captioning, hallucination, retrieval-augmented generation, transfer learning, data leakage.

@@PAGEBREAK@@

@@TITLE:TÓM TẮT@@

**Tên đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

Giám sát tiếng ồn cần biết nguồn âm nào xuất hiện, lúc nào và kéo dài bao lâu. Quy chuẩn kỹ thuật quốc gia (QCVN) 26:2025/BNNMT về tiếng ồn cho thấy nhu cầu này ở Việt Nam. Khóa luận xây dựng hệ thống bốn phần: phát hiện sự kiện âm thanh (Sound Event Detection – SED) kèm thời điểm bắt đầu và kết thúc; sinh mô tả chỉ từ sự kiện đã phát hiện; lưu sự kiện vào kho PostgreSQL có chỉ mục vector; và trả lời câu hỏi bằng sinh tăng cường truy hồi (Retrieval-Augmented Generation – RAG), có trích bản ghi và khoảng thời gian làm bằng chứng. Dữ liệu là DataSEC (5.048 đoạn) và DataSED (717 bản ghi, 21 lớp); hai bộ có chung bản ghi gốc nên 11 đoạn bị loại trước khi huấn luyện.

Kết quả chính là độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào SED, cụ thể là vào độ phủ sự kiện (tỷ lệ sự kiện thật được phát hiện): bộ sinh có ràng buộc không thêm nguồn âm ngoài danh sách sự kiện và bộ lọc cứng chỉ trả bản ghi có sự kiện thỏa điều kiện, nên cái gì SED bỏ sót thì mô tả và câu trả lời cũng bỏ sót. Huấn luyện thêm trên DataSEC không giúp (hiệu −0,003, khoảng tin cậy 95% [−0,025; +0,020]). Bước tinh chỉnh biên học được (LBR) nâng F1 theo sự kiện micro trên tập kiểm tra từ 0,181 lên 0,297 (hiệu +0,116 [+0,074; +0,159]) nhưng không tăng độ phủ sự kiện, nên truy hồi và mô tả không tốt lên theo. Hai bước này chỉ tốt lên khi độ phủ tăng: ở cấu hình LBR ưu tiên phát hiện (độ phủ 0,820) và ở chế độ truy hồi bổ sung, cao hơn cả truy hồi kết hợp lẫn truy hồi chỉ theo ngữ nghĩa ở cả bốn kho sự kiện. Ứng dụng web chạy trên máy cá nhân, trung vị 3,9 giây mỗi bản ghi. Hướng phát triển: thử trên bản ghi thu tại Việt Nam và cải thiện bộ phát hiện.

**Từ khóa:** phát hiện sự kiện âm thanh, tiếng ồn môi trường, mô tả bám sát sự kiện, ảo giác, sinh tăng cường truy hồi, học chuyển giao, rò rỉ dữ liệu.

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

@@COLWIDTHS:18,42,40@@

| Từ viết tắt | Từ đầy đủ | Nghĩa |
|---|---|---|
| ADR | Architectural Decision Record | Bản ghi quyết định kiến trúc của dự án (Phụ lục B) |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| BEATs | Bidirectional Encoder representation from Audio Transformers | Mô hình âm thanh tự giám sát, dùng làm bộ mã hóa |
| BGE-M3 | BAAI General Embedding, Multi-Linguality, Multi-Functionality, Multi-Granularity | Mô hình nhúng văn bản đa ngữ dùng cho truy hồi |
| BiGRU | Bidirectional Gated Recurrent Unit | Mạng hồi quy có cổng hai chiều |
| BLEU | Bilingual Evaluation Understudy | Chỉ số trùng cụm từ giữa câu sinh và câu tham chiếu |
| CIDEr | Consensus-based Image Description Evaluation | Chỉ số trùng cụm từ có trọng số theo độ hiếm |
| CLAP | Contrastive Language-Audio Pretraining | Tiền huấn luyện đối sánh âm thanh và văn bản |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CPU | Central Processing Unit | Bộ xử lý trung tâm |
| CRNN | Convolutional Recurrent Neural Network | Mạng nơ-ron tích chập hồi quy |
| cSEBB | change-detection-based Sound Event Bounding Boxes | Cách tách hộp sự kiện tại điểm xác suất đổi hướng |
| CTTC | Cross-Trigger Tolerance Criterion | Tiêu chí nhầm lớp của PSDS |
| DataSEC | Dataset for Sound Event Classification of environmental noise | Bộ dữ liệu phân loại sự kiện âm thanh tiếng ồn môi trường |
| DataSED | Dataset for Sound Event Detection of environmental noise | Bộ dữ liệu phát hiện sự kiện âm thanh tiếng ồn môi trường |
| dBA | A-weighted decibel | Đề-xi-ben theo đặc tuyến A |
| DCASE | Detection and Classification of Acoustic Scenes and Events | Chuỗi thử thách phát hiện và phân loại cảnh, sự kiện âm thanh |
| DESED | Domestic Environment Sound Event Detection Dataset | Bộ dữ liệu SED trong nhà của DCASE |
| DTC | Detection Tolerance Criterion | Tiêu chí phát hiện của PSDS |
| ECE | Expected Calibration Error | Sai số hiệu chuẩn kỳ vọng |
| ECHO | Evaluation of Caption Hallucination in audiO | Chỉ số ảo giác của mô tả âm thanh |
| FN | False Negative | Sự kiện bị bỏ sót |
| FP | False Positive | Sự kiện báo nhầm |
| GBNF | GGML Backus–Naur Form | Cú pháp ngữ pháp dùng để ràng buộc đầu ra của llama.cpp |
| GPU | Graphics Processing Unit | Bộ xử lý đồ họa |
| GTC | Ground Truth intersection Criterion | Tiêu chí phủ nhãn của PSDS |
| GVHD | Giảng viên hướng dẫn | Giảng viên hướng dẫn khóa luận |
| HTTP | Hypertext Transfer Protocol | Giao thức truyền siêu văn bản |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc |
| KTC | Khoảng tin cậy | Khoảng tin cậy bootstrap 95% |
| LBR | Learned Boundary Refinement | Tinh chỉnh biên học được kèm chấm lại hộp (Chương 4) |
| MD5 | MD5 Message-Digest Algorithm | Hàm băm dùng để kiểm tệp nén |
| nDCG | normalized Discounted Cumulative Gain | Lợi ích tích lũy chiết khấu chuẩn hóa |
| PANNs | Pretrained Audio Neural Networks | Mạng nơ-ron âm thanh tiền huấn luyện |
| PSDS | Polyphonic Sound Detection Score | Điểm phát hiện âm thanh đa âm trên dải ngưỡng |
| QCVN | Quy chuẩn kỹ thuật quốc gia | Văn bản kỹ thuật bắt buộc do bộ ban hành |
| RAG | Retrieval-Augmented Generation | Sinh tăng cường truy hồi |
| SEBB | Sound Event Bounding Boxes | Hộp bao sự kiện âm thanh |
| SED | Sound Event Detection | Phát hiện sự kiện âm thanh |
| SHA-256 | Secure Hash Algorithm, 256 bit | Hàm băm dùng để khóa dữ liệu |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |
| TP | True Positive | Sự kiện phát hiện đúng |

@@PAGEBREAK@@

@@HEADING1N:DANH MỤC THUẬT NGỮ@@

Mỗi khái niệm trong báo cáo chỉ dùng một tên. Bảng dưới nêu tên đó, thuật ngữ tiếng Anh tương ứng và nghĩa ngắn gọn.

@@COLWIDTHS:24,24,52@@

| Tên trong báo cáo | Tiếng Anh | Nghĩa |
|---|---|---|
| Tập huấn luyện, tập phát triển, tập kiểm tra | train, dev, test | Tập để học mô hình; tập để chọn cấu hình; tập chỉ dùng để đo cấu hình đã chọn |
| Dự đoán ngoài mẫu | out-of-fold prediction | Dự đoán cho một bản ghi bởi mô hình không được học trên bản ghi đó |
| Kiểm chứng chéo, phần | cross-validation, fold | Chia dữ liệu thành K phần, lần lượt giữ một phần để kiểm |
| Tổ hợp mô hình | ensemble | Lấy trung bình xác suất của nhiều mô hình |
| Hạt giống ngẫu nhiên | random seed | Giá trị khởi tạo ngẫu nhiên; huấn luyện nhiều lần để đo độ dao động |
| Vòng huấn luyện | epoch | Một lượt đi qua toàn bộ tập huấn luyện |
| Bản lưu trọng số | checkpoint | Trọng số mô hình lưu tại một vòng huấn luyện |
| Huấn luyện tiếp | fine-tuning | Tiếp tục huấn luyện một mô hình tiền huấn luyện trên dữ liệu mới |
| Lớp cấp trên, lớp con | coarse class, subclass | Hai cấp nhãn của DataSEC |
| Lớp gộp | merged class | Lớp gồm nhiều nguồn âm khác nhau, như `sirens_and_alarms` |
| Phép gộp | pooling | Phép nén một trục của đặc trưng bằng giá trị trung bình hoặc lớn nhất |
| Dung sai | collar | Độ lệch thời gian tối đa để một sự kiện dự đoán được tính là khớp |
| Độ chính xác, độ đầy đủ | precision, recall | Tỷ lệ dự đoán là đúng; tỷ lệ sự kiện thật được tìm thấy (mục 2.2) |
| Tỷ lệ phân loại đúng | accuracy | Tỷ lệ đoạn được gán đúng lớp |
| F1 theo sự kiện | event-based F1 | F1 tính theo từng sự kiện, có dung sai 0,2 s (mục 2.2.2) |
| F1 theo đoạn | segment-based F1 | F1 tính theo từng đoạn 1 s (mục 2.2.1) |
| Độ phủ sự kiện | intersection-based recall | Tỷ lệ sự kiện tham chiếu được dự đoán cùng lớp phủ ít nhất 10% thời lượng (mục 2.2.3) |
| Hệ mốc | (hệ f2) | Hệ SED được khóa ở vòng chọn trước, giữ làm mốc so sánh |
| Hệ cơ sở | (hệ B0) | Hệ SED cuối cùng trước khi thêm LBR |
| LBR chính | (LBR V2) | Hệ cơ sở cộng LBR, cấu hình tối đa F1 theo sự kiện; là số chính |
| LBR ứng dụng | (LBR V3) | Hệ cơ sở cộng LBR, cấu hình ưu tiên độ phủ sự kiện; dùng trong ứng dụng minh họa |
| Theo mẫu, tự do, ràng buộc, ràng buộc + phủ | template, unconstrained, constrained, constrained-cover | Bốn cách sinh mô tả (Chương 4) |
| Chỉ lọc, chỉ ngữ nghĩa, kết hợp, bổ sung | structured_only, vector_only, hybrid, backfill | Bốn chế độ truy hồi (Chương 4) |
| Câu truy vấn | query | Một câu trong bộ 100 câu dùng để đánh giá truy hồi |
| Ảo giác, bỏ sót | hallucination, omission | Nhắc nguồn âm không có trong danh sách sự kiện; không nhắc lớp có trong danh sách (mục 2.2.5) |
| Độ phủ bằng chứng | evidence coverage | Tỷ lệ lần nhắc nguồn âm có sự kiện làm bằng chứng |
| Rào đón | hedge | Nhãn "độ tin cậy thấp" gắn cho lớp có điểm thấp |
| Độ đúng bộ lọc | filter exactness | Tỷ lệ kết quả trả về thỏa mọi điều kiện của câu truy vấn |
| Ứng dụng minh họa | demo | Ứng dụng web chạy trên máy cá nhân, dùng để trình diễn hệ thống |

@@SECTION:front@@
