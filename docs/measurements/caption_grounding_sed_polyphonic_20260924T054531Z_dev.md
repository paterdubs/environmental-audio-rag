# Grounding caption — `sed_polyphonic_20260924T054531Z` (dev)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` sha256 `6f5634bb7837817c…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

| Nhánh / mức | n | Halluc. ↓ | Omission ↓ | Temporal ↑ | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 137 | 0.0000 | 0.2798 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 2.93 |
| constrained/oracle | 137 | 0.0000 | 0.0863 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 3.48 |
| template/e2e | 137 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 6.98 |
| template/oracle | 137 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 6.47 |
| unconstrained/e2e | 137 | 0.0015 | 0.0445 | 0.8738 | 0.0292 | 0.1519 | 0.3577 | 3.25 |
| unconstrained/oracle | 137 | 0.0091 | 0.0174 | 0.9122 | 0.0073 | 0.0926 | 0.2263 | 2.09 |

## Audit: từ ngoài mọi mention (dev)

rhythmic (89), punctuated (83), dominates (56), bursts (49), interrupted (47), rumble (44), roar (42), passing (38), occurring (24), scene (21), hum (21), drone (21), activity (20), chorus (19), featuring (18), clatter (17), persistent (17), wail (17), intervals (16), where (15), background (15), mechanical (14), until (14), sharp (13), unfolds (13), loud (12), concluding (12), persisting (12), dynamic (11), two (11), burst (11), noise (11), air (11), prolonged (10), clip (10), fills (10), through (9), environment (9), shortly (9), regular (9), three (8), near (8), sequence (8), nearly (8), overhead (7), series (7), layered (7), early (7), moment (7), returning (6), passes (6), interplay (6), moments (6), repeatedly (6), mark (6), ambient (6), pass (5), nearby (5), fleeting (5), noises (5), intermittently (5), four (5), all (5), marks (5), no (5), overlapping (4), calls (4), recurring (4), their (4), way (4), echoes (4), period (4), duration (4), segment (4), captured (4), finish (4), track (4), dominating (4), overlaid (4), periods (4), detected (4), constant (3), chatter (3), stream (3), fades (3), hums (3), stops (3), gives (3), urgent (3), multiple (3), short (3), playing (3), frequent (3), instances (3), lasting (3), entire (3), buzzing (3), rumbling (3), past (3), starts (3), just (3), dominated (3), echoing (3), starting (3), ten (3), middle (3), alternating (3), repeated (3), off (3), two-minute (3), five (3), fading (3), crack (3), events (3), profound (3), flying (2), fifteen (2), blending (2), running (2), passage (2), each (2), punctuates (2), long (2), noisy (2), operating (2), resembling (2), irregular (2), again (2), against (2), scratching (2), capturing (2), inside (2), tolling (2), continuing (2), dominate (2), transition (2), interspersed (2), one (2), very (2), persistently (2), clash (2), piercing (2), cutting (2), creating (2), another (2), return (2), dominant (2), intro (2), concludes (2), drives (2)
