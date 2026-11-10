# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_lbr_B0v3_20261110T042337Z:recall_first`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.156 | 0.471 | 0.598 | 0.815 | 0.664 [0.600, 0.723] | 1.000 |
| structured_only/vi | 97 | 0.152 | 0.471 | 0.603 | 0.808 | 0.666 [0.601, 0.723] | 1.000 |
| vector_only/en | 97 | 0.114 | 0.428 | 0.635 | 0.731 | 0.630 [0.579, 0.679] | 0.514 |
| vector_only/vi | 97 | 0.124 | 0.381 | 0.582 | 0.729 | 0.591 [0.535, 0.643] | 0.471 |
| hybrid/en | 97 | 0.132 | 0.472 | 0.596 | 0.790 | 0.655 [0.594, 0.712] | 1.000 |
| hybrid/vi | 97 | 0.144 | 0.481 | 0.602 | 0.804 | 0.668 [0.604, 0.728] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.760 | 0.618 | 0.850 | 0.493 |
| structured_only/vi | 0.788 | 0.618 | 0.850 | 0.476 |
| vector_only/en | 0.650 | 0.592 | 0.828 | 0.501 |
| vector_only/vi | 0.614 | 0.536 | 0.815 | 0.458 |
| hybrid/en | 0.800 | 0.576 | 0.847 | 0.470 |
| hybrid/vi | 0.817 | 0.581 | 0.871 | 0.481 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.009 [-0.031, +0.013] |
| hybrid−vector_only/en | +0.025 [-0.010, +0.060] |
| hybrid−structured_only/vi | +0.003 [-0.017, +0.023] |
| hybrid−vector_only/vi | +0.077 [+0.036, +0.119] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 97 | -0.018 |
| structured_only/vi | 97 | -0.017 |
| vector_only/en | 97 | +0.000 |
| vector_only/vi | 97 | +0.000 |
| hybrid/en | 97 | -0.015 |
| hybrid/vi | 97 | -0.013 |
