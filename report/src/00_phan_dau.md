@@TITLE:ABSTRACT@@

**Title:** Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval

Outdoor noise monitoring needs to know which sound sources occur, when, and for how long. This mid-term report presents an end-to-end system that detects environmental sound events with temporal localization, captions recordings using only the detected event timeline, and answers natural-language questions over recording history with Retrieval-Augmented Generation (RAG), citing recordings and time spans as evidence.

The system uses two public datasets from the same authors: DataSEC (5,048 clips) and DataSED (717 recordings, 21 polyphonic classes). A three-tier deduplication audit found shared source recordings, so 11 DataSEC clips (0.22%) were excluded before pre-training and all splits were frozen by hash. Every choice was made on the development set and committed before the test set was evaluated once.

Additional pre-training on DataSEC did not improve event-based F1 over AudioSet pre-training (paired difference −0.003, 95% CI [−0.025, +0.020]). Sound event detection (SED) errors lie mainly in boundaries and missed events. The locked system reaches event-based macro-F1 0.121 and micro-F1 0.164 [0.110, 0.224] on the annotated test set and is not shown to beat the previous generation. Grammar-constrained captioning removed hallucinated sources and context inference relative to the predicted timeline, at a cost in omissions that a coverage constraint removes. Hard filters kept every retrieved result consistent with the query, and no answer contained unsupported claims, but retrieval is bounded by SED recall. Remaining work: a systematic literature review, development-set analyses and the final thesis.

**Keywords:** sound event detection, environmental noise, grounded captioning, hallucination, retrieval-augmented generation, transfer learning, data leakage.

@@PAGEBREAK@@

@@TITLE:TÓM TẮT@@

**Tên đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

Giám sát tiếng ồn môi trường cần biết nguồn âm nào xuất hiện, lúc nào và kéo dài bao lâu. Báo cáo giữa kỳ trình bày một hệ thống từ đầu đến cuối: phát hiện sự kiện âm thanh kèm thời gian, viết mô tả chỉ dựa trên các sự kiện đã phát hiện, và trả lời câu hỏi tự nhiên về lịch sử bản ghi bằng sinh tăng cường truy hồi (RAG), có nêu bản ghi và khoảng thời gian làm bằng chứng.

Nhóm dùng hai bộ dữ liệu công bố của cùng nhóm tác giả: DataSEC (5.048 đoạn) và DataSED (717 bản ghi, 21 lớp). Kiểm tra trùng lặp cho thấy hai bộ có chung bản ghi gốc, nên 11 đoạn DataSEC (0,22%) bị loại trước khi huấn luyện và các tập chia được khóa bằng mã băm. Mọi lựa chọn đều làm trên tập dev và được ghi lại trước khi đánh giá tập test một lần.

Huấn luyện thêm trên DataSEC không giúp event-F1 tốt hơn so với chỉ dùng mô hình tiền huấn luyện AudioSet (hiệu −0,003, khoảng tin cậy 95% [−0,025; +0,020]). Lỗi phát hiện sự kiện âm thanh (SED) chủ yếu là lệch biên và bỏ sót. Hệ thống được khóa đạt event-F1 macro 0,121 và micro 0,164 [0,110; 0,224] trên tập test có nhãn, và chưa được chứng minh tốt hơn thế hệ trước. Khi bắt mô tả bám sát danh sách sự kiện bằng ngữ pháp giải mã, mô tả không còn ảo giác nguồn âm hay suy diễn bối cảnh so với danh sách đó, đổi lại là bỏ sót nhiều hơn; thêm ràng buộc phải nhắc đủ các lớp thì hết bỏ sót. Bộ lọc cứng giữ mọi kết quả truy hồi đúng điều kiện và câu trả lời không có khẳng định thiếu bằng chứng, nhưng chất lượng truy hồi bị giới hạn bởi việc SED còn bỏ sót. Việc còn lại: tổng quan văn liệu có hệ thống, phân tích bổ sung trên tập dev và hoàn thiện khóa luận.

**Từ khóa:** phát hiện sự kiện âm thanh, tiếng ồn môi trường, mô tả có căn cứ, ảo giác, sinh tăng cường truy hồi, học chuyển giao, rò rỉ dữ liệu.

@@PAGEBREAK@@

@@TITLE:LỜI CẢM ƠN@@

Nhóm xin gửi lời cảm ơn chân thành đến TS. Huỳnh Công Bằng, người đã hướng dẫn, góp ý và định hướng cho nhóm trong suốt quá trình thực hiện khóa luận.

Nhóm cảm ơn quý thầy cô Khoa Công nghệ Thông tin, Trường Đại học Công nghiệp Thành phố Hồ Chí Minh đã truyền đạt kiến thức nền tảng để nhóm có thể thực hiện đề tài này.

Nhóm cũng cảm ơn các tác giả của hai bộ dữ liệu DataSEC và DataSED đã công bố dữ liệu mở, cùng cộng đồng nghiên cứu âm thanh đã chia sẻ mã nguồn và mô hình tiền huấn luyện mà nhóm sử dụng.

Cuối cùng, nhóm cảm ơn gia đình và bạn bè đã luôn động viên trong thời gian qua. Do thời gian có hạn, báo cáo giữa kỳ khó tránh khỏi thiếu sót; nhóm rất mong nhận được góp ý của quý thầy cô để hoàn thiện khóa luận.

@@PAGEBREAK@@

@@TITLE:NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN@@

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
| ADR | Architecture Decision Record | Bản ghi quyết định kiến trúc |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| BiGRU | Bidirectional Gated Recurrent Unit | Mạng hồi quy có cổng hai chiều |
| CI | Continuous Integration | Tích hợp liên tục |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CPU | Central Processing Unit | Bộ xử lý trung tâm |
| CRNN | Convolutional Recurrent Neural Network | Mạng nơ-ron tích chập hồi quy |
| DCASE | Detection and Classification of Acoustic Scenes and Events | Chuỗi thử thách phát hiện và phân loại cảnh, sự kiện âm thanh |
| ECE | Expected Calibration Error | Sai số hiệu chuẩn kỳ vọng |
| GPU | Graphics Processing Unit | Bộ xử lý đồ họa |
| HNSW | Hierarchical Navigable Small World | Chỉ mục đồ thị cho tìm kiếm vector gần đúng |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc |
| MFCC | Mel-Frequency Cepstral Coefficients | Hệ số cepstral thang mel |
| MRR | Mean Reciprocal Rank | Hạng nghịch đảo trung bình |
| nDCG | normalized Discounted Cumulative Gain | Lợi ích tích lũy chiết khấu chuẩn hóa |
| PANNs | Pretrained Audio Neural Networks | Mạng nơ-ron âm thanh tiền huấn luyện |
| PSDS | Polyphonic Sound Detection Score | Điểm phát hiện âm thanh đa âm |
| RAG | Retrieval-Augmented Generation | Sinh tăng cường truy hồi |
| RQ | Research Question | Câu hỏi nghiên cứu |
| SEBB | Sound Event Bounding Boxes | Hộp bao sự kiện âm thanh |
| SED | Sound Event Detection | Phát hiện sự kiện âm thanh |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |

@@SECTION:front@@
