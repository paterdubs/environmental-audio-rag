# Verify wiring caption + grounding — `sed_polyphonic_20260924T015736Z` (test)

> Sinh bởi `scripts.generate_captions ml\runs\sed_polyphonic_20260924T015736Z --split test`. Kiểm wiring end-to-end trên dự đoán thật đã đóng băng — không phải kết quả nghiên cứu W5 (chưa có nhánh unconstrained/constrained đối chứng).

## Tổng quan

| | |
|---|---:|
| Recording | 142 |
| Recording có ≥1 event | 142 |
| Tổng event | 655 |
| Event nhiều nhất trong 1 recording | 28 |
| Recording lệch bất biến G1-G3 (kỳ vọng 0) | 0 |
| `document_builder` lỗi (kỳ vọng 0) | 0 |
| Polyphony lớn nhất quan sát được | 5 |

Không có recording nào lệch bất biến hallucination=0/omission=0/coverage=1/forbidden=0/temporal_order=1 — pipeline canonicalize→caption→grounding chạy đúng trên dự đoán thật, kể cả recording nhiều event.
`document_builder` (W6 6.3) chạy không lỗi trên mọi recording, kể cả polyphony tới 5 — fixture cũ chỉ có 2 event/1 mức polyphony.

## Ví dụ (ưu tiên recording nhiều event)

- `S-0003` (9 event): A birds is audible from 0.0 to 5.3 seconds. A vehicle pass by is audible from 0.0 to 10.0 seconds. A vehicle idling is audible from 0.7 to 5.5 seconds. A train is audible from 10.0 to 26.1 seconds. A voices is audible from 28.0 to 40.0 seconds. A vehicle idling is audible from 30.0 to 40.0 seconds. A music is audible from 30.0 to 46.0 seconds. A voices is audible from 70.0 to 92.6 seconds. A music is audible from 88.1 to 95.7 seconds.
- `S-0007` (4 event): A voices is audible from 0.0 to 4.1 seconds. A vehicle idling is audible from 0.0 to 4.9 seconds. A vehicle pass by is audible from 4.7 to 13.2 seconds. A train is audible from 4.8 to 16.8 seconds.
- `S-0008` (5 event): A vehicle idling is audible from 3.3 to 46.9 seconds. A vehicle pass by is audible from 3.4 to 20.0 seconds. A voices is audible from 20.0 to 36.9 seconds. A music is audible from 29.5 to 38.2 seconds. A horn is audible from 46.2 to 46.9 seconds.