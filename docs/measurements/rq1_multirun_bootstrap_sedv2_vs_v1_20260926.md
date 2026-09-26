# Event-F1 trung bình nhiều run — bootstrap theo recording (test)

> Sinh bởi `scripts.report_multirun_bootstrap`. Mỗi lần bootstrap rút lại recording test một lần và chấm lại **mọi** run trên cùng mẫu (ghép cặp). Các run giữ nguyên, không rút lại seed — CI đo độ bất định do mẫu recording, độ lệch giữa seed xem cột SD. n = 142 recording, 1000 lần, seed 20260922. Hậu xử lý `postproc_cv.json`; F1 cộng dồn của từng run khớp `evaluation_cv.json`.

| Nhánh | n run | Mean event-F1 | CI 95% | SD giữa run | Các run (F1) |
|---|---:|---:|---|---:|---|
| v2 | 1 | 0.1476 | [0.1088, 0.1866] | 0.0000 | `155630Z` 0.1476 |
| v1 | 1 | 0.0941 | [0.0624, 0.1277] | 0.0000 | `045631Z` 0.0941 |

| Hiệu số | Ước lượng | CI 95% |
|---|---:|---|
| v1-v2 | -0.0536 | [-0.0853, -0.0261] |
