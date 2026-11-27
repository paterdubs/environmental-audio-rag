# TRIỂN KHAI HỆ THỐNG

Chương 4 trình bày phương pháp; chương này trình bày cách đóng gói phương pháp thành phần mềm chạy được. Thứ tự đi từ yêu cầu, công nghệ, kiến trúc, hai luồng xử lý chính, dữ liệu, đến giao diện và độ trễ. Các sơ đồ trong chương được sinh từ mã nguồn và tệp cấu hình, nên khớp với phiên bản mã hiện tại.

## Tình huống sử dụng và yêu cầu

**Người dùng giả định.** Nhóm thiết kế cho ba nhóm người dùng; đây là giả định của nhóm, chưa qua phỏng vấn người dùng thật. Thứ nhất, cán bộ quan trắc môi trường nhận phản ánh tiếng ồn, cần biết trong bản ghi vài phút có những nguồn nào, lúc nào, kéo dài bao lâu, mà không phải nghe hết. Thứ hai, ban quản lý tòa nhà hoặc khu dân cư, cần tìm khoảng giờ có tiếng nhạc hay máy móc trong lịch sử bản ghi. Thứ ba, nhóm nghiên cứu cảnh âm, cần truy vấn nhiều bản ghi theo lớp, thời gian và quan hệ trước–sau.

**Ba tác vụ chính.** (1) Tải một bản ghi lên và đọc dòng thời gian cùng mô tả. (2) Hỏi bằng câu tự nhiên về lịch sử, rồi sửa thẻ bộ lọc nếu hệ thống hiểu sai. (3) Bấm vào trích dẫn để mở đúng bản ghi và nghe lại đúng khoảng thời gian. Tác vụ thứ ba quan trọng: hệ thống không đòi người dùng tin vào mô tả, mà đưa bằng chứng để người dùng tự kiểm.

@@CAP:tbl:requirements|Yêu cầu, tính năng đáp ứng và bằng chứng@@

@@COLWIDTHS:8,30,32,30@@

| Mã | Yêu cầu | Tính năng | Bằng chứng |
|---|---|---|---|
| F1 | Nhận bản ghi, từ chối đầu vào sai | Nhận WAV, FLAC, OGG, MP3; từ chối tệp trên 50 MB hoặc dài hơn 600 s; tệp đã có thì trả mã cũ | Luồng tải lên (⟪fig:uploadflow⟫) |
| F2 | Cho biết nguồn nào, lúc nào, bao lâu | SED 21 lớp, có thời điểm bắt đầu và kết thúc | Event-F1 micro 0,2965 (LBR chính); recall 0,82, precision 0,78 (LBR ứng dụng) |
| F3 | Mô tả hai ngôn ngữ, bám sát sự kiện | Mô tả gộp theo lớp, có rào đón khi điểm thấp | Ảo giác và bỏ sót bằng 0 so với danh sách sự kiện (Chương 6) |
| F4 | Hỏi bằng tiếng Việt hoặc tiếng Anh | Bộ phân tích câu hỏi thành bộ lọc, thẻ sửa được | Đúng hoàn toàn 0,855 (câu theo mẫu) và 0,925 (câu diễn đạt lại) |
| F5 | Kết quả đúng điều kiện, có bằng chứng | Bộ lọc cứng; chế độ bổ sung có nhãn "gần khớp" | Khẳng định thiếu bằng chứng 0,000 (Chương 6) |
| N1 | Chạy trên máy cá nhân, dữ liệu không rời máy | Docker Compose, chạy không cần mạng, mô hình chạy trên máy | Mục "Kiến trúc triển khai" |
| N2 | Thời gian xử lý chấp nhận được | Suy luận một lần, cơ sở dữ liệu có chỉ mục | Trung vị 3,89 s mỗi bản ghi; truy vấn 0,22 s (⟪tbl:latency⟫) |
| N3 | Không kết luận ngoài bằng chứng | Danh sách từ cấm G3; không suy ra tội phạm hay tình huống khẩn cấp | Từ cấm bằng 0 với mô tả có ràng buộc |

@@NOTE:Nguồn: số liệu lấy từ Chương 6 và phép đo độ trễ; yêu cầu do nhóm đặt ra từ tình huống giả định.@@

Những gì sản phẩm **không** làm cũng là yêu cầu: không đo mức ồn dBA, không cảnh báo theo thời gian thực, chưa có đăng nhập người dùng, và chưa thử trên bản ghi ngoài hai bộ dữ liệu.

## Công nghệ sử dụng

⟪tbl:techstack⟫ liệt kê công nghệ theo tầng. Phiên bản được đọc từ các tệp khai báo phụ thuộc, không gõ tay; cột "vai trò" cho biết công nghệ đó làm gì trong hệ thống này.

@@CAP:tbl:techstack|Công nghệ sử dụng theo tầng@@

@@COLWIDTHS:13,20,22,37,8@@

@@INCLUDE:report/final_tables/f15_tech_stack.md@@

Ba lựa chọn cần nói lý do:

- **PostgreSQL với pgvector** thay cho một cơ sở dữ liệu vector riêng, vì bộ lọc theo lớp, điều kiện thời gian giữa hai sự kiện và xếp hạng vector cần nằm trong **một** câu SQL.
- **llama.cpp chạy trên máy** thay cho dịch vụ mô hình ngôn ngữ trên mạng, vì dữ liệu âm thanh và câu hỏi không rời máy, và ngữ pháp GBNF cho phép ép đầu ra theo lược đồ.
- **Hai dịch vụ tách nhau**: dịch vụ suy luận nạp PyTorch và các mô hình; dịch vụ API không nạp PyTorch, nên khởi động nhanh, kiểm thử được không cần GPU, và lỗi ở mô hình không làm hỏng phần lưu trữ. Một kiểm thử tự động chặn việc dịch vụ API dùng PyTorch.

## Kiến trúc triển khai

⟪fig:architecture⟫ là kiến trúc triển khai. Người dùng chỉ làm việc với giao diện web; giao diện gọi dịch vụ API qua HTTP. Dịch vụ API là điểm điều phối duy nhất: gọi dịch vụ suy luận để phân tích âm thanh và nhúng câu hỏi, gọi llama.cpp để phân tích câu hỏi, và đọc ghi kho sự kiện. Quy trình nghiên cứu không chạy khi phục vụ; nó chỉ cung cấp checkpoint và tham số đã khóa cho dịch vụ suy luận.

@@DIAGRAM:architecture@@

@@CAP:fig:architecture|Kiến trúc triển khai của hệ thống@@

@@NOTE:Nguồn: cấu hình Docker Compose, mã các dịch vụ và cấu hình mô hình ngôn ngữ.@@

**Dịch vụ suy luận** nạp một lần khi khởi động: mô hình SED, tham số ghép sự kiện, LBR, bộ sinh mô tả và mô hình nhúng BGE-M3. Mặc định dịch vụ chạy hệ cơ sở; demo bật thêm LBR ứng dụng. Dịch vụ báo cho giao diện biết hệ đang chạy có đúng là hệ đã khóa hay không, và giao diện hiển thị thông tin này.

**Dịch vụ API** nhận tệp, kiểm tra đầu vào, lưu trữ và điều phối. Mọi phản hồi theo một khuôn chung gồm bốn trường `success`, `data`, `error`, `meta`, nên giao diện xử lý lỗi theo một cách duy nhất. Khi một dịch vụ phụ thuộc chưa sẵn sàng, API trả mã lỗi 503 thay vì làm hỏng cả yêu cầu. Danh sách đầy đủ các điểm truy cập (endpoint) ở Phụ lục B.

## Hai luồng xử lý chính

**Luồng tải lên và phân tích** (⟪fig:uploadflow⟫). Dịch vụ API kiểm định dạng, dung lượng và độ dài, tính mã băm SHA-256 của tệp, rồi tìm trong kho: nếu tệp đã có, API trả lại mã bản ghi cũ mà không phân tích lại. Nếu chưa, API gửi tệp sang dịch vụ suy luận, nơi chạy toàn bộ luồng ở ⟪fig:dataflow⟫ và trả về dòng thời gian, mô tả, tài liệu truy hồi và vector. API ghi năm bảng (bản ghi, sự kiện, mô tả, bằng chứng của mô tả, tài liệu truy hồi) trong **một giao dịch**. Nếu dịch vụ suy luận lỗi hoặc ghi cơ sở dữ liệu lỗi, API hoàn tác và xóa tệp vừa lưu, để không bao giờ có tệp âm thanh không có bản ghi tương ứng.

@@DIAGRAM:uploadflow@@

@@CAP:fig:uploadflow|Luồng tải lên và phân tích một bản ghi@@

@@NOTE:Nguồn: mã dịch vụ API và dịch vụ suy luận.@@

**Luồng hỏi đáp** (⟪fig:queryflow⟫). Câu hỏi trước hết được gửi tới bộ phân tích: API gọi llama.cpp với lược đồ JSON, nhận về bộ lọc và trả cho giao diện dưới dạng thẻ để người dùng sửa. Khi người dùng chạy truy vấn, API nhúng câu hỏi bằng BGE-M3, rồi gửi một câu SQL vừa lọc theo điều kiện vừa xếp hạng theo khoảng cách cosine. Ở chế độ bổ sung, các chỗ còn trống được lấp bằng kết quả gần nghĩa. Câu trả lời chỉ trích dẫn các kết quả thỏa bộ lọc; kết quả gần nghĩa chỉ được nêu tên. Nếu llama.cpp không chạy, người dùng vẫn đặt bộ lọc bằng tay và truy vấn được.

@@DIAGRAM:queryflow@@

@@CAP:fig:queryflow|Luồng hỏi đáp: phân tích câu hỏi, truy hồi và trả lời có bằng chứng@@

@@NOTE:Nguồn: mã dịch vụ API, bộ phân tích câu hỏi và kho sự kiện.@@

## Kho sự kiện

⟪fig:erd⟫ là sơ đồ bảng của kho, đọc trực tiếp từ tệp tạo cơ sở dữ liệu. Kho gồm bảy bảng; xóa một bản ghi sẽ xóa theo sự kiện, mô tả và tài liệu của nó. Ba quyết định thiết kế đáng chú ý:

- Bảng `caption_evidence` nối mô tả với sự kiện. Đây chính là định nghĩa của "có căn cứ": một mô tả không có dòng bằng chứng nào là vi phạm.
- Bảng tài liệu truy hồi tách khỏi bảng mô tả, và mỗi vector ghi phiên bản mô hình nhúng, để đổi mô hình nhúng mà không phải sinh lại mô tả.
- Bảng sự kiện có một cột cho biết sự kiện đến từ nhãn gốc hay từ dự đoán, nên cùng một kho phục vụ được cả đánh giá lẫn demo.

@@DIAGRAM:erd@@

@@CAP:fig:erd|Sơ đồ bảng của kho sự kiện (PostgreSQL 16 và pgvector)@@

@@NOTE:Nguồn: tệp tạo cơ sở dữ liệu db/migrations/001_event_store.sql; bảng có hơn chín cột chỉ hiện chín cột đầu.@@

## Giao diện người dùng

Giao diện web có sáu phần: khung tải lên; danh sách bản ghi; dòng thời gian sự kiện (bấm vào sự kiện để nghe đúng đoạn); mô tả song ngữ kèm bằng chứng; khung hỏi bằng câu tự nhiên; và thanh trạng thái mô hình (⟪fig:demo1⟫). Mô tả hiển thị theo kiểu thông báo, mỗi lớp một dòng, ví dụ "Phát hiện: tiếng chim, 2 lần, 0,0–20,0 giây.", và lớp có điểm thấp được gắn nhãn "Có thể có (độ tin cậy thấp)".

![](report/gon_figures/f03a_demo_upload_timeline.png){width=12cm}

@@CAP:fig:demo1|Giao diện: thanh trạng thái, danh sách bản ghi, dòng thời gian và mô tả@@

@@NOTE:Nguồn: ảnh chụp giao diện ngày 24/11/2026; bản ghi trong demo chỉ lấy từ tập huấn luyện.@@

Khung hỏi đáp tách hai bước để người dùng kiểm soát bộ phân tích câu hỏi (⟪fig:demochip⟫): bấm "Câu hỏi" để xem bộ lọc mà hệ thống hiểu được, sửa thẻ nếu cần, rồi mới chạy truy vấn. Nhờ vậy lỗi của bộ phân tích hiện ra trước mắt người dùng, thay vì âm thầm làm sai kết quả.

![](docs/demo_screenshots/03-filter-chip.png){width=14cm}

@@CAP:fig:demochip|Giao diện: bộ lọc hiện thành thẻ sửa được trước khi truy vấn@@

@@NOTE:Nguồn: ảnh chụp giao diện ngày 24/11/2026.@@

Bấm vào một trích dẫn trong câu trả lời sẽ mở đúng bản ghi và tua tới đúng khoảng thời gian (⟪fig:demo2⟫). Các bản ghi thỏa bộ lọc đứng đầu và là phần duy nhất được trích làm bằng chứng; các bản ghi gần nghĩa được liệt kê riêng dưới nhãn "gần khớp".

![](report/gon_figures/f03b_demo_query_evidence.png){width=13cm}

@@CAP:fig:demo2|Giao diện: câu hỏi tự nhiên thành bộ lọc, câu trả lời kèm bằng chứng@@

@@NOTE:Nguồn: ảnh chụp giao diện; câu hỏi "Có tiếng chim trước tiếng còi xe không?" được hiểu thành điều kiện before.@@

## Độ trễ

⟪tbl:latency⟫ báo độ trễ của demo chạy trên CPU với LBR ứng dụng. Nhóm tải lên 10 bản ghi của tập huấn luyện, chọn đều theo độ dài (3,4 đến 179,6 s), và lặp truy vấn kết hợp 5 lần. Thời gian khởi động và nạp mô hình không tính vào bảng.

@@CAP:tbl:latency|Độ trễ của demo trên CPU@@

@@COLWIDTHS:46,10,22,22@@

@@INCLUDE:report/final_tables/f13_latency.md@@

Trung vị 3,89 s cho một lần tải lên và phân tích, tức hệ số thời gian thực 0,072: xử lý nhanh hơn thời gian thật khoảng 14 lần. Trường hợp chậm nhất so với độ dài (p95 bằng 0,294) rơi vào bản ghi ngắn nhất, nơi chi phí cố định của một lần gọi chiếm phần lớn. Truy vấn kết hợp có trung vị 0,22 s. Các số này đo trên một máy, một lần chạy, nên chỉ cho biết cỡ độ lớn.

Hệ thống chạy bằng Docker Compose với ba dịch vụ (cơ sở dữ liệu, suy luận, API kèm giao diện); mô hình ngôn ngữ chạy riêng bằng llama.cpp để dùng GPU. Ba lệnh dựng sẵn dùng để khởi động, kiểm tra và dừng hệ thống. Lịch sử demo gồm 20 bản ghi chọn **chỉ từ tập huấn luyện**, phủ đủ 21 lớp, để demo không bao giờ hiển thị dữ liệu kiểm tra. Hệ thống còn hai giới hạn: chưa có đăng nhập nên chưa sẵn sàng đưa lên mạng công khai, và chưa xử lý âm thanh dạng luồng liên tục.

Để kiểm hệ đang phục vụ có đúng là hệ đã đo, nhóm so đầu ra trên GPU với kết quả đã khóa: với LBR ứng dụng, 691 trên 692 sự kiện nằm trong dung sai 0,2 s. Bản demo chạy trên CPU; mức khớp trên CPU của LBR ứng dụng chưa được đo. Quy trình tái lập, kiểm thử và nhật ký thí nghiệm nằm ở Phụ lục B.
