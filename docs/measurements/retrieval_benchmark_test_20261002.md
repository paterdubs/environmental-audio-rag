# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_ensemble_s13_f2_20260929T045053Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.081 | 0.252 | 0.306 | 0.603 | 0.416 [0.346, 0.487] | 1.000 |
| structured_only/vi | 97 | 0.081 | 0.252 | 0.306 | 0.603 | 0.416 [0.346, 0.487] | 1.000 |
| vector_only/en | 97 | 0.087 | 0.348 | 0.503 | 0.691 | 0.526 [0.467, 0.582] | 0.274 |
| vector_only/vi | 97 | 0.071 | 0.329 | 0.462 | 0.641 | 0.489 [0.429, 0.548] | 0.263 |
| hybrid/en | 97 | 0.082 | 0.247 | 0.305 | 0.603 | 0.415 [0.344, 0.485] | 1.000 |
| hybrid/vi | 97 | 0.085 | 0.250 | 0.306 | 0.613 | 0.420 [0.350, 0.491] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.761 | 0.151 | 0.776 | 0.121 |
| structured_only/vi | 0.761 | 0.151 | 0.776 | 0.121 |
| vector_only/en | 0.621 | 0.387 | 0.733 | 0.426 |
| vector_only/vi | 0.597 | 0.312 | 0.720 | 0.396 |
| hybrid/en | 0.762 | 0.151 | 0.761 | 0.126 |
| hybrid/vi | 0.767 | 0.151 | 0.776 | 0.128 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.001 [-0.008, +0.004] |
| hybrid−vector_only/en | -0.111 [-0.166, -0.059] |
| hybrid−structured_only/vi | +0.004 [-0.001, +0.009] |
| hybrid−vector_only/vi | -0.069 [-0.120, -0.015] |
