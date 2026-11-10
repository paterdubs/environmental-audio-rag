# Câu trả lời ràng buộc evidence (6.8) — corpus `test`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 95/97 | 0.704 |
| structured_only/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 95/97 | 0.704 |
| hybrid/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 95/97 | 0.712 |
| hybrid/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 95/97 | 0.735 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0277, vehicle pass-by at 0.4–19.5 s. In datased:S-0274, vehicle pass-by at 0.4–16.4 s. In datased:S-0185, vehicle pass-by at 0.8–125.3 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0274, tiếng xe chạy qua ở 0,4–16,4 giây. Trong datased:S-0277, tiếng xe chạy qua ở 0,4–19,5 giây. Trong datased:S-0185, tiếng xe chạy qua ở 0,8–125,3 giây.
- `q-049` hybrid/en: 5 of the top 5 results satisfy the filters. In datased:S-0186, vehicle pass-by at 0.3–2.5 s, then vehicle idling at 45.0–54.0 s. In datased:S-0301, vehicle pass-by at 55.8–103.7 s, then vehicle idling at 116.0–168.3 s. In datased:S-0161, vehicle pass-by at 2.8–38.0 s, then vehicle idling at 41.6–78.0 s.
- `q-049` hybrid/vi: 5 trong 5 kết quả đầu thoả bộ lọc. Trong datased:S-0186, tiếng xe chạy qua ở 0,3–2,5 giây, sau đó tiếng động cơ xe chạy không tải ở 45,0–54,0 giây. Trong datased:S-0161, tiếng xe chạy qua ở 2,8–38,0 giây, sau đó tiếng động cơ xe chạy không tải ở 41,6–78,0 giây. Trong datased:S-0301, tiếng xe chạy qua ở 55,8–103,7 giây, sau đó tiếng động cơ xe chạy không tải ở 116,0–168,3 giây.
