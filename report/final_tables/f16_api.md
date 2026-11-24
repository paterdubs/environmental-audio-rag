# Các endpoint HTTP của hai dịch vụ

> Sinh tự động bởi `scripts.report_system_tables` tại git `0e8680f`.

| Dịch vụ | Phương thức | Đường dẫn | Chức năng |
|---|---|---|---|
| API | GET | `/health` | Kiểm tra API và kết nối cơ sở dữ liệu |
| API | GET | `/api/v1/taxonomy` | 21 lớp SED và tên hiển thị EN/VI cho giao diện |
| API | GET | `/api/v1/models/status` | Phiên bản mô hình đang phục vụ (B0, LBR, điểm vận hành) |
| API | POST | `/api/v1/audio/upload` | Nhận tệp âm thanh, gọi suy luận, lưu sự kiện và mô tả |
| API | GET | `/api/v1/recordings` | Danh sách bản ghi theo kho, lọc theo lớp, phân trang |
| API | GET | `/api/v1/recordings/{recording_id}` | Thông tin một bản ghi |
| API | GET | `/api/v1/recordings/{recording_id}/timeline` | Dòng thời gian sự kiện của bản ghi |
| API | GET | `/api/v1/recordings/{recording_id}/caption` | Mô tả EN/VI kèm sự kiện bằng chứng |
| API | GET | `/api/v1/recordings/{recording_id}/audio` | Phát lại tệp âm thanh gốc |
| API | POST | `/api/v1/retrieval/parse` | Câu hỏi tự nhiên → bộ lọc JSON (llama.cpp) |
| API | POST | `/api/v1/retrieval/query` | Truy hồi theo chế độ và trả lời có bằng chứng |
| Suy luận | GET | `/health` | Trạng thái nạp mô hình |
| Suy luận | GET | `/v1/models` | Thông tin mô hình SED, LBR, embedding đã nạp |
| Suy luận | POST | `/v1/analyze` | Tệp âm thanh → dòng thời gian, mô tả, tài liệu, vector |
| Suy luận | POST | `/v1/embed` | Nhúng câu hỏi bằng BGE-M3 |

**Nguồn:** `services/api/app/main.py`; `services/api/app/recordings.py`; `services/api/app/retrieval.py`; `services/inference/app/main.py`.
