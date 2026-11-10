# Grounding caption — `sed_ensemble_B0_final_test_20261014T085016Z` (test, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.0000 | 0.0000 | 0.0132 | 1.0000 | 1.0000 (61) | 0.0000 | 0.0000 | 0.0000 | 2.14 |
| constrained_cover/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (64) | 0.0000 | 0.0000 | 0.0000 | 2.19 |
| template/e2e | 139 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (64) | 0.0000 | 0.0000 | 0.0000 | 2.48 |
| unconstrained/e2e | 139 | 0.0048 | 0.0127 | 0.0000 | 0.9784 | 0.9143 (35) | 0.0072 | 0.1331 | 0.3597 | 1.14 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.013 [0.002, 0.029] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.005 [0.000, 0.012] | 0.000 [0.000, 0.000] | 0.914 [0.806, 1.000] | 0.133 [0.083, 0.191] | 0.360 [0.281, 0.439] | 0.007 [0.000, 0.022] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.005 [-0.012, +0.000] | +0.013 [+0.002, +0.029] | +0.086 [+0.000, +0.194] | -0.133 [-0.191, -0.083] | -0.360 [-0.439, -0.281] | -0.007 [-0.022, +0.000] |
| constrained_cover−unconstrained/e2e | -0.005 [-0.012, +0.000] | +0.000 [+0.000, +0.000] | +0.086 [+0.000, +0.194] | -0.133 [-0.191, -0.083] | -0.360 [-0.439, -0.281] | -0.007 [-0.022, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.013 [-0.029, -0.002] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
