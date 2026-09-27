# ADR-0033 — Container hoá `services/inference` (hoàn thành W7 7.4)

**Status:** Accepted — người dùng yêu cầu 27/09 ("hoàn thành đến giai đoạn demo trực tiếp được"),
chọn phương án container hoá inference khi được hỏi phạm vi cụ thể.
**Date:** 2026-09-27

## Context

ADR-0029 §8 cố ý **không** đóng image cho `services/inference` (torch + 4 checkpoint CNN14 +
BGE-M3), lý do: image nặng nhiều GB trên ổ đĩa lúc đó đã gần đầy, và GPU trong container trên
Windows cần cấu hình WSL2 + `nvidia-container-toolkit` thêm. Việc này để lại trong PLAN 7.4 làm
sau, dự kiến 19/10–02/11.

Người dùng tạm dừng giai đoạn cải thiện SED (ADR-0031) ở S10/T2a để chuyển sang hoàn thiện demo
ngay, và khi hỏi rõ phạm vi ("chỉ xác nhận demo hiện tại" / "đóng gói inference vào Docker" /
"làm luôn 7.5–7.7") đã chọn **đóng gói inference vào Docker**. 7.5–7.7 vẫn khoá bởi S13 (vòng
chọn cuối 18/10, ADR-0031 §4) nên không đổi.

Kiểm lại tình hình đĩa (27/09): còn **7.9 GB trống**. `artifacts/checkpoints/Cnn14_mAP=0.431.pth`
1.3 GB, `artifacts/hf` (cache BGE-M3) 4.3 GB — hai thứ này riêng đã gần hết chỗ trống. Docker
Desktop đang tắt (dịch vụ `com.docker.service`: Stopped).

## Decision

### 1. Không nướng checkpoint/BGE-M3 vào image — mount qua volume, chỉ đọc

`ml.inference.engine.Engine` và `ml.retrieval.embedding.Embedder` đã tính đường dẫn
(`ml/runs/…`, `artifacts/hf`) **tương đối theo chính file `.py`**, không đọc biến môi trường
riêng — nên mount `./ml/runs:/app/ml/runs:ro` và `./artifacts/hf:/app/artifacts/hf:ro` vào đúng
`/app/ml/runs`, `/app/artifacts/hf` (vì `WORKDIR /app` và code copy vào `/app/ml`) chạy được
**không cần sửa một dòng code nào**. Tránh nhân đôi vài GB nhị phân vào layer image trên ổ đĩa
đang cạn, và weight đổi (ví dụ đổi hệ thống phục vụ ở S8) không cần build lại image.

### 2. CPU trong container, không GPU

`Engine.__init__` đã tự chọn `"cuda" if torch.cuda.is_available() else "cpu"` — container không
được cấp GPU nên tự rơi về CPU, không cần sửa code. Đổi lại: chậm hơn GPU, nhưng cho một bản ghi
âm ngắn ở quy mô demo là chấp nhận được, và tránh hẳn việc cấu hình `nvidia-container-toolkit`
trong WSL2 trên Windows — chi phí đó không xứng đáng chỉ để demo. Muốn dùng GPU thật thì vẫn
chạy inference trên host như ADR-0029 §8 (comment trong `docker-compose.yml` ghi lại cách đổi).

**Hạn chế cần ghi vào Hạn chế báo cáo:** parity 7.1 gốc đo trên CUDA (ADR-0029 §7); CPU đi qua
một đường số học khác (fp32 toàn bộ, không autocast). Chưa đo lại parity trên CPU trong ADR này —
nếu demo dùng để trích số báo cáo (không nên, demo chỉ minh hoạ) thì phải đo lại như §7.

### 3. `requirements-inference.txt` riêng, tối thiểu theo import thật

Không dùng `requirements.txt` gộp (có `pytest`, `ruff`, `iterative-stratification`,
`scikit-learn`… không cần lúc chạy). Đối chiếu **trực tiếp bằng grep import** toàn bộ chuỗi
`ml.inference` → `ml.models`/`ml.postprocessing`/`ml.evaluation`/`ml.captioning`/`ml.retrieval`
→ chỉ cần: `numpy`, `pandas`, `PyYAML`, `librosa`, `soundfile`, `torch`, `sentence-transformers`,
`fastapi`, `uvicorn`, `python-multipart`. Không cần `psycopg`/`pgvector` (inference không chạm
SQL, ADR-0029 §4) và không cần `sed_eval`/`psds_eval` (`ml.evaluation.sed_metrics` chỉ import
chúng **lười, bên trong hàm** — `event_based_f1`/`psds_score` không được inference gọi).

### 4. `COPY ml/ ml/` nguyên khối, không chọn từng thư mục con như `services/api/Dockerfile`

`services/api/Dockerfile` chọn từng thư mục con của `ml/` có chủ đích (bảo vệ bất biến "api
không import torch" khỏi trôi khi ai đó thêm import mới). Inference đã cần torch nên bất biến đó
không áp dụng; chọn cách chép nguyên `ml/` cho đơn giản và không giòn (không phải sửa Dockerfile
mỗi lần thêm module mới trong chuỗi import). `.dockerignore` đã loại `ml/runs`, `data`,
`artifacts` từ trước — không nướng nhầm checkpoint vào image dù copy nguyên khối `ml/`.

### 5. `api` gọi `inference` qua tên service trong mạng compose

`INFERENCE_URL=http://inference:8001` thay `http://host.docker.internal:8001`; `depends_on`
thêm `inference: condition: service_healthy`. Healthcheck của `inference` gọi `curl /health`
(`start_period` 90 s vì nạp 4 checkpoint + BGE-M3 từ volume mount trước khi `/health` trả 200,
đúng SYSTEM §4.4).

## Consequences

### Tích cực

- `docker compose --profile app up -d --build` chạy được toàn bộ (`db` + `inference` + `api`)
  chỉ bằng một lệnh, không cần biết chạy `uvicorn` trên host.
- Không tốn thêm đĩa cho model weight (mount, không copy).

### Đánh đổi

- CPU chậm hơn GPU cho `/v1/analyze` — chấp nhận được cho demo, không cho benchmark.
- Parity CPU chưa đo (chỉ đo trên CUDA ở ADR-0029 §7) — ghi vào Hạn chế nếu demo được dùng để
  trích số.
- `docker compose build inference` cần tải torch CPU (~200–700 MB tuỳ bản) mỗi lần build lại từ
  đầu nếu cache lớp bị xoá — chấp nhận được, một lần.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Nướng checkpoint/BGE-M3 vào image | Nhân đôi ~5.6 GB nhị phân trên ổ đĩa chỉ còn 7.9 GB trống; build lại mỗi lần đổi hệ thống phục vụ (S8) |
| GPU trong container (nvidia-container-toolkit + WSL2) | Chi phí cấu hình không xứng cho một demo cục bộ; CPU đã đủ nhanh cho một bản ghi ngắn |
| Giữ nguyên host-based (ADR-0029 §8) | Người dùng yêu cầu rõ "đóng gói inference vào Docker" khi được hỏi |
| Dùng `requirements.txt` gộp cho image | Kéo theo `pytest`/`ruff`/`scikit-learn` không cần lúc chạy, ảnh hưởng kích thước image |
