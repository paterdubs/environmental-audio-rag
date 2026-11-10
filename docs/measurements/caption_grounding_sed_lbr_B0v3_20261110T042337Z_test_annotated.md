# Grounding caption — `sed_lbr_B0v3_20261110T042337Z` (test, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.0000 | 0.0000 | 0.0812 | 1.0000 | 1.0000 (101) | 0.0000 | 0.0000 | 0.0000 | 2.81 |
| constrained_cover/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (104) | 0.0000 | 0.0000 | 0.0000 | 3.54 |
| template/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (104) | 0.0000 | 0.0000 | 0.0000 | 4.81 |
| unconstrained/e2e | 139 | 0.0224 | 0.0347 | 0.0230 | 0.9002 | 0.8309 (82) | 0.0144 | 0.1336 | 0.2590 | 2.07 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.081 [0.051, 0.112] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.022 [0.010, 0.037] | 0.023 [0.010, 0.039] | 0.831 [0.760, 0.895] | 0.134 [0.090, 0.181] | 0.259 [0.187, 0.331] | 0.014 [0.000, 0.036] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.022 [-0.037, -0.010] | +0.058 [+0.024, +0.093] | +0.169 [+0.105, +0.240] | -0.134 [-0.181, -0.090] | -0.259 [-0.331, -0.187] | -0.014 [-0.036, +0.000] |
| constrained_cover−unconstrained/e2e | -0.022 [-0.037, -0.010] | -0.023 [-0.039, -0.010] | +0.169 [+0.105, +0.240] | -0.134 [-0.181, -0.090] | -0.259 [-0.331, -0.187] | -0.014 [-0.036, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.081 [-0.112, -0.051] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
