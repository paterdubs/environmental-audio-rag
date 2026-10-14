# Event-F1 trung bình nhiều run — bootstrap theo recording (test)

> Sinh bởi `scripts.report_multirun_bootstrap`. Mỗi lần bootstrap rút lại recording test một lần và chấm lại **mọi** run trên cùng mẫu (ghép cặp). Các run giữ nguyên, không rút lại seed — CI đo độ bất định do mẫu recording, độ lệch giữa seed xem cột SD. n = 139 recording, 1000 lần, seed 20260922. Hậu xử lý `từ từng evaluation`; F1 cộng dồn của từng run khớp `evaluation.json`.

| Nhánh | n run | Mean event-F1 | CI 95% | SD giữa run | Các run (F1) |
|---|---:|---:|---|---:|---|
| f2 | 1 | 0.1643 | [0.1103, 0.2242] | 0.0000 | `045053Z` 0.1643 |
| B0 | 1 | 0.1806 | [0.1261, 0.2384] | 0.0000 | `085016Z` 0.1806 |

| Hiệu số | Ước lượng | CI 95% |
|---|---:|---|
| B0-f2 | +0.0164 | [-0.0128, +0.0495] |
