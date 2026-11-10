# Grounding caption — `sed_lbr_oofevents_sed_lbr_B0_20261109T172809Z_f1_20261110T062901Z` (dev, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `3ba7fc37…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 134 | 0.0000 | 0.0000 | 0.0075 | 1.0000 | 1.0000 (70) | 0.0000 | 0.0000 | 0.0000 | 2.79 |
| constrained_cover/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (72) | 0.0000 | 0.0000 | 0.0000 | 2.81 |
| template/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (72) | 0.0000 | 0.0000 | 0.0000 | 2.99 |
| unconstrained/e2e | 134 | 0.0124 | 0.0292 | 0.0000 | 0.9776 | 0.9118 (34) | 0.0075 | 0.0933 | 0.4403 | 1.02 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.007 [0.000, 0.019] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.012 [0.002, 0.025] | 0.000 [0.000, 0.000] | 0.912 [0.808, 1.000] | 0.093 [0.052, 0.146] | 0.440 [0.358, 0.522] | 0.007 [0.000, 0.022] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.012 [-0.025, -0.002] | +0.007 [+0.000, +0.019] | +0.088 [+0.000, +0.192] | -0.093 [-0.146, -0.052] | -0.440 [-0.522, -0.358] | -0.007 [-0.022, +0.000] |
| constrained_cover−unconstrained/e2e | -0.012 [-0.025, -0.002] | +0.000 [+0.000, +0.000] | +0.088 [+0.000, +0.192] | -0.093 [-0.146, -0.052] | -0.440 [-0.522, -0.358] | -0.007 [-0.022, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.007 [-0.019, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
