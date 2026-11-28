@@SECTION:body@@

@@HEADING1N:TÀI LIỆU THAM KHẢO@@

@@BIB@@

@@SECTION:refs@@

@@HEADING1N:PHỤ LỤC@@

@@APPENDIX@@

@@HEADING2N:Phụ lục A. Hệ lớp và số sự kiện đa âm@@

Bảng dưới liệt kê 22 lớp, nhãn gốc tương ứng, các lớp con (chỉ có trên DataSEC) và số sự kiện trong bản nhãn đa âm của DataSED. Lớp `wind_turbine` không thuộc 21 lớp của mô hình SED.

@@CAP:tbl:taxonomy|Hệ lớp phiên bản 0.1@@

@@COLWIDTHS:30,22,25,11,12@@

@@INCLUDE:report/tables/m08_taxonomy.md@@

@@HEADING2N:Phụ lục B. Tái lập và nhật ký thí nghiệm@@

Phụ lục này gom các chi tiết quy trình mà thân bài chỉ nhắc tới: tên nội bộ của các hệ, cách bảo đảm tái lập, nhật ký các lần chạy và các bảng phụ.

**Bảng tra tên hệ thống.** Thân bài dùng tên có nghĩa; mã trong kho mã và trong tệp kết quả như sau.

@@CAP:tbl:codes|Tên trong báo cáo và mã nội bộ@@

@@COLWIDTHS:24,14,62@@

| Tên trong báo cáo | Mã | Ghi chú |
|---|---|---|
| Nhánh A, B, C | A, B, C | Ba nhánh của Câu hỏi nghiên cứu 1: học từ đầu; khởi tạo AudioSet; AudioSet rồi DataSEC |
| SED v1, SED v2 | v1, v2 | Hai thế hệ dùng CNN14: v1 nén thời gian 64 lần; v2 nén 8 lần, thêm BiGRU và tăng cường dữ liệu |
| BEATs đóng băng; Frame-MobileNet | T2a; T2b | Hai bộ mã hóa tiền huấn luyện theo khung |
| Ứng viên vòng chọn trước | a–e, f1–f4, g1–g2 | 11 ứng viên của vòng chọn hệ mốc (⟪tbl:s13⟫) |
| Hệ mốc | f2 | Tổ hợp 3 mô hình Frame-MobileNet, cSEBB; khóa ở vòng chọn S13 |
| Hệ cơ sở | B0 | 5 mô hình Frame-MobileNet theo phần dữ liệu, suy luận chồng lấn, cSEBB; hệ cuối của giai đoạn tối ưu |
| LBR chính | LBR V2 | Bộ tinh chỉnh và bộ chấm lại, điểm tối đa F1 theo sự kiện |
| LBR ứng dụng | LBR V3 | Bộ chấm lại dùng nhãn theo giao nhau, điểm "ưu tiên phát hiện" (`recall_first`) |

**Tái lập.** Mỗi lần chạy ghi một tệp mô tả (manifest) gồm cấu hình, hạt giống ngẫu nhiên, phiên bản mã, mã băm của tập chia, hệ lớp, đặc trưng và tham số ghép sự kiện. Dự đoán thô được lưu thành tệp có mã băm, tách khỏi bước tính chỉ số, nên chọn lại ngưỡng không cần chạy lại mô hình. Mỗi quyết định thiết kế được ghi thành một bản ghi quyết định (Architecture Decision Record – ADR); dự án có 50 ADR. Trước khi viết báo cáo, mọi lần chạy, mô hình gộp và checkpoint được trích dẫn đã được kiểm sự tồn tại và ghi mã băm (⟪tbl:freeze⟫); không thiếu tệp nào. Mọi lần dùng tập kiểm tra được ghi vào một sổ (⟪tbl:ledger⟫). Một số lượt đánh giá trên tập kiểm tra chạy khi kho mã có tệp chưa lưu vào git, do chính script đánh giá sinh ra; mã và cấu hình không đổi, và các lượt này không được chạy lại.

@@CAP:tbl:freeze|Các thành phần đã khóa và kiểm mã băm SHA-256@@

@@COLWIDTHS:32,40,9,9@@

@@INCLUDE:report/final_tables/f08_freeze.md@@

@@CAP:tbl:ledger|Sổ ghi các lần dùng tập kiểm tra@@

@@INCLUDE:report/final_tables/f07_ledger.md@@

**Nhật ký các lần chạy.** Vì mọi lần chạy đều có manifest, có thể dựng lại toàn bộ sổ thí nghiệm mà không cần công cụ theo dõi riêng (⟪tbl:registry⟫, ⟪fig:runtimeline⟫). Trong 103 lần huấn luyện SED, 99 lần hoàn tất; 4 lần không hoàn tất đều có lý do đã ghi.

@@CAP:tbl:registry|Sổ các lần chạy theo loại@@

@@COLWIDTHS:40,8,12,11,13,16@@

@@INCLUDE:report/final_tables/f14_run_registry.md@@

![](report/gon_figures/r12_run_timeline.png){width=15cm}

@@CAP:fig:runtimeline|Số lần chạy theo ngày và loại@@

@@NOTE:Nguồn: run_registry_20261123.json.@@

**Khối lượng thực hiện** được đếm từ chính kho mã (⟪tbl:workload⟫). Bộ kiểm thử phủ hợp đồng dữ liệu, ranh giới giữa API và PyTorch, các cổng dữ liệu, điều kiện thời gian bằng SQL và Python, chỉ số bám sát, ba ràng buộc G1–G3, tích hợp PostgreSQL, và sự khớp giữa sơ đồ hệ thống với mã nguồn.

@@CAP:tbl:workload|Khối lượng thực hiện, đếm từ kho mã@@

@@COLWIDTHS:34,66@@

@@INCLUDE:report/final_tables/f12_workload.md@@

**Nhật ký huấn luyện hệ cơ sở.** ⟪fig:training⟫ là nhật ký huấn luyện của năm mô hình, mỗi mô hình ứng với một phần dữ liệu. Hàm mất mát trên phần giữ lại để kiểm ổn định sau khoảng 10 vòng huấn luyện và không tăng trở lại. Bản lưu trọng số được chọn theo độ chính xác trung bình (Average Precision – AP) theo khung, lấy trung bình macro, và rơi vào vòng 15, 23, 25, 26 và 28 trên 30.

![](report/gon_figures/r03_training_curves.png){width=15cm}

@@CAP:fig:training|Nhật ký huấn luyện năm mô hình của hệ cơ sở (mỗi mô hình một phần dữ liệu)@@

@@NOTE:Nguồn: nhật ký huấn luyện của năm lần chạy thành viên.@@

**Vòng chọn hệ mốc.** ⟪tbl:s13⟫ là xếp hạng 11 ứng viên bằng kiểm chứng chéo trên tập phát triển và kết quả đo một lần trên tập kiểm tra. ⟪fig:devtest⟫ cho thấy thứ hạng trên hai tập không trùng nhau.

@@CAP:tbl:s13|Xếp hạng 11 ứng viên trên tập phát triển và kết quả trên tập kiểm tra@@

@@INCLUDE:docs/thesis/tables/06_s13_ranking_test.md|cols=1,2,4,5,6,7,8,9|best=5+,7+,8+|used=2:^f2$@@

![](report/gon_figures/r08_dev_vs_test.png){width=10cm}

@@CAP:fig:devtest|Micro trên tập phát triển so với micro trên tập kiểm tra của 11 ứng viên@@

@@NOTE:Nguồn: s13_ranking_annotated_20260928.json và s13_test_20261018.json.@@

**Chẩn đoán PSDS.** Hiện tượng "F1 theo sự kiện tăng nhưng PSDS không tăng" xuất hiện từ SED v1 sang v2. Nhóm kiểm bốn giả thuyết ghi trước trên tập phát triển (⟪tbl:psdsdiag⟫). Đổi sang dải ngưỡng log và bỏ phần phạt độ lệch giữa các lớp đều làm hiện tượng gần biến mất. Đây là phép đo trên tập phát triển, hiệu rất nhỏ, nên chỉ gợi ý nguyên nhân.

@@CAP:tbl:psdsdiag|Chẩn đoán PSDS từ SED v1 sang v2 trên tập phát triển@@

@@INCLUDE:report/final_tables/f06_psds.md@@

**Giao diện lập trình.** ⟪tbl:api⟫ liệt kê các điểm truy cập của hai dịch vụ, sinh bằng cách đọc mã nguồn; nếu mã thêm hoặc bỏ một điểm truy cập mà bảng chưa cập nhật, script báo lỗi.

@@CAP:tbl:api|Các điểm truy cập HTTP của hai dịch vụ@@

@@COLWIDTHS:11,10,47,32@@

@@INCLUDE:report/final_tables/f16_api.md@@

@@HEADING2N:Phụ lục C. Kết quả theo lớp@@

Lớp có dưới 10 mẫu kiểm tra chỉ được báo bằng số tuyệt đối. Bảng đầu là mô hình phân loại DataSEC; bảng sau là hệ cơ sở và LBR chính trên tập kiểm tra; bảng cuối là hệ mốc.

@@CAP:tbl:classperclass|Mô hình phân loại DataSEC theo lớp cấp trên (tập kiểm tra)@@

@@INCLUDE:report/tables/m02_classifier_per_class.md@@

@@CAP:tbl:b0perclass|F1 theo sự kiện theo lớp của hệ cơ sở và LBR chính trên tập kiểm tra@@

@@COLWIDTHS:33,13,12,12,15,15@@

@@INCLUDE:report/final_tables/f09_per_class.md@@

@@CAP:tbl:f2perclass|F1 theo sự kiện theo lớp của hệ mốc trên tập kiểm tra@@

@@INCLUDE:report/tables/m05_f2_per_class.md@@

@@HEADING2N:Phụ lục D. Phân công công việc và khai báo sử dụng trí tuệ nhân tạo@@

Hai thành viên chia công việc thành hai phần có khối lượng tương đương; mỗi mảng có một người phụ trách chính và một người kiểm chéo, nên cả hai đều đọc, chạy lại và trình bày được mọi phần của đề tài. Các quyết định thiết kế, mọi lần dùng tập kiểm tra và mọi kết luận đều do cả hai cùng duyệt. Mã nguồn được lưu từ một tài khoản chung, nên lịch sử git không phản ánh việc phân công này.

@@CAP:tbl:division|Phân công công việc@@

@@COLWIDTHS:9,41,25,25@@

| TT | Mảng công việc | Phụ trách chính | Kiểm chéo |
|---:|---|---|---|
| 1 | Dữ liệu: kiểm tệp nén, kiểm kê, tìm bản trùng, chia tập | Phạm Hoàng Phát | Thân Trọng Tính |
| 2 | Mô hình phân loại DataSEC và Câu hỏi nghiên cứu 1 | Thân Trọng Tính | Phạm Hoàng Phát |
| 3 | Mô hình SED, hậu xử lý, cách chọn trên dự đoán ngoài mẫu | Phạm Hoàng Phát | Thân Trọng Tính |
| 4 | Tinh chỉnh biên học được (LBR) và chỉ số ứng dụng | Thân Trọng Tính | Phạm Hoàng Phát |
| 5 | Mô tả bám sát sự kiện, bộ đo và Câu hỏi nghiên cứu 2 | Thân Trọng Tính | Phạm Hoàng Phát |
| 6 | Kho sự kiện, truy hồi, câu trả lời có bằng chứng và Câu hỏi nghiên cứu 3 | Phạm Hoàng Phát | Thân Trọng Tính |
| 7 | Dịch vụ suy luận và API, giao diện web, Docker Compose | Thân Trọng Tính | Phạm Hoàng Phát |
| 8 | Tra cứu văn liệu và bối cảnh quy chuẩn | Phạm Hoàng Phát | Thân Trọng Tính |
| 9 | Báo cáo, slide và tài liệu tái lập | Cả hai | Cả hai |

**Khai báo sử dụng trí tuệ nhân tạo.** Nhóm khai báo việc dùng công cụ trí tuệ nhân tạo tạo sinh như sau.

- **Công cụ:** trợ lý lập trình dựa trên mô hình ngôn ngữ lớn (Claude của Anthropic và Codex của OpenAI).
- **Mục đích và phạm vi:** hỗ trợ viết, rà soát và kiểm thử mã nguồn và các script đo; hỗ trợ tra cứu và tóm tắt tài liệu; soạn bản nháp và biên tập câu chữ của báo cáo.
- **Kiểm soát của nhóm:** các quyết định thiết kế, việc dùng tập kiểm tra và các kết luận do nhóm quyết định. Mọi số liệu trong báo cáo do script trong kho mã sinh ra từ kết quả đã lưu và chạy lại được; mọi trích dẫn được nhóm đối chiếu với nguồn gốc. Lịch sử phiên bản của mã và báo cáo được lưu đầy đủ trong git.
- **Trách nhiệm:** nhóm chịu trách nhiệm toàn bộ nội dung khóa luận.

Mô hình Qwen3.5-9B nhắc đến ở Chương 4 là một thành phần của hệ thống được nghiên cứu, không phải công cụ dùng để viết báo cáo.

@@PAGEBREAK@@

@@HEADING1N:NHẬT KÍ LÀM VIỆC@@

**Đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

**Giảng viên hướng dẫn (GVHD):** TS. Huỳnh Công Bằng

**Ngày bắt đầu:** 22/09/2026

@@COLWIDTHS:5,14,14,11,38,18@@

| Tuần | Từ ngày | Đến ngày | Ngày báo cáo GVHD | Tóm tắt công việc đã thực hiện | Nhận xét của GVHD |
|---|---|---|---|---|---|
| 1 | 22/09/2026 | 28/09/2026 | 04/10/2026 | Kiểm tệp nén, kiểm kê, tìm bản trùng, khóa tập chia; mô hình phân loại DataSEC; SED ba nhánh và Câu hỏi nghiên cứu 1 với nhiều lần huấn luyện; chỉ số F1 theo sự kiện và PSDS; mô tả bám sát sự kiện (Câu hỏi nghiên cứu 2); kho sự kiện và truy hồi (Câu hỏi nghiên cứu 3); SED v2; dịch vụ suy luận, API, giao diện; bộ phân tích câu hỏi | |
| 2 | 29/09/2026 | 03/10/2026 | 04/10/2026 | Vòng chọn hệ mốc và đo trên tập kiểm tra; Câu hỏi nghiên cứu 1 với SED v2; chạy lại Câu hỏi nghiên cứu 2, Câu hỏi nghiên cứu 3 trên hệ mốc; hoàn thiện ứng dụng minh họa, khóa artifact, tài liệu tái lập; báo cáo giữa kỳ | |
| 3 | 04/10/2026 | 10/10/2026 | | Biên tập báo cáo giữa kỳ; lập kế hoạch tối ưu SED; sàng lọc trên tập phát triển: suy luận chồng lấn, sửa dữ liệu huấn luyện; chọn trên dự đoán ngoài mẫu vòng 1 | |
| 4 | 11/10/2026 | 17/10/2026 | | Chọn trên dự đoán ngoài mẫu vòng 2; chọn hệ cơ sở theo luật ghi trước và đo trên tập kiểm tra (14/10) | |
| 5 | 18/10/2026 | 24/10/2026 | |  | |
| 6 | 25/10/2026 | 31/10/2026 | |  | |
| 7 | 01/11/2026 | 07/11/2026 | |  | |
| 8 | 08/11/2026 | 14/11/2026 | | Phục vụ hệ cơ sở; bốn hướng thử thêm (đều âm tính); LBR và đo trên tập kiểm tra; Câu hỏi nghiên cứu 2, Câu hỏi nghiên cứu 3 trên LBR; chẩn đoán PSDS; tra văn liệu | |
| 9 | 15/11/2026 | 21/11/2026 | |  | |
| 10 | 22/11/2026 | 28/11/2026 | | Rà soát trước khi nộp; sửa nội dung báo cáo; đo độ trễ ứng dụng minh họa; chụp lại ảnh giao diện; bản báo cáo tinh gọn; nộp ngày 28/11 (kế hoạch) | |
