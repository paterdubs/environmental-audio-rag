# Kịch bản demo — lượt chạy thật

- Upload mới: `S-0049` → `upload:e422d64b-a9c7-4a5a-912d-7e0adaa56014` (TRAIN).

| # | Ngôn ngữ | Câu hỏi | Bộ lọc parse | Số evidence |
|---:|---|---|---|---:|
| 1 | vi | Bản ghi nào có tiếng người nói? | `{"classes_all": ["voices"]}` | 3 |
| 2 | en | Which recordings contain both voices and vehicle idling? | `{"classes_all": ["voices", "vehicle_idling"]}` | 6 |
| 3 | vi | Có tiếng người nói trước tiếng động cơ xe chạy không tải không? | `{"temporal": {"predicate": "before", "a": "voices", "b": "vehicle_idling", "tolerance_s": 0.0}}` | 2 |
| 4 | en | Which recordings have voices lasting longer than 20.22 seconds? | `{"duration": {"class_id": "voices", "min_s": 20.22}}` | 2 |
| 5 | vi | Bản ghi nào có tiếng động cơ xe chạy không tải? | `{"classes_all": ["vehicle_idling"]}` | 3 |

Grounding minh hoạ lấy từ artifact W5 f2 đã có, không chạy lại chấm test:
`docs/measurements/caption_grounding_sed_ensemble_s13_f2_20260929T045053Z_test_annotated.json`.
