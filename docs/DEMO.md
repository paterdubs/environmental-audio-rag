# Kịch bản demo local f2 (7–10 phút)

Demo phục vụ hệ thống SED f2 đã khóa: `sed_ensemble_t2b_20260927T200914Z` +
`sebb_cv_selection_annotated.json`. Máy demo cần Docker Desktop, checkpoint/BGE-M3/Qwen
đã tải sẵn trong repo local và llama.cpp Qwen3.5-9B theo `ml/configs/caption_llm.yaml`.

## Một lệnh khởi động

PowerShell 5.1, từ thư mục repo:

```powershell
.\scripts\demo_up.ps1
```

Script kiểm Docker, đọc model path từ `caption_llm.yaml`, khởi động llama.cpp cổng 8081 nếu
chưa có, build và khởi động Compose, chờ `/health` và f2 `official=true`, kiểm parser, nạp
history TRAIN nếu corpus `upload` đang rỗng, rồi mở `http://127.0.0.1:8088`.

Tuỳ chọn làm lại riêng history demo:

```powershell
.\scripts\demo_up.ps1 -ResetHistory -HistoryCount 20
```

Lệnh này chỉ xoá bản ghi `source_dataset='upload'` và audio upload tương ứng; không đụng
corpus `validation`/`test`, raw annotation hoặc split. Dừng app bằng:

```powershell
.\scripts\demo_down.ps1
```

Trước buổi demo khoảng 10 phút, chạy kiểm tra không khởi động service:

```powershell
.\scripts\demo_check.ps1
```

History được chọn tự động từ TRAIN, greedy theo độ phủ lớp và ưu tiên lớp dễ nghe. Lượt đã
chạy thật được ghi ở [demo_seed_20261002.md](measurements/demo_seed_20261002.md): 15 lựa chọn,
21 lớp phủ. Lượt kịch bản thật ở [demo_script_20261002.md](measurements/demo_script_20261002.md).

## Kịch bản nói và thao tác

| Thời gian | Thao tác | Bằng chứng cần chỉ |
|---|---|---|
| 0:00–1:00 | Chọn một WAV TRAIN chưa có trong history, upload | timeline, nhãn f2 chính thức, thời gian xử lý |
| 1:00–2:30 | Mở event, đổi EN/VI, bấm event để nghe | onset/offset, caption EN/VI và evidence |
| 2:30–6:00 | Nhập câu hỏi tự nhiên, kiểm chip rồi chạy | bộ lọc parser, câu trả lời và citation |
| 6:00–7:00 | Bấm citation | mở đúng recording và seek đúng đoạn audio |
| 7:00–8:00 | Nêu grounding | constrained-cover không bịa, đối chiếu artifact W5 |
| 8:00–9:00 | Tắt llama.cpp, chuyển bộ lọc thủ công | hệ thống vẫn truy vấn được khi parser unavailable |

Câu hỏi đã chạy thật qua API (artifact là nguồn chính, không chép tay):

- VI: “Bản ghi nào có tiếng động cơ xe chạy không tải?”
- EN: “Which recordings contain both vehicle idling and horn?”
- VI: “Có tiếng động cơ xe chạy không tải trước tiếng còi xe không?”
- EN: “Which recordings have vehicle idling lasting longer than 44.89 seconds?”
- VI: “Bản ghi nào có tiếng còi xe?”

Script chạy lại đúng luồng này và ghi JSON/Markdown:

```powershell
.venv\Scripts\python.exe scripts/report_demo_script.py --base-url http://127.0.0.1:8088
```

Grounding minh hoạ lấy từ W5 f2 đã có, không chạy lại test: các file
`caption_grounding_sed_ensemble_s13_f2_20260929T045053Z_test_annotated.*`.

## Offline và phương án dự phòng

Compose đặt `HF_HUB_OFFLINE=1` và `TRANSFORMERS_OFFLINE=1`; inference chỉ đọc cache
`artifacts/hf/models--BAAI--bge-m3`. Qwen đọc file GGUF local, không cần mạng. Kiểm tra
checksum/path model trước demo bằng `demo_check.ps1`; không tải model trong lúc trình bày.

Nếu parser lỗi hoặc llama.cpp bị tắt, bấm “Bộ lọc thủ công”, chọn lớp/predicate/thời lượng
rồi chạy truy vấn. Đây là fallback chức năng, không phải đổi metric. Nếu CPU inference quá
chậm, dùng `scripts.serve_demo.py` trên host GPU theo ADR-0033; không đổi f2/postproc.

Ảnh fallback 1440×900 đã chụp bằng Playwright:

- [01-start.png](demo_screenshots/01-start.png)
- [02-timeline.png](demo_screenshots/02-timeline.png)
- [03-filter-chip.png](demo_screenshots/03-filter-chip.png)
- [04-rag-evidence.png](demo_screenshots/04-rag-evidence.png)

Sinh lại ảnh khi Compose đang chạy:

```powershell
cd services/frontend
node scripts/capture_demo_screenshots.mjs
```

## Checklist ngày demo

- [ ] Docker Desktop đã chạy; `docker compose ps` cho `db`, `inference`, `api` healthy.
- [ ] `demo_check.ps1` pass; status báo `official=true`, `served_run` là f2.
- [ ] RAM/VRAM còn trống, đóng IDE/browser/app nặng, cắm sạc.
- [ ] Qwen, BGE-M3 và f2 có trên đĩa; không phụ thuộc mạng.
- [ ] Đo thời gian khởi động thật từ `demo_up.ps1` đến trang sẵn sàng; ghi vào sổ buổi demo.
- [ ] Có sẵn một WAV TRAIN chưa nằm trong history và đã nghe thử đoạn audio.
- [ ] Nếu cần làm sạch dữ liệu demo: `.\scripts\demo_up.ps1 -ResetHistory`.
- [ ] Nếu live lỗi: dùng ảnh trong `docs/demo_screenshots/`, hoặc tắt llama.cpp và chuyển
      bộ lọc thủ công.
