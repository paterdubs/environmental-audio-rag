# Pilot focal loss — t2b_focal, 2026-09-28

Sinh bởi `scripts.report_pilot_loss.py`; chỉ macro-AP frame trên dev, không mở test.

| gamma | epoch 1 | epoch 2 | epoch 3 | run |
|---:|---:|---:|---:|---|
| 0.5 | 0.5754 | 0.6770 | 0.6917 | `sed_polyphonic_20260928T161127Z` |
| 1 | 0.5846 | 0.6842 | 0.6923 | `sed_polyphonic_20260928T161532Z` |
| 2 | **0.5978** | **0.6667** | **0.6925** | `sed_polyphonic_20260928T162033Z` |

→ Chọn gamma **2** theo macro-AP epoch 3 (hoà chọn gamma nhỏ hơn).
