# Grounding caption — `sed_ensemble_s13_f2_20260929T045053Z` (dev, annotated)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `08b14a95…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 134 | 0.0000 | 0.0000 | 0.0075 | 1.0000 | 1.0000 (74) | 0.0000 | 0.0000 | 0.0000 | 2.89 |
| constrained/oracle | 134 | 0.0000 | 0.0000 | 0.0845 | 1.0000 | 1.0000 (103) | 0.0000 | 0.0000 | 0.0000 | 3.99 |
| constrained_cover/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (75) | 0.0000 | 0.0000 | 0.0000 | 2.91 |
| constrained_cover/oracle | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 5.81 |
| template/e2e | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (75) | 0.0000 | 0.0000 | 0.0000 | 2.94 |
| template/oracle | 134 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (107) | 0.0000 | 0.0000 | 0.0000 | 6.61 |
| unconstrained/e2e | 134 | 0.0149 | 0.0375 | 0.0000 | 0.9851 | 0.9500 (40) | 0.0000 | 0.0709 | 0.3507 | 1.19 |
| unconstrained/oracle | 134 | 0.0093 | 0.0138 | 0.0178 | 0.9027 | 0.8484 (86) | 0.0075 | 0.0922 | 0.2164 | 2.16 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.007 [0.000, 0.019] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained/oracle | 0.000 [0.000, 0.000] | 0.084 [0.051, 0.119] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/oracle | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/oracle | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.015 [0.005, 0.027] | 0.000 [0.000, 0.000] | 0.950 [0.875, 1.000] | 0.071 [0.030, 0.116] | 0.351 [0.276, 0.425] | 0.000 [0.000, 0.000] |
| unconstrained/oracle | 0.009 [0.002, 0.019] | 0.018 [0.007, 0.033] | 0.848 [0.782, 0.909] | 0.092 [0.057, 0.132] | 0.216 [0.149, 0.291] | 0.007 [0.000, 0.022] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.015 [-0.027, -0.005] | +0.007 [+0.000, +0.019] | +0.050 [+0.000, +0.125] | -0.071 [-0.116, -0.030] | -0.351 [-0.425, -0.276] | +0.000 [+0.000, +0.000] |
| constrained−unconstrained/oracle | -0.009 [-0.019, -0.002] | +0.067 [+0.038, +0.098] | +0.152 [+0.091, +0.218] | -0.092 [-0.132, -0.057] | -0.216 [-0.291, -0.149] | -0.007 [-0.022, +0.000] |
| constrained_cover−unconstrained/e2e | -0.015 [-0.027, -0.005] | +0.000 [+0.000, +0.000] | +0.050 [+0.000, +0.125] | -0.071 [-0.116, -0.030] | -0.351 [-0.425, -0.276] | +0.000 [+0.000, +0.000] |
| constrained_cover−unconstrained/oracle | -0.009 [-0.019, -0.002] | -0.018 [-0.033, -0.007] | +0.152 [+0.091, +0.218] | -0.092 [-0.132, -0.057] | -0.216 [-0.291, -0.149] | -0.007 [-0.022, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.007 [-0.019, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| constrained_cover−constrained/oracle | +0.000 [+0.000, +0.000] | -0.084 [-0.119, -0.051] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

## Audit: từ ngoài mọi mention (dev)

rhythmic (76), bursts (65), dominates (65), punctuated (45), interrupted (34), rumble (33), occurring (32), until (24), environment (23), roar (22), intervals (22), activity (22), hum (22), nearly (20), wail (20), scene (19), passing (19), drone (19), through (18), no (18), chorus (17), two (17), clatter (17), persisting (17), detected (16), air (15), events (15), sharp (15), regular (15), fills (14), three (14), featuring (14), clip (13), repeatedly (13), mechanical (13), sequence (13), mark (11), captured (11), shortly (11), series (10), near (10), where (10), duration (10), moment (9), ambient (9), echoes (8), prolonged (8), recurring (8), burst (7), noise (7), lasting (6), calls (6), repeated (6), echoing (6), buzzing (6), persistent (6), track (6), finish (6), concluding (5), early (5), just (5), high-pitched (5), very (5), starting (5), two-minute (5), five (5), entire (4), marks (4), soundless (4), detectable (4), their (4), stops (4), four (4), overhead (4), again (4), starts (4), moments (4), playing (4), fades (3), chatter (3), stream (3), creating (3), returning (3), each (3), profound (3), cutting (3), human (3), thirty-second (3), way (3), echo (3), thirty (3), free (3), background (3), inside (3), one (3), around (3), ten (3), dominating (3), twenty (3), piercing (3), middle (3), dominant (3), twice (3), turned (3), off (3), within (3), interplay (3), low-frequency (3), constant (2), fading (2), passes (2), filled (2), rhythm (2), unfolds (2), passage (2), long (2), reveals (2), animal (2), fourth (2), only (2), gives (2), operating (2), arrival (2), nearby (2), multiple (2), against (2), instances (2), fighting (2), moaning (2), dominate (2), scratching (2), twenty-five (2), capturing (2), pauses (2), begins (2), segment (2), rumbling (2), twelve (2), persistently (2), onset (2), sustained (2), interwoven (2), several (2), alternating (2), breaking (2), whirring (2), likely (2), usage (2), minute-long (2), raucous (2)
