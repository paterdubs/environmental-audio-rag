# Archive audit — DataSEC and DataSED

> Generated from `data/manifests/<dataset>_archive_audit.json` by
> `python -m scripts.report_archive_audit`. Do not edit the numbers by hand.

- Generated at: `2026-09-22T12:45:04Z`
- Taxonomy version: `0.1`
- Taxonomy SHA-256: `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`

## Provenance and licence

| Dataset | Record DOI | Licence |
|---|---|---|
| `datasec` | `10.5281/zenodo.17033970` | `cc-by-nc-sa-4.0` |
| `datased` | `10.5281/zenodo.15346092` | `cc-by-nc-sa-4.0` |

Licence comes from the stored Zenodo record, **not** from the archive: the audit
found no LICENSE or README entry inside either ZIP (see table below).

## Audit summary

| Field | `datasec` | `datased` |
|---|---:|---:|
| Archive bytes | 6,414,663,316 | 4,510,378,259 |
| Size matches contract | True | True |
| MD5 | `29fa9b8cc84cfa69aa4e5e674e780383` | `44e093f675fc44cfb8a11b68456b72d7` |
| MD5 matches contract | True | True |
| ZIP entries | 5,099 | 722 |
| Audio files | 5,048 | 717 |
| Uncompressed GiB | 7.01 | 5.55 |
| Annotation tables | 0 | 2 |
| LICENSE/README inside archive | 0 | 0 |
| Coarse labels in layout | 22 | 0 |
| Subclass labels in layout | 28 | 0 |
| Labels outside taxonomy | 0 | 0 |
| Verdict | **pass** | **pass** |

Verdict meanings:

- `pass` — size and MD5 verified, every observed label maps to the taxonomy

## Label layout

### `datasec` label layout

| Source label | Canonical class ID | Files | Subclasses (files) |
|---|---|---:|---|
| Bells | `bells` | 67 | — |
| Birds | `birds` | 69 | — |
| Cat fights and moans | `cat_fights_and_moans` | 50 | — |
| Chicken coop | `chicken_coop` | 58 | — |
| Cicadas and crickets | `cicadas_and_crickets` | 74 | `Cicadas` (54), `Crickets` (20) |
| Crows seagulls and magpies | `crows_seagulls_magpies` | 106 | `Crows` (50), `Magpies` (21), `Seagulls` (35) |
| Dog barkings and howlings | `dog_barkings_and_howlings` | 70 | — |
| Glass breaking | `glass_breaking` | 109 | — |
| Horn | `horn` | 57 | — |
| Jet aircrafts | `jet_aircrafts` | 103 | — |
| Lawn mower brush cutter and olive shaker | `lawn_mower_brush_cutter_olive_shaker` | 127 | `Brush cutter` (86), `Lawn mower` (21), `Olive shaker` (20) |
| Music | `music` | 1,001 | — |
| Propeller aircrafts | `propeller_aircrafts` | 108 | `Airplanes` (50), `Helicopters` (58) |
| Sirens and alarms | `sirens_and_alarms` | 105 | `Alarms` (37), `Sirens` (68) |
| Thunder fireworks and gunshot | `thunder_fireworks_gunshot` | 235 | `Fireworks` (68), `Gunshot` (141), `Thunder` (26) |
| Train | `train` | 67 | — |
| Vacuum cleaner fan and hairdryer | `vacuum_cleaner_fan_hairdryer` | 95 | `fan` (32), `hairdryer` (32), `vacuum cleaner` (31) |
| Vehicle idling | `vehicle_idling` | 112 | `car truck idling` (81), `motorbike idling` (31) |
| Vehicle pass-by | `vehicle_pass_by` | 217 | `car pass-by` (110), `motorbike pass-by` (57), `truck pass-by` (50) |
| Voices | `voices` | 1,900 | — |
| Wind turbine | `wind_turbine` | 100 | — |
| Workshop | `workshop` | 218 | `air compressor` (30), `drill` (45), `grinder` (38), `jackhammer` (63), `saw` (42) |
| **Total** | | **5,048** | |

### `datased` label layout

Labels are not encoded in the directory tree. The archive ships 2 annotation table(s):

- `DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_ground_truth/Monophonic_sound_detection.csv`
- `DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_ground_truth/Polyphonic_sound_detection.csv`

## Boundary

This audit reads the ZIP central directory only. It verifies archive integrity,
audio counts and label-name coverage. It does **not** open any audio file, so it
says nothing about sample rate, duration, decodability, annotation validity or
duplicates. Those belong to gates D1–D3 and require extraction plus inventory.
