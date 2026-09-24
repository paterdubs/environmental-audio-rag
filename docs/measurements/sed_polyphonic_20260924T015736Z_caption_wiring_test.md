# Verify wiring caption + grounding — `sed_polyphonic_20260924T015736Z` (test)

> Sinh bởi `scripts.generate_captions ml\runs\sed_polyphonic_20260924T015736Z --split test`. Kiểm wiring end-to-end trên dự đoán thật đã đóng băng — không phải kết quả nghiên cứu W5 (chưa có nhánh unconstrained/constrained đối chứng).

## Tổng quan

| | |
|---|---:|
| Recording | 142 |
| Recording có ≥1 event | 142 |
| Tổng event | 804 |
| Event nhiều nhất trong 1 recording | 32 |
| Recording lệch bất biến G1-G3 (kỳ vọng 0) | 0 |
| `document_builder` lỗi (kỳ vọng 0) | 0 |
| Polyphony lớn nhất quan sát được | 6 |

Không có recording nào lệch bất biến hallucination=0/omission=0/coverage=1/forbidden=0/temporal_order=1 — pipeline canonicalize→caption→grounding chạy đúng trên dự đoán thật, kể cả recording nhiều event.
`document_builder` (W6 6.3) chạy không lỗi trên mọi recording, kể cả polyphony tới 6 — fixture cũ chỉ có 2 event/1 mức polyphony.

## Ví dụ (ưu tiên recording nhiều event)

- `S-0003` (11 event): A birds is audible from 0.0 to 5.3 seconds. A vehicle pass by is audible from 0.0 to 10.0 seconds. A vehicle idling is audible from 0.7 to 5.5 seconds. A train is audible from 10.0 to 26.1 seconds. A voices is audible from 27.3 to 43.9 seconds. A vehicle idling is audible from 30.0 to 40.0 seconds. A music is audible from 30.0 to 46.0 seconds. A chicken coop is audible from 38.8 to 44.0 seconds. A vehicle pass by is audible from 62.8 to 66.0 seconds. A voices is audible from 70.0 to 97.4 seconds. A music is audible from 88.8 to 100.0 seconds.
- `S-0007` (4 event): A voices is audible from 0.0 to 4.7 seconds. A vehicle idling is audible from 0.0 to 4.9 seconds. A vehicle pass by is audible from 4.0 to 16.6 seconds. A train is audible from 4.8 to 20.0 seconds.
- `S-0008` (9 event): A voices is audible from 0.0 to 4.0 seconds. A vehicle pass by is audible from 3.3 to 20.0 seconds. A vehicle idling is audible from 3.3 to 50.0 seconds. A voices is audible from 20.0 to 38.0 seconds. A chicken coop is audible from 25.1 to 29.3 seconds. A music is audible from 29.5 to 41.3 seconds. A train is audible from 37.4 to 47.8 seconds. A voices is audible from 48.5 to 50.0 seconds. A horn is audible from 49.3 to 50.0 seconds.