# N-gram caption (chỉ tham khảo) — `sed_ensemble_B0_final_test_20261014T085016Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.5684 | 0.3679 | 3.6924 |
| constrained_cover/e2e | 139 | 0.5700 | 0.3679 | 3.7774 |
| unconstrained/e2e | 139 | 0.1359 | 0.0228 | 0.1538 |
