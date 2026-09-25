# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_polyphonic_20260924T054531Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.109 | 0.364 | 0.512 | 0.610 | 0.523 [0.460, 0.589] | 1.000 |
| structured_only/vi | 97 | 0.109 | 0.364 | 0.512 | 0.610 | 0.523 [0.460, 0.589] | 1.000 |
| vector_only/en | 97 | 0.069 | 0.256 | 0.427 | 0.532 | 0.418 [0.361, 0.472] | 0.587 |
| vector_only/vi | 97 | 0.051 | 0.212 | 0.341 | 0.463 | 0.340 [0.291, 0.391] | 0.467 |
| hybrid/en | 97 | 0.072 | 0.335 | 0.486 | 0.588 | 0.481 [0.424, 0.539] | 1.000 |
| hybrid/vi | 97 | 0.057 | 0.331 | 0.497 | 0.540 | 0.472 [0.412, 0.530] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.605 | 0.485 | 0.701 | 0.361 |
| structured_only/vi | 0.605 | 0.485 | 0.701 | 0.361 |
| vector_only/en | 0.433 | 0.285 | 0.662 | 0.347 |
| vector_only/vi | 0.369 | 0.217 | 0.597 | 0.240 |
| hybrid/en | 0.641 | 0.359 | 0.682 | 0.317 |
| hybrid/vi | 0.617 | 0.360 | 0.674 | 0.309 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.042 [-0.085, -0.004] |
| hybrid−vector_only/en | +0.063 [+0.020, +0.109] |
| hybrid−structured_only/vi | -0.052 [-0.096, -0.007] |
| hybrid−vector_only/vi | +0.131 [+0.087, +0.181] |
