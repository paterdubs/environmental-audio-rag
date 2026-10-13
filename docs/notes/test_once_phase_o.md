# Runbook O5 — test một lần cho giai đoạn O (ADR-0041 §2, §8, §9)

Soạn 14/10/2026 trong lúc tầng C vòng 2 chạy. **Chưa chạy.** Chỉ chạy sau khi lựa chọn tầng C cuối
(`oof_selection_*` vòng 2 + cập nhật ADR-0041) đã được commit, và người dùng xác nhận mở test.

## 0. Điều kiện trước (dừng nếu một điều kiện sai)

- `git status --porcelain` rỗng; HEAD chứa commit lựa chọn tầng C cuối.
- Chưa có `predictions/test.npz` trong bất kỳ run fold nào của hệ thống cuối, B0 và ablation
  (`dir ml\runs\<run>\predictions`): mọi run fold giai đoạn O đến nay chỉ có `dev.npz`.
- Hash split/taxonomy/manifest dữ liệu khớp `oof_selection_*` (report_oof ghi `sources_sha256`).

## 1. Hệ thống được test (ADR-0041 §2: hệ thống cuối, B0, tối đa 2 ablation ghi trước)

"Hệ thống cuối là ensemble 5 model fold của nó". Mỗi hệ thống test = trung bình xác suất của các
model fold, suy luận hop 5 s tam giác sàn 0.3, hậu xử lý = họ/cấu hình đã chọn trên OOF của nó.

| Hệ thống | Run fold (5) | Hậu xử lý |
|---|---|---|
| B0 | `night_state.json`: `B0_fold0..4` | `ml/runs/sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` (cSEBB `tau0.32_abs0.3`) |
| O-D | `night_state.json`: `OD_fold0..4` | file selection của họ thắng trong `ml/runs/sed_oof_OD_h5_*` |
| Ensemble B0 + O-D | 10 run fold trên | file selection của họ thắng trong `ml/runs/sed_oof_ENS_B0_OD_h5_*` |

Họ θ → `--postproc <oof>/postproc_cv_annotated.json`; họ cSEBB → `--postproc
<oof>/sebb_cv_selection_annotated.json` (evaluate_run đọc `family`).

## 2. Lệnh (PowerShell, từ gốc repo; `$py = ".venv\Scripts\python.exe"`)

```powershell
# 2.1 Dự đoán test chồng lấn cho từng run fold (một lần mỗi run)
foreach ($k in 0..4) {
  & $py -m scripts.dump_predictions ml\runs\<B0_fold$k> --split test --hop-seconds 5 `
    --weighting triangular:0.3 --label B0_f${k}_h5_test
}
# (lặp lại với O-D nếu O-D là hệ thống cuối hoặc thành phần ensemble)

# 2.2 Ensemble các model fold, chỉ split test
& $py -m scripts.build_ensemble <5 hoặc 10 run sed_rewindow_*_test> --label <HỆ_THỐNG>_test --splits test

# 2.3 Đánh giá đúng một lần, recording có nhãn (ADR-0034)
& $py -m scripts.evaluate_run ml\runs\sed_ensemble_<HỆ_THỐNG>_test_<ts> --eval-set annotated `
  --postproc <file hậu xử lý ở §1> --tag phase_o
```

Thứ tự: hệ thống cuối → B0 → ablation (nếu có). Mỗi `evaluate_run` chạy **một lần**; không chạy
lại dù số xấu. Giữ tree sạch giữa các bước (artifact chỉ ghi vào `ml/runs`).

## 3. Sau test (chỉ đọc evaluation đã lưu)

- So với f2 trên 139 recording annotated: bootstrap ghép cặp theo recording (1000 lần, seed
  20260922), báo cả macro (số chính) và micro.
- `scripts.report_test_ledger` và `scripts.freeze_artifacts` thêm các run mới (XO-12 đã nhận
  `sed_rewindow`/`sed_oof`/`cv_fold`).
- Báo mọi số, kể cả khi thứ tự trên test khác OOF (ADR-0041 §2).

## 4. Đã kiểm khi soạn (14/10, không mở test)

- `scripts/dump_predictions.py::dump` gọi `apply_cv_fold`, hàm này giữ nguyên nhãn `test`, nên
  model fold dự đoán đúng 142 recording test của split đóng băng.
- `scripts/evaluate_run.py` với họ cSEBB chỉ đọc cấu hình đã chọn, không so hash `dev.npz` của
  run đánh giá; ensemble chỉ có `test.npz` đánh giá được.
- Chưa kiểm: thời gian dump test của BEATs (ước tính vài phút mỗi fold).
