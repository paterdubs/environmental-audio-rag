# Câu trả lời ràng buộc evidence (6.8) — corpus `validation`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 94/96 | 0.613 |
| structured_only/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 94/96 | 0.613 |
| hybrid/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 94/96 | 0.635 |
| hybrid/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 94/96 | 0.631 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0275, vehicle pass-by at 1.0–20.8 s. In datased:S-0309, vehicle pass-by at 0.1–1.3 s. In datased:S-0237, vehicle pass-by at 0.2–0.7 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0309, tiếng xe chạy qua ở 0,1–1,3 giây. Trong datased:S-0174, tiếng xe chạy qua ở 25,0–40,3 giây. Trong datased:S-0030, tiếng xe chạy qua ở 0,0–2,3 giây.
- `q-049` hybrid/en: 4 of the top 4 results satisfy the filters. In datased:S-0275, vehicle pass-by at 1.0–20.8 s, then vehicle idling at 94.7–113.5 s. In datased:S-0293, vehicle pass-by at 91.6–93.3 s, then vehicle idling at 141.1–148.1 s. In datased:S-0544, vehicle pass-by at 6.4–7.9 s, then vehicle idling at 45.1–50.0 s.
- `q-049` hybrid/vi: 4 trong 4 kết quả đầu thoả bộ lọc. Trong datased:S-0275, tiếng xe chạy qua ở 1,0–20,8 giây, sau đó tiếng động cơ xe chạy không tải ở 94,7–113,5 giây. Trong datased:S-0293, tiếng xe chạy qua ở 91,6–93,3 giây, sau đó tiếng động cơ xe chạy không tải ở 141,1–148,1 giây. Trong datased:S-0544, tiếng xe chạy qua ở 6,4–7,9 giây, sau đó tiếng động cơ xe chạy không tải ở 45,1–50,0 giây.
