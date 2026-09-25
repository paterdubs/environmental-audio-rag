# ADR-0029 — W7: inference service, API service và corpus upload

**Status:** Proposed — agent tự quyết trong chế độ tự động (26/09), **chờ người dùng duyệt**;
mọi lựa chọn dưới đây đổi được mà không đụng số liệu nghiên cứu đã khoá
**Date:** 2026-09-26

## Context

W7 (7.1–7.4) dựng hệ thống chạy được đầu-cuối: upload → timeline → caption → truy vấn có
evidence. SYSTEM §4 đã chốt ranh giới (`api` không load model, post-processing nằm trong
inference, envelope `{success, data, error, meta}`, `/health` phản ánh readiness thật) và bảng
công nghệ (FastAPI, Pydantic v2, PostgreSQL + pgvector). Còn mở: hệ thống SED nào được phục vụ,
caption nào lúc suy luận, cách tách logic khỏi HTTP, và upload nằm ở corpus nào.

## Decision

### 1. Hệ thống SED phục vụ = hệ thống đã chọn trên dev ở ADR-0024

Ensemble C (`sed_ensemble_C_clean_20260925T045631Z`: trung bình xác suất 4 checkpoint nhánh C)
+ `postproc_cv.json` (θ global 0.95, `g_max` p25). `model_version` của event = run id ensemble.
Không chọn lại gì: đây là cấu hình đã khoá trước test. Corpus dev/test của RQ3 (ADR-0027) giữ
nguyên event của run B — hai corpus đó là benchmark, không phải dữ liệu vận hành.

### 2. Logic suy luận là thư viện `ml/inference`, HTTP chỉ là lớp mỏng

`ml/inference` (được import torch) làm: audio → `logmel_panns_v1` (cùng hàm trích đặc trưng,
**ép float16 như file đặc trưng đã lưu**) → cửa sổ 10 s theo đúng luật `SedFeatureDataset` →
từng checkpoint (autocast trên CUDA như `collect_predictions`) → trung bình xác suất → ghép
cửa sổ (`stack_predictions_by_recording`) → `process_recordings` với postproc đóng băng →
`canonicalize_timeline` → caption template EN + VI (ADR-0025) → document (ADR-0027 §3).
Mọi bước dùng lại hàm đã dùng khi đo, không viết lại.

**Nghiệm thu bằng parity:** chạy từ WAV DataSED test phải tái tạo xác suất trong
`predictions/test.npz` của ensemble (sai lệch nhỏ do fp16 được đo và ghi lại) và timeline
khớp event. Không có parity thì demo không chứng minh được nó là hệ thống đã đo.

### 3. Caption lúc suy luận = template, không LLM

Tất định, grounded theo cấu tạo, không cần GPU thứ hai cho LLM (ADR-0027 §3). Caption LLM
constrained là kết quả nghiên cứu RQ2, không phải thành phần phục vụ.

### 4. `services/inference` (FastAPI, có torch)

`GET /health` (200 chỉ khi mọi checkpoint + embedder đã nạp), `GET /v1/models`,
`POST /v1/analyze` (file audio → timeline + caption EN/VI + document + embedding),
`POST /v1/embed` (danh sách câu → vector BGE-M3, cho truy vấn). Không SQL.

### 5. `services/api` (FastAPI, không torch — kiểm cả tĩnh lẫn lúc chạy)

Endpoint theo SYSTEM §4.4 (tiền tố `/api/v1`, envelope). Persistence qua `ml.retrieval.store`
(psycopg, không torch); gọi inference qua HTTP (`httpx`). Truy vấn dùng lại
`ml.retrieval.answer` — câu trả lời luôn kèm `evidence[]` và bộ lọc đã áp. Test kiểm
`torch` vắng mặt trong `sys.modules` sau khi import app (guard grep hiện tại chỉ bắt import
trực tiếp).

### 6. Corpus `upload`

Recording upload: `source_dataset='upload'`, `split=NULL`, `recording_id='upload:<uuid>'`;
trùng `sha256` thì trả recording đã có. Truy vấn nhận `corpus ∈ {upload, validation, test}`
(mặc định `upload`); với `validation`/`test` câu SQL giữ nguyên như RQ3. Giới hạn: file ≤
50 MB, thời lượng ≤ 600 s; audio lưu ở `data/uploads/` (gitignored).

### 7. Kết quả parity (26/09, `inference_parity_20260925.md`, git `48615a0`, sạch)

142 recording test, CUDA. Đặc trưng từ WAV trùng file `.npy` 142/142 (lệch 0). Dựng đúng
batch lúc dump (24 cửa sổ trộn nhiều recording) → logit trùng **từng bit** ở cả 4
checkpoint: pipeline phục vụ là pipeline đã đo. Phục vụ từng recording riêng (batch khác)
thì autocast fp16 cho logit lệch tới ~0.06 (fp32 cũng lệch cỡ đó so với bản fp16 đã đóng
băng), xác suất lệch tối đa 0.0118: 332/408 event trùng khít, 377/408 trong 1 frame,
405/408 trong collar 0.2 s. Không phải lỗi: là nhiễu số học vốn có của chính số đã báo cáo
— ghi vào Hạn chế (biên event tại θ = 0.95 nhạy với nhiễu fp16 ở mức vài phần nghìn).

### 8. Triển khai (7.4): api trong Docker, inference trên host

`docker compose --profile app up -d --build` chạy `db` + `api`; image api (build nhiều tầng:
Node build frontend → Python slim, chỉ `requirements-api.txt`, không torch) phục vụ luôn
giao diện đã build — một origin, không cần container web riêng. **Inference không đóng image:**
torch CUDA + 4 checkpoint + BGE-M3 làm image nặng nhiều GB trên ổ đĩa đang gần đầy, và GPU
trong container trên Windows cần thêm cấu hình WSL2; inference chạy trên host
(`uvicorn ... --host 0.0.0.0 --port 8001`), api gọi qua `host.docker.internal`.
`scripts.serve_demo` là đường một lệnh cho máy dev (db qua compose, inference + api trên
host, chờ `/health` thật). Cổng api trong compose là 8088 vì 8000 trên máy dev đã bị một
ứng dụng khác dùng.

## Consequences

### Tích cực

- Demo chạy đúng hệ thống đã đo, kiểm được bằng parity.
- `api` test được không cần GPU/model (inference giả qua HTTP mock).

### Đánh đổi

- Nạp 4 checkpoint CNN14 + BGE-M3 trong một tiến trình: tốn VRAM/RAM hơn một run đơn.
- Upload và benchmark dùng hai hệ thống SED khác nhau (ensemble C vs run B) — tách corpus để
  không trộn; `model_version` ghi trên từng event.
- Demo chạy cục bộ: **không có xác thực, không giới hạn tần suất** (SYSTEM §4.4 không đặt
  yêu cầu này cho khóa luận). Chỉ bind 127.0.0.1 (compose publish 8088 trên máy dev); không
  đưa ra mạng công cộng khi chưa thêm hai lớp này.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Phục vụ run B `054531Z` (khớp index RQ3) | Không phải hệ thống tốt nhất đã chọn trên dev; RQ3 là benchmark riêng |
| Caption LLM constrained lúc suy luận | Cần llama.cpp + GPU song song; template đã grounded 100% |
| Một service duy nhất | Vi phạm SYSTEM §4.2 (api không load model) |
| SQLAlchemy ORM cho api | `ml.retrieval.store` (psycopg) đã được test tích hợp với RQ3; thêm ORM là viết lại |
