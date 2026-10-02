# Grounding caption — `sed_ensemble_s13_f2_20260929T045053Z` (dev, all)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `08b14a95…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 137 | 0.0000 | 0.0000 | 0.0122 | 1.0000 | 1.0000 (75) | 0.0000 | 0.0000 | 0.0000 | 2.86 |
| constrained/oracle | 137 | 0.0000 | 0.0000 | 0.0826 | 1.0000 | 1.0000 (103) | 0.0000 | 0.0000 | 0.0000 | 3.90 |
| constrained_cover/e2e | 137 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (76) | 0.0000 | 0.0000 | 0.0000 | 2.91 |
| constrained_cover/oracle | 137 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 5.68 |
| template/e2e | 137 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (76) | 0.0000 | 0.0000 | 0.0000 | 2.93 |
| template/oracle | 137 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 6.47 |
| unconstrained/e2e | 137 | 0.0146 | 0.0368 | 0.0000 | 0.9854 | 0.9512 (41) | 0.0000 | 0.0742 | 0.3577 | 1.19 |
| unconstrained/oracle | 137 | 0.0091 | 0.0138 | 0.0174 | 0.9049 | 0.8484 (86) | 0.0073 | 0.0901 | 0.2336 | 2.11 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.012 [0.000, 0.028] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained/oracle | 0.000 [0.000, 0.000] | 0.083 [0.051, 0.118] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/oracle | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/oracle | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.015 [0.005, 0.027] | 0.000 [0.000, 0.000] | 0.951 [0.870, 1.000] | 0.074 [0.035, 0.119] | 0.358 [0.285, 0.438] | 0.000 [0.000, 0.000] |
| unconstrained/oracle | 0.009 [0.002, 0.020] | 0.017 [0.006, 0.033] | 0.848 [0.776, 0.913] | 0.090 [0.052, 0.133] | 0.234 [0.168, 0.299] | 0.007 [0.000, 0.022] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.015 [-0.027, -0.005] | +0.012 [+0.000, +0.028] | +0.049 [+0.000, +0.130] | -0.074 [-0.119, -0.035] | -0.358 [-0.438, -0.285] | +0.000 [+0.000, +0.000] |
| constrained−unconstrained/oracle | -0.009 [-0.020, -0.002] | +0.065 [+0.039, +0.097] | +0.152 [+0.087, +0.224] | -0.090 [-0.133, -0.052] | -0.234 [-0.299, -0.168] | -0.007 [-0.022, +0.000] |
| constrained_cover−unconstrained/e2e | -0.015 [-0.027, -0.005] | +0.000 [+0.000, +0.000] | +0.049 [+0.000, +0.130] | -0.074 [-0.119, -0.035] | -0.358 [-0.438, -0.285] | +0.000 [+0.000, +0.000] |
| constrained_cover−unconstrained/oracle | -0.009 [-0.020, -0.002] | -0.017 [-0.033, -0.006] | +0.152 [+0.087, +0.224] | -0.090 [-0.133, -0.052] | -0.234 [-0.299, -0.168] | -0.007 [-0.022, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.012 [-0.028, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| constrained_cover−constrained/oracle | +0.000 [+0.000, +0.000] | -0.083 [-0.118, -0.051] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

## Audit: từ ngoài mọi mention (dev)

rhythmic (76), bursts (65), dominates (65), punctuated (46), interrupted (34), rumble (33), occurring (32), environment (25), until (24), no (23), activity (23), roar (22), intervals (22), hum (22), detected (21), nearly (20), wail (20), scene (19), passing (19), drone (19), through (18), events (18), chorus (17), two (17), clatter (17), persisting (17), air (15), sharp (15), regular (15), fills (14), three (14), featuring (14), clip (13), moment (13), repeatedly (13), mechanical (13), sequence (13), where (12), series (11), mark (11), captured (11), shortly (11), near (10), duration (10), ambient (9), echoes (8), noise (8), prolonged (8), recurring (8), profound (7), burst (7), lasting (6), calls (6), repeated (6), echoing (6), buzzing (6), persistent (6), track (6), finish (6), concluding (5), early (5), just (5), high-pitched (5), very (5), starting (5), two-minute (5), five (5), entire (4), marks (4), soundless (4), detectable (4), their (4), stops (4), four (4), overhead (4), again (4), starts (4), moments (4), playing (4), fades (3), chatter (3), stream (3), creating (3), returning (3), each (3), cutting (3), human (3), thirty-second (3), way (3), echo (3), thirty (3), free (3), background (3), inside (3), one (3), around (3), ten (3), dominating (3), twenty (3), piercing (3), middle (3), dominant (3), twice (3), turned (3), off (3), within (3), interplay (3), period (3), low-frequency (3), loud (2), constant (2), fading (2), passes (2), filled (2), rhythm (2), unfolds (2), passage (2), long (2), reveals (2), animal (2), fourth (2), only (2), gives (2), operating (2), arrival (2), nearby (2), multiple (2), against (2), instances (2), fighting (2), moaning (2), dominate (2), scratching (2), twenty-five (2), capturing (2), pauses (2), begins (2), segment (2), rumbling (2), twelve (2), persistently (2), onset (2), sustained (2), interwoven (2), several (2), alternating (2), breaking (2), whirring (2), likely (2), usage (2)
