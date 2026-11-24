# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Chương này tóm tắt những gì khóa luận đã làm được, đối chiếu với mục tiêu và câu hỏi nghiên cứu ở Chương 1, nêu mức khẳng định hợp lý cho từng đóng góp và đề xuất hướng phát triển. Mọi con số trích từ Chương 6; chương này không đưa số mới.

Kết luận chung của khóa luận gói trong một luận điểm: **trong hệ thống này, độ đúng của mô tả và của câu trả lời bị chặn bởi bước phát hiện sự kiện. Ràng buộc ngữ pháp và bộ lọc cứng bảo đảm hai tầng sau không thêm lỗi ngoài lỗi của SED, nên cải tiến có tác dụng nằm ở SED (LBR nâng event-F1 micro trên test từ 0,1806 lên 0,2965) và ở độ phủ sự kiện khi truy hồi (backfill), không ở việc thêm mô hình ngôn ngữ.** Các mục dưới đây là bằng chứng cho từng vế.

## Kết quả đạt được

Khóa luận xây dựng một quy trình tái lập được, đi từ hai bộ dữ liệu công bố đến câu trả lời có bằng chứng về lịch sử bản ghi âm môi trường.

- **Dữ liệu.** Kiểm tra trùng lặp ba tầng tìm ra ba nhóm bản ghi chung nguồn giữa DataSEC và DataSED; 11 đoạn DataSEC (0,22%) bị loại trước khi huấn luyện và mọi tập chia được khóa bằng mã băm. Chuyển giao vì vậy được đo trong điều kiện rò rỉ đã được kiểm soát.
- **Phát hiện sự kiện.** Hệ cuối là B0 kèm tầng tinh chỉnh biên và chấm lại hộp (LBR). Trên tập test có nhãn (139 bản ghi), LBR V2 đạt event-F1 micro 0,2965 và macro 0,2356, so với 0,1806 và 0,1366 của B0; hiệu micro +0,1159 [+0,0741; +0,1593]. Cấu hình ứng dụng V3 đạt recall giao nhau 0,8203 với precision 0,7812 và được dùng cho demo.
- **Mô tả có căn cứ.** Ràng buộc bằng ngữ pháp giải mã đưa ảo giác nguồn âm, suy diễn bối cảnh, gọi tên quá cụ thể và từ cấm về 0 ở cả bốn hệ SED được thử; nhánh constrained-cover còn đưa bỏ sót về 0.
- **Truy hồi.** Bốn điều kiện quan hệ thời gian giữa hai sự kiện được cài thành SQL; mọi kết quả trả về thỏa bộ lọc đã áp trên sự kiện lưu trong kho (độ đúng bộ lọc 1,000; không đo đúng với âm thanh) và không có câu trả lời nào chứa khẳng định thiếu bằng chứng.
- **Ứng dụng.** Một ứng dụng web chạy cục bộ bằng Docker Compose cho phép tải bản ghi, xem dòng thời gian, mô tả song ngữ Anh–Việt và hỏi bằng câu tự nhiên, với bằng chứng bấm được về đúng khoảng thời gian.

## Trả lời các câu hỏi nghiên cứu

**RQ1 (DataSEC có giúp SED so với chỉ AudioSet?):** không có bằng chứng. Với cả hai công thức huấn luyện và nhiều seed, hiệu C − B về event-F1 micro có khoảng tin cậy chứa 0 (v1: −0,0071 [−0,0164; +0,0021]; v2: −0,0029 [−0,0254; +0,0199]). PSDS-2 của công thức v2 tăng có ý nghĩa khi xét riêng, nhưng chưa hiệu chỉnh cho việc so nhiều chỉ số. Đây là kết quả âm tính hợp lệ và được giữ nguyên.

**RQ2 (ràng buộc có giảm ảo giác không, và giảm bao nhiêu?):** có, theo cấu tạo. Ảo giác nguồn âm của cách viết tự do vốn đã thấp (0,005 đến 0,022), nên phần ràng buộc thực sự loại bỏ là suy diễn bối cảnh (0,259 đến 0,403 số mô tả, xuống 0) và gọi tên quá cụ thể (0,126 đến 0,140, xuống 0). Cái giá là bỏ sót khi danh sách sự kiện dày (constrained: 0,081 với V3 so với 0,012 với f2) và được khử bằng biến thể cover. Kết luận này chỉ nói về mô tả so với **dự đoán** của SED. Chấm lại so với nhãn gốc trên dev cho thấy mọi cách sinh đều bỏ sót khoảng 34–42% số lớp có thật ở f2, B0 và V2, và chênh lệch giữa các cách sinh nhỏ hơn nhiều so với chênh lệch giữa các hệ SED: độ đúng của mô tả với âm thanh do SED quyết định, ràng buộc chỉ bảo đảm bộ sinh không thêm lỗi.

**RQ3 (truy hồi kết hợp so với chỉ lọc hoặc chỉ ngữ nghĩa):** về nDCG@10, hybrid **không** tốt hơn chỉ xếp hạng ngữ nghĩa. Trên ba kho có độ phủ thấp (f2, B0, V2) hybrid thấp hơn vector_only có ý nghĩa (hiệu từ −0,075 đến −0,111), tập trung ở các câu hỏi nhiều lớp và quan hệ thời gian; trên kho V3, độ phủ cao, chiều này đảo lại (+0,040). Hybrid gần như trùng structured_only. Điều bộ lọc cứng đem lại là độ đúng ràng buộc (1,000 so với khoảng 0,27 của vector_only), còn chất lượng xếp hạng bị chặn bởi việc SED dự đoán những sự kiện nào: nDCG@10 của f2, B0 và V2 không phân biệt được dù event-F1 khác nhau nhiều, và V3 cao hơn vì độ phủ, đổi lại độ chính xác trích dẫn thấp hơn. Cơ chế này là cách giải thích khớp số liệu, chưa kiểm bằng thí nghiệm kiểm soát. Hệ quả thực tế của nó đã được kiểm: chế độ backfill (giữ danh sách hybrid, nối kết quả ngữ nghĩa có gắn nhãn cho đủ 10), ghi trước ở ADR-0049, cao hơn vector_only từ +0,041 đến +0,097 và cao hơn hybrid từ +0,057 đến +0,160 trên test, đổi lại chỉ 29–57% kết quả thỏa bộ lọc.

## Mức khẳng định cho các đóng góp

Sau đợt tra văn liệu tháng 11/2026 (Chương 2), mỗi đóng góp được trình bày là áp dụng và mở rộng của kỹ thuật đã có. C1 (bộ sinh mô tả có ràng buộc, kiểm được bằng máy) có bằng chứng mạnh nhất về tính đúng theo cấu tạo, nhưng chưa được so trực tiếp với bộ sinh có mốc thời gian của công trình khác, và ứng dụng dùng template chứ không dùng mô hình ngôn ngữ để viết mô tả. C2 (chỉ số bám sát) là áp dụng và mở rộng so với các chỉ số ảo giác đã có; C3 (kiểm soát rò rỉ xuyên bộ dữ liệu) là áp dụng quy trình kiểm tra trùng vào cặp DataSEC–DataSED; C4 (RAG có điều kiện thời gian giữa hai sự kiện) là đóng góp kỹ thuật bên cạnh các hệ event store + RAG đã có; ở nhóm câu hỏi quan hệ thời gian, hybrid vẫn thấp hơn vector_only, và backfill là cách khắc phục đã đo được. C5 (LBR) là cách khác tiếp cận bài toán biên mà SEBB và RED/EPN đã nêu, với bằng chứng tốt nhất của đề tài (hiệu micro +0,1159 trên test, cùng hướng ngoài mẫu) nhưng có đánh đổi PSDS-2 và độ phủ, thiết kế thăm dò trên tập ngoài mẫu dùng để chọn, và chưa được kiểm trên bộ dữ liệu khác. C6 (giao thức đánh giá) là quy trình của dự án, còn tái sử dụng thích nghi được công khai (Chương 6). Phần đóng góp chung là tích hợp các mắt xích có nguồn gốc xuyên suốt, kiểm chứng được bằng máy, và báo cáo cả kết quả âm tính lẫn kết quả kém đi.

⟪tbl:goals⟫ đối chiếu bảy mục tiêu nêu ở Chương 1 với mức đạt được.

@@CAP:tbl:goals|Bảy mục tiêu ở Chương 1 và mức đạt được@@

@@COLWIDTHS:34,14,52@@

| Mục tiêu | Mức đạt | Ghi chú |
|---|---|---|
| (1) Dữ liệu có nguồn gốc rõ, tập chia cố định | Đạt | Kiểm trùng ba tầng, cổng D4 5/5, tập chia khóa bằng SHA-256 (Chương 3) |
| (2) Phân loại 22 lớp trên DataSEC | Đạt | Macro-F1 0,8466 trên test; hiệu chuẩn nhiệt độ không cải thiện ECE (Chương 6) |
| (3) SED 21 lớp và tinh chỉnh biên | Đạt một phần | LBR V2 đạt event-F1 micro 0,2965, khoảng 51% mức đồng thuận giữa hai lần gán nhãn; định vị biên vẫn là nút thắt |
| (4) Đo chuyển giao DataSEC sang DataSED | Đạt (âm tính) | Không có khác biệt đo được ở cả hai công thức |
| (5) Mô tả có căn cứ và đo ảo giác | Đạt | Không vi phạm so với dự đoán; so với nhãn gốc, lỗi do SED vẫn còn |
| (6) Truy hồi kết hợp lọc và ngữ nghĩa | Đạt một phần | Lọc cứng đúng 1,000 nhưng hybrid thấp hơn vector_only ở ba kho; backfill hơn cả hai |
| (7) Ứng dụng web từ đầu đến cuối | Đạt, có giới hạn | Chạy cục bộ trên CPU; chưa có xác thực, chưa xử lý luồng, chưa thử với người dùng thật và bản ghi thực địa |

@@NOTE:Nguồn: tổng hợp từ Chương 3 đến Chương 6; mức đạt do nhóm đánh giá theo bằng chứng đã nêu.@@

## Hạn chế

Các hạn chế chi tiết ở cuối Chương 6. Năm hạn chế quan trọng nhất: chưa đo trên bản ghi thu tại Việt Nam hay ngoài họ DataSEC/DataSED, nên chưa biết hệ thống hoạt động thế nào ở bối cảnh mà Chương 1 nhắm tới; tập test nhỏ (139 bản ghi) nên khoảng tin cậy rộng; huấn luyện SED không tất định nên so sánh cần nhiều seed; PSDS phụ thuộc lưới ngưỡng, và LBR đánh đổi PSDS-2 và độ phủ lấy độ chính xác biên; bộ đo mô tả dựa trên từ điển và chỉ đối chiếu với một người đọc. Ứng dụng chưa có xác thực người dùng nên chưa sẵn sàng triển khai công khai.

## Hướng phát triển

- **Thử thực địa.** Thu bản ghi thực tế tại Việt Nam (đường phố, công trường, khu dân cư) và đánh giá hệ thống trên đó, trước hết bằng kiểm tra định tính rồi bằng một tập có nhãn nhỏ; đây là hướng ưu tiên nhất vì trả lời trực tiếp câu hỏi về tính thực tế.
- **Dữ liệu.** Dùng bản DataSEC mới nhất (bản 4, sửa lỗi số tệp của lớp Music) và chạy lại RQ1; thêm nhãn lớp con cho một tập con DataSED để trả lời đầy đủ câu hỏi phụ về lớp con.
- **Phát hiện.** Kiểm LBR trên một bộ dữ liệu khác; huấn luyện chung nhãn mạnh của DataSED với nhãn yếu của DataSEC; soundscape tổng hợp từ đoạn DataSEC (kiểu DESED).
- **Đánh giá mô tả.** Mở rộng đối chiếu với người đọc (nhiều người, nhiều mô tả) và thêm chỉ số phía âm thanh như FLAM để bổ sung cho đánh giá theo dòng thời gian.
- **Truy hồi.** Thay cách nối đơn giản của backfill bằng điểm trộn có trọng số chọn trên validation, và thêm dung sai cho các điều kiện thời gian; hỗ trợ câu hỏi tổng quát về bản ghi đang mở; kiểm bộ phân tích câu hỏi với người dùng thật; so sánh trực tiếp với hệ event store + RAG khác trên cùng bộ truy vấn.
- **Ứng dụng.** Thêm xác thực, xử lý luồng liên tục, đo độ trễ trên nhiều máy và đo parity của bản phục vụ trên CPU.
