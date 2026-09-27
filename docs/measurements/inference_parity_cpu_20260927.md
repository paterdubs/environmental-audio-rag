# Parity hệ thống phục vụ — `sed_ensemble_C_clean_20260925T045631Z` + `postproc_cv.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cpu`, torch `2.14.0+cpu`) |
|---|---|
| Đặc trưng WAV → log-mel trùng file `.npy` | 0/142 (lệch lớn nhất 0.000488) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.0118 (trung vị theo recording 0.00334) |
| Recording có event trùng khít | 48/142 |
| Event trùng khít (class + onset + offset) | 239 / 408 đóng băng, 408 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 343 / 403 trên 408 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `033537Z` 0.0589, `061000Z` 0.0703, `072736Z` 0.0678, `080715Z` 0.0584 |

Recording lệch event: S-0008, S-0011, S-0017, S-0019, S-0028, S-0040, S-0042, S-0047, S-0055, S-0062, S-0068, S-0070, S-0075, S-0080, S-0086, S-0087, S-0098, S-0099, S-0101, S-0103, S-0105, S-0110, S-0123, S-0130, S-0161, S-0164, S-0167, S-0176, S-0183, S-0185, S-0186, S-0188, S-0191, S-0196, S-0198, S-0203, S-0222, S-0230, S-0241, S-0244, S-0245, S-0250, S-0259, S-0269, S-0277, S-0288, S-0296, S-0301, S-0307, S-0312, S-0319, S-0320, S-0323, S-0332, S-0353, S-0358, S-0363, S-0364, S-0368, S-0383, S-0385, S-0388, S-0400, S-0408, S-0412, S-0414, S-0419, S-0424, S-0431, S-0432, S-0435, S-0436, S-0495, S-0499, S-0502, S-0517, S-0521, S-0523, S-0537, S-0563, S-0582, S-0586, S-0590, S-0615, S-0629, S-0636, S-0641, S-0646, S-0656, S-0668, S-0681, S-0689, S-0702, S-0716
