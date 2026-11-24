@@SECTION:body@@

@@HEADING1N:TÀI LIỆU THAM KHẢO@@

@@BIB@@

@@SECTION:refs@@

@@HEADING1N:PHỤ LỤC@@

@@APPENDIX@@

@@HEADING2N:Phụ lục A. Hệ lớp và số sự kiện đa âm@@

Bảng dưới liệt kê 22 lớp của hệ lớp phiên bản 0.1, nhãn gốc tương ứng, các lớp con chỉ có trên DataSEC, và số sự kiện trong bản nhãn đa âm của DataSED (toàn bộ ba tập). Lớp `wind_turbine` không thuộc 21 lớp của mô hình SED.

@@CAP:tbl:taxonomy|Hệ lớp phiên bản 0.1@@

@@COLWIDTHS:30,22,25,11,12@@

@@INCLUDE:report/tables/m08_taxonomy.md@@

@@HEADING2N:Phụ lục B. Artifact đã đóng băng@@

Mọi run, ensemble và checkpoint ngoài được trích trong báo cáo đã được kiểm sự tồn tại và ghi SHA-256 ngày 11/11/2026 bằng `scripts.freeze_artifacts`. Danh sách đầy đủ của 129 lần chạy hoặc ensemble, 5 checkpoint ngoài và 8 tệp đầu vào cố định, kèm SHA-256 từng tệp, nằm ở `docs/measurements/artifact_freeze_20261111.md`; không thiếu tệp nào. Bảng dưới liệt kê các hệ chính và gộp các run phụ của giai đoạn O.

@@CAP:tbl:freeze|Artifact đã đóng băng và kiểm SHA-256@@

@@COLWIDTHS:32,40,9,9@@

@@INCLUDE:report/final_tables/f08_freeze.md@@

Bảng dưới là sổ ghi mọi lần chạm tập test tính đến mốc báo cáo, sinh tự động từ các tệp kết quả đã khóa.

@@CAP:tbl:ledger|Sổ ghi các lần chạm tập test tính đến mốc báo cáo@@

@@INCLUDE:report/final_tables/f07_ledger.md@@

@@HEADING2N:Phụ lục C. Kết quả theo lớp@@

Theo giao thức đánh giá, lớp có dưới 10 mẫu test chỉ được báo bằng số tuyệt đối. Bảng đầu là mô hình phân loại DataSEC ở cấp lớp gộp; bảng sau là hệ SED trên test annotated: trước hết B0 và LBR V2 (hệ cuối), sau đó f2 (mốc so sánh của S13). Ở bảng sau, số sự kiện tham chiếu được đếm từ nhãn gốc, còn F1, precision và recall đọc từ tệp đánh giá đã lưu, không chạy lại đánh giá.

@@CAP:tbl:classperclass|Mô hình phân loại DataSEC theo lớp gộp (test)@@

@@INCLUDE:report/tables/m02_classifier_per_class.md@@

@@CAP:tbl:b0perclass|Event-F1 theo lớp của B0 và LBR V2 trên test annotated@@

@@COLWIDTHS:33,13,12,12,15,15@@

@@INCLUDE:report/final_tables/f09_per_class.md@@

@@CAP:tbl:f2perclass|Event-F1 theo lớp của hệ f2 (mốc so sánh) trên test annotated@@

@@INCLUDE:report/tables/m05_f2_per_class.md@@

@@HEADING2N:Phụ lục D. Phân công công việc và công cụ hỗ trợ@@

Hai thành viên chia các mảng công việc thành hai phần có khối lượng tương đương; mỗi mảng có một người phụ trách chính và một người kiểm chéo, nên cả hai đều đọc, chạy lại và có thể trình bày mọi phần của đề tài. Các quyết định thiết kế (50 ADR), mọi lần mở tập test và mọi kết luận đều do cả hai cùng duyệt. Mã nguồn được commit từ một tài khoản chung, nên lịch sử git không phản ánh việc phân công này.

@@CAP:tbl:division|Phân công công việc@@

@@COLWIDTHS:9,41,25,25@@

| TT | Mảng công việc | Phụ trách chính | Kiểm chéo |
|---:|---|---|---|
| 1 | Dữ liệu: kiểm chứng tệp nén, kiểm kê, khử trùng lặp, chia tập, cổng rò rỉ | Phạm Hoàng Phát | Thân Trọng Tính |
| 2 | Bộ phân loại DataSEC, hiệu chuẩn và câu hỏi RQ1 | Thân Trọng Tính | Phạm Hoàng Phát |
| 3 | Mô hình SED B0, hậu xử lý, giao thức chọn trên dự đoán ngoài mẫu và test một lần | Phạm Hoàng Phát | Thân Trọng Tính |
| 4 | Tinh chỉnh biên học được (LBR) và thước đo ứng dụng | Thân Trọng Tính | Phạm Hoàng Phát |
| 5 | Mô tả có căn cứ, bộ đo grounding và RQ2 | Thân Trọng Tính | Phạm Hoàng Phát |
| 6 | Kho sự kiện, truy hồi, câu trả lời có bằng chứng và RQ3 | Phạm Hoàng Phát | Thân Trọng Tính |
| 7 | Dịch vụ suy luận và API, giao diện web, triển khai Docker Compose | Thân Trọng Tính | Phạm Hoàng Phát |
| 8 | Tra cứu văn liệu, đối chiếu nguồn và bối cảnh quy chuẩn | Phạm Hoàng Phát | Thân Trọng Tính |
| 9 | Báo cáo, slide và tài liệu tái lập | Cả hai | Cả hai |

**Công cụ hỗ trợ.** Nhóm có dùng công cụ trí tuệ nhân tạo (mô hình ngôn ngữ lớn) làm công cụ hỗ trợ lập trình, tra cứu và biên tập văn bản. Các quyết định thiết kế, thí nghiệm và kết luận do nhóm đưa ra và chịu trách nhiệm; số liệu trong báo cáo do các script trong kho mã sinh ra và có thể chạy lại, không do công cụ tự ghi.

@@PAGEBREAK@@

@@HEADING1N:NHẬT KÍ LÀM VIỆC@@

**Đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

**Giảng viên hướng dẫn:** TS. Huỳnh Công Bằng

**Ngày bắt đầu:** 22/09/2026

@@COLWIDTHS:5,14,14,11,38,18@@

| Tuần | Từ ngày | Đến ngày | Ngày báo cáo GVHD | Tóm tắt công việc đã thực hiện | Nhận xét của GVHD |
|---|---|---|---|---|---|
| 1 | 22/09/2026 | 28/09/2026 | 04/10/2026 | Kiểm chứng tệp nén, kiểm kê, khử trùng lặp nội bộ và xuyên dataset, đóng băng tập chia; mô hình phân loại DataSEC; SED ba nhánh và RQ1 nhiều seed; metric event-F1/PSDS; mô tả có căn cứ (RQ2); kho sự kiện và truy hồi (RQ3); chẩn đoán và chốt SED v2; dịch vụ suy luận, API, giao diện; Track 2a; bộ phân tích câu hỏi | |
| 2 | 29/09/2026 | 03/10/2026 | 04/10/2026 | Focal loss (S11); vòng chọn cuối S13 khóa f2 và test một lần; RQ1-v2; chạy lại RQ2/RQ3 trên f2 (S8); hoàn thiện demo, đóng băng artifact, tài liệu tái lập; báo cáo giữa kỳ | |
| 3 | 04/10/2026 | 10/10/2026 | | Dựng lại slide và biên tập báo cáo giữa kỳ; lập kế hoạch giai đoạn tối ưu SED (chẩn đoán RQ1, rà dữ liệu và suy luận); sàng lọc trên dev: suy luận chồng lấn, sửa dữ liệu huấn luyện, GRU tiền huấn luyện; chọn bằng dự đoán ngoài mẫu vòng 1 | |
| 4 | 11/10/2026 | 17/10/2026 | | Chọn bằng dự đoán ngoài mẫu vòng 2 (BEATs tinh chỉnh, ensemble); chọn B0 theo luật ghi trước và test một lần (14/10) | |
| 5 | 18/10/2026 | 24/10/2026 | |  | |
| 6 | 25/10/2026 | 31/10/2026 | |  | |
| 7 | 01/11/2026 | 07/11/2026 | |  | |
| 8 | 08/11/2026 | 14/11/2026 | | Phục vụ B0 và mô tả/truy hồi trên B0; giai đoạn P (bốn hướng, đều âm tính); LBR (tinh chỉnh biên, chấm lại hộp), test một lần; RQ2/RQ3 trên LBR; chẩn đoán PSDS; tra văn liệu; đồng bộ tài liệu | |
| 9 | 15/11/2026 | 21/11/2026 | |  | |
| 10 | 22/11/2026 | 28/11/2026 | | Rà soát độc lập trước khi nộp; sửa nội dung báo cáo (RQ3, giải thích kết quả, bối cảnh quy chuẩn, đóng góp, thước định cỡ); đo độ trễ demo; chụp lại ảnh giao diện; hoàn thiện hình thức; nộp ngày 28/11 (kế hoạch) | |
