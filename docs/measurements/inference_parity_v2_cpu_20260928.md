# Parity hệ thống phục vụ — `sed_ensemble_v2_20260926T150934Z` + `postproc_cv.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_v2_20260926T155630Z`.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cpu`, torch `2.14.0+cpu`) |
|---|---|
| Đặc trưng WAV → log-mel trùng file `.npy` | 0/142 (lệch lớn nhất 0.000488) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.0135 (trung vị theo recording 0.0026) |
| Recording có event trùng khít | 121/142 |
| Event trùng khít (class + onset + offset) | 400 / 425 đóng băng, 426 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 400 / 425 trên 425 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `033312Z` 0.0529, `053024Z` 0.0237, `064832Z` 0.043 |

Recording lệch event: S-0007, S-0008, S-0018, S-0028, S-0042, S-0048, S-0080, S-0098, S-0110, S-0186, S-0222, S-0250, S-0258, S-0259, S-0408, S-0419, S-0431, S-0502, S-0517, S-0673, S-0711
