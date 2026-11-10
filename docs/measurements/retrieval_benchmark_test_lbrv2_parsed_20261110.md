# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_lbr_B0_20261109T172809Z:f1`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.092 | 0.255 | 0.308 | 0.591 | 0.407 [0.333, 0.483] | 1.000 |
| structured_only/vi | 97 | 0.094 | 0.258 | 0.308 | 0.598 | 0.410 [0.337, 0.485] | 1.000 |
| vector_only/en | 97 | 0.097 | 0.322 | 0.460 | 0.637 | 0.491 [0.432, 0.553] | 0.289 |
| vector_only/vi | 97 | 0.093 | 0.260 | 0.387 | 0.604 | 0.432 [0.370, 0.490] | 0.263 |
| hybrid/en | 97 | 0.089 | 0.247 | 0.307 | 0.577 | 0.398 [0.325, 0.472] | 1.000 |
| hybrid/vi | 97 | 0.093 | 0.252 | 0.307 | 0.588 | 0.405 [0.332, 0.479] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.600 | 0.141 | 0.797 | 0.209 |
| structured_only/vi | 0.613 | 0.141 | 0.797 | 0.209 |
| vector_only/en | 0.534 | 0.325 | 0.774 | 0.398 |
| vector_only/vi | 0.518 | 0.251 | 0.743 | 0.300 |
| hybrid/en | 0.585 | 0.140 | 0.773 | 0.209 |
| hybrid/vi | 0.614 | 0.136 | 0.780 | 0.209 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.009 [-0.019, +0.000] |
| hybrid−vector_only/en | -0.093 [-0.143, -0.045] |
| hybrid−structured_only/vi | -0.005 [-0.013, +0.002] |
| hybrid−vector_only/vi | -0.027 [-0.074, +0.020] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 97 | -0.004 |
| structured_only/vi | 97 | -0.001 |
| vector_only/en | 97 | +0.000 |
| vector_only/vi | 97 | +0.000 |
| hybrid/en | 97 | -0.006 |
| hybrid/vi | 97 | -0.001 |
