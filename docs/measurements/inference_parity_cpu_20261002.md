# Parity hệ thống phục vụ — `sed_ensemble_t2b_20260927T200914Z` + `sebb_cv_selection_annotated.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_s13_f2_20260929T045053Z`.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cpu`, torch `2.14.0+cpu`) |
|---|---|
| Input WAV → cache/đặc trưng trùng | 1/142 (lệch lớn nhất 1) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.0239 (trung vị theo recording 0.00808) |
| Recording có event trùng khít | 132/142 |
| Event trùng khít (class + onset + offset) | 290 / 299 đóng băng, 300 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 290 / 294 trên 299 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `172924Z` 0.0966, `180358Z` 0.0779, `185137Z` 0.0559 |

Recording lệch event: S-0055, S-0086, S-0161, S-0183, S-0412, S-0419, S-0514, S-0524, S-0542, S-0548
