# Kịch bản demo f2 (5 phút)

Demo phục vụ hệ thống SED f2 đã khóa: `sed_ensemble_t2b_20260927T200914Z` +
`sebb_cv_selection_annotated.json`. Khi chạy mặc định, `/api/v1/models/status` phải báo
`official=true`. Máy cần Docker Desktop và llama.cpp Qwen3.5-9B theo
`ml/configs/caption_llm.yaml` (endpoint `http://127.0.0.1:8081`).

## Khởi động

Từ repo:

```text
docker compose --profile app up -d --build
```

Chờ cả `db`, `inference`, `api` healthy rồi mở `http://localhost:8088`. Kiểm tra nhanh:

```text
curl http://localhost:8088/api/v1/models/status
```

Nếu cần chạy frontend riêng: `npm ci && npm test && npm run build` trong `services/frontend`,
đặt `VITE_API_TARGET=http://localhost:8088`.

Chỉ dùng WAV thuộc split **train**, ví dụ `S-0016`. Lệnh kiểm chứng đầu-cuối:

```text
.venv/Scripts/python.exe scripts/report_demo_e2e.py --recording-id S-0016 --base-url http://localhost:8088
```

Artifact đã chạy thật: [demo_f2_e2e_20261002.md](measurements/demo_f2_e2e_20261002.md). Lượt này
dùng CPU container, upload + phân tích mất 2.012 s, có 2 event; caption EN/VI đều có evidence;
RAG hybrid mất 0.250 s và trả 1 evidence. Đây là thời gian của một lượt demo, không phải benchmark.

## Kịch bản 5 phút

* 0:00–1:00: upload WAV train, chờ phân tích, mở timeline và bấm event để phát đúng vị trí.
* 1:00–2:00: chuyển EN/VI, kiểm caption và evidence; nhãn phải là “SED f2 — T2b×3 + cSEBB,
  hệ thống chính thức”.
* 2:00–4:00: hỏi tự nhiên, kiểm chip trước khi chạy, rồi kiểm recording/khoảng thời gian trong
  evidence; có thể dùng “Có tiếng chim trước tiếng còi xe không?”.
* 4:00–5:00: sửa/xóa một chip và chạy lại; nếu parser không sẵn sàng, chuyển sang bộ lọc thủ công.

## Sự cố và override chẩn đoán

Nếu parser báo unavailable, bật llama.cpp hoặc kiểm tra `EARAG_LLM_ENDPOINT`. Nếu DB chưa healthy,
chạy `docker compose up -d db` và chờ healthcheck. Nếu inference CPU chậm, chờ hoàn tất; buổi demo
chính thức nên dùng `scripts.serve_demo` trên host GPU theo hướng dẫn vận hành.

Các biến `EARAG_SERVED_RUN` và `EARAG_SERVED_POSTPROC` chỉ dành cho chẩn đoán cục bộ. Khi đặt
override, status phải báo `official=false`; không dùng override trong demo chính thức và không
phân tích lại recording cũ.
