# Grounding caption — `sed_lbr_B0v3_20261110T042337Z` (test, all)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.0000 | 0.0877 | 1.0000 | 1.0000 (103) | 0.0000 | 0.0000 | 0.0000 | 2.83 |
| constrained_cover/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 3.63 |
| template/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 4.87 |
| unconstrained/e2e | 142 | 0.0243 | 0.0373 | 0.0249 | 0.9023 | 0.8369 (85) | 0.0141 | 0.1343 | 0.2606 | 2.08 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.088 [0.057, 0.121] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.024 [0.011, 0.040] | 0.025 [0.011, 0.041] | 0.837 [0.763, 0.903] | 0.134 [0.092, 0.185] | 0.261 [0.197, 0.331] | 0.014 [0.000, 0.035] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.024 [-0.040, -0.011] | +0.063 [+0.030, +0.098] | +0.163 [+0.097, +0.237] | -0.134 [-0.185, -0.092] | -0.261 [-0.331, -0.197] | -0.014 [-0.035, +0.000] |
| constrained_cover−unconstrained/e2e | -0.024 [-0.040, -0.011] | -0.025 [-0.041, -0.011] | +0.163 [+0.097, +0.237] | -0.134 [-0.185, -0.092] | -0.261 [-0.331, -0.197] | -0.014 [-0.035, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.088 [-0.121, -0.057] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
