# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_served_B0_20261107T175659Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.083 | 0.237 | 0.310 | 0.585 | 0.420 [0.348, 0.504] | 1.000 |
| structured_only/vi | 96 | 0.083 | 0.247 | 0.310 | 0.587 | 0.421 [0.350, 0.505] | 1.000 |
| vector_only/en | 96 | 0.119 | 0.337 | 0.497 | 0.735 | 0.551 [0.498, 0.607] | 0.317 |
| vector_only/vi | 96 | 0.103 | 0.294 | 0.428 | 0.666 | 0.488 [0.429, 0.550] | 0.283 |
| hybrid/en | 96 | 0.079 | 0.242 | 0.310 | 0.570 | 0.417 [0.345, 0.499] | 1.000 |
| hybrid/vi | 96 | 0.081 | 0.250 | 0.311 | 0.576 | 0.420 [0.349, 0.503] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.671 | 0.145 | 0.800 | 0.183 |
| structured_only/vi | 0.679 | 0.145 | 0.800 | 0.183 |
| vector_only/en | 0.671 | 0.336 | 0.787 | 0.475 |
| vector_only/vi | 0.637 | 0.285 | 0.774 | 0.341 |
| hybrid/en | 0.659 | 0.145 | 0.803 | 0.180 |
| hybrid/vi | 0.671 | 0.145 | 0.803 | 0.183 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.003 [-0.008, +0.001] |
| hybrid−vector_only/en | -0.134 [-0.178, -0.092] |
| hybrid−structured_only/vi | -0.001 [-0.005, +0.001] |
| hybrid−vector_only/vi | -0.068 [-0.117, -0.020] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 96 | -0.007 |
| structured_only/vi | 96 | -0.006 |
| vector_only/en | 96 | +0.000 |
| vector_only/vi | 96 | +0.000 |
| hybrid/en | 96 | -0.011 |
| hybrid/vi | 96 | -0.007 |
