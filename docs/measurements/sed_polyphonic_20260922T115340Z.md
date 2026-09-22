# Run `sed_polyphonic_20260922T115340Z`

> Generated from run artifacts by `python -m scripts.report_run`.

## Provenance

- Complete: `True`
- Torch: `2.11.0+cu128`
- GPU: `NVIDIA GeForce RTX 3070 Laptop GPU`
- Taxonomy SHA-256: `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`
- Split SHA-256: `656c1851de7c22a5eb6b2c2dc2b20397ad1bce98b136c591b7fe68b88cd130b1`
- Best validation frame macro-F1: `0.357305`

## Frozen test result

- Frame macro-F1 at threshold 0.5: `0.359448`
- Frame macro average precision: `0.466312`
- Evaluated frames: `671570`

| Class | Frame F1 |
|---|---:|
| `bells` | 0.377025 |
| `birds` | 0.343184 |
| `cat_fights_and_moans` | 0.357928 |
| `chicken_coop` | 0.270273 |
| `cicadas_and_crickets` | 0.676579 |
| `crows_seagulls_magpies` | 0.134646 |
| `dog_barkings_and_howlings` | 0.442734 |
| `glass_breaking` | 0.368057 |
| `horn` | 0.134842 |
| `jet_aircrafts` | 0.290783 |
| `lawn_mower_brush_cutter_olive_shaker` | 0.198201 |
| `music` | 0.478766 |
| `propeller_aircrafts` | 0.432831 |
| `sirens_and_alarms` | 0.549780 |
| `thunder_fireworks_gunshot` | 0.367377 |
| `train` | 0.374889 |
| `vacuum_cleaner_fan_hairdryer` | 0.454170 |
| `vehicle_idling` | 0.280073 |
| `vehicle_pass_by` | 0.272978 |
| `voices` | 0.263426 |
| `workshop` | 0.479872 |

## Boundary

These are frame-level baseline metrics. Event-based F1 and PSDS require calibrated post-processing and are not implied by this report.
