# Grounding caption — `sed_lbr_B0_20261109T172809Z` (test, all)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.0000 | 0.0070 | 1.0000 | 1.0000 (68) | 0.0000 | 0.0000 | 0.0000 | 2.05 |
| constrained_cover/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (70) | 0.0000 | 0.0000 | 0.0000 | 2.08 |
| template/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (70) | 0.0000 | 0.0000 | 0.0000 | 2.70 |
| unconstrained/e2e | 142 | 0.0182 | 0.0437 | 0.0035 | 0.9507 | 0.8542 (48) | 0.0070 | 0.1268 | 0.4085 | 1.29 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.007 [0.000, 0.018] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.018 [0.007, 0.031] | 0.004 [0.000, 0.011] | 0.854 [0.750, 0.946] | 0.127 [0.077, 0.176] | 0.408 [0.331, 0.493] | 0.007 [0.000, 0.021] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.018 [-0.031, -0.007] | +0.004 [-0.007, +0.014] | +0.146 [+0.054, +0.250] | -0.127 [-0.176, -0.077] | -0.408 [-0.493, -0.331] | -0.007 [-0.021, +0.000] |
| constrained_cover−unconstrained/e2e | -0.018 [-0.031, -0.007] | -0.004 [-0.011, +0.000] | +0.146 [+0.054, +0.250] | -0.127 [-0.176, -0.077] | -0.408 [-0.493, -0.331] | -0.007 [-0.021, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.007 [-0.018, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
