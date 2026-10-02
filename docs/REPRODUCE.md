# Tái lập kết quả

Tài liệu này tách hai việc: (1) **audit** các artifact đã đóng băng, có thể chạy ngay trong
repository hiện tại; (2) tái tạo toàn bộ thí nghiệm trong một clone/máy mới. Không chạy lại các
lệnh có test ở clone đã tạo ra số chính thức: test đã mở đúng một lần và được ghi ở
[`test_ledger_20261002.md`](measurements/test_ledger_20261002.md).

## Môi trường đã đo

Máy thực nghiệm Windows dùng Python 3.12.10, PyTorch `2.11.0+cu128`, CUDA runtime PyTorch 12.8,
GPU RTX 3070 Laptop 8 GB; driver hiển thị CUDA 13.1. llama.cpp là `b11158` (commit `3423f940e`).
CPU container của parity dùng torch `2.14.0+cpu`. Khác biệt phiên bản CPU/CUDA được ghi thẳng trong
[`inference_parity_cpu_20261002.md`](measurements/inference_parity_cpu_20261002.md), không được coi
là bit-identical.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pytest -q
cd services/frontend
npm ci
npm test
npm run build
```

## Dữ liệu và trọng số

Tải đúng hai archive DataSEC/DataSED được khai báo trong `ml/configs/sources.yaml`; kiểm MD5 và
giấy phép từ Zenodo bằng `scripts.report_archive_audit`. Không tự tạo lại split: dùng
`data/splits/datased_polyphonic.frozen.json` và xác minh leakage trước khi trích đặc trưng.

Các file ngoài cần có tại các đường dẫn sau: CNN14 AudioSet, BEATs, `frame_mn10`, Qwen GGUF và
cache BGE-M3. Tên, sự tồn tại và SHA-256 của chúng (cùng `best.pt`, prediction, postproc/cSEBB,
split, taxonomy, lexicon và grammar) được đóng băng tại
[`artifact_freeze_20261002.md`](measurements/artifact_freeze_20261002.md). Không commit các file
này vào Git.

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m scripts.freeze_artifacts
```

## Số chính và lệnh audit

| Số/kết luận | Artifact nguồn | Lệnh tái lập hoặc audit |
|---|---|---|
| S13 chọn f2 bằng CV dev annotated | `s13_selection_20261018` | `scripts.report_s13_ranking` với 11 `--candidate` của ADR-0031 §9 và `--eval-set annotated --final-selection` (dev-only) |
| f2 test annotated macro 0.1206, micro 0.1643 | `s13_test_20261018`, `event_f1_macro_20261002` | `scripts.report_s13_test --selection <selection.json> --candidate <11 ứng viên> --output <file>` chỉ **đọc evaluation test đã có**; không chạy `evaluate_run` |
| RQ1-v2 âm tính | `rq1_v2_multiseed_20260929`, `rq1_multirun_bootstrap_rq1_v2_annotated_20260929` | `scripts.report_rq1_multiseed --branch-b <3 B-v2> --branch-c <3 C-v2> --evaluation-name evaluation_cv_annotated.json`; bootstrap gốc là audit có đọc prediction test, không chạy lại trong clone này |
| RQ2/RQ3 của S8 trên f2 | `s8_summary_20261002` | `.venv/Scripts/python.exe -m scripts.report_s8_summary` (đọc measurement đã khóa) |
| Mọi event-F1 micro/macro | `event_f1_macro_20261002` | `.venv/Scripts/python.exe -m scripts.report_event_f1_macro` (đọc evaluation JSON, không prediction) |
| Mọi lượt đã chạm test | `test_ledger_20261002` | `.venv/Scripts/python.exe -m scripts.report_test_ledger` (đọc artifact, không chạy test) |
| Parity/e2e f2 | `inference_parity_20260929`, `inference_parity_cpu_20261002`, `demo_f2_e2e_20261002` | `docker compose --profile app up -d --build`; `.venv/Scripts/python.exe -m scripts.check_inference_parity` |

## Tái tạo từ đầu trong clone mới

1. Tạo virtual environment, cài dependency, tải archive/checkpoint rồi chạy audit archive, split và
   leakage. Lưu output vào `docs/measurements/`; không sửa annotation/split/taxonomy.
2. Trích đặc trưng và train các run theo ADR tương ứng. Mỗi run phải lưu manifest, revision, config,
   seed, manifest dữ liệu và prediction. Lựa chọn hậu xử lý/hệ thống chỉ dùng CV 5 fold trên dev.
3. Commit quyết định chọn trước khi sinh bất kỳ prediction/metric test mới. Với S13, hệ thống đã khóa
   là f2; không thay checkpoint hoặc cSEBB.
4. Chỉ khi có phê duyệt một lượt test cho clone mới, chạy đúng protocol trong
   `docs/evaluation_protocol.md`, sau đó `scripts.report_test_ledger` ngay để lưu toàn bộ lượt.

Thời gian đã đo có thể dùng để lập lịch: T2a mã hóa một epoch khoảng 64 s
([`track2_t0_beats_20260927.md`](measurements/track2_t0_beats_20260927.md)); demo f2 S-0016 mất
2.012 s upload+phân tích và RAG mất 0.250 s
([`demo_f2_e2e_20261002.md`](measurements/demo_f2_e2e_20261002.md)). Những thời gian khác phụ thuộc
GPU/CPU và không được suy diễn thành cam kết runtime.

## Demo local

Xem [`DEMO.md`](DEMO.md). Trên máy đã có artifact offline, dùng
`powershell -ExecutionPolicy Bypass -File scripts/demo_up.ps1`; kiểm tra trước buổi trình bày bằng
`scripts/demo_check.ps1`. Seed demo chỉ lấy split TRAIN và không đụng corpus validation/test.
