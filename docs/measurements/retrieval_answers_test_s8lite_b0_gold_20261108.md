# Câu trả lời ràng buộc evidence (6.8) — corpus `test`

> Sinh bởi `scripts.evaluate_answers`. Bộ sinh tất định chỉ trích recording có event đã index thoả bộ lọc; bộ kiểm độc lập đọc lại văn bản bằng lexicon cùng ngôn ngữ (A1, A3). "Trích đúng GT" = tỷ lệ recording được trích mà ground truth cũng coi là relevant (đo chất lượng SED + retrieval, không phải grounding).

| Cấu hình / ngôn ngữ | n | Contract | Unsupported-claim ↓ | Evidence có thật | Trích thoả lọc | Có trả lời | Trích đúng GT |
|---|---:|---:|---:|---:|---:|---:|---:|
| structured_only/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 58/97 | 0.922 |
| structured_only/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 58/97 | 0.922 |
| hybrid/en | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 58/97 | 0.915 |
| hybrid/vi | 97 | 97/97 | 0.000 | 97/97 | 97/97 | 58/97 | 0.915 |

## Ví dụ

- `q-001` hybrid/en: 10 of the top 10 results satisfy the filters. In datased:S-0419, vehicle pass-by at 0.0–28.4 s. In datased:S-0186, vehicle pass-by at 4.2–114.6 s. In datased:S-0017, vehicle pass-by at 0.1–6.8 s.
- `q-001` hybrid/vi: 10 trong 10 kết quả đầu thoả bộ lọc. Trong datased:S-0186, tiếng xe chạy qua ở 4,2–114,6 giây. Trong datased:S-0017, tiếng xe chạy qua ở 0,1–6,8 giây. Trong datased:S-0185, tiếng xe chạy qua ở 0,0–125,0 giây.
- `q-049` hybrid/en: No indexed recording satisfies the applied filters.
- `q-049` hybrid/vi: Không bản ghi nào trong kho thoả bộ lọc đã áp dụng.
