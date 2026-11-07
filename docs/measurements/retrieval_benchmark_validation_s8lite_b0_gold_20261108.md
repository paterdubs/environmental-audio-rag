# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_served_B0_20261107T175659Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.086 | 0.253 | 0.313 | 0.597 | 0.427 [0.357, 0.507] | 1.000 |
| structured_only/vi | 96 | 0.086 | 0.253 | 0.313 | 0.597 | 0.427 [0.357, 0.507] | 1.000 |
| vector_only/en | 96 | 0.119 | 0.337 | 0.497 | 0.735 | 0.551 [0.498, 0.607] | 0.299 |
| vector_only/vi | 96 | 0.103 | 0.294 | 0.428 | 0.666 | 0.488 [0.429, 0.550] | 0.276 |
| hybrid/en | 96 | 0.088 | 0.255 | 0.313 | 0.597 | 0.428 [0.358, 0.507] | 1.000 |
| hybrid/vi | 96 | 0.085 | 0.254 | 0.314 | 0.592 | 0.427 [0.357, 0.508] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.685 | 0.145 | 0.800 | 0.198 |
| structured_only/vi | 0.685 | 0.145 | 0.800 | 0.198 |
| vector_only/en | 0.671 | 0.336 | 0.787 | 0.475 |
| vector_only/vi | 0.637 | 0.285 | 0.774 | 0.341 |
| hybrid/en | 0.690 | 0.145 | 0.803 | 0.196 |
| hybrid/vi | 0.683 | 0.145 | 0.803 | 0.198 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | +0.001 [-0.002, +0.005] |
| hybrid−vector_only/en | -0.123 [-0.168, -0.080] |
| hybrid−structured_only/vi | -0.000 [-0.002, +0.002] |
| hybrid−vector_only/vi | -0.061 [-0.108, -0.012] |
