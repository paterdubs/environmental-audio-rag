# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_lbr_B0_20261109T172809Z:f1`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.090 | 0.213 | 0.262 | 0.580 | 0.366 [0.296, 0.438] | 1.000 |
| structured_only/vi | 96 | 0.099 | 0.222 | 0.267 | 0.599 | 0.376 [0.308, 0.450] | 1.000 |
| vector_only/en | 96 | 0.092 | 0.323 | 0.397 | 0.698 | 0.466 [0.407, 0.528] | 0.253 |
| vector_only/vi | 96 | 0.101 | 0.265 | 0.337 | 0.681 | 0.417 [0.357, 0.476] | 0.229 |
| hybrid/en | 96 | 0.089 | 0.221 | 0.263 | 0.578 | 0.369 [0.300, 0.443] | 1.000 |
| hybrid/vi | 96 | 0.098 | 0.226 | 0.268 | 0.594 | 0.378 [0.310, 0.452] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.556 | 0.113 | 0.688 | 0.203 |
| structured_only/vi | 0.572 | 0.113 | 0.688 | 0.226 |
| vector_only/en | 0.534 | 0.264 | 0.721 | 0.406 |
| vector_only/vi | 0.530 | 0.217 | 0.693 | 0.303 |
| hybrid/en | 0.558 | 0.113 | 0.699 | 0.203 |
| hybrid/vi | 0.577 | 0.113 | 0.693 | 0.226 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | +0.003 [-0.002, +0.009] |
| hybrid−vector_only/en | -0.097 [-0.139, -0.058] |
| hybrid−structured_only/vi | +0.002 [-0.002, +0.007] |
| hybrid−vector_only/vi | -0.039 [-0.081, +0.004] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 96 | -0.010 |
| structured_only/vi | 96 | +0.001 |
| vector_only/en | 96 | +0.000 |
| vector_only/vi | 96 | +0.000 |
| hybrid/en | 96 | -0.009 |
| hybrid/vi | 96 | +0.001 |
