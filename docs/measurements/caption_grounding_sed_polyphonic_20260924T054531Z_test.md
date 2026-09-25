# Grounding caption — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `c3bf5893…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.0000 | 0.2842 | 0.9986 | 0.9981 (106) | 0.0000 | 0.0000 | 0.0000 | 2.75 |
| constrained/oracle | 142 | 0.0000 | 0.0000 | 0.0995 | 0.9983 | 0.9975 (98) | 0.0000 | 0.0000 | 0.0000 | 3.06 |
| template/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (114) | 0.0000 | 0.0000 | 0.0000 | 6.13 |
| template/oracle | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 5.21 |
| unconstrained/e2e | 142 | 0.0038 | 0.0045 | 0.0599 | 0.9025 | 0.8707 (107) | 0.0141 | 0.1856 | 0.4225 | 3.13 |
| unconstrained/oracle | 142 | 0.0126 | 0.0211 | 0.0124 | 0.9413 | 0.8874 (74) | 0.0070 | 0.1365 | 0.3239 | 2.01 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.284 [0.233, 0.340] | 0.998 [0.994, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained/oracle | 0.000 [0.000, 0.000] | 0.100 [0.067, 0.135] | 0.998 [0.993, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/oracle | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.004 [0.000, 0.010] | 0.060 [0.041, 0.079] | 0.871 [0.828, 0.912] | 0.186 [0.145, 0.229] | 0.423 [0.345, 0.500] | 0.014 [0.000, 0.035] |
| unconstrained/oracle | 0.013 [0.004, 0.022] | 0.012 [0.004, 0.022] | 0.887 [0.821, 0.948] | 0.137 [0.090, 0.186] | 0.324 [0.239, 0.408] | 0.007 [0.000, 0.021] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.004 [-0.010, +0.000] | +0.224 [+0.178, +0.274] | +0.127 [+0.087, +0.170] | -0.186 [-0.229, -0.145] | -0.423 [-0.500, -0.345] | -0.014 [-0.035, +0.000] |
| constrained−unconstrained/oracle | -0.013 [-0.022, -0.004] | +0.087 [+0.054, +0.123] | +0.110 [+0.049, +0.177] | -0.137 [-0.186, -0.090] | -0.324 [-0.408, -0.239] | -0.007 [-0.021, +0.000] |
