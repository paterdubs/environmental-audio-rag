# Runbook — test một lần cho LBR (ADR-0045 §8, §11; ADR-0046)

> **Chỉ chạy khi người dùng duyệt.** Đây là lần tái sử dụng test thích nghi sau O5. Không chọn lại
> theo số test; báo nguyên văn cả chiều giảm. Một lượt chấm cả V2 (số chính) và V3 (cấu hình ứng
> dụng); không mở test lần nữa cho riêng V3.

## 0. Điều kiện

- Tree sạch (`git status --porcelain` rỗng) — người dùng commit các thay đổi ngày 10/11 trước.
- Run LBR số chính: `ml/runs/sed_lbr_B0_20261109T172809Z` (V2, model SHA-256 `e2d84c09…`).
- Run LBR ứng dụng: V3 sinh ở bước 1 trên tree sạch (bản xem trước chạy lúc tree bẩn chỉ nằm ở
  scratchpad, không dùng).
- Posterior test đã có từ O5: `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz`.
- B0 để so ghép cặp: `ml/runs/sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json`.

## 1. Fit V3 trên OOF (không đọc test, ~15 phút CPU)

```powershell
$py = ".venv\Scripts\python.exe"
& $py -W ignore -m scripts.fit_lbr_application `
  --source ml\runs\sed_oof_B0_h5_20261008T130849Z `
  --transfer ml\runs\sed_oof_P1_B0x3_h5_20261107T224434Z
```

Ghi `ml/runs/sed_lbr_B0v3_<ts>/` và `docs/measurements/oof_selection_<ngày>_LBR_v3.{json,md}`.
Kiểm `git.dirty=false` trong manifest, số khớp bản xem trước (ADR-0045 §11), rồi commit measurement
để tree sạch lại.

## 2. Lệnh mở test (PowerShell, gốc repo)

```powershell
& $py -m scripts.evaluate_run ml\runs\sed_ensemble_B0_final_test_20261014T085016Z `
  --eval-set annotated `
  --postproc ml\runs\sed_lbr_B0_20261109T172809Z\manifest.json `
  --extra-lbr ml\runs\sed_lbr_B0v3_<ts>\manifest.json `
  --baseline-postproc ml\runs\sed_oof_B0_h5_20261008T130849Z\sebb_cv_selection_annotated.json `
  --tag phase_lbr
```

Một lệnh = một lượt mở test: V2 ở điểm F1 (số chính) và ưu tiên phát hiện, 21 và 19 lớp, thước ứng
dụng, PSDS theo lưới t, Δ micro ghép cặp với B0; mục V3 cùng các thước đó, ghi rõ không phải số chính.

## 3. Sau khi chạy

1. Commit ngay `evaluation_phase_lbr_annotated.json` + measurement md (bài học PAPER_NOTES §8 #12).
2. `scripts.report_test_ledger` và `scripts.freeze_artifacts` thêm hai run LBR.
3. Ghi PAPER_NOTES (S65), ADR-0045 §10–§11, STATUS, CLAUDE.
4. Demo: `EARAG_SERVED_LBR` trỏ run V3, chế độ `recall_first` (docs/DEMO.md); rebuild Docker kèm
   scikit-learn rồi kiểm parity + E2E.
