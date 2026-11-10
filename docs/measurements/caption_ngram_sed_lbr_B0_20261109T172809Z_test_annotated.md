# N-gram caption (chỉ tham khảo) — `sed_lbr_B0_20261109T172809Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.5524 | 0.3584 | 3.5997 |
| constrained_cover/e2e | 139 | 0.5614 | 0.3639 | 3.6307 |
| unconstrained/e2e | 139 | 0.1222 | 0.0147 | 0.1164 |
