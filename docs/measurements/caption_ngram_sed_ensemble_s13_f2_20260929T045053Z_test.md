# N-gram caption (chỉ tham khảo) — `sed_ensemble_s13_f2_20260929T045053Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.5681 | 0.3689 | 3.8169 |
| constrained/oracle | 142 | 0.4278 | 0.2700 | 1.6348 |
| constrained_cover/e2e | 142 | 0.5670 | 0.3659 | 3.8312 |
| constrained_cover/oracle | 142 | 0.5887 | 0.3625 | 1.7671 |
| unconstrained/e2e | 142 | 0.1711 | 0.0279 | 0.1436 |
| unconstrained/oracle | 142 | 0.0474 | 0.0052 | 0.0691 |
