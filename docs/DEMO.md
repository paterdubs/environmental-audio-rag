# Kịch bản demo (5 phút)

Demo dùng profile `app`, phục vụ SED v2 theo ADR-0035. Đây là demo, không phải hệ thống chính thức; mặc định code vẫn v1. Máy cần Docker Desktop, NVIDIA/CUDA hoặc CPU đủ cho inference, Node.js 20+ nếu chạy frontend dev, và llama.cpp server Qwen3.5-9B.

## Khởi động

1. Bật llama.cpp theo `ml/configs/caption_llm.yaml` (endpoint `http://127.0.0.1:8081`, grammar/schema JSON của ADR-0036).
2. Từ repo chạy `docker compose --profile app up -d --build` rồi mở `http://localhost:8088`.
3. Nếu chạy frontend riêng: `npm ci && npm test && npm run build` trong `services/frontend`, đặt `VITE_API_TARGET=http://localhost:8088`.

File mẫu chỉ được dùng từ split **train**, ví dụ `S-0016` trong manifest DataSED. Không dùng validation/test để trình diễn vì demo cần tránh mở test và không tạo số đánh giá mới. Có thể chạy kiểm chứng tự động bằng:

```text
.venv/Scripts/python.exe scripts/report_demo_e2e.py --recording-id S-0016 --base-url http://localhost:8088
```

Artifact đã chạy thật: [demo_v2_e2e_20260928.md](measurements/demo_v2_e2e_20260928.md) ghi upload + phân tích 5.113 s, 2 event; caption EN/VI có evidence; RAG hybrid 0.270 s và 2 evidence. Đây là thời gian của lần chạy ghi trong artifact, không phải cam kết cho mọi máy.

## Kịch bản 5 phút

* 0:00–1:00: upload file train, chờ trạng thái “Đang phân tích…”, mở timeline và bấm một bar để phát đúng vị trí.
* 1:00–2:00: chuyển EN/VI, kiểm caption và evidence; nhãn model phải hiện “Demo — SED v2, chưa phải hệ thống chính thức”.
* 2:00–4:00: dùng ô hỏi tự nhiên, kiểm chip trước khi chạy rồi hỏi lần lượt: “Có tiếng chim trước tiếng còi xe không?”, “Which recordings have voices overlapping with vehicle pass-by?”, “Có tiếng nhạc và tiếng người cùng xuất hiện không?”. Các câu này được gửi qua `/retrieval/parse`; kiểm recording/khoảng thời gian trong evidence trên stack đang chạy.
* 4:00–5:00: xoá một chip hoặc đổi predicate, chạy lại; tắt llama.cpp để thấy lỗi rõ và chuyển sang “Bộ lọc thủ công”.

## Quay về v1 và xử lý sự cố

Để quay về v1, bỏ `EARAG_SERVED_RUN` và `EARAG_SERVED_POSTPROC` khỏi môi trường compose rồi tạo lại service inference/api; không đổi hằng mặc định và không phân tích lại recording đã upload. Nếu parser báo unavailable, bật lại llama.cpp/kiểm tra `EARAG_LLM_ENDPOINT`; nếu upload lâu, chờ CPU hoàn tất và không tải lại trang. Nếu DB chưa healthy, chạy `docker compose up -d db` rồi chờ healthcheck.
