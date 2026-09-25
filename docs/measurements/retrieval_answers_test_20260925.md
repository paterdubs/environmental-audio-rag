# Câu trả lời ràng buộc evidence (6.8) — corpus `test`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 96/97 | 0.482 |
| structured_only/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 96/97 | 0.482 |
| hybrid/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 96/97 | 0.454 |
| hybrid/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 96/97 | 0.433 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0681, vehicle pass-by at 0.0–17.5 s. In datased:S-0495, vehicle pass-by at 0.0–36.8 s. In datased:S-0277, vehicle pass-by at 1.0–20.3 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0245, tiếng xe chạy qua ở 0,0–16,4 giây. Trong datased:S-0495, tiếng xe chạy qua ở 0,0–36,8 giây. Trong datased:S-0681, tiếng xe chạy qua ở 0,0–17,5 giây.
- `q-049` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0332, vehicle pass-by at 0.0–70.0 s, then vehicle idling at 94.4–98.3 s. In datased:S-0412, vehicle pass-by at 3.3–20.0 s, then vehicle idling at 130.0–151.7 s. In datased:S-0717, vehicle pass-by at 0.0–19.5 s, then vehicle idling at 105.4–138.1 s.
- `q-049` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0332, tiếng xe chạy qua ở 0,0–70,0 giây, sau đó tiếng động cơ xe chạy không tải ở 94,4–98,3 giây. Trong datased:S-0716, tiếng xe chạy qua ở 0,0–35,8 giây, sau đó tiếng động cơ xe chạy không tải ở 101,4–119,9 giây. Trong datased:S-0042, tiếng xe chạy qua ở 0,0–20,7 giây, sau đó tiếng động cơ xe chạy không tải ở 190,0–200,0 giây.
