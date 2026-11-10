# Câu trả lời ràng buộc evidence (6.8) — corpus `validation`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 58/96 | 0.888 |
| structured_only/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 59/96 | 0.917 |
| hybrid/en | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 58/96 | 0.918 |
| hybrid/vi | 96 | 96/96 | 0.000 | 96/96 | 96/96 | 59/96 | 0.947 |

## Ví dụ

- `q-001` hybrid/en: 4 of the top 4 results satisfy the filters. In datased:S-0032, vehicle pass-by at 75.5–88.7 s. In datased:S-0025, vehicle pass-by at 82.9–91.6 s. In datased:S-0690, vehicle pass-by at 110.3–113.5 s.
- `q-001` hybrid/vi: 4 trong 4 kết quả đầu thoả bộ lọc. Trong datased:S-0032, tiếng xe chạy qua ở 75,5–88,7 giây. Trong datased:S-0025, tiếng xe chạy qua ở 82,9–91,6 giây. Trong datased:S-0690, tiếng xe chạy qua ở 110,3–113,5 giây.
- `q-049` hybrid/en: No indexed recording satisfies the applied filters.
- `q-049` hybrid/vi: Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.
