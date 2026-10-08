# Rà soát báo cáo giữa kỳ — 03/10/2026

**Phạm vi:** task L3, đánh giá bản `Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx` và PDF cùng tên; chưa sửa nội dung, script dựng, DOCX hoặc PDF. Đọc cả bảy chương trong `report/src/`, kiểm tra XML của DOCX, trích văn bản PDF, xem ảnh một số trang và đối chiếu các kết quả chính với artifact đã lưu. Không huấn luyện, chạy inference, đánh giá lại test hoặc đọc prediction test. Đây chưa phải kiểm toán lại toàn bộ văn liệu hay chứng nhận mọi ô số liệu.

**Bằng chứng máy đọc:** [midterm_report_review_20261003.json](../docs/measurements/midterm_report_review_20261003.json), gồm SHA-256 của tài liệu, cấu hình section/style, tiêu đề thật trong DOCX, kết quả bộ kiểm tra hiện có và số lấy trực tiếp từ artifact. Lệnh kiểm tra nền: `.venv/Scripts/python.exe -m scripts.check_midterm_docx`. Kiểm tra bổ sung bằng `zipfile`/`xml.etree.ElementTree`, `pdfinfo`, `pdftotext -layout`; render trang chọn lọc bằng `pdftoppm -r 90`.

## 1. Kết luận để quyết định cách sửa

Bản báo cáo có cơ sở dữ liệu và kết quả thực nghiệm đủ để biên tập tiếp. Các thông số trình bày chính đúng mẫu, các số chính được đối chiếu khớp artifact. Vấn đề lớn là cách tổ chức lời giải thích: nhiều đoạn viết cho người đã biết repo, sử dụng mã thí nghiệm và quy tắc vận hành trước khi người đọc hiểu bài toán. Một số câu còn suy rộng hơn phép đo, nên cần sửa tính chính xác trước khi rút gọn.

Hai nhận xét của người dùng có cơ sở, nhưng không nên rút ngắn mọi tiêu đề. Các tên như “Bối cảnh và lý do chọn đề tài”, “Mục tiêu nghiên cứu”, “Kiến trúc tổng thể” đã rõ. Cần ưu tiên tiêu đề chứa thuật ngữ chưa giải thích, mã nội bộ hoặc nhiều ý khác nhau. Mục tiêu là người đọc biết mục đó trả lời câu hỏi gì.

Giữ khung bảy chương ở vòng sửa đầu. Biên tập theo từng mục trong `report/src/`, sau đó dựng lại DOCX để tránh mất sửa đổi khi build. Mỗi lượt nên xử lý một chương và kiểm tra liên kết với các chương khác.

## 2. Thông số và lỗi trình bày

| Hạng mục | Kết quả kiểm tra | Xử lý |
|---|---|---|
| Khổ giấy và lề | Các section có khổ A4; trên/dưới 3 cm, trái 3,5 cm, phải 2 cm theo giá trị twip của mẫu | Giữ |
| Nội dung | Content kế thừa Times New Roman 13 pt; giãn dòng 1,5; trước 10 pt, sau 0; căn đều; không thụt đầu dòng | Giữ |
| Tiêu đề chương | Heading 1: 14 pt, đậm, in hoa, trước/sau 24 pt, giãn 1,15; numbering chương có lề trái và firstLine bằng 0 | Giữ |
| Tiêu đề mục | Heading 2–3: 13 pt, trước 6 pt/sau 12 pt, giãn 1,15; cấp 2 đậm, cấp 3 đậm nghiêng | Giữ; giản lược tên mục |
| Chú thích | Caption 13 pt, căn giữa, trước 6 pt/sau 12 pt, giãn 1,15; bảng trên, hình dưới ở các trang đã xem | Giữ |
| Bảng | TableText 11 pt, TableTextSmall 10 pt; được mẫu cho phép với bảng nhiều nội dung | Đúng cỡ nhưng một số bảng dày và khó đọc; giảm cột hoặc chuyển chi tiết sang phụ lục |
| Danh mục | Có TOC cấp 1–3, danh mục hình/bảng và trường tham chiếu | Có cấu trúc cập nhật được; cần cập nhật lại và kiểm sau biên tập |
| Số trang | Nội dung bắt đầu 1, chân trang bên phải; phụ lục không in số | Phần đầu và tài liệu tham khảo có số nội bộ trong mục lục nhưng không in ở chân trang; cần thống nhất quy ước trình bày |
| Tài liệu tham khảo | Có nhóm tiếng Anh, thụt treo 1 cm; tên ấn phẩm in nghiêng ở trang kiểm tra | Chưa xác minh độc lập lại metadata của tất cả nguồn |
| Toàn tài liệu | PDF 85 trang; phần nội dung có số trang 1–64 | Độ dài tự nó không phải lỗi vì chưa có giới hạn trang giữa kỳ; cần giảm lặp và chi tiết vận hành |

Các lỗi hoặc điểm cần hoàn thiện:

1. **Trang PDF 4 trắng hoàn toàn**, sau bìa tiếng Anh. Mẫu yêu cầu in một mặt nên không có căn cứ giữ trang đệm chẵn/lẻ này. Kiểm tra page break/section break khi dựng lại.
2. **Hai chỗ lặp nhãn:** “Bảng Bảng 4.1” ở mục 4.1 (trang nội dung 23) và “Bảng Bảng 5.1” ở mục 5.2.2. Nguồn đã ghi “Bảng” trước một field REF vốn trả cả nhãn và số. Bỏ tiền tố ở nguồn, không gõ đè kết quả field.
3. **Hình 5.1** ghép bốn ảnh khiến chữ giao diện quá nhỏ. Chọn một ảnh tổng quan và ảnh cắt của thao tác cần chứng minh; đưa ảnh đầy đủ sang phụ lục.
4. Các bảng 6.8–6.10 có nhiều cột, xen tiếng Anh, mã và chữ nhỏ. Bảng 6.8 chưa nêu rõ `all`, n = 142 trong caption hiển thị, dù tệp bảng nguồn có ghi. Phải giữ phạm vi đánh giá khi chèn bảng.
5. Có **18 lần xuất hiện placeholder trong thân DOCX**, ngoài ra placeholder họ tên xuất hiện lặp ở footer. Chưa thể coi là bản nộp sau cùng. Metadata còn tên tác giả và ngày tạo của mẫu; làm sạch khi hoàn thiện.
6. Danh mục viết tắt dùng **CI = Continuous Integration**, trong khi hình/bảng còn dùng CI cho *confidence interval*. Viết đầy đủ “khoảng tin cậy 95%” trong kết quả hoặc giải thích rõ hai nghĩa.
7. Số thập phân trong văn xuôi dùng dấu phẩy nhưng trong bảng dùng dấu chấm; nên chọn quy ước và ghi rõ. Chuỗi cấu hình như `global|25`, `tau0.64_rel2` cần diễn giải bằng lời ở phần chính.

**Giới hạn của bộ kiểm tra có sẵn:** “đạt” không đồng nghĩa tài liệu đã nghiệm thu. Một số dòng chỉ thống kê và luôn trả True, kể cả placeholder và bảng; nhiều style không bị bắt buộc kiểm cỡ chữ trong EXPECTED_STYLES; không kiểm nội dung khoa học, trang trắng, nhãn lặp hay tính dễ đọc. Rà soát này đã kiểm bổ sung các thuộc tính kế thừa và những trang nêu trên, chưa xác nhận bằng mắt từng trang ở độ phân giải cao.

## 3. Số liệu đã đối chiếu và các diễn giải cần sửa trước

### 3.1. Các số chính khớp nguồn

- **Classifier DataSEC:** artifact ghi `0.8466317979797467`, làm tròn bốn chữ số là **0,8466** như báo cáo. Không sửa thành 0,8467 chỉ vì một số tài liệu trạng thái cũ ghi như vậy. Nguồn: `ml/runs/classifier_datasec_20260923T121808Z/metrics.json`.
- **SED f2 trên test annotated:** macro 0,1206; micro 0,1643; CI micro [0,1103; 0,2242]; PSDS-1/2 0,3164/0,7253; 139 bản ghi. Nguồn: `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/evaluation_cv_annotated.json`.
- **Parser:** 171/200 câu mẫu đúng hoàn toàn, 37/40 câu diễn đạt lại đúng; tương ứng 0,855/0,925. Độ đúng vị từ 0,7667 trên nhóm 60 câu thời gian, không phải toàn bộ 200 câu. Nguồn: `docs/measurements/query_parser_20260928.json`.
- **Parity CPU:** 290 sự kiện trùng khít và 294 trong dung sai so với 299 sự kiện tham chiếu; đầu ra CPU có 300 sự kiện. Nên thêm mẫu số và số đầu ra CPU để tránh đọc nhầm thành hai tập đầu ra cùng kích thước. Nguồn: `docs/measurements/inference_parity_cpu_20261002.json`.
- **Dữ liệu:** số tệp/tổng giờ 5.048/23,71 và 717/18,68 khớp hai inventory summary; bảng theo lớp f2 nhất quán với việc chỉ báo số tuyệt đối cho lớp có ít mẫu.

### 3.2. Danh sách sửa tính chính xác

| Mã | Vị trí | Vấn đề | Cách sửa |
|---|---|---|---|
| K01 | 2.4.1 | Nói CNN14 gốc có pooling 2×2 ở **mỗi** khối; lẫn bản gốc với bản v1 trong repo | CNN14 gốc dùng 2×2 ở khối 1–5 và 1×1 ở khối 6. Nêu rõ bản v1 của đề tài nén /64; không quy hạn chế này cho CNN14 gốc |
| K02 | 3.1 | Khẳng định cứ công bố mô hình học từ dữ liệu thì mô hình bắt buộc mang cùng license | Bỏ suy diễn tự động. Nêu license dữ liệu đã xác minh và chính sách phát hành của dự án; nghĩa vụ đối với trọng số cần xác minh riêng |
| K03 | 3.4.2; 6.3.1; 7.2 | Từ tám cặp âm thanh trùng suy ra “trần người”, rồi suy ra cải thiện nhỏ hơn bất đồng nhãn không thể phân biệt | Gọi là “mức đồng thuận quan sát trên tám cặp”. Không coi là trần tuyệt đối của mô hình, không suy ngưỡng ý nghĩa thống kê từ con số này. Chưa có thông tin người gán nhãn thì không gọi chắc là hai người gán độc lập |
| K04 | 4.2 | Nói cross-entropy không phạt phân bố xác suất sai nếu lớp đúng vẫn là argmax | CE vẫn phạt khi xác suất lớp đúng giảm. Viết: CE không biểu diễn tường minh cấu trúc nhóm; loss bổ sung khuyến khích tổng xác suất trong đúng nhóm. Comment code cũng có diễn giải chưa chuẩn, không lấy comment làm bằng chứng toán học |
| K05 | 4.4.1 | Gom mọi tham số vào “phân bố thời lượng sự kiện” | Code lấy d_min từ **độ dài sự kiện**, g_max từ **khoảng cách giữa sự kiện cùng lớp**, median_w suy từ d_min và tốc độ khung. Mô tả đúng ba đại lượng |
| K06 | 4.4.2 | Công thức viết h = τ/2 theo khung nhưng lưới τ lại có đơn vị giây | Bổ sung phép đổi giây sang số khung và quy tắc làm tròn đúng theo code trước khi dùng tổng rời rạc |
| K07 | 4.5.1 | Nói chỉ cho LLM xem timeline thì nó “không thể bịa” | Bản unconstrained vẫn có lỗi ngay trong Chương 6. Timeline là nguồn đầu vào; ràng buộc giải mã và kiểm tra đầu ra mới hạn chế các lỗi đã định nghĩa |
| K08 | 4.7.2 | Công thức H/O chưa nêu trường hợp tập lần nhắc hoặc tập lớp rỗng; MRR mô tả như RR của một truy vấn | Bổ sung quy ước mẫu số bằng 0 đúng code, cách lấy trung bình; phân biệt RR và MRR. Nói rõ loại truy vấn không có bản ghi liên quan khỏi phép chấm và cách tính filter exactness khi kết quả rỗng |
| K09 | 4.7.2 | Từ việc từ điển chấm dễ dãi suy ra “hiệu số hai chế độ là một cận dưới” | Chưa có chứng minh rằng sai số giữa hai chế độ có hướng như nhau. Đổi thành giới hạn của phép đo dựa trên từ điển |
| K10 | 4.7.3; 6.3.2–6.3.4 | Dùng CI riêng lẻ chồng lấp hoặc chênh lệch nhỏ hơn SD fold như quy tắc kiểm định tổng quát | Phân biệt quy tắc báo cáo thận trọng đã đăng ký của dự án với kiểm định thống kê. Diễn giải CI của **hiệu ghép cặp**/kiểm định đã lưu; không chạy thêm test. Chưa có phép so phù hợp thì ghi chưa đủ bằng chứng |
| K11 | 6.3.3; 6.4 | “349 bỏ sót” dễ bị hiểu là FN trong event-F1 | 349 là `deletion` của bộ chẩn đoán theo overlap, khác FN của sed_eval. Từ precision/recall và số sự kiện đã lưu suy ra TP = 85, FN = 655, FP = 210; không phải đánh giá test mới. Không thay 349 bằng 655 trong bảng chẩn đoán; giải thích hai định nghĩa |
| K12 | 6.3.1; 6.4 | Kết luận lỗi “không nằm ở nhận dạng lớp”; suy từ F1 thấp rằng “phần lớn mô tả” sai | Số phân rã cho thấy vấn đề biên/bỏ sót, chưa loại trừ nhầm lớp. F1 sự kiện thấp cũng chưa cho tỷ lệ mô tả sai theo bản ghi. Nêu rủi ro lan truyền lỗi, không lượng hóa tỷ lệ chưa đo |
| K13 | 6.5–6.7; 7.2 | “Bộ lọc bảo đảm tính đúng tuyệt đối”, “mọi câu trả lời có bằng chứng thật” dễ bị hiểu là đúng với ý người hỏi và âm thanh | Kết quả chỉ đo sự nhất quán với **bộ lọc đã áp và sự kiện lưu trong kho**. Parser và SED vẫn có thể sai; kết quả rỗng được code cho filter exactness = 1. Cần báo tỷ lệ truy vấn có kết quả nếu đã có nguồn phù hợp |
| K14 | 6.7 | Khẳng định “chưa có baseline công bố” trong khi 2.7 nói chưa tìm kiếm có hệ thống | Viết “chưa xác định được mốc so sánh công bố trong phạm vi tài liệu đã khảo sát” |
| K15 | 7.5; tóm tắt | Kết luận “tiền huấn luyện thêm trên DataSEC không cải thiện SED” mạnh hơn 6.2.2 | Giữ kết luận hẹp: chưa thấy bằng chứng cải thiện event-F1 trong thiết lập đã khảo sát; PSDS-2 của v2 tăng trong kiểm định đơn lẻ chưa hiệu chỉnh so sánh bội |
| K16 | 5.4; 6.7; tóm tắt | Câu “run dirty không dùng cho số chính thức”, “test một lần” quá tuyệt đối so với lịch sử và ngoại lệ đã công khai | Giải thích test một lần cho cấu hình/lượt đánh giá đã đăng ký; phân biệt tính lại sau sửa lỗi, đánh giá annotated và parity. Nêu ngoại lệ provenance rõ ràng, không che chúng bằng câu tổng quát |

Nguồn K01: [mã CNN14 của tác giả PANNs](https://github.com/qiuqiangkong/audioset_tagging_cnn/blob/master/pytorch/models.py), lớp `Cnn14`, đọc trực tiếp. Nguồn K02: [FAQ Creative Commons](https://creativecommons.org/faq/), các mục adaptation, ShareAlike và AI; tài liệu này không thiết lập một quy tắc chung rằng mọi trọng số huấn luyện đều là bản phái sinh. Đây là yêu cầu giới hạn khẳng định của báo cáo, không phải kết luận pháp lý về checkpoint cụ thể.

Nguồn K04–K13: `ml/models/hierarchical.py`, `ml/postprocessing/calibration.py`, `ml/evaluation/errors.py`, `scripts/evaluate_retrieval.py`, artifact f2 đã lưu và các đoạn tự đối chiếu trong Chương 4–6. Không đổi protocol hoặc metric trong lượt rà soát này.

## 4. Đánh giá và kế hoạch sửa từng chương

### Chương 1 — Giới thiệu (trang nội dung 1–6)

**Mức sửa: vừa.** Mạch đặt vấn đề tốt, có ví dụ âm thanh và phân biệt đầu ra với bằng chứng. Tuy nhiên, mở đầu đã đưa nhiều cặp thuật ngữ Anh–Việt; mục 1.3–1.6 lặp mục tiêu/câu hỏi/đóng góp dưới nhiều bảng.

- **1.1:** giữ bối cảnh, nhu cầu và khó khăn; rút phần nhãn mạnh/yếu về một câu, dành giải thích cho 2.1. Thêm một tình huống người dùng cụ thể làm sợi chỉ xuyên suốt.
- **1.2:** trình bày đầu vào và ba đầu ra bằng ví dụ trước; công thức để cuối mục hoặc chuyển sang Chương 4 nếu không được dùng tiếp trong Chương 1.
- **1.3:** bỏ khẳng định không có nguồn “các hệ thống mô tả âm thanh thường không đo”; ghi mục tiêu của chính đề tài. Tiêu chí O2/O3 hiện là có phép đo, chưa phải ngưỡng chất lượng; không tự đặt ngưỡng mới để hợp thức hóa kết quả.
- **1.4.1–1.4.3:** giữ ba câu hỏi, đổi tiêu đề gọn; giải thích A/B/C, oracle/end-to-end ngay nơi cần, không đưa chi tiết thiết kế thí nghiệm quá sớm.
- **1.5:** gom phạm vi dữ liệu, nhiệm vụ và đầu ra; rút danh sách loại trừ. Câu “phân tích nội dung vi phạm quyền riêng tư” quá tuyệt đối; chỉ cần nói không thuộc phạm vi và dữ liệu không hỗ trợ mục tiêu đó.
- **1.6:** tách rõ đóng góp dự kiến và mức đã chứng minh; tránh lặp bảng kết quả Chương 6. Đổi “hợp đồng căn cứ” thành “quy tắc kiểm tra mô tả theo bằng chứng”.
- **1.7:** giữ một đoạn ngắn; không nhắc lại chi tiết mỗi phương pháp.

### Chương 2 — Cơ sở lý thuyết và nghiên cứu liên quan (trang 7–14)

**Mức sửa: nhiều.** Chương hiện trộn định nghĩa, cấu hình riêng của repo, lịch sử quyết định và số kết quả công bố. Thiếu một bảng so sánh công trình liên quan theo vấn đề, phương pháp, giới hạn và quan hệ với đề tài.

- **2.1.1–2.1.2:** giải thích âm thanh chồng lấp và nhãn theo thời gian bằng hình/ví dụ trước; sau đó mới vào log-mel, CNN, CRNN, BiGRU. Phân biệt “đa âm” của tín hiệu với “đa nhãn” của bài toán học máy.
- **2.2.1–2.2.3:** dùng cùng một ví dụ để giải thích khớp sự kiện, precision/recall/F1 và macro/micro. Giữ định nghĩa metric ở đây; chuyển collar cụ thể, cấu hình PSDS và mốc đổi cách báo cáo sang giao thức Chương 4.
- **2.2.4:** số DCASE chỉ là ví dụ khác bối cảnh; rút gọn hoặc đưa vào bảng nghiên cứu liên quan. Không dùng số thấp của bài toán khác để biện minh cho kết quả thấp của đề tài.
- **2.3.1–2.3.2:** thay “posterior”, “ưu tiên thời lượng”, “hộp bao” bằng lời giải thích gần chức năng. Giữ tên cSEBB sau khi đã nói nó xác định đầu/cuối sự kiện như thế nào.
- **2.4.1:** sửa K01. **2.4.2:** tách hai khái niệm tiền huấn luyện theo khung và tự giám sát; đừng để người đọc hiểu chúng là cùng một phương pháp. **2.4.3:** mô tả tác dụng của mixup/FilterAugment bằng ví dụ. **2.4.4:** giữ nguyên lý rò rỉ, chuyển chi tiết dữ liệu của đề tài sang Chương 3.
- **2.5:** giải thích “ảo giác” bằng trường hợp nguồn âm bị thêm, thời gian sai và bối cảnh suy diễn; phân biệt khái niệm với bộ đo dựa trên từ điển.
- **2.6.1–2.6.2:** giới thiệu RAG trước, embedding sau; ví dụ câu hỏi → điều kiện → tìm bản ghi → câu trả lời. Nêu rõ hệ hiện tại dùng câu trả lời theo mẫu, còn LLM hỗ trợ phân tích câu hỏi và thí nghiệm sinh mô tả.
- **2.7:** thêm bảng tổng hợp nghiên cứu; phát biểu khoảng trống trong phạm vi tài liệu đã đọc. Nhật ký mức V3 và việc đọc metadata không cần làm câu mở đầu của chương học thuật.

### Chương 3 — Dữ liệu và chuẩn bị dữ liệu (trang 15–21)

**Mức sửa: vừa đến nhiều.** Có bằng chứng dữ liệu tốt; phần thao tác kiểm toán và lịch sử sửa bug đang lấn phần giải thích phương pháp.

- **3.1.1–3.1.2:** giữ thông tin quy mô, nhãn, phân bố, phiên bản và nguồn. Sửa K02; không cần số byte archive trong văn xuôi chính.
- **3.2:** đổi tiêu đề “Hệ thống nhãn”; dùng bảng ngắn làm rõ 22 lớp phân loại và 21 lớp phát hiện. Giải thích “lớp lớn/lớp con” nhất quán; không gọi mọi lớp lớn đều là “lớp gộp” nếu không thực sự gộp nhiều nguồn âm.
- **3.3:** bỏ D0–D4 khỏi tiêu đề chính, giữ mã nhỏ trong sơ đồ/phụ lục. **3.3.1:** lược bỏ bug kiểm MD5, để thông số đặc trưng trong bảng. **3.3.2:** đổi “Hợp đồng chú giải” thành “Chuẩn hóa và kiểm tra nhãn”. **3.3.3:** giữ ba tầng tìm trùng và kết quả loại trừ, giảm chi tiết lịch sử hiệu chỉnh fingerprint. **3.3.4:** giải thích vì sao các bản ghi cùng nguồn phải ở cùng tập; chuyển hai lỗi định danh và thao tác thử ngược sang phụ lục kiểm chứng.
- **3.4.1:** giữ và làm nổi bật `all`/`annotated`, số bản ghi từng tập và lý do không đổi split. **3.4.2:** sửa K03; không biến thống kê tám cặp thành kết luận chung về mọi nhãn.
- **3.5:** giữ rủi ro dữ liệu; không lặp toàn bộ hạn chế ở 6.7 và 7.3.

### Chương 4 — Phương pháp (trang 22–35)

**Mức sửa: nhiều, ưu tiên cao.** Đây là chương khó đọc nhất: nhiều mã hệ thống, công thức, chi tiết triển khai và quy tắc đánh giá cùng xuất hiện. Cần giải thích hệ hiện hành trước, rồi giới thiệu các phương án đối chứng.

- **4.1:** sơ đồ luồng dễ hiểu, nên giữ. Sửa nhãn “Bảng Bảng”. Rút bảng mã về các tên cần đọc trong chương; bảng toàn bộ a–g/S13 chuyển sang phụ lục hoặc đầu phần so sánh.
- **4.2:** giải thích hai đầu dự đoán bằng ví dụ nhãn lớn/nhãn con rồi đến loss; sửa K04. Thông tin hash checkpoint chuyển sang phụ lục.
- **4.3.1:** giữ hàm mất mát và lý do trọng số lớp, bổ sung các trường hợp biên đúng code khi trình bày công thức. **4.3.2–4.3.4:** dùng bảng so sánh backbone, độ phân giải, lớp thời gian, dữ liệu khởi tạo và cách huấn luyện; giảm cách kể “thế hệ/track”. **4.3.5:** gọi “kết hợp nhiều mô hình”; phân biệt ba seed mỗi họ với các ngoại lệ/run v1 và ứng viên chỉ một mô hình.
- **4.4.1:** sửa K05. **4.4.2:** sửa K06; giữ quy trình chọn trên tập phát triển, không liệt kê lưới dài trong đoạn văn.
- **4.5.1:** sửa K07, giải thích ba quy tắc bằng ví dụ hợp lệ/không hợp lệ. **4.5.2:** bảng bốn chế độ gồm đầu vào, ràng buộc và quyền lựa chọn của mô hình. **4.5.3:** phần ví dụ tiếng Anh và đối chiếu SED hiện đang đặt dưới “Mô tả tiếng Việt”; chuyển ví dụ sang mục chung về minh họa, giữ nội dung riêng tiếng Việt đúng tên mục.
- **4.6.1:** giữ nội dung bản ghi/sự kiện/tài liệu, chuyển tên cột DB sang Chương 5. **4.6.2:** giải thích “điều kiện thời gian” thay “vị từ” trong lời dẫn, giữ bảng công thức. **4.6.3:** làm rõ hợp schema khác hiểu đúng câu hỏi. **4.6.4:** gọi rõ câu trả lời theo mẫu và bằng chứng; không khiến người đọc hiểu LLM tự sinh đáp án cuối.
- **4.7.1:** giải thích train/dev/test bằng tên tiếng Việt ở lần đầu, công khai phạm vi “một lần”. **4.7.2:** sửa K08–K09; tách chỉ số mô tả và truy hồi nếu cần. **4.7.3:** sửa K10, phân biệt dao động theo bản ghi, fold và seed.

### Chương 5 — Triển khai hệ thống (trang 36–42)

**Mức sửa: vừa.** Mô tả thành phần khá rõ, nhưng nội dung giống hướng dẫn cho lập trình viên hơn báo cáo về hệ thống đã xây dựng.

- **5.1:** tiêu đề “Tổ chức mã nguồn”; thay “nguyên tắc ranh giới” bằng “phân chia trách nhiệm”. Giải thích tác dụng của việc tách API và suy luận, không cần định nghĩa AST ngay ở đoạn mở đầu.
- **5.2.1–5.2.3:** giữ nhiệm vụ từng dịch vụ và luồng thao tác người dùng; các endpoint vẫn có ích nhưng không để đường dẫn thay cho giải thích. Sửa nhãn lặp ở 5.2.2; chỉnh Hình 5.1.
- **5.3:** trình bày một kịch bản tải âm thanh → xem sự kiện → hỏi → nghe bằng chứng. Đưa cổng mạng, biến môi trường, mount và lệnh PowerShell sang phụ lục hướng dẫn chạy. Giữ thời gian 2,012 s/0,250 s với chú thích một lần đo, không suy ra hiệu năng phổ quát.
- **5.4:** giải thích khả năng tái lập bằng những thông tin cần lưu; sửa phát biểu tuyệt đối về dirty (K16). Tránh dẫn hash và git nhiều lần trong văn xuôi.
- **5.5:** dùng bảng nhóm kiểm thử → hành vi được kiểm → kết quả và ngày đo. Con số 738 của 02/10 có ghi mốc nên không tự coi là sai; nếu lấy 03/10 làm mốc chốt thì đưa rõ 744 pass/4 skip từ báo cáo kiểm tra, không gọi chung mọi test đều đạt. Danh sách bug chỉ giữ một ví dụ có ý nghĩa với độ tin cậy kết quả.

### Chương 6 — Kết quả và thảo luận (trang 43–59)

**Mức sửa: nhiều, ưu tiên cao nhất về diễn giải.** Bảng có nguồn và phần lớn giới hạn đã được công khai. Tuy nhiên, nhiều mã làm kết quả khó theo dõi; một số kết luận cuối đoạn mạnh hơn chính giới hạn ở đầu đoạn.

- **6.1:** giữ số 0,8466; giải thích macro-F1 lớp con trên mọi nút khác tập đủ mẫu. Định nghĩa mẫu số của tỷ lệ nhất quán theo đúng hàm tính; 203 là số mẫu có nhãn con, chưa mặc nhiên là số được dùng cho mọi metric cha–con.
- **6.2.1–6.2.2:** giữ kết quả âm tính và kết quả PSDS-2. So A với B còn đổi kiến trúc/đặc trưng, nên không tách riêng được tác động thuần của tiền huấn luyện. Trả lời RQ1 bằng B–C như đã thiết kế.
- **6.3.1:** đổi “trần người” và giới hạn cứng sang cách gọi thận trọng; không loại trừ lỗi lớp chỉ từ phân rã overlap. **6.3.2:** trình bày ablation bằng thành phần bỏ → kết quả → giới hạn; không gọi khác biệt “phân biệt được” chỉ vì lớn hơn SD fold. **6.3.3:** trình bày hệ được chọn và các đối chứng chính trước bảng toàn bộ ứng viên; sửa K11. **6.3.4:** “có điểm cao hơn trong phép đo” thay “thắng”; cơ chế đề xuất vẫn là giả thuyết.
- **6.4:** tách đúng theo timeline với đúng theo âm thanh; bổ sung n/eval-set trên bảng. Đổi “phần lớn mô tả sai” thành nguy cơ lỗi SED truyền xuống mô tả khi chưa có phép đo tỷ lệ trực tiếp. Bỏ sót bằng 0 của cover chỉ là phủ lớp trong timeline, không phải phủ mọi sự kiện thật.
- **6.5:** giữ nguyên kết quả truy hồi suy giảm. Giải thích gold/parsed, structured/vector/hybrid bằng tên dễ đọc. Sửa K13 và nhắc bộ trả lời theo mẫu; kiểm tra cả trường hợp kết quả rỗng. Không nâng giả thuyết thiếu recall thành nguyên nhân đã chứng minh.
- **6.6:** tách thành hai mục nhỏ “Độ chính xác phân tích câu hỏi” và “Độ nhất quán khi triển khai”, vì hiện tên mục gộp hai đánh giá khác nhau. Phân biệt schema đúng, nghĩa đúng và đầu ra CPU/GPU khớp.
- **6.7:** gom hạn chế theo dữ liệu, phương pháp và phép đo; để chi tiết dirty/test ledger trong bảng hoặc phụ lục, giữ kết luận chính trong thân bài. Sửa K14 và K16.

### Chương 7 — Tiến độ và kế hoạch tiếp theo (trang 60–64)

**Mức sửa: vừa.** Phù hợp báo cáo giữa kỳ nhưng lặp nhiều kết luận Chương 6 và hạn chế ở 3.5/6.7.

- **7.1:** giữ bảng kế hoạch/thực tế; phân biệt mốc dự kiến 18/10 với ngày thực hiện 29/09 và tên artifact mang ngày dự kiến. Lý do “làm song song, chạy ngoài giờ” chỉ giữ nếu nhật ký chứng minh; không cần dùng để tô đậm tiến độ.
- **7.2:** đánh giá từng mục tiêu theo tiêu chí ở 1.3; “đã chạy quy trình” và “đã đạt chất lượng” cần phân biệt. Sửa các câu khẳng định tuyệt đối của RQ2/RQ3.
- **7.3:** chỉ giữ những hạn chế ảnh hưởng kế hoạch tiếp theo; dẫn lại 6.7 thay vì lặp toàn bộ.
- **7.4:** giữ công việc, mốc, đầu ra và điều kiện hoàn thành; phân biệt việc đã nằm trong PLAN với đề xuất cần bổ sung. Không tự xem lịch phân tích mới là đã được duyệt chỉ vì đưa vào báo cáo.
- **7.5:** một đoạn kết luận ngắn gắn ba câu hỏi nghiên cứu và việc còn lại; sửa K15. Bỏ lối tu từ “hệ thống biết giới hạn của mình”, thay bằng “báo cáo đã xác định các giới hạn…”.

## 5. Quy ước biên tập dùng cho các lượt sửa tiếp theo

| Từ/cụm đang dùng | Cách viết ưu tiên trong lời văn |
|---|---|
| metric | chỉ số đánh giá |
| dev / test / train | tập phát triển / kiểm tra / huấn luyện; ghi tên tắt sau lần giải thích đầu |
| posterior | xác suất dự đoán theo thời gian; giữ thuật ngữ gốc khi cần phân biệt về xác suất |
| onset / offset | thời điểm bắt đầu / kết thúc |
| grounded caption / hợp đồng căn cứ | mô tả dựa trên sự kiện; quy tắc kiểm tra bằng chứng |
| vị từ thời gian | điều kiện về quan hệ thời gian |
| leakage group | nhóm bản ghi có chung hoặc trùng nội dung, phải nằm cùng tập |
| duration prior / ưu tiên thời lượng | thông tin thời lượng từ dữ liệu huấn luyện; diễn giải riêng độ dài và khoảng cách |
| artifact | tệp kết quả hoặc tệp cấu hình đã lưu, tùy đối tượng |
| run / seed / ensemble / ablation | lần huấn luyện / hạt giống ngẫu nhiên / kết hợp mô hình / thí nghiệm loại bỏ từng thành phần |
| parity / phục vụ | độ khớp đầu ra khi triển khai / chạy suy luận cho ứng dụng |
| lớp gộp / lớp con | chọn thống nhất lớp lớn–lớp con hoặc nhãn cấp 1–cấp 2; không đổi class_id trong dữ liệu |

Không dịch cứng tên mô hình, metric chuẩn hay class_id. Giải thích một lần rồi dùng nhất quán. Một đoạn tập trung một ý: vấn đề → cách làm → bằng chứng → giới hạn. Đưa ví dụ trước công thức khó. Tách câu có nhiều mệnh đề và ngoặc, nhưng không ép mọi câu vào một độ dài máy móc.

**Ví dụ biên tập, chưa áp dụng vào báo cáo:**

> Gốc (4.5.1): “Thiết kế này có chủ ý: bộ sinh không thể bịa một nguồn âm mà nó chưa từng thấy bằng chứng, và căn cứ trở thành một bất biến cấu trúc thay vì một mục tiêu mềm.”
>
> Đề xuất: “Bộ sinh mô tả sử dụng danh sách sự kiện làm nguồn thông tin. Ở chế độ có ràng buộc, ngữ pháp chỉ cho phép dùng tên lớp và thời điểm có trong danh sách này. Cách làm hạn chế việc thêm thông tin không có bằng chứng, nhưng không sửa được sự kiện do mô hình âm thanh dự đoán sai.”

**Thứ tự sửa:** chốt cách gọi và các lỗi K01–K16; biên tập Chương 1 → 2 → 3 → 4 → 5 → 6 → 7; viết lại tóm tắt sau khi nội dung đã ổn định; cuối cùng dựng lại Word, cập nhật fields và kiểm PDF. Trong mỗi chương, sửa tiêu đề trước, rồi từng mục, bảng/hình và tham chiếu. Không sửa số trong bảng sinh tự động bằng tay.

## 6. Danh sách tiêu đề nên đổi

Các mục không nêu dưới đây có thể giữ tên ở vòng sửa đầu. Đây là đề xuất biên tập, chưa áp dụng vào nguồn hay DOCX.

| Mục | Tiêu đề hiện tại | Đề xuất |
|---|---|---|
| 1.4.1 | RQ1 — Chuyển giao từ DataSEC sang DataSED | Hiệu quả học chuyển giao |
| 1.4.2 | RQ2 — Mức căn cứ và ảo giác của mô tả | Độ chính xác của mô tả theo bằng chứng |
| 1.4.3 | RQ3 — Truy hồi có cấu trúc, vector và lai | Hiệu quả các phương pháp truy hồi |
| 1.6 | Đóng góp dự kiến và bằng chứng hiện có | Đóng góp của đề tài |
| 2.1.1 | Nhãn yếu, nhãn mạnh và tính đa âm | Các loại nhãn âm thanh |
| 2.2.1 | Metric theo khung, theo đoạn và theo sự kiện | Các mức đánh giá kết quả phát hiện |
| 2.2.2 | Trung bình micro và macro | Hai cách tổng hợp điểm F1 |
| 2.2.4 | Mức tham chiếu từ ghi âm thực | Kết quả từ nghiên cứu trước |
| 2.3 | Hậu xử lý posterior thành sự kiện | Xác định khoảng thời gian sự kiện |
| 2.3.1 | Ngưỡng và ưu tiên thời lượng | Ngưỡng và thông tin thời lượng |
| 2.3.2 | Hộp bao sự kiện cSEBB | Phương pháp cSEBB |
| 2.5 | Sinh mô tả có căn cứ và hiện tượng ảo giác | Sinh mô tả dựa trên bằng chứng |
| 2.6 | Sinh tăng cường truy hồi và truy hồi lai | Truy hồi và trả lời câu hỏi |
| 2.6.2 | Embedding đa ngữ và bộ lọc có cấu trúc | Biểu diễn văn bản và lọc kết quả |
| 2.7 | Tổng hợp và định vị đề tài | Tổng hợp nghiên cứu liên quan |
| Chương 3 | Dữ liệu và quy trình chuẩn bị dữ liệu | Dữ liệu và tiền xử lý |
| 3.1 | Hai bộ dữ liệu | Giới thiệu dữ liệu |
| 3.2 | Hệ lớp: 22 lớp gộp và 21 lớp đa âm | Hệ thống nhãn |
| 3.3 | Quy trình chuẩn bị dữ liệu D0–D4 | Quy trình chuẩn bị dữ liệu |
| 3.3.1 | Kiểm chứng tệp nén và kiểm kê (D0–D1) | Kiểm tra dữ liệu đầu vào |
| 3.3.2 | Hợp đồng chú giải (D2) | Chuẩn hóa và kiểm tra nhãn |
| 3.3.3 | Khử trùng lặp nội bộ và xuyên bộ dữ liệu (D3) | Phát hiện và xử lý dữ liệu trùng |
| 3.3.4 | Chia tập theo nhóm rò rỉ (D4) | Chia tập và phòng tránh rò rỉ |
| 3.4 | Độ phủ nhãn và độ nhất quán chú giải | Chất lượng nhãn |
| 3.4.1 | Độ phủ nhãn gốc đa âm | Các bản ghi thiếu nhãn |
| 3.4.2 | Độ nhất quán giữa hai lần chú giải | Mức độ thống nhất của nhãn |
| 3.5 | Rủi ro dữ liệu còn lại | Hạn chế của dữ liệu |
| Chương 4 | Phương pháp | Phương pháp nghiên cứu |
| 4.3.1 | Hàm mất mát và trọng số lớp dương | Hàm mất mát và cân bằng lớp |
| 4.3.2 | Thế hệ v1 và ba nhánh của RQ1 | Mô hình ban đầu và các phương án khởi tạo |
| 4.3.3 | Thế hệ SED v2 | Mô hình cải tiến |
| 4.3.4 | Track 2: bộ mã hóa tiền huấn luyện theo khung | Mô hình tiền huấn luyện theo khung |
| 4.3.5 | Ensemble và tập ứng viên | Kết hợp và lựa chọn mô hình |
| 4.4 | Hậu xử lý và lựa chọn trên dev | Hậu xử lý kết quả phát hiện |
| 4.4.1 | Ngưỡng và ưu tiên thời lượng | Xử lý theo ngưỡng và thời lượng |
| 4.5 | Sinh mô tả có căn cứ | Sinh mô tả từ sự kiện |
| 4.5.1 | Ba ràng buộc G1–G3 | Các quy tắc kiểm tra mô tả |
| 4.5.2 | Bốn chế độ sinh | Các phương pháp sinh mô tả |
| 4.6.1 | Kho sự kiện và tài liệu truy hồi | Lưu trữ và biểu diễn sự kiện |
| 4.6.2 | Ba chế độ truy hồi và vị từ thời gian | Các phương pháp tìm kiếm sự kiện |
| 4.6.3 | Bộ phân tích câu hỏi | Chuyển câu hỏi thành điều kiện tìm kiếm |
| 4.6.4 | Trả lời ràng buộc bằng chứng | Tạo câu trả lời kèm bằng chứng |
| 4.7 | Giao thức đánh giá | Thiết kế đánh giá |
| 4.7.1 | Chọn trên dev, kiểm tra một lần | Quy trình lựa chọn và đánh giá |
| 4.7.2 | Metric cho mô tả và truy hồi | Chỉ số đánh giá mô tả và truy hồi |
| 4.7.3 | Khoảng tin cậy bootstrap | Đánh giá độ bất định của kết quả |
| 5.1 | Tổ chức mã nguồn và nguyên tắc ranh giới | Tổ chức mã nguồn |
| 5.3 | Triển khai và kịch bản demo | Triển khai và minh họa sử dụng |
| 5.4 | Tái lập và truy nguồn kết quả | Lưu vết và tái lập thí nghiệm |
| Chương 6 | Kết quả hiện có và thảo luận | Kết quả và thảo luận |
| 6.2 | RQ1 — Tiền huấn luyện thêm trên DataSEC | Hiệu quả học chuyển giao |
| 6.2.1 | RQ1 với công thức v1 | Kết quả với mô hình ban đầu |
| 6.2.2 | RQ1 với công thức v2 | Kết quả với mô hình cải tiến |
| 6.3 | Tiến triển của mô hình SED | Kết quả phát hiện sự kiện âm thanh |
| 6.3.1 | Chẩn đoán lỗi và giới hạn trên | Phân tích lỗi phát hiện |
| 6.3.2 | SED v2 và các ablation | Ảnh hưởng của từng thành phần mô hình |
| 6.3.3 | Vòng chọn cuối S13 và kết quả test | Lựa chọn mô hình và kết quả kiểm tra |
| 6.4 | RQ2 — Mô tả có căn cứ | Kết quả sinh mô tả |
| 6.5 | RQ3 — Truy hồi và câu trả lời có bằng chứng | Kết quả truy hồi và trả lời câu hỏi |
| 6.6 | Bộ phân tích câu hỏi và độ khớp khi phục vụ | Kiểm tra phân tích câu hỏi và triển khai |
| 6.7 | Thảo luận và các mối đe dọa đến tính hợp lệ | Thảo luận và giới hạn đánh giá |
| Chương 7 | Tiến độ, kết luận giữa kỳ và kế hoạch tiếp theo | Tiến độ và kế hoạch tiếp theo |
| 7.1 | Đối chiếu tiến độ với kế hoạch | Tiến độ thực hiện |
| 7.2 | Mức độ đạt mục tiêu tại giữa kỳ | Kết quả đạt được |
| 7.4 | Kế hoạch giai đoạn tiếp theo | Kế hoạch tiếp theo |

Mã RQ1–RQ3 vẫn giữ trong bảng câu hỏi nghiên cứu và câu mở đầu mục. Tên mô hình/mã run vẫn giữ trong bảng cấu hình và phụ lục để truy nguồn. Đổi tiêu đề không được xóa khả năng liên hệ kết quả với câu hỏi nghiên cứu.
