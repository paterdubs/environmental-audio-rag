# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_lbr_B0v3_20261110T042337Z:recall_first`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.074 | 0.452 | 0.584 | 0.672 | 0.595 [0.537, 0.656] | 1.000 |
| structured_only/vi | 96 | 0.074 | 0.452 | 0.584 | 0.672 | 0.595 [0.537, 0.656] | 1.000 |
| vector_only/en | 96 | 0.090 | 0.402 | 0.585 | 0.696 | 0.584 [0.528, 0.639] | 0.527 |
| vector_only/vi | 96 | 0.081 | 0.333 | 0.536 | 0.653 | 0.530 [0.473, 0.588] | 0.448 |
| hybrid/en | 96 | 0.106 | 0.462 | 0.586 | 0.757 | 0.628 [0.570, 0.686] | 1.000 |
| hybrid/vi | 96 | 0.097 | 0.451 | 0.584 | 0.727 | 0.618 [0.560, 0.677] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.830 | 0.410 | 0.741 | 0.467 |
| structured_only/vi | 0.830 | 0.410 | 0.741 | 0.467 |
| vector_only/en | 0.634 | 0.396 | 0.827 | 0.537 |
| vector_only/vi | 0.568 | 0.357 | 0.778 | 0.471 |
| hybrid/en | 0.834 | 0.404 | 0.820 | 0.526 |
| hybrid/vi | 0.835 | 0.396 | 0.801 | 0.513 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | +0.033 [+0.008, +0.058] |
| hybrid−vector_only/en | +0.044 [-0.004, +0.091] |
| hybrid−structured_only/vi | +0.024 [-0.000, +0.046] |
| hybrid−vector_only/vi | +0.089 [+0.035, +0.142] |
