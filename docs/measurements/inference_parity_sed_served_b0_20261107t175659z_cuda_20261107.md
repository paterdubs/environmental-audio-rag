# Parity hệ thống phục vụ — `sed_served_B0_20261107T175659Z` + `sebb_cv_selection_annotated.json`

> Sinh bởi `scripts.check_inference_parity` (ADR-0029 §2). So với output đã đóng băng trên test; không đánh giá lại, không chọn gì.

Nguồn output đóng băng: `sed_ensemble_B0_final_test_20261014T085016Z`.

| Tầng | Kết quả (n = 142 recording test, thiết bị `cuda`, torch `2.11.0+cu128`) |
|---|---|
| Input WAV → cache/đặc trưng trùng | 142/142 (lệch lớn nhất 0) |
| Số frame khớp | 142/142 |
| Xác suất, lệch tuyệt đối lớn nhất | 0.00203 (trung vị theo recording 0.000506) |
| Recording có event trùng khít | 141/142 |
| Event trùng khít (class + onset + offset) | 351 / 352 đóng băng, 352 phục vụ |
| Event khớp khi lệch biên ≤ 1 frame / ≤ collar 0.2 s | 351 / 352 trên 352 |
| Tái tạo đúng batch dump (batch test đầu, 24 cửa sổ), Δlogit tuyệt đối lớn nhất | `092903Z` không kiểm (member không có test.npz), `102530Z` không kiểm (member không có test.npz), `111605Z` không kiểm (member không có test.npz), `115845Z` không kiểm (member không có test.npz), `123531Z` không kiểm (member không có test.npz) |

Recording lệch event: S-0048
