# Grounding caption — `sed_lbr_B0_20261109T172809Z` (test, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.0000 | 0.0000 | 0.0072 | 1.0000 | 1.0000 (65) | 0.0000 | 0.0000 | 0.0000 | 2.02 |
| constrained_cover/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (67) | 0.0000 | 0.0000 | 0.0000 | 2.05 |
| template/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (67) | 0.0000 | 0.0000 | 0.0000 | 2.68 |
| unconstrained/e2e | 139 | 0.0162 | 0.0398 | 0.0036 | 0.9496 | 0.8444 (45) | 0.0072 | 0.1259 | 0.4029 | 1.27 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.007 [0.000, 0.018] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.016 [0.005, 0.029] | 0.004 [0.000, 0.014] | 0.844 [0.741, 0.939] | 0.126 [0.082, 0.181] | 0.403 [0.331, 0.482] | 0.007 [0.000, 0.022] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.016 [-0.029, -0.005] | +0.004 [-0.007, +0.018] | +0.156 [+0.061, +0.259] | -0.126 [-0.181, -0.082] | -0.403 [-0.482, -0.331] | -0.007 [-0.022, +0.000] |
| constrained_cover−unconstrained/e2e | -0.016 [-0.029, -0.005] | -0.004 [-0.014, +0.000] | +0.156 [+0.061, +0.259] | -0.126 [-0.181, -0.082] | -0.403 [-0.482, -0.331] | -0.007 [-0.022, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.007 [-0.018, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
