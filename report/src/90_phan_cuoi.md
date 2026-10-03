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

Mọi run, ensemble và checkpoint ngoài được trích trong báo cáo đã được kiểm sự tồn tại và ghi SHA-256 ngày 02/10/2026 bằng `scripts.freeze_artifacts`. Danh sách đầy đủ của 11 lần chạy hoặc ensemble, các checkpoint ngoài và các tệp đầu vào cố định, kèm SHA-256 từng tệp, nằm ở `docs/measurements/artifact_freeze_20261002.md`; không thiếu tệp nào.

Bảng dưới là sổ ghi mọi lần chạm tập test tính đến mốc báo cáo, sinh tự động từ các tệp kết quả đã khóa.

@@CAP:tbl:ledger|Sổ ghi các lần chạm tập test tính đến mốc báo cáo@@

@@INCLUDE:report/tables/m06_test_ledger.md@@

@@HEADING2N:Phụ lục C. Kết quả theo lớp@@

Theo giao thức đánh giá, lớp có dưới 10 mẫu test chỉ được báo bằng số tuyệt đối. Bảng đầu là mô hình phân loại DataSEC ở cấp lớp gộp; bảng sau là hệ SED f2 trên test annotated. Ở bảng sau, số sự kiện tham chiếu được đếm từ nhãn gốc, còn F1, precision và recall đọc từ tệp đánh giá đã lưu, không chạy lại đánh giá.

@@CAP:tbl:classperclass|Mô hình phân loại DataSEC theo lớp gộp (test)@@

@@INCLUDE:report/tables/m02_classifier_per_class.md@@

@@CAP:tbl:f2perclass|Event-F1 theo lớp của hệ f2 trên test annotated@@

@@INCLUDE:report/tables/m05_f2_per_class.md@@

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
| 3 | 04/10/2026 | 10/10/2026 | | (chưa diễn ra) | |
| 4 | 11/10/2026 | 17/10/2026 | | (chưa diễn ra) | |
| 5 | 18/10/2026 | 24/10/2026 | | (chưa diễn ra) | |
| 6 | 25/10/2026 | 31/10/2026 | | (chưa diễn ra) | |
| 7 | 01/11/2026 | 07/11/2026 | | (chưa diễn ra) | |
| 8 | 08/11/2026 | 14/11/2026 | | (chưa diễn ra) | |
