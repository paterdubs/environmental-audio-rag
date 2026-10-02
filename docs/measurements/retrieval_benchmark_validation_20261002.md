# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_ensemble_s13_f2_20260929T045053Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.078 | 0.234 | 0.286 | 0.566 | 0.399 [0.326, 0.478] | 1.000 |
| structured_only/vi | 96 | 0.078 | 0.234 | 0.286 | 0.566 | 0.399 [0.326, 0.478] | 1.000 |
| vector_only/en | 96 | 0.093 | 0.355 | 0.500 | 0.675 | 0.540 [0.483, 0.600] | 0.275 |
| vector_only/vi | 96 | 0.081 | 0.308 | 0.434 | 0.631 | 0.477 [0.417, 0.542] | 0.252 |
| hybrid/en | 96 | 0.081 | 0.233 | 0.286 | 0.561 | 0.398 [0.325, 0.475] | 1.000 |
| hybrid/vi | 96 | 0.073 | 0.233 | 0.287 | 0.545 | 0.394 [0.321, 0.472] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.635 | 0.128 | 0.733 | 0.207 |
| structured_only/vi | 0.635 | 0.128 | 0.733 | 0.207 |
| vector_only/en | 0.602 | 0.343 | 0.737 | 0.525 |
| vector_only/vi | 0.549 | 0.276 | 0.723 | 0.419 |
| hybrid/en | 0.629 | 0.128 | 0.726 | 0.213 |
| hybrid/vi | 0.620 | 0.128 | 0.729 | 0.207 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.001 [-0.008, +0.007] |
| hybrid−vector_only/en | -0.142 [-0.194, -0.090] |
| hybrid−structured_only/vi | -0.004 [-0.011, +0.001] |
| hybrid−vector_only/vi | -0.082 [-0.134, -0.027] |
