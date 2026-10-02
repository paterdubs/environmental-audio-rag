# Parity hệ thống phục vụ — `sed_ensemble_t2b_20260927T200914Z` + `sebb_cv_selection_annotated.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_s13_f2_20260929T045053Z`.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cuda`, torch `2.11.0+cu128`) |
|---|---|
| Input WAV → cache/đặc trưng trùng | 142/142 (lệch lớn nhất 0) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.00501 (trung vị theo recording 0.00083) |
| Recording có event trùng khít | 142/142 |
| Event trùng khít (class + onset + offset) | 299 / 299 đóng băng, 299 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 299 / 299 trên 299 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `172924Z` 0, `180358Z` 0, `185137Z` 0 |

Recording lệch event: không có
