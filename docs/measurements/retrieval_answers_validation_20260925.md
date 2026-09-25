# Câu trả lời ràng buộc evidence (6.8) — corpus `validation`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 96/96 | 0.442 |
| structured_only/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 96/96 | 0.442 |
| hybrid/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 96/96 | 0.460 |
| hybrid/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 96/96 | 0.475 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0216, vehicle pass-by at 0.0–23.1 s. In datased:S-0309, vehicle pass-by at 0.0–4.9 s. In datased:S-0510, vehicle pass-by at 0.0–8.0 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0216, tiếng xe chạy qua ở 0,0–23,1 giây. Trong datased:S-0309, tiếng xe chạy qua ở 0,0–4,9 giây. Trong datased:S-0345, tiếng xe chạy qua ở 0,0–20,4 giây.
- `q-049` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0703, vehicle pass-by at 0.0–20.0 s, then vehicle idling at 72.7–90.0 s. In datased:S-0409, vehicle pass-by at 0.0–30.0 s, then vehicle idling at 59.2–65.9 s. In datased:S-0033, vehicle pass-by at 33.8–50.7 s, then vehicle idling at 56.0–67.7 s.
- `q-049` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0703, tiếng xe chạy qua ở 0,0–20,0 giây, sau đó tiếng động cơ xe chạy không tải ở 72,7–90,0 giây. Trong datased:S-0409, tiếng xe chạy qua ở 0,0–30,0 giây, sau đó tiếng động cơ xe chạy không tải ở 59,2–65,9 giây. Trong datased:S-0275, tiếng xe chạy qua ở 0,0–26,9 giây, sau đó tiếng động cơ xe chạy không tải ở 97,3–114,1 giây.
