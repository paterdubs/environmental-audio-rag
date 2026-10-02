# Câu trả lời ràng buộc evidence (6.8) — corpus `validation`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 57/96 | 0.938 |
| structured_only/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 57/96 | 0.952 |
| hybrid/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 57/96 | 0.925 |
| hybrid/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 57/96 | 0.932 |

## Ví dụ

- `q-001` hybrid/en: 7 of the top 7 results satisfy the filters. In datased:S-0021, vehicle pass-by at 10.0–60.0 s. In datased:S-0027, vehicle pass-by at 0.0–10.0 s. In datased:S-0033, vehicle pass-by at 109.2–130.0 s.
- `q-001` hybrid/vi: 7 trong 7 kết quả đầu thoả bộ lọc. Trong datased:S-0033, tiếng xe chạy qua ở 109,2–130,0 giây. Trong datased:S-0027, tiếng xe chạy qua ở 0,0–10,0 giây. Trong datased:S-0021, tiếng xe chạy qua ở 10,0–60,0 giây.
- `q-049` hybrid/en: No indexed recording satisfies the applied filters.
- `q-049` hybrid/vi: Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.
