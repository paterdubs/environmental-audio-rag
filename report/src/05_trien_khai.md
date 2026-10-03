# TRIỂN KHAI HỆ THỐNG

Chương này mô tả phần hiện thực của hệ thống: tổ chức mã nguồn, các dịch vụ, cơ sở dữ liệu, giao diện, cách triển khai và cơ chế bảo đảm tái lập. Nội dung chỉ mô tả những gì đã có mã nguồn và đã được kiểm chứng bằng lệnh và artifact. Các phần mới ở mức thiết kế được ghi rõ là chưa thực hiện.

## Tổ chức mã nguồn và nguyên tắc ranh giới

Mã nguồn chia thành ba tầng có trách nhiệm tách biệt:

- `ml/` chứa logic nhập (import) được: xử lý dữ liệu, mô hình, huấn luyện, hậu xử lý, đánh giá, sinh mô tả và truy hồi.
- `scripts/` chỉ điều phối dòng lệnh (CLI) và sinh báo cáo đo.
- `services/` chứa các dịch vụ phục vụ.

Hai nguyên tắc ranh giới được kiểm bằng máy chứ không chỉ quy ước. Thứ nhất, dịch vụ giao diện lập trình ứng dụng (Application Programming Interface – API) không được nhập PyTorch hay nạp checkpoint. Một kiểm thử phân tích cây cú pháp (Abstract Syntax Tree – AST) trong quy trình tích hợp liên tục (Continuous Integration – CI) chặn mọi lệnh nhập `torch` trong `services/api`, để API khởi động nhanh, kiểm thử được không cần GPU và mở rộng độc lập với phần suy luận. Thứ hai, dữ liệu trao đổi giữa các thành phần tuân theo tám hợp đồng JSON Schema trung lập với framework trong `contracts/`: bản ghi, sự kiện, dòng thời gian, phản hồi suy luận, kết quả truy hồi, tham số hậu xử lý, bộ truy vấn và manifest của run. Mỗi hợp đồng có kiểm thử theo chuẩn Draft 2020-12.

Thứ tự lớp không bị khai báo rải rác trong mã. Mọi thành phần đọc danh sách lớp từ tệp cấu hình hệ lớp, và mỗi checkpoint lưu hash hệ lớp. Siêu tham số nằm trong tệp YAML trong `ml/configs/` hoặc trong công thức huấn luyện được ghi vào manifest.

## Các dịch vụ

### Dịch vụ suy luận

Dịch vụ suy luận (`services/inference`, FastAPI) nạp **một lần** khi khởi động mọi thứ cần cho phân tích: mô hình SED đang phục vụ cùng tệp hậu xử lý, các bộ sinh mô tả, và mô hình embedding BGE-M3. Run được phục vụ đọc từ biến môi trường `EARAG_SERVED_RUN` và `EARAG_SERVED_POSTPROC`, chỉ chấp nhận đường dẫn nằm trong kho mã. Kiến trúc mạng được dựng lại từ khóa trong manifest của run (`ml/models/sed_factory.py`) chứ không mã hóa cứng. Dịch vụ trả cờ `official` cho biết run đang phục vụ có đúng là hệ thống đã khóa (f2) hay không, và giao diện hiển thị cờ này. Dịch vụ cung cấp bốn điểm cuối: `/health`, `/v1/models`, `/v1/analyze` (âm thanh → sự kiện và mô tả) và `/v1/embed`.

### Dịch vụ API và cơ sở dữ liệu

Dịch vụ API (`services/api`, FastAPI) chịu trách nhiệm tải lên, kiểm tra đầu vào, lưu trữ và điều phối. Mọi phản hồi dùng một khuôn chung `{success, data, error, meta}`. Tệp tải lên bị từ chối nếu không đúng định dạng âm thanh cho phép (mã 415), lớn hơn 50 MB hoặc dài hơn 600 s. Bảng ⟪tbl:endpoints⟫ liệt kê các điểm cuối đã triển khai.

@@CAP:tbl:endpoints|Các điểm cuối của dịch vụ API (tiền tố /api/v1)@@

| Nhóm | Điểm cuối | Chức năng |
|---|---|---|
| Tải lên | POST /audio/upload | Nhận tệp, gọi suy luận, lưu bản ghi, sự kiện và mô tả |
| Bản ghi | GET /recordings, /recordings/{id} | Liệt kê có lọc; siêu dữ liệu, dòng thời gian, mô tả |
| Bản ghi | GET /recordings/{id}/timeline, /caption, /audio | Dòng thời gian kèm phiên bản mô hình; mô tả kèm bằng chứng; phát lại âm thanh |
| Truy hồi | POST /retrieval/parse | Câu hỏi → bộ lọc (LLM có ràng buộc lược đồ) |
| Truy hồi | POST /retrieval/query | Truy hồi + câu trả lời có bằng chứng; tự phân tích câu hỏi khi thiếu bộ lọc |
| Hệ thống | GET /taxonomy, /models/status, /health | Hệ lớp; run đang phục vụ và cờ official; tình trạng sẵn sàng |

@@NOTE:Nguồn: services/api/app/main.py, recordings.py, retrieval.py.@@

Lược đồ cơ sở dữ liệu (`db/migrations/001_event_store.sql`) gồm bảy bảng: `recordings`, `events`, `event_subclass_predictions`, `captions`, `caption_evidence`, `retrieval_documents` và `runs`. Ba quyết định lược đồ có ý nghĩa phương pháp:

- `caption_evidence` là bảng riêng nối mô tả với sự kiện. Bảng này chính là định nghĩa của "có căn cứ": một mô tả không có dòng bằng chứng nào là vi phạm hợp đồng.
- `retrieval_documents` tách khỏi `captions` để có thể đổi mô hình embedding mà không phải sinh lại mô tả.
- Cột `provenance` trên `events` phân biệt nhãn gốc với dự đoán.

Truy vấn lọc dùng chỉ mục B-tree trên (bản ghi, onset), (lớp, onset) và thời lượng, chỉ mục GIN trên mảng lớp, và chỉ mục đồ thị HNSW (Hierarchical Navigable Small World) cho khoảng cách cosine.

### Giao diện người dùng

Giao diện web viết bằng React với Vite và TanStack Query (`services/frontend`). Giao diện gồm sáu phần:

- khung tải lên tệp âm thanh;
- danh sách bản ghi;
- dòng thời gian sự kiện, bấm vào sự kiện để nghe đúng đoạn âm thanh;
- mô tả song ngữ Anh–Việt kèm bằng chứng;
- khung tìm kiếm bằng câu hỏi tự nhiên, hiển thị bộ lọc đã phân tích dưới dạng thẻ sửa được;
- thanh trạng thái cho biết run đang phục vụ.

Khi bấm vào một trích dẫn trong câu trả lời, giao diện mở đúng bản ghi và tua tới đúng khoảng thời gian (⟪fig:demo⟫). Trạng thái lọc được lưu trong URL để chia sẻ được. Phần logic dòng thời gian và lớp gọi API có kiểm thử đơn vị bằng Vitest.

![](docs/thesis/figures/07_demo_interface.png){width=15.5cm}

@@CAP:fig:demo|Giao diện demo: tải lên, dòng thời gian, bộ lọc từ câu hỏi và bằng chứng@@

@@NOTE:Nguồn: docs/demo_screenshots/ (Playwright, 1440×900), ghép bằng scripts/build_thesis_figures.py; bản ghi trong lịch sử demo chỉ lấy từ tập train.@@

## Triển khai và kịch bản demo

Hệ thống chạy cục bộ bằng Docker Compose (`docker-compose.yml`). Dịch vụ `db` dùng ảnh `pgvector/pgvector:pg16`. Hồ sơ `app` bổ sung dịch vụ `inference` (chạy trên bộ xử lý trung tâm – CPU – trong container) và `api` (phục vụ cả giao diện đã build, cổng 8088). Checkpoint và mô hình embedding không được đóng vào ảnh mà được gắn (mount) chỉ đọc. Container đặt chế độ ngoại tuyến (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`), nên demo không cần mạng. LLM chạy trên máy chủ bằng llama.cpp (cổng 8081) để dùng GPU; container truy cập qua `host.docker.internal`.

Ba script PowerShell gói các thao tác demo. `demo_up.ps1` kiểm Docker, khởi động llama.cpp nếu chưa chạy, dựng và khởi động Compose, chờ `/health` và cờ `official=true`, kiểm bộ phân tích câu hỏi, rồi nạp lịch sử demo. `demo_check.ps1` kiểm tra mà không khởi động dịch vụ, còn `demo_down.ps1` dừng hệ thống. Lịch sử demo gồm 15 bản ghi được chọn tự động **chỉ từ tập train** sao cho phủ đủ 21 lớp, để demo không bao giờ phơi bày dữ liệu test. Một lượt kịch bản thật qua API đã chạy năm câu hỏi Anh/Việt thuộc các nhóm một lớp, hai lớp, quan hệ "trước" và thời lượng, và lưu kết quả thành artifact.

Thời gian xử lý được đo trên một lượt đầu–cuối với bản ghi train `S-0016` (⟪tbl:runtime⟫): tải lên và phân tích bằng CPU trong container mất 2,012 s, một truy vấn lai mất 0,250 s. Đây là số đo của một lượt trên một bản ghi, không phải phép đo hiệu năng có thống kê.

@@CAP:tbl:runtime|Thời gian xử lý đã đo@@

@@INCLUDE:docs/thesis/tables/12_runtime.md@@

Hai giới hạn triển khai được ghi nhận. Thứ nhất, hệ thống chưa có xác thực người dùng, và mật khẩu cơ sở dữ liệu trong tệp Compose chỉ dùng cho môi trường phát triển cục bộ. Hệ thống **không** sẵn sàng để triển khai công khai. Thứ hai, dịch vụ xử lý luồng (`services/stream`) mới chỉ là thư mục khung, chưa có mã.

## Tái lập và truy nguồn kết quả

Mỗi run ghi một manifest gồm cấu hình, seed, phiên bản git kèm cờ `dirty` (cây làm việc có thay đổi chưa commit), hash của tập chia, hệ lớp, đặc trưng và tham số hậu xử lý, và cờ `complete`. Một run thiếu một trong các trường này, hoặc chạy trên cây làm việc bẩn, không được dùng cho số chính thức. Các trường hợp vi phạm đã xảy ra đều được công khai (Mục 6.7). Dự đoán thô được lưu thành tệp NPZ có SHA-256, tách khỏi bước tính metric. Nhờ vậy, ngưỡng có thể được quét lại trên dev mà không phải chạy lại suy luận, và tệp test chỉ được sinh sau khi lựa chọn đã commit.

Trước khi viết báo cáo, mọi artifact được trích dẫn đã được đóng băng: script `freeze_artifacts` kiểm sự tồn tại và ghi SHA-256 của 11 run hoặc ensemble, các checkpoint ngoài và các tệp đầu vào đóng băng (tập chia, hệ lớp, từ điển, ngữ pháp, bộ truy vấn). Không thiếu artifact nào (Phụ lục B). Tài liệu `docs/REPRODUCE.md` tách hai quy trình. Quy trình kiểm toán an toàn chạy trong bản sao hiện tại. Quy trình tái tạo số test chỉ được làm trong một bản sao mới và cần phê duyệt, để tránh tạo thêm lượt chạm test ngoài sổ ghi.

Các bảng số và hình định lượng trong báo cáo này được sinh bằng script từ các artifact trên (`scripts/build_thesis_tables.py`, `scripts/build_midterm_tables.py`, `scripts/build_thesis_figures.py`, `scripts/build_midterm_figures.py`), mỗi bảng ghi tệp nguồn và phiên bản git. Bản thân tệp DOCX này được dựng lại bằng `scripts/build_midterm_report.py` từ nguồn Markdown trong `report/src/`.

## Kiểm thử và tích hợp liên tục

Bộ kiểm thử Python dùng pytest, kiểm tra mã nguồn dùng ruff. Tại lần kiểm gần nhất trước báo cáo (02/10/2026, Windows), bộ kiểm thử đạt 738 kiểm thử, không có kiểm thử bị bỏ qua, và ruff không báo lỗi; trạng thái tại mốc chốt báo cáo được ghi trong báo cáo kiểm tra đi kèm. Các kiểm thử phủ:

- hợp đồng dữ liệu và ranh giới API–torch;
- các cổng dữ liệu, bao gồm phép thử chứng minh cổng D4 không đạt rỗng;
- ngữ nghĩa vị từ thời gian SQL và Python;
- metric căn cứ và ba ràng buộc G1–G3;
- tính trùng từng bit của đường sinh dự đoán;
- tích hợp với PostgreSQL, tự bỏ qua khi Docker không chạy.

Quy trình CI trên GitHub Actions (Linux, Python 3.12) chạy ruff, pytest, kiểm tra cấm `torch` trong API, kiểm thử và build giao diện.

Nhiều lỗi thật đã được bắt nhờ chạy toàn bộ quy trình trên dữ liệu thật chứ không chỉ trên dữ liệu mẫu (fixture):

- metric thứ tự bị sai khi một lớp lặp lại nhiều lần trong dòng thời gian;
- `sed_eval` từ chối khi một lần gọi trộn nhiều bản ghi;
- thư viện `psds_eval` lỗi với numpy 2;
- quét ngưỡng chậm 20 lần;
- ghép cửa sổ dự đoán sai làm khoảng 10 s cuối mỗi bản ghi bị nhân đôi.

Lỗi cuối cùng làm thay đổi mọi số SED đã có; sau khi sửa, toàn bộ 11 run được tính lại, và kết luận của RQ1 không đổi.
