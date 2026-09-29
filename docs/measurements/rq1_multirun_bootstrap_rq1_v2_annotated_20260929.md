# Event-F1 trung bình nhiều run — bootstrap theo recording (test)

> Sinh bởi `scripts.report_multirun_bootstrap`. Mỗi lần bootstrap rút lại recording test một lần và chấm lại **mọi** run trên cùng mẫu (ghép cặp). Các run giữ nguyên, không rút lại seed — CI đo độ bất định do mẫu recording, độ lệch giữa seed xem cột SD. n = 139 recording, 1000 lần, seed 20260922. Hậu xử lý `từ từng evaluation`; F1 cộng dồn của từng run khớp `evaluation_cv_annotated.json`.

| Nhánh | n run | Mean event-F1 | CI 95% | SD giữa run | Các run (F1) |
|---|---:|---:|---|---:|---|
| B | 3 | 0.1324 | [0.0985, 0.1681] | 0.0068 | `033312Z` 0.1275, `053024Z` 0.1401, `064832Z` 0.1295 |
| C | 3 | 0.1294 | [0.0966, 0.1644] | 0.0099 | `161726Z` 0.1378, `172229Z` 0.1320, `185208Z` 0.1185 |

| Hiệu số | Ước lượng | CI 95% |
|---|---:|---|
| C-B | -0.0029 | [-0.0254, +0.0199] |
