# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Chương này tóm tắt những gì khóa luận đã làm được, đối chiếu với mục tiêu và câu hỏi nghiên cứu ở Chương 1, nêu mức khẳng định hợp lý cho từng đóng góp và đề xuất hướng phát triển. Mọi con số trích từ Chương 6; chương này không đưa số mới.

## Kết quả đạt được

Khóa luận xây dựng một quy trình tái lập được, đi từ hai bộ dữ liệu công bố đến câu trả lời có bằng chứng về lịch sử bản ghi âm môi trường.

- **Dữ liệu.** Kiểm tra trùng lặp ba tầng tìm ra ba nhóm bản ghi chung nguồn giữa DataSEC và DataSED; 11 đoạn DataSEC (0,22%) bị loại trước khi huấn luyện và mọi tập chia được khóa bằng mã băm. Chuyển giao vì vậy được đo trong điều kiện rò rỉ đã được kiểm soát.
- **Phát hiện sự kiện.** Hệ cuối là B0 kèm tầng tinh chỉnh biên và chấm lại hộp (LBR). Trên tập test có nhãn (139 bản ghi), LBR V2 đạt event-F1 micro 0,2965 và macro 0,2356, so với 0,1806 và 0,1366 của B0; hiệu micro +0,1159 [+0,0741; +0,1593]. Cấu hình ứng dụng V3 đạt recall giao nhau 0,8203 với precision 0,7812 và được dùng cho demo.
- **Mô tả có căn cứ.** Ràng buộc bằng ngữ pháp giải mã đưa ảo giác nguồn âm, suy diễn bối cảnh, gọi tên quá cụ thể và từ cấm về 0 ở cả bốn hệ SED được thử; nhánh constrained-cover còn đưa bỏ sót về 0.
- **Truy hồi.** Bốn điều kiện quan hệ thời gian giữa hai sự kiện được cài thành SQL; bộ lọc cứng đúng 100% và không có câu trả lời nào chứa khẳng định thiếu bằng chứng.
- **Ứng dụng.** Một ứng dụng web chạy cục bộ bằng Docker Compose cho phép tải bản ghi, xem dòng thời gian, mô tả song ngữ Anh–Việt và hỏi bằng câu tự nhiên, với bằng chứng bấm được về đúng khoảng thời gian.

## Trả lời các câu hỏi nghiên cứu

**RQ1 (DataSEC có giúp SED so với chỉ AudioSet?):** không có bằng chứng. Với cả hai công thức huấn luyện và nhiều seed, hiệu C − B về event-F1 micro có khoảng tin cậy chứa 0 (v1: −0,0071 [−0,0164; +0,0021]; v2: −0,0029 [−0,0254; +0,0199]). PSDS-2 của công thức v2 tăng có ý nghĩa khi xét riêng, nhưng chưa hiệu chỉnh cho việc so nhiều chỉ số. Đây là kết quả âm tính hợp lệ và được giữ nguyên.

**RQ2 (ràng buộc có giảm ảo giác không?):** có, theo cấu tạo, với cái giá là bỏ sót khi danh sách sự kiện dày (constrained: 0,081 với V3 so với 0,012 với f2) và được khử bằng biến thể cover. Kết luận này chỉ nói về mô tả so với **dự đoán** của SED, không nói mô tả đúng với âm thanh.

**RQ3 (bộ lọc có cấu trúc đóng góp gì?):** bảo đảm đúng ràng buộc cứng tuyệt đối, nhưng chất lượng xếp hạng bị chặn bởi việc SED dự đoán những sự kiện nào: nDCG@10 của f2, B0 và V2 không phân biệt được dù event-F1 khác nhau nhiều; V3 cao hơn vì độ phủ, đổi lại độ chính xác trích dẫn thấp hơn.

## Mức khẳng định cho các đóng góp

Sau đợt tra văn liệu tháng 11/2026 (Chương 2), khóa luận **không** khẳng định "lần đầu" cho đóng góp nào. C2 (chỉ số bám sát) là áp dụng và mở rộng so với các chỉ số ảo giác đã có; C3 (kiểm soát rò rỉ xuyên bộ dữ liệu) là áp dụng quy trình kiểm tra trùng vào cặp DataSEC–DataSED; C4 (RAG có điều kiện thời gian giữa hai sự kiện) là đóng góp kỹ thuật bên cạnh các hệ event store + RAG đã có. Điều khóa luận đóng góp là tích hợp các mắt xích có nguồn gốc xuyên suốt, kiểm chứng được bằng máy, và báo cáo trung thực cả kết quả âm tính và kết quả kém đi.

## Hạn chế

Các hạn chế chi tiết ở cuối Chương 6. Bốn hạn chế quan trọng nhất: tập test nhỏ (139 bản ghi) nên khoảng tin cậy rộng; huấn luyện SED không tất định nên so sánh cần nhiều seed; PSDS phụ thuộc lưới ngưỡng, và LBR đánh đổi PSDS-2 và độ phủ lấy độ chính xác biên; bộ đo mô tả dựa trên từ điển và chỉ đối chiếu với một người đọc. Ứng dụng chưa có xác thực người dùng nên chưa sẵn sàng triển khai công khai.

## Hướng phát triển

- **Dữ liệu.** Dùng bản DataSEC mới nhất (bản 4, sửa lỗi số tệp của lớp Music) và chạy lại RQ1; thêm nhãn lớp con cho một tập con DataSED để trả lời đầy đủ câu hỏi phụ về lớp con.
- **Phát hiện.** Kiểm LBR trên một bộ dữ liệu khác; huấn luyện chung nhãn mạnh của DataSED với nhãn yếu của DataSEC; soundscape tổng hợp từ đoạn DataSEC (kiểu DESED).
- **Đánh giá mô tả.** Mở rộng đối chiếu với người đọc (nhiều người, nhiều mô tả) và thêm chỉ số phía âm thanh như FLAM để bổ sung cho đánh giá theo dòng thời gian.
- **Truy hồi.** Hỗ trợ câu hỏi tổng quát về bản ghi đang mở; kiểm bộ phân tích câu hỏi với người dùng thật; so sánh trực tiếp với hệ event store + RAG khác trên cùng bộ truy vấn.
- **Ứng dụng.** Thêm xác thực, xử lý luồng liên tục và đo hiệu năng có thống kê.
