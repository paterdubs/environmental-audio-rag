# Grounding caption — `sed_ensemble_B0_final_test_20261014T085016Z` (test, all)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `9e0a458f…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.0000 | 0.0129 | 1.0000 | 1.0000 (63) | 0.0000 | 0.0000 | 0.0000 | 2.14 |
| constrained_cover/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (66) | 0.0000 | 0.0000 | 0.0000 | 2.19 |
| template/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (66) | 0.0000 | 0.0000 | 0.0000 | 2.48 |
| unconstrained/e2e | 142 | 0.0047 | 0.0124 | 0.0000 | 0.9789 | 0.9167 (36) | 0.0070 | 0.1303 | 0.3732 | 1.13 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.013 [0.002, 0.028] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.005 [0.000, 0.012] | 0.000 [0.000, 0.000] | 0.917 [0.818, 1.000] | 0.130 [0.077, 0.183] | 0.373 [0.289, 0.451] | 0.007 [0.000, 0.021] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.005 [-0.012, +0.000] | +0.013 [+0.002, +0.028] | +0.083 [+0.000, +0.182] | -0.130 [-0.183, -0.077] | -0.373 [-0.451, -0.289] | -0.007 [-0.021, +0.000] |
| constrained_cover−unconstrained/e2e | -0.005 [-0.012, +0.000] | +0.000 [+0.000, +0.000] | +0.083 [+0.000, +0.182] | -0.130 [-0.183, -0.077] | -0.373 [-0.451, -0.289] | -0.007 [-0.021, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.013 [-0.028, -0.002] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
