# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_served_B0_20261107T175659Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.073 | 0.235 | 0.292 | 0.552 | 0.388 [0.313, 0.466] | 1.000 |
| structured_only/vi | 97 | 0.073 | 0.236 | 0.294 | 0.552 | 0.390 [0.314, 0.467] | 1.000 |
| vector_only/en | 97 | 0.076 | 0.296 | 0.407 | 0.614 | 0.458 [0.391, 0.522] | 0.286 |
| vector_only/vi | 97 | 0.066 | 0.219 | 0.354 | 0.559 | 0.406 [0.339, 0.474] | 0.266 |
| hybrid/en | 97 | 0.067 | 0.230 | 0.291 | 0.519 | 0.377 [0.301, 0.454] | 1.000 |
| hybrid/vi | 97 | 0.071 | 0.232 | 0.294 | 0.534 | 0.383 [0.308, 0.460] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.728 | 0.090 | 0.752 | 0.126 |
| structured_only/vi | 0.733 | 0.090 | 0.752 | 0.126 |
| vector_only/en | 0.583 | 0.264 | 0.737 | 0.330 |
| vector_only/vi | 0.550 | 0.222 | 0.723 | 0.224 |
| hybrid/en | 0.677 | 0.090 | 0.747 | 0.131 |
| hybrid/vi | 0.705 | 0.090 | 0.746 | 0.131 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.011 [-0.024, -0.001] |
| hybrid−vector_only/en | -0.081 [-0.125, -0.033] |
| hybrid−structured_only/vi | -0.006 [-0.014, +0.001] |
| hybrid−vector_only/vi | -0.022 [-0.064, +0.023] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 97 | -0.003 |
| structured_only/vi | 97 | -0.002 |
| vector_only/en | 97 | +0.000 |
| vector_only/vi | 97 | +0.000 |
| hybrid/en | 97 | -0.006 |
| hybrid/vi | 97 | -0.003 |
