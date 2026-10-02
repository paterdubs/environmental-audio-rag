# Đề cương báo cáo khóa luận tốt nghiệp

**Tên đề tài:** Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG

## Quy cách của mẫu khoa

- Mẫu nguồn: `report/Mau bao cao KLTN_DS.docx` (SHA-256
  `9d3bc27605d682083e9aea09de9aabae47ba499a85344d95936d06a3cb4c6667`).
- Khổ A4, trình bày một mặt; Times New Roman cỡ 13; giãn dòng 1,5.
- Lề trên 3 cm, dưới 3 cm, trái 3,5 cm, phải 2 cm.
- Tên chương dùng Heading 1, cỡ 14, in đậm, chữ in hoa; các cấp mục dùng Heading 2–4.
- Chú thích bảng đặt phía trên; chú thích hình đặt phía dưới; đánh số theo chương.
- Mục lục hiển thị đến cấp mục thứ ba; phần nội dung bắt đầu đánh số trang từ trang 1.

## Phần đầu

1. Bìa tiếng Việt — dùng nguyên văn tên đề tài chính thức.
2. Bìa phụ tiếng Việt — dùng nguyên văn tên đề tài chính thức.
3. Bìa tiếng Anh — chỉ điền sau khi tên tiếng Anh được người dùng/GVHD duyệt.
4. Abstract và Keywords tiếng Anh — một trang.
5. Tóm tắt và từ khóa tiếng Việt — một trang.
6. Lời cảm ơn.
7. Nhận xét của giảng viên hướng dẫn.
8. Nhận xét của giảng viên phản biện 1 và 2.
9. Mục lục.
10. Danh mục hình ảnh.
11. Danh mục bảng biểu.
12. Danh mục thuật ngữ viết tắt.

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và lý do chọn đề tài

## 1.2. Phát biểu bài toán

## 1.3. Mục tiêu nghiên cứu

## 1.4. Câu hỏi nghiên cứu

### 1.4.1. RQ1 — Transfer learning DataSEC → DataSED

### 1.4.2. RQ2 — Grounding và hallucination của caption

### 1.4.3. RQ3 — Structured, vector và hybrid retrieval

## 1.5. Phạm vi và giới hạn

## 1.6. Đóng góp của đề tài

## 1.7. Cấu trúc báo cáo

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG TRÌNH LIÊN QUAN

## 2.1. Phát hiện sự kiện âm thanh đa nhãn

### 2.1.1. Nhãn clip-level và strong label

### 2.1.2. Event-based F1, collar và PSDS

### 2.1.3. Hậu xử lý ngưỡng và cSEBB

## 2.2. Transfer learning cho âm thanh môi trường

### 2.2.1. AudioSet và encoder tiền huấn luyện

### 2.2.2. Pretraining theo frame

### 2.2.3. Domain shift và nguy cơ leakage

## 2.3. Sinh mô tả có ràng buộc bằng chứng

## 2.4. Retrieval-Augmented Generation trên event timeline

## 2.5. Tổng hợp khoảng trống nghiên cứu

# CHƯƠNG 3. DỮ LIỆU VÀ QUY TRÌNH CHUẨN BỊ

## 3.1. DataSEC

## 3.2. DataSED

## 3.3. Taxonomy và ánh xạ nhãn

## 3.4. Quy trình D0–D4

### 3.4.1. Kiểm chứng archive và inventory

### 3.4.2. Chuẩn hóa annotation

### 3.4.3. Phát hiện trùng lặp nội bộ và xuyên dataset

### 3.4.4. Chia tập theo leakage group

## 3.5. Thống kê và độ phủ nhãn

## 3.6. Rủi ro dữ liệu và biện pháp kiểm soát

# CHƯƠNG 4. PHƯƠNG PHÁP VÀ KIẾN TRÚC HỆ THỐNG

## 4.1. Kiến trúc tổng thể

## 4.2. Mô hình phân loại DataSEC

## 4.3. Mô hình SED

### 4.3.1. Baseline v1

### 4.3.2. SED v2

### 4.3.3. T2b: Frame-MobileNet và ensemble f2

### 4.3.4. Hậu xử lý cSEBB

## 4.4. Grounded captioning

### 4.4.1. Event timeline và grammar

### 4.4.2. Chế độ unconstrained, constrained và constrained-cover

### 4.4.3. Caption tiếng Anh và tiếng Việt

## 4.5. Tầng RAG

### 4.5.1. Event store và tài liệu truy hồi

### 4.5.2. Structured, vector và hybrid retrieval

### 4.5.3. Parser câu hỏi thành bộ lọc

## 4.6. API, inference service và frontend

## 4.7. Khả năng tái lập và provenance

# CHƯƠNG 5. THỰC NGHIỆM VÀ KẾT QUẢ

## 5.1. Giao thức đánh giá

### 5.1.1. Luật chọn trên dev và test một lần

### 5.1.2. Metric và bootstrap CI

## 5.2. RQ1 và RQ1-v2

## 5.3. Tiến triển SED v1 → v2 → S13

### 5.3.1. Ablation SED v2

### 5.3.2. Xếp hạng S13 trên dev

### 5.3.3. Kết quả test và phân tích theo lớp

### 5.3.4. Ảnh hưởng của cSEBB

## 5.4. RQ2 — Grounded captioning

## 5.5. RQ3 — Retrieval và trả lời có bằng chứng

## 5.6. Parser câu hỏi tự nhiên

## 5.7. Parity triển khai và thời gian xử lý

## 5.8. Thảo luận kết quả và đe dọa tính hợp lệ

# CHƯƠNG 6. ỨNG DỤNG DEMO

## 6.1. Kiến trúc triển khai local

## 6.2. Quy trình khởi động một lệnh

## 6.3. Upload, timeline và caption song ngữ

## 6.4. Truy vấn RAG và evidence playback

## 6.5. Phương án fallback và kiểm tra offline

# CHƯƠNG 7. KẾT LUẬN, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Kết luận theo câu hỏi nghiên cứu

## 7.2. Hạn chế

## 7.3. Hướng phát triển

# TÀI LIỆU THAM KHẢO

- Chỉ đưa nguồn mức V3/V4 trong `docs/RELATED_WORK.md` vào bản hiện tại.
- Danh mục BibTeX nguồn: `docs/thesis/bibliography.bib`.

# PHỤ LỤC

## A. Taxonomy và ánh xạ nhãn

## B. Cấu hình thí nghiệm và artifact freeze

## C. Bảng kết quả đầy đủ

## D. Kịch bản và ảnh dự phòng demo

## E. Lệnh tái lập
