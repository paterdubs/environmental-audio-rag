@@TITLE:ABSTRACT@@

**Title:** Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval

Outdoor noise monitoring needs to know which sound sources occur, when, and for how long; Vietnam's noise regulation QCVN 26:2025/BNNMT makes this a practical need. This thesis builds a four-block system: sound event detection (SED) with onset and offset, captions written only from the detected event timeline, an event store in PostgreSQL with a vector index, and question answering with Retrieval-Augmented Generation (RAG) that cites recordings and time spans as evidence. It uses two public datasets, DataSEC (5,048 clips) and DataSED (717 recordings, 21 classes); a three-tier deduplication audit found shared source recordings, so 11 clips were excluded and all splits were frozen before training.

The main finding is that caption and answer correctness are bounded by SED. Grammar constraints and hard filters add no errors of their own, so effective improvements lie in SED and in event coverage at retrieval time. Extra pre-training on DataSEC did not help (paired difference −0.003, 95% CI [−0.025, +0.020]). A learned boundary refinement and box rescoring stage (LBR) raised test event-based micro-F1 from 0.181 to 0.297 (+0.116 [+0.074, +0.159]), at the cost of lower segment-F1 and PSDS-2. Constrained captions contained no hallucinated sources relative to the predicted timeline. Hybrid retrieval was significantly worse than semantic-only ranking on three of four event stores, while a backfill mode beat both on all four. The web application runs locally with a median of 3.9 s per recording. Future work: field recordings in Vietnam and a stronger detector.

**Keywords:** sound event detection, environmental noise, grounded captioning, hallucination, retrieval-augmented generation, transfer learning, data leakage.

@@PAGEBREAK@@

@@TITLE:TÓM TẮT@@

**Tên đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

Giám sát tiếng ồn môi trường cần biết nguồn âm nào xuất hiện, lúc nào và kéo dài bao lâu; quy chuẩn QCVN 26:2025/BNNMT về tiếng ồn cho thấy nhu cầu này ở Việt Nam. Khóa luận xây dựng một hệ thống bốn khối: phát hiện sự kiện âm thanh (SED) kèm thời điểm bắt đầu và kết thúc, sinh mô tả chỉ từ danh sách sự kiện đã phát hiện, lưu sự kiện vào kho PostgreSQL có chỉ mục vector, và trả lời câu hỏi tự nhiên bằng sinh tăng cường truy hồi (RAG) có trích bản ghi và khoảng thời gian làm bằng chứng. Dữ liệu là DataSEC (5.048 đoạn) và DataSED (717 bản ghi, 21 lớp); kiểm trùng ba tầng cho thấy hai bộ có chung bản ghi gốc, nên 11 đoạn bị loại và các tập chia được khóa trước khi huấn luyện.

Luận điểm chính của khóa luận là độ đúng của mô tả và của câu trả lời bị chặn bởi bước SED. Ràng buộc ngữ pháp và bộ lọc cứng không thêm lỗi riêng, nên cải tiến có tác dụng nằm ở SED và ở độ phủ sự kiện khi truy hồi. Huấn luyện thêm trên DataSEC không giúp (hiệu −0,003, KTC 95% [−0,025; +0,020]). Tầng tinh chỉnh biên và chấm lại hộp học được (LBR) nâng event-F1 micro trên test từ 0,181 lên 0,297 (hiệu +0,116 [+0,074; +0,159]), đổi lại F1 theo đoạn và PSDS-2 thấp hơn. Mô tả có ràng buộc không còn ảo giác nguồn âm so với danh sách sự kiện. Truy hồi kết hợp thấp hơn có ý nghĩa so với chỉ xếp hạng ngữ nghĩa ở ba trên bốn kho sự kiện, còn chế độ backfill hơn cả hai ở cả bốn kho. Ứng dụng web chạy cục bộ, trung vị 3,9 giây cho mỗi bản ghi. Hướng phát triển: thử trên bản ghi thu thực địa tại Việt Nam và cải thiện bộ phát hiện.

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
| ADR | Architecture Decision Record | Bản ghi quyết định kiến trúc |
| AP | Average Precision | Độ chính xác trung bình |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| BGE-M3 | BAAI General Embedding (Multi-Linguality, Multi-Functionality, Multi-Granularity) | Mô hình nhúng văn bản đa ngữ dùng cho truy hồi |
| BiGRU | Bidirectional Gated Recurrent Unit | Mạng hồi quy có cổng hai chiều |
| BLEU | Bilingual Evaluation Understudy | Chỉ số trùng n-gram giữa câu sinh và câu tham chiếu |
| CI | Confidence Interval; Continuous Integration | Khoảng tin cậy (trong bảng ghi “CI 95%”, văn bản ghi KTC 95%); tích hợp liên tục (Chương 5) |
| CIDEr | Consensus-based Image Description Evaluation | Chỉ số đồng thuận n-gram có trọng số TF-IDF |
| CLAP | Contrastive Language-Audio Pretraining | Tiền huấn luyện đối sánh âm thanh–văn bản |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CPU | Central Processing Unit | Bộ xử lý trung tâm |
| CRNN | Convolutional Recurrent Neural Network | Mạng nơ-ron tích chập hồi quy |
| cSEBB | change-detection-based Sound Event Bounding Boxes | Biến thể SEBB dùng phát hiện điểm đổi để chọn biên hộp bao |
| dBA | A-weighted decibel | Mức áp suất âm theo đặc tuyến A |
| DCASE | Detection and Classification of Acoustic Scenes and Events | Chuỗi thử thách phát hiện và phân loại cảnh, sự kiện âm thanh |
| DESED | Domestic Environment Sound Event Detection | Bộ dữ liệu SED trong nhà của DCASE |
| ECE | Expected Calibration Error | Sai số hiệu chuẩn kỳ vọng |
| EPN | (tên mạng trong bài của Schmid và cộng sự) | Mạng ước lượng thời gian từ onset tới offset của sự kiện |
| ERD | Entity-Relationship Diagram | Sơ đồ thực thể–quan hệ |
| GPU | Graphics Processing Unit | Bộ xử lý đồ họa |
| HNSW | Hierarchical Navigable Small World | Chỉ mục đồ thị cho tìm kiếm vector gần đúng |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc |
| KTC | Khoảng tin cậy | Khoảng tin cậy bootstrap 95% |
| LBR | Learned Boundary Refinement | Tinh chỉnh biên học được: bộ tinh chỉnh biên và bộ chấm lại hộp, học bằng cross-fit |
| LLM | Large Language Model | Mô hình ngôn ngữ lớn |
| MFCC | Mel-Frequency Cepstral Coefficients | Hệ số cepstral thang mel |
| nDCG | normalized Discounted Cumulative Gain | Lợi ích tích lũy chiết khấu chuẩn hóa |
| OOF | Out-of-Fold | Dự đoán ngoài mẫu, tạo bằng kiểm chứng chéo |
| PANNs | Pretrained Audio Neural Networks | Mạng nơ-ron âm thanh tiền huấn luyện |
| PSDS | Polyphonic Sound Detection Score | Điểm phát hiện âm thanh đa âm |
| QCVN | Quy chuẩn kỹ thuật quốc gia | Quy chuẩn kỹ thuật quốc gia Việt Nam |
| RAG | Retrieval-Augmented Generation | Sinh tăng cường truy hồi |
| RED | Recurrent Event Detection | Phép truy hồi xác suất khả vi chuyển xác suất bắt đầu/kết thúc thành onset, offset |
| RQ | Research Question | Câu hỏi nghiên cứu |
| RRF | Reciprocal Rank Fusion | Gộp xếp hạng theo hạng nghịch đảo |
| SEBB | Sound Event Bounding Boxes | Hộp bao sự kiện âm thanh |
| SED | Sound Event Detection | Phát hiện sự kiện âm thanh |
| SHA | Secure Hash Algorithm | Hàm băm (SHA-256) dùng khóa dữ liệu và artifact |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |
| TCVN | Tiêu chuẩn quốc gia | Tiêu chuẩn quốc gia Việt Nam |
| UI | User Interface | Giao diện người dùng |

@@SECTION:front@@
