# Kịch bản demo — lượt chạy thật

- Upload mới: `S-0036` → `upload:14602c83-3dc7-43f8-a1e1-01872969341d` (TRAIN).

| # | Ngôn ngữ | Câu hỏi | Bộ lọc parse | Số evidence |
|---:|---|---|---|---:|
| 1 | vi | Bản ghi nào có tiếng động cơ xe chạy không tải? | `{"classes_all": ["vehicle_idling"]}` | 3 |
| 2 | en | Which recordings contain both vehicle idling and horn? | `{"classes_all": ["vehicle_idling", "horn"]}` | 6 |
| 3 | vi | Có tiếng động cơ xe chạy không tải trước tiếng còi xe không? | `{"temporal": {"predicate": "before", "a": "vehicle_idling", "b": "horn", "tolerance_s": 0.0}}` | 2 |
| 4 | en | Which recordings have vehicle idling lasting longer than 44.89 seconds? | `{"duration": {"class_id": "vehicle_idling", "min_s": 44.89}}` | 2 |
| 5 | vi | Bản ghi nào có tiếng còi xe? | `{"classes_all": ["horn"]}` | 3 |

Grounding minh hoạ lấy từ artifact W5 f2 đã có, không chạy lại chấm test:
`docs/measurements/caption_grounding_sed_ensemble_s13_f2_20260929T045053Z_test_annotated.json`.
