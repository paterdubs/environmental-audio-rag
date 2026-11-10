# Tái lập kết quả

Tài liệu tách hai việc:

1. **Audit** artifact đã đóng băng — chạy được ngay trong repository này, chỉ đọc file đã có.
2. **Tái tạo** từ đầu trong một clone/máy mới — train, chọn trên dev, rồi mở test theo protocol.

**Không chạy lại lệnh có test trong clone đã sinh số chính thức.** Mỗi lượt chạm test đã được ghi ở
sổ test mới nhất ([`test_ledger_20261110.md`](measurements/test_ledger_20261110.md)). Mọi lệnh dưới
đây là đúng lệnh đã chạy, lấy từ trường `command` trong manifest của run tương ứng; kiểm máy bằng
`scripts.check_doc_commands` (module và cờ còn tồn tại).

## Môi trường đã đo

Máy thực nghiệm Windows dùng Python 3.12.10, PyTorch `2.11.0+cu128`, CUDA runtime PyTorch 12.8, GPU
RTX 3070 Laptop 8 GB; driver hiển thị CUDA 13.1. llama.cpp là `b11158` (commit `3423f940e`). CPU
container của parity dùng torch `2.14.0+cpu`. Khác biệt phiên bản CPU/CUDA được ghi thẳng trong các
báo cáo parity, không được coi là bit-identical. LBR cần `scikit-learn` (có trong `requirements.txt`
và `requirements-inference.txt`).

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

Tải đúng hai archive DataSEC/DataSED khai báo trong `ml/configs/sources.yaml`; kiểm MD5 và giấy
phép bằng `scripts.report_archive_audit`. Không tự tạo lại split: dùng
`data/splits/datased_polyphonic.frozen.json`, và fold train ∪ dev của tầng C ở
`data/splits/datased_trainval_folds.csv` (ADR-0041 §2).

File ngoài cần có: CNN14 AudioSet, BEATs, `frame_mn10_strong_1.pt`, Qwen GGUF, cache BGE-M3. Tên,
sự tồn tại và SHA-256 của chúng cùng mọi `best.pt`, prediction, postproc/cSEBB, model LBR, split,
taxonomy, lexicon và grammar được đóng băng ở
[`artifact_freeze_20261110.md`](measurements/artifact_freeze_20261110.md). Không commit các file
này vào Git.

## Audit trong repository này (chỉ đọc)

```powershell
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
.venv/Scripts/python.exe -m scripts.freeze_artifacts        # SHA-256 + sự tồn tại; thiếu → báo
.venv/Scripts/python.exe -m scripts.report_test_ledger      # mọi lượt đã chạm test
.venv/Scripts/python.exe -m scripts.make_cv_folds --check   # fold tầng C khớp split + annotation
.venv/Scripts/python.exe -m scripts.check_doc_claims        # số chính trong tài liệu ↔ artifact
.venv/Scripts/python.exe -m scripts.check_doc_commands      # lệnh trong tài liệu ↔ code
```

| Số/kết luận | Artifact nguồn | Ghi chú |
|---|---|---|
| Hệ thống cuối B0, test annotated macro 0.1366, micro 0.1806 | `sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_o_annotated.json`, ADR-0041 §12 | Chọn bằng OOF 5 fold ([oof_selection_20261014](measurements/oof_selection_20261014.md)) |
| LBR V2 `f1` (số chính) và V3 `recall_first` (demo) | `evaluation_phase_lbr_annotated.json` của cùng run, ADR-0045 §12 | Một lượt mở test chấm cả hai |
| PSDS cùng lưới log: B0, V2, V3 | [lbr_psds_grid_20261110_annotated](measurements/lbr_psds_grid_20261110_annotated.md), [_b0](measurements/lbr_psds_grid_20261110_annotated_b0.md) | Lưới ghi trước ADR-0047; B0 ADR-0048 §3 |
| RQ2 template trên B0/V2/V3 | `caption_template_{B0,lbrv2,lbrv3}_test_annotated_*` | ADR-0044, ADR-0047 |
| RQ3 trên B0/V2/V3 | `retrieval_{benchmark,answers}_test_{s8lite_b0,lbrv2,lbrv3}_*` | ADR-0044, ADR-0047 |
| Phục vụ demo B0 + LBR V3 | [parity](measurements/inference_parity_sed_lbr_b0v3_20261110t042337z_recall_first_cuda_20261110.md), [E2E](measurements/demo_lbrv3_e2e_20261110.md) | `official=false` khi LBR bật |
| f2 (hệ thống cuối giai đoạn S13, giờ là mốc) | `s13_test_20261018`, `s8_summary_20261002` | ADR-0031 §9, ADR-0040 |

## Tái tạo từ đầu trong clone mới

Thứ tự bắt buộc: train và chọn **chỉ trên train ∪ dev**; commit lựa chọn; chỉ khi được duyệt mới
sinh prediction/metric test, rồi chạy `scripts.report_test_ledger` ngay. Mỗi run phải lưu manifest,
revision, config, seed, manifest dữ liệu và prediction; số chính thức chỉ từ tree sạch.

### 1. B0 — `frame_mn10` fine-tune, 5 fold, suy luận chồng lấn (ADR-0041)

```powershell
$py = ".venv/Scripts/python.exe"
& $py -m scripts.make_cv_folds --check
# k = 0..4: một model mỗi fold của train ∪ dev annotated
& $py -m scripts.train_sed --encoder frame_mn --recipe t2b `
  --frame-mn-checkpoint artifacts/checkpoints/frame_mn10_strong_1.pt `
  --learning-rate 0.0003 --batch-size 24 --seed 20260922 --train-fixes --cv-fold 0
# dự đoán lại fold giữ ra, hop 5 s, gộp tam giác sàn 0.3
& $py -m scripts.dump_predictions ml/runs/<run fold 0> --split dev --hop-seconds 5 `
  --weighting triangular:0.3 --label B0_f0_h5
& $py -m scripts.build_oof <5 run sed_rewindow_B0_f*_h5> --label B0_h5
& $py -m scripts.select_sebb_cv ml/runs/<sed_oof_B0_h5_*> --eval-set annotated --workers 6
& $py -m scripts.report_oof --baseline ml/runs/<sed_oof_B0_h5_*> --candidate <nhãn>=ml/runs/<oof ứng viên>
```

`select_sebb_cv` chọn cSEBB `tau0.32_abs0.3`, ngưỡng box 0.9, bằng CV 5 fold theo `leakage_group`
trên posterior OOF (`sebb_cv_selection_annotated.json`; cSEBB không dùng duration prior).
Mở test (một lần, ADR-0041 §12; runbook `docs/notes/test_once_phase_o.md`):

```powershell
& $py -m scripts.dump_predictions ml/runs/<run fold 0> --split test --hop-seconds 5 `
  --weighting triangular:0.3 --label B0_f0_h5_test
& $py -m scripts.build_ensemble <5 run sed_rewindow_B0_f*_h5_test> --label B0_final_test --splits test
& $py -m scripts.evaluate_run ml/runs/<sed_ensemble_B0_final_test_*> --eval-set annotated `
  --postproc ml/runs/<sed_oof_B0_h5_*>/sebb_cv_selection_annotated.json --tag phase_o
```

Hệ thống phục vụ (ADR-0042), không chạm test mới:

```powershell
& $py -m scripts.build_served_system --label B0 --members <5 run fold> --hop-seconds 5 `
  --weighting triangular:0.3 --postproc ml/runs/<sed_oof_B0_h5_*>/sebb_cv_selection_annotated.json `
  --evaluated ml/runs/<sed_ensemble_B0_final_test_*>
```

### 2. LBR — tinh chỉnh biên + chấm lại box trên OOF (ADR-0045)

OOF kiểm chuyển P1 là đúng công thức B0 với `--seed 2` và `--seed 3` (ADR-0043), qua cùng
`dump_predictions`/`build_oof`, rồi gộp ba seed:

```powershell
& $py -m scripts.build_ensemble ml/runs/<sed_oof_B0_h5_*> ml/runs/<sed_oof_P1_s2_h5_*> `
  ml/runs/<sed_oof_P1_s3_h5_*> --label P1_B0x3_h5 --splits dev
& $py -m scripts.fit_lbr_oof --source ml/runs/<sed_oof_B0_h5_*> `
  --transfer ml/runs/<sed_oof_P1_B0x3_h5_*> --label B0                    # V2, tầng C
& $py -m scripts.fit_lbr_application --source ml/runs/<sed_oof_B0_h5_*> `
  --transfer ml/runs/<sed_oof_P1_B0x3_h5_*>                               # V3, cấu hình ứng dụng
```

Kết quả OOF: [oof_selection_20261109_LBR](measurements/oof_selection_20261109_LBR.md),
[oof_selection_20261110_LBR_v3](measurements/oof_selection_20261110_LBR_v3.md). Mở test (một lần,
`docs/notes/test_once_lbr.md`) và PSDS cùng lưới:

```powershell
& $py -m scripts.evaluate_run ml/runs/<sed_ensemble_B0_final_test_*> --eval-set annotated `
  --postproc ml/runs/<sed_lbr_B0_*>/manifest.json --extra-lbr ml/runs/<sed_lbr_B0v3_*>/manifest.json `
  --baseline-postproc ml/runs/<sed_oof_B0_h5_*>/sebb_cv_selection_annotated.json --tag phase_lbr
& $py -m scripts.report_lbr_psds_grid --lbr-run ml/runs/<sed_lbr_B0_*> --lbr-run ml/runs/<sed_lbr_B0v3_*>
& $py -m scripts.report_lbr_psds_grid `
  --predictions ml/runs/<sed_ensemble_B0_final_test_*>/predictions/test.npz `
  --b0-postproc ml/runs/<sed_oof_B0_h5_*>/sebb_cv_selection_annotated.json `
  --b0-reference-evaluation ml/runs/<sed_ensemble_B0_final_test_*>/evaluation_phase_o_annotated.json `
  --eval-set annotated --tag _b0
```

### 3. Caption (RQ2) và RAG (RQ3) trên event B0/LBR (ADR-0044, ADR-0047, ADR-0048)

Dev không dùng model cuối (đã thấy dev): B0 dùng posterior OOF lọc theo split, LBR dùng event
cross-fit.

```powershell
& $py -m scripts.filter_predictions ml/runs/<sed_oof_B0_h5_*> --split validation --label B0_oof_dev `
  --copy sebb_cv_selection_annotated.json
& $py -m scripts.export_lbr_oof_events --lbr-run ml/runs/<sed_lbr_B0_*> --point f1
& $py -m scripts.export_lbr_oof_events --lbr-run ml/runs/<sed_lbr_B0v3_*> --point recall_first
```

Caption template (ví dụ V2 trên test; B0 bỏ `--lbr-point`, dev dùng posterior OOF và event cross-fit):

```powershell
& $py -m scripts.score_template_e2e --label lbrv2 `
  --predictions-run ml/runs/<sed_ensemble_B0_final_test_*> --postproc ml/runs/<sed_lbr_B0_*>/manifest.json `
  --split test --eval-set annotated --lbr-point f1 `
  --frozen-lexicon-sha256 6f5634bb7837817c94dd16fe0c0b07a6eae15996fe93064c325599d3321edc73
```

Caption LLM (ba nhánh × ba hệ thống, mức e2e; bảng đầu vào ở ADR-0048 §1; llama.cpp chạy trước theo
`ml/configs/caption_llm.yaml`):

```powershell
& $py -m scripts.generate_llm_captions ml/runs/<sed_lbr_B0_*> --branch constrained --split test `
  --postproc ml/runs/<sed_lbr_B0_*>/manifest.json --predictions-run ml/runs/<sed_ensemble_B0_final_test_*> `
  --levels e2e --lbr-point f1 `
  --frozen-lexicon-sha256 6f5634bb7837817c94dd16fe0c0b07a6eae15996fe93064c325599d3321edc73
& $py -m scripts.score_captions ml/runs/<sed_lbr_B0_*> --split test --eval-set annotated `
  --frozen-lexicon-sha256 6f5634bb7837817c94dd16fe0c0b07a6eae15996fe93064c325599d3321edc73
```

RAG (PostgreSQL + pgvector qua `docker compose up -d`; validation trước, test sau):

```powershell
& $py -m scripts.build_retrieval_index --run ml/runs/<sed_served_B0_*> `
  --predictions-run ml/runs/<sed_ensemble_B0_final_test_*> --postproc ml/runs/<sed_lbr_B0_*>/manifest.json `
  --lbr-point f1 --split test --replace
& $py -m scripts.evaluate_retrieval --split test --output docs/measurements/<tên>.json
& $py -m scripts.evaluate_retrieval --split test --parsed-filters --output docs/measurements/<tên>.json
& $py -m scripts.evaluate_answers --split test --output docs/measurements/<tên>.json
```

### 4. Kiểm sau cùng

```powershell
& $py -m scripts.report_test_ledger
& $py -m scripts.freeze_artifacts
& $py -m scripts.check_doc_claims
```

Thời gian đã đo, chỉ để lập lịch: caption LLM mức e2e trên B0 dev, 134 recording — unconstrained
130.5 s, constrained 529.4 s (`wall_clock_s` trong `captions/*_dev.meta.json`); demo LBR V3 upload +
phân tích 3.7 s
([`demo_lbrv3_e2e_20261110.md`](measurements/demo_lbrv3_e2e_20261110.md)). Thời gian khác phụ
thuộc GPU/CPU, không phải cam kết runtime.

## Demo local

Xem [`DEMO.md`](DEMO.md). Trên máy đã có artifact offline:
`powershell -ExecutionPolicy Bypass -File scripts/demo_up.ps1` (mặc định LBR V3 `recall_first`;
`-NoLbr` để chạy B0); kiểm trước buổi trình bày bằng `scripts/demo_check.ps1`. Seed demo chỉ lấy
split TRAIN và không đụng corpus validation/test.
