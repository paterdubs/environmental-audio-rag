# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_ensemble_s13_f2_20260929T045053Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.080 | 0.244 | 0.306 | 0.596 | 0.412 [0.340, 0.484] | 1.000 |
| structured_only/vi | 97 | 0.078 | 0.245 | 0.304 | 0.593 | 0.411 [0.341, 0.483] | 1.000 |
| vector_only/en | 97 | 0.087 | 0.348 | 0.503 | 0.691 | 0.526 [0.467, 0.582] | 0.292 |
| vector_only/vi | 97 | 0.071 | 0.329 | 0.462 | 0.641 | 0.489 [0.429, 0.548] | 0.269 |
| hybrid/en | 97 | 0.077 | 0.242 | 0.304 | 0.593 | 0.409 [0.336, 0.481] | 1.000 |
| hybrid/vi | 97 | 0.081 | 0.247 | 0.304 | 0.603 | 0.416 [0.345, 0.489] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.742 | 0.151 | 0.776 | 0.121 |
| structured_only/vi | 0.761 | 0.151 | 0.776 | 0.104 |
| vector_only/en | 0.621 | 0.387 | 0.733 | 0.426 |
| vector_only/vi | 0.597 | 0.312 | 0.720 | 0.396 |
| hybrid/en | 0.736 | 0.151 | 0.761 | 0.126 |
| hybrid/vi | 0.772 | 0.151 | 0.776 | 0.111 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.003 [-0.012, +0.004] |
| hybrid−vector_only/en | -0.117 [-0.170, -0.067] |
| hybrid−structured_only/vi | +0.005 [-0.000, +0.010] |
| hybrid−vector_only/vi | -0.073 [-0.128, -0.018] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 97 | -0.004 |
| structured_only/vi | 97 | -0.005 |
| vector_only/en | 97 | +0.000 |
| vector_only/vi | 97 | +0.000 |
| hybrid/en | 97 | -0.006 |
| hybrid/vi | 97 | -0.004 |
