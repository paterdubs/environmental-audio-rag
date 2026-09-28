# Pilot focal loss — t2b_focal, 2026-09-28

Sinh bởi `scripts.report_pilot_loss.py`; chỉ macro-AP frame trên dev, không mở test.

| gamma | epoch 1 | epoch 2 | epoch 3 | run |
|---:|---:|---:|---:|---|
| 0.5 | **0.5678** | **0.6738** | **0.6920** | `sed_polyphonic_20260928T154005Z` |
| 1 | 0.5770 | 0.6701 | 0.6892 | `sed_polyphonic_20260928T155421Z` |
| 2 | 0.5929 | 0.6661 | 0.6783 | `sed_polyphonic_20260928T155829Z` |

→ Chọn gamma **0.5** theo macro-AP epoch 3 (hoà chọn gamma nhỏ hơn).
