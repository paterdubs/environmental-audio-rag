# Grounding caption — `sed_lbr_oofevents_sed_lbr_B0v3_20261110T042337Z_recall_first_20261110T063606Z` (dev, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `3ba7fc37…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 134 | 0.0000 | 0.0000 | 0.1447 | 1.0000 | 1.0000 (113) | 0.0000 | 0.0000 | 0.0000 | 4.13 |
| constrained_cover/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (121) | 0.0000 | 0.0000 | 0.0000 | 6.10 |
| template/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (121) | 0.0000 | 0.0000 | 0.0000 | 7.05 |
| unconstrained/e2e | 134 | 0.0111 | 0.0181 | 0.0306 | 0.8530 | 0.8106 (104) | 0.0149 | 0.0917 | 0.2985 | 2.48 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.145 [0.106, 0.184] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.011 [0.004, 0.021] | 0.031 [0.016, 0.046] | 0.811 [0.739, 0.877] | 0.092 [0.063, 0.125] | 0.299 [0.216, 0.373] | 0.015 [0.000, 0.037] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.011 [-0.021, -0.004] | +0.114 [+0.076, +0.151] | +0.189 [+0.123, +0.261] | -0.092 [-0.125, -0.063] | -0.299 [-0.373, -0.216] | -0.015 [-0.037, +0.000] |
| constrained_cover−unconstrained/e2e | -0.011 [-0.021, -0.004] | -0.031 [-0.046, -0.016] | +0.189 [+0.123, +0.261] | -0.092 [-0.125, -0.063] | -0.299 [-0.373, -0.216] | -0.015 [-0.037, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.145 [-0.184, -0.106] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
