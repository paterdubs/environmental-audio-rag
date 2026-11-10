# Parity hệ thống phục vụ — `sed_served_B0_20261107T175659Z` + `sebb_cv_selection_annotated.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_B0_final_test_20261014T085016Z`.

Event dựng bằng LBR `sed_lbr_B0v3_20261110T042337Z` ở điểm `recall_first`; phía phục vụ và phía đóng băng dùng cùng bộ LBR, xác suất khác nhau do fp16.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cuda`, torch `2.11.0+cu128`) |
|---|---|
| Input WAV → cache/đặc trưng trùng | 142/142 (lệch lớn nhất 0) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.00203 (trung vị theo recording 0.000506) |
| Recording có event trùng khít | 71/142 |
| Event trùng khít (class + onset + offset) | 573 / 692 đóng băng, 693 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 665 / 691 trên 692 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `092903Z` không kiểm (member không có test.npz), `102530Z` không kiểm (member không có test.npz), `111605Z` không kiểm (member không có test.npz), `115845Z` không kiểm (member không có test.npz), `123531Z` không kiểm (member không có test.npz) |

Recording lệch event: S-0017, S-0018, S-0019, S-0040, S-0047, S-0048, S-0070, S-0075, S-0077, S-0080, S-0086, S-0087, S-0098, S-0101, S-0105, S-0126, S-0159, S-0161, S-0164, S-0177, S-0183, S-0186, S-0188, S-0191, S-0196, S-0244, S-0245, S-0286, S-0296, S-0301, S-0312, S-0319, S-0323, S-0332, S-0357, S-0358, S-0363, S-0364, S-0385, S-0387, S-0388, S-0408, S-0414, S-0419, S-0424, S-0431, S-0436, S-0473, S-0479, S-0482, S-0495, S-0499, S-0502, S-0521, S-0524, S-0537, S-0548, S-0564, S-0573, S-0582, S-0600, S-0617, S-0629, S-0636, S-0656, S-0668, S-0689, S-0702, S-0711, S-0716, S-0717
