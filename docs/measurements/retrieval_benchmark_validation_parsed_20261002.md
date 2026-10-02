# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_ensemble_s13_f2_20260929T045053Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.080 | 0.232 | 0.298 | 0.574 | 0.406 [0.334, 0.483] | 1.000 |
| structured_only/vi | 96 | 0.080 | 0.238 | 0.294 | 0.576 | 0.406 [0.334, 0.483] | 1.000 |
| vector_only/en | 96 | 0.093 | 0.355 | 0.500 | 0.675 | 0.540 [0.483, 0.600] | 0.295 |
| vector_only/vi | 96 | 0.081 | 0.308 | 0.434 | 0.631 | 0.477 [0.417, 0.542] | 0.261 |
| hybrid/en | 96 | 0.080 | 0.235 | 0.298 | 0.565 | 0.404 [0.333, 0.480] | 1.000 |
| hybrid/vi | 96 | 0.077 | 0.238 | 0.295 | 0.561 | 0.403 [0.330, 0.478] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.654 | 0.128 | 0.733 | 0.218 |
| structured_only/vi | 0.654 | 0.128 | 0.733 | 0.218 |
| vector_only/en | 0.602 | 0.343 | 0.737 | 0.525 |
| vector_only/vi | 0.549 | 0.276 | 0.723 | 0.419 |
| hybrid/en | 0.645 | 0.128 | 0.726 | 0.224 |
| hybrid/vi | 0.643 | 0.128 | 0.729 | 0.218 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.002 [-0.009, +0.006] |
| hybrid−vector_only/en | -0.135 [-0.184, -0.086] |
| hybrid−structured_only/vi | -0.003 [-0.010, +0.001] |
| hybrid−vector_only/vi | -0.074 [-0.122, -0.024] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 96 | +0.007 |
| structured_only/vi | 96 | +0.008 |
| vector_only/en | 96 | +0.000 |
| vector_only/vi | 96 | +0.000 |
| hybrid/en | 96 | +0.007 |
| hybrid/vi | 96 | +0.008 |
