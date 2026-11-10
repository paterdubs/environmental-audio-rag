# Câu trả lời ràng buộc evidence (6.8) — corpus `test`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 62/97 | 0.926 |
| structured_only/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 62/97 | 0.926 |
| hybrid/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 62/97 | 0.899 |
| hybrid/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 62/97 | 0.912 |

## Ví dụ

- `q-001` hybrid/en: 9 of the top 9 results satisfy the filters. In datased:S-0017, vehicle pass-by at 0.1–7.1 s. In datased:S-0274, vehicle pass-by at 0.9–15.7 s. In datased:S-0277, vehicle pass-by at 0.9–19.5 s.
- `q-001` hybrid/vi: 9 trong 9 kết quả đầu thoả bộ lọc. Trong datased:S-0274, tiếng xe chạy qua ở 0,9–15,7 giây. Trong datased:S-0017, tiếng xe chạy qua ở 0,1–7,1 giây. Trong datased:S-0277, tiếng xe chạy qua ở 0,9–19,5 giây.
- `q-049` hybrid/en: No indexed recording satisfies the applied filters.
- `q-049` hybrid/vi: Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.
