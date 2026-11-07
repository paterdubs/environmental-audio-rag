# Câu trả lời ràng buộc evidence (6.8) — corpus `validation`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 61/96 | 0.953 |
| structured_only/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 61/96 | 0.953 |
| hybrid/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 61/96 | 0.939 |
| hybrid/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 61/96 | 0.939 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0032, vehicle pass-by at 74.7–88.4 s. In datased:S-0025, vehicle pass-by at 81.8–91.3 s. In datased:S-0228, vehicle pass-by at 1.5–15.0 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0032, tiếng xe chạy qua ở 74,7–88,4 giây. Trong datased:S-0030, tiếng xe chạy qua ở 89,6–141,4 giây. Trong datased:S-0228, tiếng xe chạy qua ở 1,5–15,0 giây.
- `q-049` hybrid/en: No indexed recording satisfies the applied filters.
- `q-049` hybrid/vi: Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.
