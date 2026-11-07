# Benchmark retrieval RQ3 — corpus `test`

> Sinh bởi `scripts.evaluate_retrieval`. Query set `e900fec3…`, 97/100 câu có relevant (còn lại loại); embedding `BAAI/bge-m3@5617a9f61b02+doc-v1-template-en-vi`; SED `sed_served_B0_20261107T175659Z`. Relevance từ ground truth; filter exactness trên event đã index. Không có tham số nào được chỉnh.

| Cấu hình / ngôn ngữ | n | R@1 | R@5 | R@10 | MRR | nDCG@10 [CI 95%] | Filter exactness |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 0.076 | 0.239 | 0.292 | 0.557 | 0.392 [0.315, 0.469] | 1.000 |
| structured_only/vi | 97 | 0.076 | 0.239 | 0.292 | 0.557 | 0.392 [0.315, 0.469] | 1.000 |
| vector_only/en | 97 | 0.076 | 0.296 | 0.407 | 0.614 | 0.458 [0.391, 0.522] | 0.271 |
| vector_only/vi | 97 | 0.066 | 0.219 | 0.354 | 0.559 | 0.406 [0.339, 0.474] | 0.259 |
| hybrid/en | 97 | 0.068 | 0.237 | 0.292 | 0.527 | 0.383 [0.307, 0.461] | 1.000 |
| hybrid/vi | 97 | 0.072 | 0.236 | 0.292 | 0.541 | 0.386 [0.311, 0.465] | 1.000 |

## nDCG@10 theo nhóm câu hỏi

| Cấu hình / ngôn ngữ | duration | multi_class | single_class | temporal |
|---|---:|---:|---:|---:|
| structured_only/en | 0.732 | 0.090 | 0.752 | 0.134 |
| structured_only/vi | 0.732 | 0.090 | 0.752 | 0.134 |
| vector_only/en | 0.583 | 0.264 | 0.737 | 0.330 |
| vector_only/vi | 0.550 | 0.222 | 0.723 | 0.224 |
| hybrid/en | 0.701 | 0.090 | 0.747 | 0.134 |
| hybrid/vi | 0.715 | 0.090 | 0.746 | 0.134 |

## Hiệu số cặp nDCG@10 (theo câu hỏi), CI 95%

| So sánh | Δ [CI 95%] |
|---|---:|
| hybrid−structured_only/en | -0.008 [-0.016, -0.001] |
| hybrid−vector_only/en | -0.075 [-0.121, -0.028] |
| hybrid−structured_only/vi | -0.005 [-0.012, -0.001] |
| hybrid−vector_only/vi | -0.019 [-0.061, +0.024] |
