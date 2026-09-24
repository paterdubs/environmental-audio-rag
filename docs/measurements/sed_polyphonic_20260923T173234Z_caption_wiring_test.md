# Verify wiring caption + grounding — `sed_polyphonic_20260923T173234Z` (test)

> Sinh bởi `scripts.generate_captions ml\runs\sed_polyphonic_20260923T173234Z --split test`. Kiểm wiring end-to-end trên dự đoán thật đã đóng băng — không phải kết quả nghiên cứu W5 (chưa có nhánh unconstrained/constrained đối chứng).

## Tổng quan

| | |
|---|---:|
| Recording | 142 |
| Recording có ≥1 event | 142 |
| Tổng event | 1256 |
| Event nhiều nhất trong 1 recording | 66 |
| Recording lệch bất biến G1-G3 (kỳ vọng 0) | 0 |

Không có recording nào lệch bất biến hallucination=0/omission=0/coverage=1/forbidden=0/temporal_order=1 — pipeline canonicalize→caption→grounding chạy đúng trên dự đoán thật, kể cả recording nhiều event.

## Ví dụ (ưu tiên recording nhiều event)

- `S-0003` (10 event): A vehicle pass by is audible from 0.0 to 70.2 seconds. A vehicle idling is audible from 0.0 to 95.1 seconds. A train is audible from 10.0 to 20.0 seconds. A voices is audible from 28.3 to 47.9 seconds. A music is audible from 28.3 to 35.4 seconds. A crows seagulls magpies is audible from 43.0 to 46.6 seconds. A birds is audible from 43.4 to 46.6 seconds. A voices is audible from 69.3 to 100.0 seconds. A music is audible from 70.6 to 100.0 seconds. A dog barkings and howlings is audible from 81.0 to 84.5 seconds.
- `S-0007` (4 event): A vehicle idling is audible from 0.0 to 8.9 seconds. A vehicle pass by is audible from 0.0 to 20.0 seconds. A train is audible from 0.0 to 20.0 seconds. A vacuum cleaner fan hairdryer is audible from 0.1 to 19.9 seconds.
- `S-0008` (12 event): A voices is audible from 0.0 to 4.8 seconds. A vehicle idling is audible from 0.0 to 50.0 seconds. A vehicle pass by is audible from 0.0 to 50.0 seconds. A train is audible from 0.9 to 39.6 seconds. A lawn mower brush cutter olive shaker is audible from 1.0 to 9.2 seconds. A vacuum cleaner fan hairdryer is audible from 10.0 to 17.3 seconds. A voices is audible from 22.3 to 50.0 seconds. A music is audible from 22.3 to 29.8 seconds. A lawn mower brush cutter olive shaker is audible from 31.1 to 39.4 seconds. A music is audible from 36.0 to 43.1 seconds. A horn is audible from 40.0 to 41.0 seconds. A siren- or alarm-like sound is audible from 40.2 to 43.2 seconds.