# Services (W7, [ADR-0029](../docs/decisions/ADR-0029-inference-va-api-service.md))

| Service | Trách nhiệm | Không chứa | Chạy |
|---|---|---|---|
| `inference` | Nạp ensemble C + postproc đóng băng + BGE-M3; audio → timeline → caption EN/VI → document + embedding | SQL, persistence | `uvicorn services.inference.app.main:app --port 8001` |
| `api` | Upload, lưu trữ (PostgreSQL + pgvector), đọc recording, truy vấn có evidence, phục vụ giao diện đã build | torch, checkpoint (kiểm cả tĩnh lẫn lúc chạy) | `uvicorn services.api.app.main:app --port 8010` hoặc Docker |
| `frontend` | Upload, timeline, caption, truy vấn, provenance (React + Vite + TanStack Query) | hằng số taxonomy tự khai (đọc `/api/v1/taxonomy`) | `npm run dev` / `npm run build` |
| `common` | Envelope `{success, data, error, meta}`, kiểm file audio upload | torch | — |
| `stream` | Dự kiến: chunk streaming/stitching | — | chưa làm (cut-list #2) |

Một lệnh cho máy dev: `.venv/Scripts/python.exe -m scripts.serve_demo`.
