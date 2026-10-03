# TRIỂN KHAI HỆ THỐNG

Chương này mô tả phần đã làm thành phần mềm: cách tổ chức mã nguồn, các dịch vụ, giao diện, cách chạy demo và cách bảo đảm tái lập. Nội dung chỉ gồm những gì đã có mã nguồn và đã được kiểm chứng bằng lệnh và tệp kết quả.

## Tổ chức mã nguồn

Mã nguồn chia ba tầng: `ml/` chứa phần xử lý dữ liệu, mô hình, huấn luyện, đánh giá, sinh mô tả và truy hồi; `scripts/` chỉ gọi các chức năng đó từ dòng lệnh và sinh báo cáo đo; `services/` chứa các dịch vụ phục vụ.

Hai nguyên tắc ranh giới được kiểm bằng máy chứ không chỉ là quy ước. Thứ nhất, dịch vụ API không được dùng PyTorch hay nạp checkpoint; một kiểm thử trong quy trình tích hợp liên tục (CI) chặn việc này, để API khởi động nhanh và kiểm thử được mà không cần GPU. Thứ hai, dữ liệu trao đổi giữa các thành phần tuân theo các hợp đồng JSON Schema trong `contracts/` (bản ghi, sự kiện, dòng thời gian, phản hồi suy luận, kết quả truy hồi, tham số hậu xử lý, bộ truy vấn, manifest của lần chạy), mỗi hợp đồng có kiểm thử riêng.

## Các dịch vụ

**Dịch vụ suy luận** (FastAPI) nạp **một lần** khi khởi động: mô hình SED đang phục vụ kèm tham số ghép sự kiện, các bộ sinh mô tả, và mô hình embedding BGE-M3. Mô hình phục vụ được chọn qua biến môi trường, và kiến trúc mạng được dựng lại từ manifest chứ không mã hóa cứng. Dịch vụ trả cờ `official` cho biết lần chạy đang phục vụ có đúng là hệ đã khóa (f2) hay không; giao diện hiển thị cờ này.

**Dịch vụ API** (FastAPI) nhận tệp tải lên, kiểm tra đầu vào, lưu trữ và điều phối. Mọi phản hồi theo một khuôn chung `{success, data, error, meta}`. Tệp bị từ chối nếu sai định dạng âm thanh, lớn hơn 50 MB hoặc dài hơn 600 s. Các chức năng chính: tải lên và phân tích; xem bản ghi cùng dòng thời gian, mô tả có bằng chứng và phát lại âm thanh; chuyển câu hỏi thành bộ lọc; truy hồi kèm câu trả lời có bằng chứng; xem trạng thái mô hình đang phục vụ.

**Cơ sở dữ liệu** PostgreSQL gồm bảy bảng. Ba quyết định thiết kế có ý nghĩa phương pháp: bảng `caption_evidence` nối mô tả với sự kiện — đó chính là định nghĩa của "có căn cứ", một mô tả không có dòng bằng chứng nào là vi phạm; bảng tài liệu truy hồi tách khỏi bảng mô tả để đổi mô hình embedding mà không phải sinh lại mô tả; và cột nguồn gốc trên bảng sự kiện phân biệt nhãn gốc với dự đoán. Truy vấn dùng chỉ mục thường cho lớp và thời gian, chỉ mục GIN cho mảng lớp, và chỉ mục đồ thị HNSW cho khoảng cách cosine.

**Giao diện web** (React) có sáu phần: khung tải lên; danh sách bản ghi; dòng thời gian sự kiện (bấm vào sự kiện để nghe đúng đoạn); mô tả song ngữ Anh–Việt kèm bằng chứng; khung hỏi bằng câu tự nhiên, hiển thị bộ lọc đã phân tích dưới dạng thẻ sửa được; và thanh trạng thái mô hình. Bấm vào một trích dẫn trong câu trả lời sẽ mở đúng bản ghi và tua tới đúng khoảng thời gian (⟪fig:demo⟫).

![](docs/thesis/figures/07_demo_interface.png){width=13cm}

@@CAP:fig:demo|Giao diện demo: tải lên, dòng thời gian, bộ lọc từ câu hỏi và bằng chứng@@

@@NOTE:Nguồn: docs/demo_screenshots/ (Playwright, 1440×900), ghép bằng scripts/build_thesis_figures.py; bản ghi trong lịch sử demo chỉ lấy từ tập train.@@

## Chạy demo

Hệ thống chạy cục bộ bằng Docker Compose: một container cơ sở dữ liệu, một container suy luận chạy trên CPU và một container API phục vụ cả giao diện (cổng 8088). Checkpoint và mô hình embedding được gắn vào ở chế độ chỉ đọc; các container đặt chế độ ngoại tuyến nên demo không cần mạng. Mô hình ngôn ngữ chạy trên máy chủ bằng llama.cpp để dùng GPU.

Ba script PowerShell gói các thao tác: khởi động (kiểm Docker, bật llama.cpp, dựng Compose, chờ dịch vụ sẵn sàng và cờ `official=true`, nạp lịch sử demo), kiểm tra, và dừng. Lịch sử demo gồm 15 bản ghi chọn tự động **chỉ từ tập train** sao cho phủ đủ 21 lớp, để demo không bao giờ phơi bày dữ liệu test. Một lượt kịch bản thật qua API đã chạy năm câu hỏi Anh/Việt (một lớp, hai lớp, quan hệ "trước", thời lượng) và lưu kết quả.

Trên một bản ghi train (`S-0016`), tải lên và phân tích bằng CPU trong container mất 2,012 s, một truy vấn kết hợp mất 0,250 s. Đây là số đo của một lượt trên một bản ghi, không phải phép đo hiệu năng có thống kê.

Hệ thống có hai giới hạn: chưa có xác thực người dùng nên **không** sẵn sàng triển khai công khai, và dịch vụ xử lý luồng mới chỉ là thư mục khung.

## Tái lập và kiểm thử

**Tái lập.** Mỗi lần chạy ghi một manifest gồm cấu hình, seed, phiên bản git kèm cờ `dirty` (cây làm việc có thay đổi chưa commit), mã băm của tập chia, hệ lớp, đặc trưng, tham số ghép sự kiện, và cờ hoàn tất. Lần chạy thiếu một trong các trường này, hoặc chạy trên cây làm việc bẩn, không được dùng cho số chính thức; các trường hợp vi phạm đã xảy ra đều được công khai (Chương 6). Dự đoán thô lưu thành tệp có SHA-256, tách khỏi bước tính chỉ số, nên quét lại ngưỡng trên dev không cần chạy lại mô hình, và tệp dự đoán test chỉ được sinh sau khi lựa chọn đã commit.

Trước khi viết báo cáo, mọi tệp được trích dẫn đã được "đóng băng": một script kiểm sự tồn tại và ghi SHA-256 của 11 lần chạy hoặc ensemble, các checkpoint ngoài và các tệp đầu vào cố định (tập chia, hệ lớp, từ điển, ngữ pháp, bộ truy vấn). Không thiếu tệp nào (Phụ lục B). Tài liệu `docs/REPRODUCE.md` tách hai quy trình: kiểm toán an toàn chạy trong bản sao hiện tại, và tái tạo số test chỉ làm trong một bản sao mới có phê duyệt, để không tạo thêm lượt chạm test ngoài sổ ghi. Các bảng số và hình trong báo cáo đều do script sinh từ các tệp trên, ghi rõ tệp nguồn và phiên bản git; chính tệp DOCX này được dựng từ nguồn Markdown bằng một script.

**Kiểm thử.** Bộ kiểm thử Python dùng pytest, kiểm tra mã bằng ruff. Ở lần kiểm cuối cùng ghi trong báo cáo kiểm tra đi kèm, ruff không báo lỗi và pytest đạt 744 kiểm thử, bỏ qua 4 kiểm thử cần PostgreSQL vì Docker đang tắt. Bộ kiểm thử phủ hợp đồng dữ liệu, ranh giới API–torch, các cổng dữ liệu (kể cả phép thử chứng minh cổng D4 không đạt rỗng), điều kiện thời gian SQL và Python, chỉ số bám sát sự kiện, ba ràng buộc G1–G3, tính trùng từng bit của đường sinh dự đoán, và tích hợp PostgreSQL. CI trên GitHub Actions chạy ruff, pytest, kiểm tra cấm `torch` trong API, kiểm thử và build giao diện.

Nhiều lỗi thật chỉ bị bắt nhờ chạy toàn bộ quy trình trên dữ liệu thật, trong đó lỗi ghép cửa sổ dự đoán (khoảng 10 s cuối mỗi bản ghi bị nhân đôi) làm đổi mọi số SED đã có; sau khi sửa, toàn bộ 11 lần chạy được tính lại và kết luận RQ1 không đổi.