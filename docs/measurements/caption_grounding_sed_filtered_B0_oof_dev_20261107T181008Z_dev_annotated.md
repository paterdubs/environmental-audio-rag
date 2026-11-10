# Grounding caption — `sed_filtered_B0_oof_dev_20261107T181008Z` (dev, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `3ba7fc37…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 134 | 0.0000 | 0.0000 | 0.0211 | 1.0000 | 1.0000 (73) | 0.0000 | 0.0000 | 0.0000 | 2.99 |
| constrained_cover/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (76) | 0.0000 | 0.0000 | 0.0000 | 3.05 |
| template/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (77) | 0.0000 | 0.0000 | 0.0000 | 3.47 |
| unconstrained/e2e | 134 | 0.0124 | 0.0229 | 0.0000 | 0.9851 | 0.9556 (45) | 0.0000 | 0.0902 | 0.3209 | 1.31 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.021 [0.006, 0.040] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.012 [0.002, 0.025] | 0.000 [0.000, 0.000] | 0.956 [0.884, 1.000] | 0.090 [0.051, 0.139] | 0.321 [0.246, 0.403] | 0.000 [0.000, 0.000] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.012 [-0.025, -0.002] | +0.021 [+0.006, +0.040] | +0.044 [+0.000, +0.116] | -0.090 [-0.139, -0.051] | -0.321 [-0.403, -0.246] | +0.000 [+0.000, +0.000] |
| constrained_cover−unconstrained/e2e | -0.012 [-0.025, -0.002] | +0.000 [+0.000, +0.000] | +0.044 [+0.000, +0.116] | -0.090 [-0.139, -0.051] | -0.321 [-0.403, -0.246] | +0.000 [+0.000, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.021 [-0.040, -0.006] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
