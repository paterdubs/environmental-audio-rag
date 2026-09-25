# Event-F1 trung bình nhiều run — bootstrap theo recording (test)

> Sinh bởi `scripts.report_multirun_bootstrap`. Mỗi lần bootstrap rút lại recording test một lần và chấm lại **mọi** run trên cùng mẫu (ghép cặp). Các run giữ nguyên, không rút lại seed — CI đo độ bất định do mẫu recording, độ lệch giữa seed xem cột SD. n = 142 recording, 1000 lần, seed 20260922. F1 cộng dồn của từng run khớp `evaluation.json`.

| Nhánh | n run | Mean event-F1 | CI 95% | SD giữa run | Các run (F1) |
|---|---:|---:|---|---:|---|
| B | 3 | 0.0610 | [0.0440, 0.0795] | 0.0048 | `054531Z` 0.0621, `070927Z` 0.0651, `074656Z` 0.0557 |
| C | 4 | 0.0539 | [0.0391, 0.0699] | 0.0088 | `033537Z` 0.0660, `061000Z` 0.0472, `072736Z` 0.0477, `080715Z` 0.0546 |

| Hiệu số | Ước lượng | CI 95% |
|---|---:|---|
| C-B | -0.0071 | [-0.0164, +0.0021] |
