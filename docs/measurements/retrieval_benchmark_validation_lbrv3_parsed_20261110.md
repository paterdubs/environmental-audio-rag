# Benchmark retrieval RQ3 — corpus `validation`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 96/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_lbr_B0v3_20261110T042337Z:recall_first`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 0.069 | 0.440 | 0.567 | 0.646 | 0.578 [0.519, 0.639] | 1.000 |
| structured_only/vi | 96 | 0.071 | 0.450 | 0.578 | 0.656 | 0.586 [0.526, 0.645] | 1.000 |
| vector_only/en | 96 | 0.090 | 0.402 | 0.585 | 0.696 | 0.584 [0.528, 0.639] | 0.545 |
| vector_only/vi | 96 | 0.081 | 0.333 | 0.536 | 0.653 | 0.530 [0.473, 0.588] | 0.458 |
| hybrid/en | 96 | 0.099 | 0.450 | 0.571 | 0.728 | 0.611 [0.551, 0.671] | 1.000 |
| hybrid/vi | 96 | 0.092 | 0.445 | 0.579 | 0.710 | 0.609 [0.549, 0.671] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.769 | 0.410 | 0.741 | 0.459 |
| structured_only/vi | 0.804 | 0.410 | 0.741 | 0.458 |
| vector_only/en | 0.634 | 0.396 | 0.827 | 0.537 |
| vector_only/vi | 0.568 | 0.357 | 0.778 | 0.471 |
| hybrid/en | 0.766 | 0.404 | 0.820 | 0.522 |
| hybrid/vi | 0.816 | 0.396 | 0.801 | 0.497 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | +0.033 [+0.007, +0.058] |
| hybrid−vector_only/en | +0.027 [-0.018, +0.073] |
| hybrid−structured_only/vi | +0.023 [-0.001, +0.047] |
| hybrid−vector_only/vi | +0.080 [+0.027, +0.132] |

## So với filter gold trên cùng câu

> Filter parse lỗi được tính retrieval rỗng, không thay bằng gold.

| Cấu hình / ngôn ngữ | n | Δ nDCG@10 parsed − gold |
|---|---:|---:|
| structured_only/en | 96 | -0.016 |
| structured_only/vi | 96 | -0.008 |
| vector_only/en | 96 | +0.000 |
| vector_only/vi | 96 | +0.000 |
| hybrid/en | 96 | -0.016 |
| hybrid/vi | 96 | -0.009 |
