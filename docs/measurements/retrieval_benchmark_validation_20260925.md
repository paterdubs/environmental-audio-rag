# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_polyphonic_20260924T054531Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.099 | 0.354 | 0.482 | 0.608 | 0.498 [0.439, 0.551] | 1.000 |
| structured_only/vi | 96 | 0.099 | 0.354 | 0.482 | 0.608 | 0.498 [0.439, 0.551] | 1.000 |
| vector_only/en | 96 | 0.058 | 0.269 | 0.401 | 0.514 | 0.408 [0.349, 0.470] | 0.598 |
| vector_only/vi | 96 | 0.057 | 0.220 | 0.371 | 0.486 | 0.373 [0.315, 0.430] | 0.499 |
| hybrid/en | 96 | 0.082 | 0.331 | 0.472 | 0.594 | 0.479 [0.421, 0.540] | 1.000 |
| hybrid/vi | 96 | 0.098 | 0.327 | 0.467 | 0.640 | 0.492 [0.429, 0.550] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.575 | 0.367 | 0.640 | 0.450 |
| structured_only/vi | 0.575 | 0.367 | 0.640 | 0.450 |
| vector_only/en | 0.451 | 0.283 | 0.617 | 0.333 |
| vector_only/vi | 0.388 | 0.223 | 0.580 | 0.345 |
| hybrid/en | 0.583 | 0.355 | 0.624 | 0.400 |
| hybrid/vi | 0.588 | 0.344 | 0.627 | 0.451 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.019 [-0.049, +0.011] |
| hybrid−vector_only/en | +0.070 [+0.038, +0.105] |
| hybrid−structured_only/vi | -0.005 [-0.035, +0.026] |
| hybrid−vector_only/vi | +0.119 [+0.080, +0.163] |
