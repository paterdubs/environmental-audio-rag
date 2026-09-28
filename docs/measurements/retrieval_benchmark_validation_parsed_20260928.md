# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_polyphonic_20260924T054531Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.100 | 0.355 | 0.501 | 0.602 | 0.507 [0.448, 0.563] | 1.000 |
| structured_only/vi | 96 | 0.103 | 0.352 | 0.491 | 0.601 | 0.502 [0.443, 0.560] | 1.000 |
| vector_only/en | 96 | 0.058 | 0.269 | 0.401 | 0.514 | 0.408 [0.349, 0.470] | 0.625 |
| vector_only/vi | 96 | 0.057 | 0.220 | 0.371 | 0.486 | 0.373 [0.315, 0.430] | 0.511 |
| hybrid/en | 96 | 0.085 | 0.334 | 0.495 | 0.595 | 0.491 [0.432, 0.552] | 1.000 |
| hybrid/vi | 96 | 0.089 | 0.319 | 0.479 | 0.616 | 0.490 [0.427, 0.552] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.570 | 0.367 | 0.640 | 0.487 |
| structured_only/vi | 0.586 | 0.367 | 0.640 | 0.458 |
| vector_only/en | 0.451 | 0.283 | 0.617 | 0.333 |
| vector_only/vi | 0.388 | 0.223 | 0.580 | 0.345 |
| hybrid/en | 0.596 | 0.355 | 0.624 | 0.434 |
| hybrid/vi | 0.597 | 0.344 | 0.627 | 0.437 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.016 [-0.049, +0.019] |
| hybrid−vector_only/en | +0.083 [+0.056, +0.115] |
| hybrid−structured_only/vi | -0.012 [-0.043, +0.021] |
| hybrid−vector_only/vi | +0.117 [+0.076, +0.164] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 96 | +0.009 |
| structured_only/vi | 96 | +0.005 |
| vector_only/en | 96 | +0.000 |
| vector_only/vi | 96 | +0.000 |
| hybrid/en | 96 | +0.012 |
| hybrid/vi | 96 | -0.002 |
