# Câu trả lời ràng buộc evidence (6.8) — corpus `test`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 69/97 | 0.869 |
| structured_only/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 66/97 | 0.892 |
| hybrid/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 69/97 | 0.881 |
| hybrid/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 66/97 | 0.917 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0185, vehicle pass-by at 0.0–125.8 s. In datased:S-0277, vehicle pass-by at 0.6–19.6 s. In datased:S-0040, vehicle pass-by at 52.7–70.0 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0185, tiếng xe chạy qua ở 0,0–125,8 giây. Trong datased:S-0277, tiếng xe chạy qua ở 0,6–19,6 giây. Trong datased:S-0040, tiếng xe chạy qua ở 52,7–70,0 giây.
- `q-049` hybrid/en: 1 of the top 1 results satisfy the filters. In datased:S-0332, vehicle pass-by at 0.0–29.4 s, then vehicle idling at 40.0–50.0 s.
- `q-049` hybrid/vi: 1 trong 1 kết quả đầu thoả bộ lọc. Trong datased:S-0332, tiếng xe chạy qua ở 0,0–29,4 giây, sau đó tiếng động cơ xe chạy không tải ở 40,0–50,0 giây.
