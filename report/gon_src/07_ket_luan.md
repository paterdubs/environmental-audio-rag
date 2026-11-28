# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Chương này tóm tắt kết quả, trả lời ba câu hỏi nghiên cứu, nêu các hạn chế và hướng phát triển. Mọi con số trích từ Chương 6.

Kết luận chung của khóa luận: **trong hệ thống này, độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào bước phát hiện sự kiện, và cụ thể là vào độ phủ sự kiện.** Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện, và bộ lọc cứng chỉ trả bản ghi có sự kiện đã lưu thỏa điều kiện. LBR chính nâng F1 theo sự kiện micro trên tập kiểm tra từ 0,1806 lên 0,2965 nhưng không tăng độ phủ sự kiện, nên không làm truy hồi hay mô tả tốt lên rõ rệt. Hai bước sau chỉ tốt lên khi độ phủ tăng: ở LBR ứng dụng (độ phủ sự kiện 0,8203, nDCG@10 kết hợp 0,670) và ở chế độ bổ sung khi truy hồi.

## Kết quả đạt được

- **Dữ liệu.** Kiểm tra trùng lặp ba tầng tìm ra ba nhóm bản ghi chung nguồn giữa DataSEC và DataSED; 11 đoạn DataSEC bị loại trước khi huấn luyện, và mọi tập chia được khóa bằng mã băm.
- **Phát hiện sự kiện.** Hệ cuối là hệ cơ sở cộng LBR. Trên 139 bản ghi kiểm tra, LBR chính đạt F1 theo sự kiện micro 0,2965 và macro 0,2356, so với 0,1806 và 0,1366 của hệ cơ sở; hiệu micro +0,1159 [+0,0741; +0,1593]. LBR ứng dụng đạt độ phủ sự kiện 0,8203 với độ chính xác theo giao nhau 0,7812 và được dùng trong ứng dụng minh họa.
- **Mô tả bám sát sự kiện.** Ràng buộc bằng ngữ pháp đưa ảo giác nguồn âm, suy diễn bối cảnh, gọi tên quá cụ thể và từ cấm về 0 ở cả bốn hệ SED; cách ràng buộc + phủ còn đưa bỏ sót về 0.
- **Truy hồi.** Bốn điều kiện quan hệ thời gian giữa hai sự kiện được cài bằng SQL; câu trả lời không có khẳng định thiếu bằng chứng; chế độ bổ sung cao hơn cả hai chế độ gốc ở cả bốn kho.
- **Ứng dụng.** Một ứng dụng web chạy trên máy cá nhân cho phép tải bản ghi, xem dòng thời gian, đọc mô tả song ngữ và hỏi bằng câu tự nhiên, với bằng chứng bấm được tới đúng khoảng thời gian.

## Trả lời các câu hỏi nghiên cứu

**Câu hỏi nghiên cứu 1 – Huấn luyện thêm trên DataSEC có giúp SED không?** Không có bằng chứng. Với cả hai thế hệ SED và nhiều lần huấn luyện, hiệu C − B về F1 theo sự kiện micro có khoảng tin cậy chứa 0 (SED v1: −0,0071 [−0,0164; +0,0021]; SED v2: −0,0029 [−0,0254; +0,0199]).

**Câu hỏi nghiên cứu 2 – Ràng buộc giảm ảo giác bao nhiêu?** So với danh sách sự kiện dự đoán, ảo giác nguồn âm của cách viết tự do vốn đã thấp (0,005 đến 0,022). Phần ràng buộc thật sự loại bỏ là suy diễn bối cảnh (0,259 đến 0,403 số mô tả, xuống 0) và gọi tên quá cụ thể (0,126 đến 0,140, xuống 0). Cái giá là bỏ sót khi danh sách sự kiện dày, và cách ràng buộc + phủ khắc phục được. So với nhãn gốc, mọi cách sinh đều bỏ sót khoảng 34% đến 42% số lớp có thật: độ đúng với âm thanh do SED quyết định.

**Câu hỏi nghiên cứu 3 – Truy hồi kết hợp có tốt hơn không?** Xét theo nDCG@10 thì không. Trên ba kho có độ phủ sự kiện thấp, chế độ kết hợp thấp hơn chế độ chỉ ngữ nghĩa (hiệu từ −0,075 đến −0,111); trên kho của LBR ứng dụng, chiều này đảo lại (+0,040). Điều bộ lọc đem lại là kết quả thỏa điều kiện (1,000 so với khoảng 0,27 của chế độ chỉ ngữ nghĩa). Chế độ bổ sung giữ ưu điểm đó cho phần đầu danh sách và cao hơn chế độ chỉ ngữ nghĩa từ +0,041 đến +0,097, đổi lại chỉ 29% đến 57% kết quả thỏa bộ lọc.

⟪tbl:goals⟫ đối chiếu bảy mục tiêu ở Chương 1 với mức đạt được.

@@CAP:tbl:goals|Bảy mục tiêu và mức đạt được@@

@@COLWIDTHS:34,14,52@@

| Mục tiêu | Mức đạt | Ghi chú |
|---|---|---|
| (1) Dữ liệu có nguồn gốc rõ, tập chia cố định | Đạt | Kiểm trùng ba tầng, cổng D4 đạt 5/5, tập chia khóa bằng SHA-256 |
| (2) Phân loại 22 lớp trên DataSEC | Đạt | Macro-F1 0,8466 trên tập kiểm tra |
| (3) SED 21 lớp và tinh chỉnh biên | Đạt một phần | LBR chính đạt F1 theo sự kiện micro 0,2965, khoảng 51% mức đồng thuận giữa hai lần gán nhãn; định vị biên vẫn là nút thắt |
| (4) Đo chuyển giao từ DataSEC sang DataSED | Đạt (kết quả âm tính) | Không có khác biệt đo được với cả hai thế hệ SED |
| (5) Mô tả bám sát sự kiện và đo ảo giác | Đạt | Không vi phạm so với dự đoán; so với nhãn gốc, lỗi do SED vẫn còn |
| (6) Truy hồi kết hợp lọc và ngữ nghĩa | Đạt một phần | Chế độ kết hợp thấp hơn chỉ ngữ nghĩa ở ba kho; chế độ bổ sung cao hơn cả hai |
| (7) Ứng dụng web từ đầu đến cuối | Đạt, có giới hạn | Chạy trên CPU; chưa có đăng nhập, chưa xử lý luồng, chưa thử với người dùng thật |

@@NOTE:Nguồn: tổng hợp từ Chương 3 đến Chương 6; mức đạt do nhóm đánh giá theo bằng chứng đã nêu.@@

## Mức khẳng định cho các đóng góp

Sau khi tra cứu văn liệu, mỗi đóng góp được trình bày là áp dụng và mở rộng kỹ thuật đã có. Đóng góp 1 (bộ sinh có ràng buộc) có bằng chứng mạnh nhất về tính đúng, nhưng tính đúng đó có được từ cấu tạo, và ứng dụng dùng mô tả theo mẫu. Đóng góp 2 (chỉ số bám sát) mở rộng các chỉ số ảo giác đã có. Đóng góp 3 (kiểm soát rò rỉ) áp dụng quy trình kiểm trùng vào cặp DataSEC–DataSED. Đóng góp 4 (RAG có điều kiện quan hệ giữa hai sự kiện) là đóng góp kỹ thuật bên cạnh các hệ lưu sự kiện kết hợp RAG đã có. Đóng góp 5 (LBR) là kết quả định lượng mạnh nhất của đề tài, nhưng có đánh đổi PSDS-2 và độ phủ sự kiện, và chưa được kiểm trên bộ dữ liệu khác. Đóng góp 6 (giao thức đánh giá) là quy trình của dự án, không phải phương pháp mới.

## Hạn chế

- **Chưa thử trên bản ghi thu tại Việt Nam** hay bất kỳ dữ liệu nào ngoài DataSEC và DataSED; kết quả 19 lớp chỉ là phép lọc lớp trên DataSED.
- **Tập đánh giá nhỏ.** Tập kiểm tra có 139 bản ghi có nhãn, nên khoảng tin cậy rộng: nửa độ rộng khoảng tin cậy của hiệu micro khoảng 0,022 đến 0,043. Một cải tiến nhỏ hơn cỡ đó không phân biệt được với nhiễu.
- **Huấn luyện SED không cho kết quả giống hệt nhau giữa các lần chạy**, nên mọi so sánh SED cần nhiều lần huấn luyện với các hạt giống ngẫu nhiên khác nhau.
- **LBR được thiết kế trên chính dữ liệu ngoài mẫu dùng để chọn.** Kiểm tra trên ba lần huấn luyện khác và trên tập kiểm tra giảm rủi ro quá khớp, nhưng LBR chưa được kiểm trên bộ dữ liệu khác.
- **Giới hạn của nhãn.** Độ đồng thuận 0,5785 chỉ đo trên 8 cặp; dung sai 0,2 s chặt hơn độ nhất quán của chính nhãn.
- **PSDS phụ thuộc dải ngưỡng**, và LBR đánh đổi PSDS-2 lấy F1 theo sự kiện.
- **Bộ đo mô tả dựa trên từ điển**, chỉ đối chiếu với một người đọc trên 60 mô tả, và bỏ lọt nguồn âm nằm ngoài hệ lớp.
- **Kết quả Câu hỏi nghiên cứu 3 với bộ lọc chuẩn** giả định bộ phân tích câu hỏi không sai; câu hỏi tổng quát kiểu "có những sự kiện gì trong bản ghi này?" chưa được hỗ trợ.
- **Rủi ro dữ liệu còn lại:** có thể trùng nguồn với AudioSet (không định lượng được); bốn lớp con DataSEC ít mẫu; bản DataSEC dùng chưa phải bản mới nhất.
- **Ứng dụng** chưa có đăng nhập nên chưa sẵn sàng đưa lên mạng công khai, và mức khớp của bản chạy trên CPU chưa được đo cho LBR ứng dụng.
- **Tra cứu văn liệu** ở mức khóa luận, không phải tổng quan hệ thống đầy đủ.

## Hướng phát triển

- **Thử thực địa.** Thu bản ghi tại Việt Nam (đường phố, công trường, khu dân cư) và đánh giá hệ thống trên đó, trước hết bằng kiểm tra định tính rồi bằng một tập nhỏ có nhãn. Đây là hướng ưu tiên nhất vì trả lời trực tiếp câu hỏi về tính thực tế.
- **Dữ liệu.** Dùng DataSEC bản 4 và chạy lại Câu hỏi nghiên cứu 1; gán nhãn lớp con cho một phần DataSED.
- **Phát hiện.** Kiểm LBR trên một bộ dữ liệu khác; huấn luyện chung nhãn mạnh của DataSED với nhãn yếu của DataSEC.
- **Đánh giá mô tả.** Mở rộng đối chiếu với nhiều người đọc và thêm chỉ số đo trực tiếp trên âm thanh.
- **Truy hồi.** Thay cách nối đơn giản của chế độ bổ sung bằng điểm trộn có trọng số chọn trên tập phát triển; hỗ trợ câu hỏi tổng quát về bản ghi đang mở; thử bộ phân tích câu hỏi với người dùng thật.
- **Ứng dụng.** Thêm đăng nhập, xử lý luồng liên tục, đo độ trễ trên nhiều máy.
