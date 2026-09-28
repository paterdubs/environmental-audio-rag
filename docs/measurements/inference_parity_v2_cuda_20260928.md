# Parity hệ thống phục vụ — `sed_ensemble_v2_20260926T150934Z` + `postproc_cv.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_v2_20260926T155630Z`.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cuda`, torch `2.11.0+cu128`) |
|---|---|
| Đặc trưng WAV → log-mel trùng file `.npy` | 142/142 (lệch lớn nhất 0) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.000419 (trung vị theo recording 0.000162) |
| Recording có event trùng khít | 136/142 |
| Event trùng khít (class + onset + offset) | 419 / 425 đóng băng, 425 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 419 / 425 trên 425 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `033312Z` 0, `053024Z` 0, `064832Z` 0 |

Recording lệch event: S-0019, S-0110, S-0186, S-0222, S-0388, S-0711
