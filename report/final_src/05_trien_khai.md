# TRIỂN KHAI HỆ THỐNG

Chương 4 trình bày phương pháp theo luồng dữ liệu; chương này trình bày cách phương pháp đó được đóng gói thành phần mềm chạy được. Thứ tự đi từ yêu cầu, công nghệ, kiến trúc, hai luồng xử lý chính, dữ liệu và giao diện lập trình, tới giao diện người dùng, độ trễ, cách chạy demo và cách bảo đảm tái lập. Mọi hình và bảng mô tả hệ thống trong chương đều do script đọc thẳng từ mã nguồn và tệp cấu hình, nên khớp với phiên bản mã ghi ở chân bảng.

## Tình huống sử dụng và yêu cầu

**Người dùng giả định.** Nhóm thiết kế cho ba nhóm người dùng, đều là **giả định của nhóm**; nhóm chưa phỏng vấn người dùng thật (đây là việc để sau, Chương 7). Thứ nhất, cán bộ hoặc kỹ sư quan trắc môi trường ở địa phương, nhận phản ánh tiếng ồn và cần biết trong bản ghi vài phút có những nguồn nào, vào lúc nào, kéo dài bao lâu, mà không phải nghe hết. Thứ hai, ban quản lý tòa nhà hoặc khu dân cư, cần chỉ ra khoảng giờ có tiếng nhạc hay máy móc trong lịch sử bản ghi. Thứ ba, nhóm nghiên cứu cảnh âm, cần truy vấn một tập bản ghi lớn theo lớp, thời gian và quan hệ trước–sau. Bối cảnh quy chuẩn và giới hạn của sản phẩm nêu ở Chương 1.

**Ba tác vụ đi qua giao diện.** (1) Tải một bản ghi WAV và đọc dòng thời gian cùng mô tả (tiếng Việt cho giao diện, tiếng Anh cho đánh giá). (2) Hỏi bằng câu tự nhiên về lịch sử, ví dụ về nguồn âm này xuất hiện trước nguồn âm kia, hay về sự kiện kéo dài quá một khoảng, rồi sửa các thẻ bộ lọc nếu bộ phân tích hiểu sai. (3) Kiểm chứng một câu trả lời bằng cách bấm trích dẫn để mở đúng bản ghi và nghe lại đúng khoảng thời gian. Tác vụ thứ ba quan trọng: hệ thống không đòi người dùng tin vào mô tả mà đưa bằng chứng để tự kiểm.

@@CAP:tbl:requirements|Yêu cầu, tính năng đáp ứng và bằng chứng@@

@@COLWIDTHS:8,30,30,32@@

| Mã | Yêu cầu | Tính năng | Bằng chứng trong báo cáo |
|---|---|---|---|
| F1 | Nhận bản ghi âm thanh, từ chối đầu vào sai | Tải lên WAV, FLAC, OGG, MP3; từ chối định dạng khác, trên 50 MB hoặc trên 600 s; bản ghi trùng mã băm trả lại mã cũ | Mục "Luồng xử lý của hệ thống" |
| F2 | Cho biết nguồn nào, lúc nào, bao lâu | SED đa âm 21 lớp trả sự kiện có onset và offset | Event-F1 micro 0,2965 (V2); recall giao nhau 0,82 và precision 0,78 (V3, ưu tiên phát hiện) |
| F3 | Mô tả bằng hai ngôn ngữ, bám sát sự kiện | Mô tả gộp theo lớp (đếm số lần, rào đón theo điểm tin cậy) tiếng Anh và tiếng Việt kèm bằng chứng | Ảo giác và bỏ sót bằng 0 so với dòng thời gian dự đoán ở cả bốn hệ (dev; Chương 6); số RQ2 trên test là của template gốc |
| F4 | Hỏi bằng tiếng Việt hoặc tiếng Anh | Bộ phân tích câu hỏi thành bộ lọc, thẻ sửa được | Hợp lược đồ 240/240; đúng hoàn toàn 0,855 (template) và 0,925 (diễn đạt lại) |
| F5 | Kết quả đúng điều kiện và có bằng chứng | Bộ lọc cứng, nối thêm kết quả gần nghĩa có nhãn (backfill); câu trả lời chỉ trích dẫn kết quả thỏa bộ lọc | Độ đúng bộ lọc 1,000; khẳng định thiếu bằng chứng 0,000 (Chương 6, RQ3) |
| N1 | Chạy trên máy cá nhân, dữ liệu không rời máy | Docker Compose, chế độ ngoại tuyến, mô hình chạy cục bộ | Mục "Chạy demo" |
| N2 | Thời gian xử lý chấp nhận được | Suy luận một lần, cơ sở dữ liệu có chỉ mục | Trung vị 3,89 s mỗi bản ghi (n = 10), truy vấn kết hợp 0,22 s (n = 5); mục "Độ trễ" |
| N3 | Không đưa kết luận ngoài bằng chứng | Từ cấm ở G3; không suy tội phạm, khẩn cấp (ADR-0001) | Từ cấm bằng 0 với mô tả có ràng buộc |
| N4 | Truy nguồn được | Manifest, mã băm, đóng băng artifact | Mục "Tái lập và kiểm thử" |

@@NOTE:Nguồn: các số lấy từ Chương 6, final_numbers_20261110.json và latency_lbrv3_20261123.json; yêu cầu do nhóm đặt ra từ tình huống giả định ở trên, không từ khảo sát người dùng.@@

Những gì sản phẩm **không** làm cũng thuộc yêu cầu: không đo mức ồn dBA, không cảnh báo thời gian thực, không có xác thực người dùng, và chưa thử trên bản ghi thu ngoài hai bộ dữ liệu.

## Công nghệ sử dụng

⟪tbl:techstack⟫ liệt kê công nghệ theo tầng. Phiên bản trong bảng không gõ tay mà đọc từ các tệp khai báo phụ thuộc (`requirements-*.txt`, `package.json`, `docker-compose.yml`, Dockerfile, cấu hình mô hình ngôn ngữ); với thư viện Python, đó là khoảng phiên bản cho phép. Cột "vai trò" nói công nghệ đó làm gì **trong hệ thống này**, kèm ADR ghi lý do chọn khi có.

@@CAP:tbl:techstack|Công nghệ sử dụng theo tầng, phiên bản đọc từ tệp cấu hình@@

@@COLWIDTHS:13,20,22,37,8@@

@@INCLUDE:report/final_tables/f15_tech_stack.md@@

Ba lựa chọn đáng nói lý do. **PostgreSQL với pgvector** thay cho một cơ sở dữ liệu vector riêng: bộ lọc theo lớp, điều kiện thời gian giữa hai sự kiện và xếp hạng cosine cần nằm trong **một** câu SQL để bộ lọc cứng luôn được áp trước khi xếp hạng (ADR-0005). **llama.cpp chạy cục bộ** thay cho dịch vụ mô hình ngôn ngữ trên mạng: dữ liệu âm thanh và câu hỏi không rời máy, và ngữ pháp giải mã GBNF cho phép ép đầu ra theo lược đồ (Chương 2). **Hai dịch vụ FastAPI tách nhau**: dịch vụ suy luận nạp PyTorch và các mô hình; dịch vụ API không được nạp PyTorch, nên khởi động nhanh, kiểm thử được không cần GPU và hỏng mô hình không kéo theo hỏng phần lưu trữ (ADR-0029).

Mã nguồn chia ba tầng: `ml/` chứa phần xử lý dữ liệu, mô hình, huấn luyện, đánh giá, sinh mô tả và truy hồi; `scripts/` gọi các chức năng đó từ dòng lệnh và sinh báo cáo đo; `services/` chứa các dịch vụ phục vụ và giao diện. Hai nguyên tắc ranh giới được kiểm bằng máy chứ không chỉ là quy ước. Thứ nhất, một kiểm thử trong quy trình tích hợp liên tục (CI) chặn việc dịch vụ API dùng PyTorch hay nạp checkpoint. Thứ hai, dữ liệu trao đổi giữa các thành phần tuân theo các hợp đồng JSON Schema trong `contracts/` (bản ghi, sự kiện, dòng thời gian, phản hồi suy luận, kết quả truy hồi, tham số hậu xử lý, bộ truy vấn, manifest của lần chạy), mỗi hợp đồng có kiểm thử riêng.

## Kiến trúc triển khai

⟪fig:architecture⟫ là kiến trúc triển khai. Người dùng chỉ làm việc với giao diện web; giao diện gọi dịch vụ API qua HTTP. Dịch vụ API là điểm điều phối duy nhất: gọi dịch vụ suy luận để phân tích âm thanh và nhúng câu hỏi, gọi llama.cpp để phân tích câu hỏi, và đọc ghi kho sự kiện. Quy trình nghiên cứu ngoại tuyến không chạy khi phục vụ; nó chỉ cung cấp checkpoint và tham số đã khóa, được gắn vào dịch vụ suy luận ở chế độ chỉ đọc.

![](report/final_figures/s03_deployment.png){width=13cm}

@@CAP:fig:architecture|Kiến trúc triển khai của hệ thống@@

@@NOTE:Nguồn: scripts/build_system_figures.py; đối chiếu services/, ml/inference/engine.py, docker-compose.yml.@@

⟪tbl:services⟫ liệt kê các thành phần chạy khi triển khai. Mô hình ngôn ngữ không nằm trong Compose mà chạy trên máy chủ để dùng GPU.

@@CAP:tbl:services|Các thành phần triển khai@@

@@COLWIDTHS:22,26,52@@

| Thành phần | Cách chạy | Vai trò |
|---|---|---|
| Cơ sở dữ liệu | Container `pgvector/pgvector:pg16`, có kiểm tra sức khỏe | Sự kiện, mô tả, tài liệu truy hồi, chỉ mục vector |
| Dịch vụ suy luận | Container (CPU), hồ sơ `app` | Nạp SED, LBR, bộ sinh mô tả, BGE-M3; trả sự kiện, mô tả, tài liệu và vector |
| Dịch vụ API và giao diện | Container, cổng 8088 | Nhận tệp, điều phối, truy hồi, phục vụ giao diện web |
| Mô hình ngôn ngữ (Qwen3.5-9B) | llama.cpp trên máy chủ, GPU | Chỉ phân tích câu hỏi thành bộ lọc |

@@NOTE:Nguồn: docker-compose.yml; ml/configs/caption_llm.yaml.@@

**Dịch vụ suy luận** nạp **một lần** khi khởi động: mô hình SED đang phục vụ kèm tham số ghép sự kiện, tầng LBR nếu bật, bộ sinh mô tả và mô hình embedding BGE-M3. Mô hình phục vụ được chọn qua biến môi trường, và kiến trúc mạng được dựng lại từ manifest chứ không mã hóa cứng. Mặc định dịch vụ phục vụ **B0** (5 mô hình theo fold, suy luận chồng lấn bước 5 s, gộp tam giác, cSEBB); demo bật thêm **LBR V3** ở điểm ưu tiên phát hiện (ADR-0042, ADR-0047). Mô hình trước đó (f2) giữ làm đường lùi. Dịch vụ trả cờ `official` cho biết lần chạy đang phục vụ có đúng là hệ đã khóa hay không, và giao diện hiển thị cờ này. Sự kiện của LBR được kẹp trong độ dài bản ghi, vì bộ tinh chỉnh có thể đẩy biên vượt cuối bản ghi; việc này không đổi số event-F1.

**Dịch vụ API** nhận tệp tải lên, kiểm tra đầu vào, lưu trữ và điều phối. Mọi phản hồi theo một khuôn chung `{success, data, error, meta}`, nên giao diện xử lý lỗi theo một cách duy nhất. Lỗi của dịch vụ phụ thuộc được trả về có mã riêng (ví dụ 503 khi dịch vụ suy luận hay llama.cpp chưa sẵn sàng) thay vì làm hỏng cả yêu cầu.

## Luồng xử lý của hệ thống

Hệ thống có hai luồng chính: phân tích một bản ghi mới, và trả lời một câu hỏi về lịch sử.

**Luồng tải lên và phân tích** (⟪fig:uploadflow⟫). Dịch vụ API kiểm định dạng, dung lượng và độ dài, tính SHA-256 của tệp, rồi tìm trong kho: nếu nội dung đã có, API trả lại mã bản ghi cũ mà không phân tích lại. Nếu chưa, API chuyển tệp sang dịch vụ suy luận, nơi chạy toàn bộ luồng dữ liệu của Chương 4 (⟪fig:dataflow⟫) và trả về dòng thời gian, mô tả hai ngôn ngữ, tài liệu truy hồi và vector của nó. API đối chiếu mã băm của tệp mà dịch vụ suy luận nhận với tệp đã lưu, rồi ghi năm bảng (bản ghi, sự kiện, mô tả, bằng chứng của mô tả, tài liệu truy hồi) trong **một giao dịch**. Hai nhánh lỗi được xử lý tường minh: dịch vụ suy luận không sẵn sàng thì trả 503 và xóa tệp vừa lưu; ghi cơ sở dữ liệu lỗi thì rollback và cũng xóa tệp, để không bao giờ có tệp âm thanh không có dòng bản ghi tương ứng.

![](report/final_figures/s04_upload_flow.png){width=15.5cm}

@@CAP:fig:uploadflow|Luồng tải lên và phân tích một bản ghi@@

@@NOTE:Nguồn: scripts/build_system_figures.py; đối chiếu services/api/app/recordings.py, services/inference/app/main.py, ml/inference/engine.py.@@

**Luồng hỏi đáp** (⟪fig:queryflow⟫). Câu hỏi tự nhiên trước hết được gửi tới bộ phân tích: API gọi llama.cpp với lược đồ JSON sinh từ 21 lớp và bốn điều kiện thời gian, nhận về bộ lọc và trả cho giao diện dưới dạng thẻ để người dùng sửa. Khi người dùng chạy truy vấn, API nhúng câu hỏi bằng BGE-M3 qua dịch vụ suy luận, rồi gửi một câu SQL vừa áp bộ lọc cứng vừa xếp hạng theo khoảng cách cosine trên chỉ mục HNSW. Ở chế độ backfill, các chỗ còn trống được lấp bằng kết quả ngữ nghĩa không thỏa bộ lọc. Câu trả lời được sinh tất định từ các sự kiện bằng chứng của tầng thỏa bộ lọc; kết quả gần nghĩa chỉ được nêu tên. Nếu llama.cpp không chạy, bước phân tích trả 503 nhưng người dùng vẫn đặt bộ lọc thủ công và truy vấn được.

![](report/final_figures/s05_query_flow.png){width=15.5cm}

@@CAP:fig:queryflow|Luồng hỏi đáp: phân tích câu hỏi, truy hồi và trả lời có bằng chứng@@

@@NOTE:Nguồn: scripts/build_system_figures.py; đối chiếu services/api/app/retrieval.py, ml/retrieval/query_parser.py, ml/retrieval/store.py.@@

## Dữ liệu và giao diện lập trình

**Kho sự kiện.** ⟪fig:erd⟫ là sơ đồ bảng của kho, đọc trực tiếp từ tệp migration SQL. Kho gồm bảy bảng; mọi khóa ngoại đều xóa theo bảng cha, nên xóa một bản ghi sẽ xóa sạch sự kiện, mô tả và tài liệu của nó. Ba quyết định thiết kế có ý nghĩa phương pháp. Thứ nhất, bảng `caption_evidence` nối mô tả với sự kiện; đó chính là định nghĩa của "có căn cứ": một mô tả không có dòng bằng chứng nào là vi phạm. Thứ hai, bảng tài liệu truy hồi tách khỏi bảng mô tả, và mỗi vector mang phiên bản embedding, để đổi mô hình embedding mà không phải sinh lại mô tả và không trộn vector của hai mô hình. Thứ ba, cột nguồn gốc trên bảng sự kiện phân biệt nhãn gốc với dự đoán, nên cùng một kho phục vụ được cả đánh giá lẫn demo. Truy vấn dùng chỉ mục B-tree cho lớp, thời điểm và thời lượng, chỉ mục GIN cho mảng lớp của tài liệu, và chỉ mục đồ thị HNSW cho khoảng cách cosine.

![](report/final_figures/s06_erd.png){width=15cm}

@@CAP:fig:erd|Sơ đồ bảng của kho sự kiện (PostgreSQL 16 + pgvector)@@

@@NOTE:Nguồn: db/migrations/001_event_store.sql, đọc bằng scripts/build_system_figures.py; bảng có hơn chín cột chỉ hiện chín cột đầu.@@

**Giao diện lập trình.** ⟪tbl:api⟫ liệt kê mọi endpoint của hai dịch vụ. Bảng được sinh bằng cách đọc decorator trong mã nguồn; nếu mã thêm hoặc bỏ một endpoint mà bảng mô tả chưa cập nhật, script dừng với lỗi. Giao diện web chỉ gọi dịch vụ API; các endpoint của dịch vụ suy luận chỉ dùng nội bộ giữa hai container.

@@CAP:tbl:api|Các endpoint HTTP của hai dịch vụ@@

@@COLWIDTHS:11,10,47,32@@

@@INCLUDE:report/final_tables/f16_api.md@@

## Giao diện người dùng

Giao diện web (React) có sáu phần: khung tải lên; danh sách bản ghi; dòng thời gian sự kiện (bấm vào sự kiện để nghe đúng đoạn); mô tả song ngữ Anh–Việt kèm bằng chứng; khung hỏi bằng câu tự nhiên, hiển thị bộ lọc đã phân tích dưới dạng thẻ sửa được; và thanh trạng thái mô hình. Thanh trạng thái ghi rõ mô hình đang phục vụ đọc từ dịch vụ suy luận; với LBR V3 thanh này ghi "cấu hình ứng dụng, không phải số chính" (⟪fig:demo1⟫). Mô tả trong giao diện dùng bộ sinh gộp theo lớp (Chương 4): mỗi lớp một dòng kiểu thông báo, lớp lặp lại được đếm ("Phát hiện: tiếng chim, 2 lần, 0,0–20,0 giây."), và lớp có điểm tin cậy thấp được gắn nhãn "Có thể có (độ tin cậy thấp)".

![](report/final_figures/f03a_demo_upload_timeline.png){width=12cm}

@@CAP:fig:demo1|Giao diện demo: thanh trạng thái mô hình, danh sách bản ghi, dòng thời gian và mô tả@@

@@NOTE:Nguồn: docs/demo_screenshots/ (Playwright, 1440×900, chụp trên LBR V3 ngày 24/11/2026), ghép bằng scripts/build_final_figures.py; bản ghi trong lịch sử demo chỉ lấy từ tập train.@@

Khung hỏi đáp tách hai bước để người dùng kiểm soát được bộ phân tích (⟪fig:demochip⟫): bấm "Câu hỏi" để xem bộ lọc mà mô hình ngôn ngữ hiểu ra, sửa thẻ nếu cần (ví dụ đổi "xảy ra trước" thành điều kiện khác), chọn chế độ truy hồi rồi mới chạy truy vấn. Như vậy một lỗi của bộ phân tích hiện ra trước mắt người dùng thay vì âm thầm làm sai kết quả.

![](docs/demo_screenshots/03-filter-chip.png){width=14cm}

@@CAP:fig:demochip|Giao diện demo: bộ lọc đã hiểu hiện thành thẻ sửa được trước khi truy vấn@@

@@NOTE:Nguồn: docs/demo_screenshots/03-filter-chip.png (Playwright, chụp ngày 24/11/2026).@@

Bấm vào một trích dẫn trong câu trả lời sẽ mở đúng bản ghi và tua tới đúng khoảng thời gian (⟪fig:demo2⟫). Truy hồi mặc định chạy ở chế độ backfill (ADR-0049): các bản ghi thỏa bộ lọc đứng đầu và là phần duy nhất được trích làm bằng chứng; các bản ghi gần nghĩa nhưng không thỏa bộ lọc được liệt kê riêng dưới nhãn "gần khớp", và câu trả lời chỉ nêu tên chúng mà không khẳng định lớp hay thời gian.

![](report/final_figures/f03b_demo_query_evidence.png){width=13cm}

@@CAP:fig:demo2|Giao diện demo: câu hỏi tự nhiên thành bộ lọc, câu trả lời kèm bằng chứng@@

@@NOTE:Nguồn: như hình trước; câu hỏi "Có tiếng chim trước tiếng còi xe không?" do bộ phân tích câu hỏi chuyển thành bộ lọc `before`, còn câu trả lời lấy từ mẫu cố định của hệ thống.@@

## Độ trễ

⟪tbl:latency⟫ báo độ trễ của demo đang chạy trên CPU trong container, với tầng LBR V3 ở điểm ưu tiên phát hiện. Nhóm tải lên 12 bản ghi chọn đều theo độ dài từ tập train (3,4 đến 818 s), nhưng 2 bản ghi trong số đó (S-0049 và S-0713, bản ghi dài nhất) đã có sẵn trong lịch sử demo nên bị hệ thống từ chối trùng; vì vậy bảng chỉ có 10 lần đo, bản dài nhất là 179,6 s. Truy vấn kết hợp được lặp 5 lần. Thời gian khởi động và nạp mô hình không nằm trong bảng; lần gọi đầu tiên sau khi khởi động chậm hơn đáng kể vì dịch vụ suy luận nạp mô hình lúc đó (trước đây đo được khoảng 50 s với B0).

@@CAP:tbl:latency|Độ trễ của demo trên CPU (LBR V3, bản ghi TRAIN)@@

@@COLWIDTHS:46,10,22,22@@

@@INCLUDE:report/final_tables/f13_latency.md@@

Trung vị 3,89 s cho một lần tải lên và phân tích, tương ứng hệ số thời gian thực 0,072: xử lý nhanh hơn thời gian thật khoảng 14 lần. Trường hợp xấu nhất (p95) là 0,294 và rơi vào bản ghi ngắn nhất (3,4 s), nơi chi phí cố định của một lượt gọi chiếm phần lớn; với bản dài trên 16 s hệ số này nằm trong khoảng 0,06 đến 0,10. Truy vấn kết hợp trung vị 0,22 s. Bộ nhớ của container suy luận ở mức 1,24 GiB trên tổng 7,39 GiB, gần như không đổi qua các bản ghi (đo bằng `docker stats` sau mỗi lần tải). Các số này đo trên một máy, một lần chạy, nên chỉ cho biết cỡ độ lớn; nhóm không dùng chúng để khẳng định yêu cầu thời gian thực trên máy khác. Phép đo chạy khi cây làm việc chưa sạch vì chính script đo chưa được commit lúc chạy (chỉ ảnh hưởng ghi chú nguồn gốc, không ảnh hưởng thời gian).

@@NOTE:Nguồn: docs/measurements/latency_lbrv3_20261123.json (scripts.report_latency); chỉ tải bản ghi thuộc tập train, không chấm metric.@@

## Chạy demo

Hệ thống chạy cục bộ bằng Docker Compose: một container cơ sở dữ liệu, một container suy luận và một container API phục vụ cả giao diện (cổng 8088). Checkpoint và mô hình embedding được gắn vào ở chế độ chỉ đọc; các container đặt chế độ ngoại tuyến nên demo không cần mạng. Mô hình ngôn ngữ chạy trên máy chủ bằng llama.cpp để dùng GPU.

Ba script PowerShell gói các thao tác: khởi động (kiểm Docker, bật llama.cpp, dựng Compose, chờ dịch vụ sẵn sàng và kiểm cờ `official` khớp cấu hình: `true` khi chạy B0 thuần, còn khi bật LBR thì kiểm đúng lần chạy LBR và điểm vận hành, nạp lịch sử demo), kiểm tra, và dừng. Lịch sử demo gồm 20 bản ghi chọn tự động **chỉ từ tập train** sao cho phủ đủ 21 lớp, để demo không bao giờ phơi bày dữ liệu test. Một lượt kịch bản thật qua API đã chạy năm câu hỏi Anh/Việt (một lớp, hai lớp, quan hệ "trước", thời lượng) và lưu kết quả.

Để kiểm tra hệ phục vụ có đúng là hệ đã đo, đầu ra phục vụ trên GPU được so với đầu ra đã đóng băng (Chương 6): với LBR V3, 573 trên 692 sự kiện trùng khít, 665 lệch không quá một khung và 691 nằm trong collar 0,2 s. Phần lệch do bộ tinh chỉnh khuếch đại sai khác số học rất nhỏ (lệch xác suất lớn nhất 0,0020) thành dịch biên một khung. Parity trên CPU, nơi demo chạy, chưa được đo cho LBR V3.

Hệ thống có hai giới hạn: chưa có xác thực người dùng nên **không** sẵn sàng triển khai công khai, và dịch vụ xử lý luồng mới chỉ là thư mục khung.

## Tái lập và kiểm thử

**Tái lập.** Mỗi lần chạy ghi một manifest gồm cấu hình, seed, phiên bản git kèm cờ `dirty` (cây làm việc có thay đổi chưa commit), mã băm của tập chia, hệ lớp, đặc trưng, tham số ghép sự kiện, và cờ hoàn tất. Lần chạy thiếu một trong các trường này, hoặc chạy trên cây làm việc có thay đổi chưa commit, được coi là không đủ truy nguồn; một số lượt đánh giá test đã chạy khi cờ này bật (do chính script sinh ra tệp chưa commit) và được liệt kê công khai ở Chương 6 và Phụ lục B. Dự đoán thô lưu thành tệp có SHA-256, tách khỏi bước tính chỉ số, nên quét lại ngưỡng trên dev không cần chạy lại mô hình, và tệp dự đoán test chỉ được sinh sau khi lựa chọn đã commit.

Trước khi viết báo cáo, mọi lần chạy, ensemble và checkpoint được trích dẫn đã được "đóng băng": một script kiểm sự tồn tại và ghi SHA-256 của 129 lần chạy hoặc ensemble, 5 checkpoint ngoài và 8 tệp đầu vào cố định (tập chia, hệ lớp, từ điển, ngữ pháp, bộ truy vấn). Không thiếu tệp nào (Phụ lục B). Các tệp đo sinh sau mốc đóng băng (giai đoạn hoàn thiện 23–24/11) không nằm trong bản đóng băng nhưng được lưu trong git cùng phiên bản mã sinh ra chúng. Ba bộ kiểm tài liệu chạy trước mỗi lần commit: một bộ đối chiếu các con số chính trong tài liệu dự án (`docs/`, ADR) với tệp kết quả, một bộ kiểm lệnh trong hướng dẫn tái lập so với mã nguồn, và một bộ kiểm liên kết. Bộ thứ nhất chưa phủ văn bản của khóa luận; với khóa luận, các bảng số và hình đều do script sinh từ tệp kết quả, ghi rõ tệp nguồn và phiên bản git, còn số trong văn xuôi được đối chiếu tay với các bảng đó. Tài liệu `docs/REPRODUCE.md` tách hai quy trình: kiểm toán an toàn chạy trong bản sao hiện tại, và tái tạo số test chỉ làm trong một bản sao mới có phê duyệt, để không tạo thêm lượt chạm test ngoài sổ ghi. Chính tệp DOCX này được dựng từ nguồn Markdown bằng một script, và một script kiểm định dạng (lề, style, chú thích, mục chỉ có một tiểu mục, trang mở đầu bằng dòng nguồn) chạy trên bản dựng.

**Theo dõi thí nghiệm.** Vì mọi lần chạy đều có manifest, có thể dựng lại toàn bộ sổ thí nghiệm mà không cần công cụ theo dõi ngoài. ⟪tbl:registry⟫ tổng hợp 218 lần chạy trong `ml/runs/` theo loại, và ⟪fig:runtimeline⟫ cho thấy chúng phân bố theo ngày tạo. 103 lần là huấn luyện SED, 99 lần hoàn tất; 4 lần không hoàn tất đều có lý do đã ghi (một lần loss focal ra NaN, ba lần dừng giữa chừng ở giai đoạn P). 17 lần chạy trên cây làm việc chưa sạch, tất cả trước ngày 29/09: sáu lần thử bộ phân loại, hai lần dò đường ngày 22/09, ba lần thăm dò nhánh B và C (đã loại khỏi phân tích RQ1 chính, vốn chỉ dùng 7 lần chạy sạch), hai lần thử focal loss 3 epoch, một ensemble v2 chỉ dùng cho demo trước S8, và ba ensemble công thức v1 ngày 25/09. Ensemble C trong số đó là mốc v1 trong bảng tiến triển; nhóm đã dựng lại ba ensemble này trên cây sạch và nhận được dữ liệu trùng từng byte, nên con số không đổi, nhưng manifest gốc vẫn ghi cờ bẩn và được giữ nguyên. Mọi lần chạy SED cùng dùng một mã băm tập chia DataSED, trừ hai lần dò đường ngày 22/09 chạy trước khi tập chia được sinh lại sau bước khử trùng lặp; mọi lần huấn luyện bộ phân loại dùng mã băm tập chia DataSEC. Hình cũng cho thấy công việc tập trung theo đợt: phần lớn các lần chạy rơi vào bốn giai đoạn thí nghiệm.

@@CAP:tbl:registry|Sổ đăng ký các lần chạy theo loại@@

@@COLWIDTHS:40,8,12,11,13,16@@

@@INCLUDE:report/final_tables/f14_run_registry.md@@

![](report/research_figures/r12_run_timeline.png){width=15cm}

@@CAP:fig:runtimeline|Số lần chạy được tạo theo ngày và loại, kèm bốn giai đoạn thí nghiệm@@

@@NOTE:Nguồn: docs/measurements/run_registry_20261123.json (scripts.report_run_registry, đọc manifest của mọi run); ngày lấy từ mã run.@@

**Kiểm thử.** Bộ kiểm thử Python dùng pytest, kiểm tra mã bằng ruff. Ở lần kiểm ngày 24/11/2026 (cơ sở dữ liệu bật), ruff không báo lỗi và pytest đạt 1261 mục kiểm thử (con số sau khi tham số hóa; bảng khối lượng đếm số hàm kiểm thử trong mã), không bỏ qua mục nào, có 1 mục xfail có chủ ý (bản kê run cũ thiếu trường `environment`). Bộ kiểm thử phủ hợp đồng dữ liệu, ranh giới API–torch, các cổng dữ liệu (kể cả phép thử chứng minh cổng D4 không đạt rỗng), điều kiện thời gian SQL và Python, chỉ số bám sát sự kiện, ba ràng buộc G1–G3, tính trùng từng bit của đường sinh dự đoán, tích hợp PostgreSQL, và sự khớp giữa các bảng, sơ đồ hệ thống của chương này với mã nguồn. CI trên GitHub Actions chạy ruff, pytest, kiểm tra cấm `torch` trong API, kiểm thử và build giao diện.

Nhiều lỗi thật chỉ bị bắt nhờ chạy toàn bộ quy trình trên dữ liệu thật, trong đó lỗi ghép cửa sổ dự đoán (khoảng 10 s cuối mỗi bản ghi bị nhân đôi) làm đổi mọi số SED đã có; sau khi sửa, toàn bộ 11 lần chạy được tính lại và kết luận RQ1 không đổi.

**Khối lượng thực hiện.** ⟪tbl:workload⟫ tóm tắt khối lượng công việc bằng số đếm từ chính kho mã, để người đọc đo được độ lớn của phần hiện thực mà các chương kết quả chỉ nói gián tiếp. Số run đếm thư mục trong `ml/runs/` của máy làm việc (thư mục này không nằm trong git); các số còn lại đếm được từ kho mã tại phiên bản ghi ở chân bảng.

@@CAP:tbl:workload|Khối lượng thực hiện, đếm từ kho mã@@

@@COLWIDTHS:34,66@@

@@INCLUDE:report/final_tables/f12_workload.md@@

Tóm lại, hệ thống đáp ứng các yêu cầu đặt ra ở đầu chương với hai giới hạn đã nêu (không xác thực, không xử lý luồng). Chương 6 tiếp theo báo kết quả đo của các thành phần này trên dữ liệu test.
