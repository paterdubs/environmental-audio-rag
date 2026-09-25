# Parity hệ thống phục vụ — `sed_ensemble_C_clean_20260925T045631Z` + `postproc_cv.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cuda`) |
|---|---|
| Đặc trưng WAV → log-mel trùng file `.npy` | 142/142 (lệch lớn nhất 0) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.0118 (trung vị theo recording 0.00245) |
| Recording có event trùng khít | 79/142 |
| Event trùng khít (class + onset + offset) | 332 / 408 đóng băng, 409 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 377 / 405 trên 408 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `033537Z` 0, `061000Z` 0, `072736Z` 0, `080715Z` 0 |

Recording lệch event: S-0008, S-0040, S-0047, S-0062, S-0068, S-0070, S-0077, S-0087, S-0101, S-0110, S-0123, S-0130, S-0161, S-0164, S-0167, S-0176, S-0185, S-0186, S-0188, S-0196, S-0198, S-0203, S-0222, S-0230, S-0241, S-0244, S-0245, S-0250, S-0259, S-0269, S-0277, S-0288, S-0301, S-0319, S-0320, S-0323, S-0353, S-0358, S-0363, S-0368, S-0383, S-0388, S-0408, S-0424, S-0431, S-0432, S-0435, S-0495, S-0499, S-0517, S-0523, S-0537, S-0563, S-0564, S-0586, S-0615, S-0629, S-0636, S-0646, S-0656, S-0681, S-0689, S-0716
