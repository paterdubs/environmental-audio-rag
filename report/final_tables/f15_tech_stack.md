# Công nghệ sử dụng theo tầng

> Sinh tự động bởi `scripts.report_system_tables` tại git `0e8680f`.

| Tầng | Công nghệ | Phiên bản (từ tệp cấu hình) | Vai trò trong hệ thống | ADR |
|---|---|---|---|---|
| Hạ tầng | Docker Compose | 3 dịch vụ: db, inference, api | Dựng ba dịch vụ db, api, inference bằng một lệnh; cô lập phụ thuộc của từng dịch vụ | 0029 |
| Hạ tầng | Python; Node.js (build giao diện) | python 3.12-slim; node 24-slim | Python cho học máy, đánh giá và hai dịch vụ; Node.js chỉ dùng khi build giao diện | — |
| Học máy | PyTorch | >=2.8, <3 | Huấn luyện và suy luận mô hình SED, mô hình phân loại DataSEC | 0002 |
| Học máy | librosa, soundfile | librosa >=0.11, <1; soundfile >=0.13, <1 | Đọc âm thanh, đổi tần số lấy mẫu, trích log-mel | — |
| Học máy | scikit-learn | >=1.6, <2 | Hai bộ học tăng cường gradient của LBR | 0045 |
| Đánh giá | sed_eval, psds_eval | sed_eval >=0.2.1, <1; psds_eval >=0.5.3, <1 | Event-F1 theo collar và PSDS bằng thư viện chuẩn, không tự viết lại | 0020 |
| Đánh giá | pytest, ruff | pytest >=8, <10; ruff >=0.12, <1 | Kiểm thử tự động và kiểm tra mã trong CI | — |
| Mô hình ngôn ngữ | llama.cpp + Qwen3.5-9B | build b11158; Qwen_Qwen3.5-9B-Q4_K_M.gguf | Chạy cục bộ: phân tích câu hỏi thành bộ lọc JSON; sinh mô tả cho thí nghiệm RQ2 | 0022, 0036 |
| Truy hồi | sentence-transformers (BGE-M3) | >=3, <6 | Nhúng tài liệu và câu hỏi tiếng Việt, tiếng Anh vào cùng không gian 1024 chiều | 0004 |
| Lưu trữ | PostgreSQL 16 + pgvector | pg16 | Kho sự kiện: bộ lọc, điều kiện thời gian và xếp hạng vector trong một câu SQL | 0005 |
| Lưu trữ | psycopg | >=3.2, <4 | Trình điều khiển PostgreSQL cho API và script dựng kho | — |
| Dịch vụ | FastAPI, Uvicorn | fastapi >=0.115, <1; uvicorn >=0.30, <1 | Hai dịch vụ HTTP: API (không nạp torch) và suy luận | 0029 |
| Dịch vụ | httpx | >=0.27, <1 | API gọi dịch vụ suy luận và llama.cpp | — |
| Giao diện | React | ^19.3.0 | Giao diện một trang: tải lên, dòng thời gian, thẻ bộ lọc, câu trả lời | 0037 |
| Giao diện | TypeScript, Vite | typescript ^7.0.2; vite ^8.3.1 | Kiểu tĩnh cho giao diện; đóng gói bản build phục vụ qua API | — |
| Giao diện | TanStack Query | ^5.103.2 | Gọi API và lưu đệm kết quả phía trình duyệt | — |
| Giao diện | Vitest, Playwright | vitest ^5.0.2; playwright ^1.63.0 | Kiểm thử thành phần giao diện và chụp ảnh màn hình demo | — |

**Nguồn:** `requirements*.txt`; `services/frontend/package.json`; `docker-compose.yml`; `services/*/Dockerfile`; `ml/configs/caption_llm.yaml`.
