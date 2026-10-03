# GIỚI THIỆU

## Vì sao chọn đề tài

Giám sát tiếng ồn ngoài trời thường chỉ dựa vào mức ồn trung bình. Con số này cho biết khu vực ồn đến đâu, nhưng không cho biết tiếng ồn đến từ nguồn nào, xuất hiện lúc nào và kéo dài bao lâu. Hai đêm có cùng mức ồn có thể do xe cộ hoặc do công trường, và mỗi trường hợp cần cách xử lý khác nhau. Vì vậy, nhóm quan tâm đến bài toán phát hiện sự kiện âm thanh (Sound Event Detection – SED): trong một bản ghi dài, xác định nguồn âm nào xuất hiện, bắt đầu (onset) và kết thúc (offset) lúc nào [@mesaros2021tutorial].

Bài toán này khó hơn việc phân loại một đoạn âm thanh đã cắt sẵn, vì ba lý do. Thứ nhất, nhiều nguồn âm có thể vang lên cùng lúc (đa âm, polyphonic) [@mesaros2021tutorial]. Thứ hai, dữ liệu có đánh dấu chính xác thời điểm (nhãn mạnh) tốn công làm nên thường ít, còn nhãn yếu chỉ cho biết lớp nào có mặt trong bản ghi [@mesaros2021tutorial]. Thứ ba, khi kết quả phát hiện được viết lại thành câu văn cho người đọc, mô hình ngôn ngữ dễ viết ra những điều không có trong dữ liệu đầu vào. Hiện tượng này gọi là ảo giác (hallucination) [@ji2023hallucination].

Nhóm dùng hai bộ dữ liệu công bố năm 2025 của cùng một nhóm tác giả: DataSEC gồm các đoạn âm thanh rời để phân loại, và DataSED gồm các bản ghi dài có đánh dấu thời gian [@fredianelli2025environmental]. Hai bộ dữ liệu cùng miền nên có thể hỗ trợ nhau (học chuyển giao), nhưng cũng có nguy cơ chứa cùng một bản ghi gốc. Nếu không kiểm soát, mô hình sẽ vô tình được huấn luyện trên chính dữ liệu dùng để kiểm tra.

Từ đó, đề tài xây dựng một hệ thống khép kín gồm bốn bước: nhận bản ghi và phát hiện sự kiện; viết mô tả chỉ dựa trên các sự kiện đã phát hiện; lưu sự kiện có cấu trúc; và trả lời câu hỏi về lịch sử bằng kỹ thuật sinh tăng cường truy hồi (Retrieval-Augmented Generation – RAG). RAG là cách cho mô hình ngôn ngữ tra cứu một kho dữ liệu bên ngoài trước khi trả lời [@lewis2020rag]. Mỗi câu trả lời phải nêu được bản ghi và khoảng thời gian làm bằng chứng.

## Bài toán đặt ra

Với một bản ghi âm liên tục $x(t)$, hệ thống cần cho ba đầu ra liên quan với nhau. Đầu ra thứ nhất là danh sách sự kiện (dòng thời gian):

$$E = \{(c_i,\ t^{on}_i,\ t^{off}_i,\ s_i)\}_{i=1}^{N}$$

⟪eqno:timeline⟫

trong đó $c_i$ là lớp nguồn âm, $t^{on}_i < t^{off}_i$ là thời điểm bắt đầu và kết thúc (giây), $s_i \in [0, 1]$ là độ tin cậy, và các sự kiện được phép chồng nhau. Đầu ra thứ hai là một đoạn mô tả $y$ chỉ được viết từ $E$, sao cho mọi nguồn âm được nhắc đến đều có trong $E$:

$$\operatorname{mention}(y) \subseteq \{\, c_i : (c_i, t^{on}_i, t^{off}_i, s_i) \in E \,\}$$

⟪eqno:grounding⟫

Đầu ra thứ ba là câu trả lời cho một câu hỏi tự nhiên về lịch sử các bản ghi, kèm bằng chứng dạng (mã bản ghi, khoảng thời gian).

Điều kiện ⟪eq:grounding⟫ giúp phân biệt đề tài với việc viết mô tả âm thanh tự do, vì máy có thể kiểm tra được điều kiện này. Tuy nhiên điều kiện chỉ bảo đảm mô tả **khớp với danh sách sự kiện mà hệ thống dự đoán**, chứ không bảo đảm khớp với âm thanh thật: nếu bước phát hiện sai thì mô tả cũng sai theo. Nhóm luôn tách riêng hai mức đúng này khi đánh giá (Chương 4 và 6).

## Mục tiêu và câu hỏi nghiên cứu

Mục tiêu chung là dựng một quy trình tái lập được, đi từ dữ liệu công bố đến câu trả lời có bằng chứng, và đo ba điều mà các hệ thống mô tả âm thanh thường bỏ qua: học chuyển giao có thật sự giúp không, mô tả có bị ảo giác không, và bộ lọc có cấu trúc đóng góp gì cho việc truy hồi. Cụ thể gồm bảy việc: (1) chuẩn bị dữ liệu có nguồn gốc rõ và tập chia cố định; (2) huấn luyện mô hình phân loại 22 lớp trên DataSEC; (3) huấn luyện mô hình SED 21 lớp trên DataSED; (4) đo hiệu quả của việc chuyển giao DataSEC sang DataSED; (5) sinh mô tả có căn cứ và đo ảo giác; (6) truy hồi kết hợp lọc và tìm theo ngữ nghĩa; (7) làm ứng dụng web minh họa từ đầu đến cuối.

Ba câu hỏi nghiên cứu (Research Question – RQ) chính được tóm tắt ở ⟪tbl:rq⟫. Câu hỏi phụ về phân loại lớp con chỉ trả lời được trên DataSEC vì DataSED không có nhãn lớp con (xem Chương 6).

@@CAP:tbl:rq|Ba câu hỏi nghiên cứu chính@@

| Mã | Câu hỏi | Cách trả lời |
|---|---|---|
| RQ1 | Huấn luyện thêm trên DataSEC có giúp SED tốt hơn so với chỉ dùng mô hình tiền huấn luyện AudioSet không? | So nhánh C (AudioSet rồi DataSEC) với nhánh B (chỉ AudioSet), nhiều lần chạy, có khoảng tin cậy |
| RQ2 | Bắt mô tả bám sát danh sách sự kiện thì giảm ảo giác bao nhiêu so với viết tự do? | So tỷ lệ ảo giác và bỏ sót giữa các cách sinh, trên cùng một kết quả SED |
| RQ3 | Truy hồi kết hợp (lọc cứng và xếp hạng theo ngữ nghĩa) so với chỉ lọc hoặc chỉ ngữ nghĩa thì sao? | So nDCG@10, Recall và độ đúng bộ lọc; độ liên quan tính bằng máy từ nhãn gốc |

@@NOTE:Nguồn: docs/SYSTEM.md §1.3; ADR-0002; ADR-0021.@@

Với RQ1, nhóm so ba nhánh: A học từ đầu, B dùng trọng số tiền huấn luyện AudioSet [@kong2020panns], C dùng AudioSet rồi huấn luyện tiếp trên DataSEC. Phép so sánh đúng là **C với B**, vì C với A trộn lẫn tác dụng của tiền huấn luyện nói chung với tác dụng riêng của DataSEC. Với RQ2, nhóm so các cách sinh mô tả (Chương 4) ở mức *oracle* (dùng sự kiện từ nhãn gốc) và mức *đầu–cuối* (dùng sự kiện do SED dự đoán).

## Phạm vi và giới hạn

Đề tài xử lý âm thanh môi trường ngoài trời theo lô (không phải thời gian thực), gồm SED 21 lớp trên DataSED, phân loại 22 lớp trên DataSEC, mô tả tiếng Anh (để đánh giá) và tiếng Việt (cho giao diện), cùng truy vấn theo lớp, thời gian, thời lượng, độ tin cậy và quan hệ trước–sau.

Một số hướng bị loại có chủ ý vì dữ liệu không đủ cơ sở (ADR-0001): nhận dạng nội dung lời nói hay người nói; suy ra tội phạm, ý định, tai nạn, tình huống khẩn cấp; chấm điểm nguy hiểm. Mô tả chỉ nói về *nguồn âm quan sát được*, không nói về *tình huống*: "phát hiện tiếng kính vỡ lúc 5,4 s" là hợp lệ, còn "phát hiện đột nhập" thì không. Xử lý thời gian thực và định vị nguồn âm trong không gian cũng nằm ngoài phạm vi.

## Đóng góp dự kiến

Đề cương nêu bốn đóng góp dự kiến. ⟪tbl:contrib⟫ cho biết ở mốc giữa kỳ, đóng góp nào đã có bằng chứng, đóng góp nào còn là định hướng. Nhóm **chưa** khảo sát văn liệu có hệ thống, nên chưa dám khẳng định tính mới so với công trình khác; việc này để giai đoạn sau (Chương 7).

@@CAP:tbl:contrib|Bốn đóng góp dự kiến và mức bằng chứng ở giữa kỳ@@

| Mã | Đóng góp dự kiến | Bằng chứng đã có | Chưa khẳng định |
|---|---|---|---|
| C1 | Bộ sinh mô tả có điều kiện bám sát sự kiện, máy kiểm tra được | Ràng buộc có kiểm thử tự động; trên tập test, bộ sinh có ràng buộc không còn ảo giác nguồn âm | Tính mới so với văn liệu |
| C2 | Bộ chỉ số đo mức bám sát của mô tả, không cần câu mẫu | Đo ảo giác, bỏ sót, thứ tự, từ cấm, có khoảng tin cậy; đối chiếu 60 mô tả với một người đọc | Mẫu đối chiếu nhỏ |
| C3 | Đo chuyển giao có kiểm soát trùng lặp giữa hai bộ dữ liệu | Tìm ra ba nhóm trùng, loại 11 đoạn; RQ1 cho kết quả âm tính | Việc "các nghiên cứu khác thường không kiểm tra" |
| C4 | RAG trên dòng thời gian sự kiện, có điều kiện thời gian | Bốn điều kiện thời gian viết bằng SQL; bộ lọc đúng 100%; câu trả lời không có khẳng định thiếu bằng chứng | Tính mới so với văn liệu |

@@NOTE:Nguồn: docs/PAPER_NOTES.md §2; docs/RELATED_WORK.md §9.@@

## Bố cục báo cáo

Chương 2 giới thiệu kiến thức nền. Chương 3 mô tả dữ liệu và cách kiểm soát trùng lặp. Chương 4 trình bày phương pháp. Chương 5 mô tả hệ thống đã triển khai. Chương 6 báo cáo kết quả, kể cả kết quả âm tính hoặc kém đi. Chương 7 đối chiếu tiến độ, nêu kết luận giữa kỳ và kế hoạch tiếp theo.
