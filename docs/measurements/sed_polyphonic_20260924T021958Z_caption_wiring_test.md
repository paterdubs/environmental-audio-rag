# Verify wiring caption + grounding — `sed_polyphonic_20260924T021958Z` (test)

> Sinh bởi `scripts.generate_captions ml\runs\sed_polyphonic_20260924T021958Z --split test`. Kiểm wiring end-to-end trên dự đoán thật đã đóng băng — không phải kết quả nghiên cứu W5 (chưa có nhánh unconstrained/constrained đối chứng).

## Tổng quan

| | |
|---|---:|
| Recording | 142 |
| Recording có ≥1 event | 139 |
| Tổng event | 704 |
| Event nhiều nhất trong 1 recording | 18 |
| Recording lệch bất biến G1-G3 (kỳ vọng 0) | 0 |
| `document_builder` lỗi (kỳ vọng 0) | 0 |
| Polyphony lớn nhất quan sát được | 5 |

Không có recording nào lệch bất biến hallucination=0/omission=0/coverage=1/forbidden=0/temporal_order=1 — pipeline canonicalize→caption→grounding chạy đúng trên dự đoán thật, kể cả recording nhiều event.
`document_builder` (W6 6.3) chạy không lỗi trên mọi recording, kể cả polyphony tới 5 — fixture cũ chỉ có 2 event/1 mức polyphony.

## Ví dụ (ưu tiên recording nhiều event)

- `S-0003` (6 event): A jet aircrafts is audible from 0.0 to 64.7 seconds. A train is audible from 4.5 to 20.0 seconds. A voices is audible from 28.0 to 44.6 seconds. A vehicle idling is audible from 35.3 to 40.0 seconds. A voices is audible from 68.7 to 96.8 seconds. A music is audible from 88.3 to 100.0 seconds.
- `S-0007` (2 event): A train is audible from 0.0 to 20.0 seconds. A vehicle pass by is audible from 6.1 to 12.0 seconds.
- `S-0008` (12 event): A voices is audible from 0.0 to 3.0 seconds. A train is audible from 5.1 to 50.0 seconds. A vehicle idling is audible from 16.7 to 19.3 seconds. A voices is audible from 17.3 to 40.6 seconds. A impulsive sound resembling thunder, fireworks, or a gunshot is audible from 19.6 to 40.2 seconds. A glass breaking is audible from 20.0 to 22.1 seconds. A glass breaking is audible from 25.0 to 30.0 seconds. A workshop is audible from 27.3 to 30.0 seconds. A glass breaking is audible from 35.5 to 37.4 seconds. A glass breaking is audible from 48.1 to 50.0 seconds. A impulsive sound resembling thunder, fireworks, or a gunshot is audible from 48.7 to 50.0 seconds. A horn is audible from 48.9 to 50.0 seconds.