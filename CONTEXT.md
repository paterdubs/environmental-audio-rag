# CONTEXT.md — Bối cảnh sống

## Mục tiêu hiện tại

Dựng pipeline tối thiểu tái lập được:

```text
download metadata → verify archives → normalize labels → audit duplicates → freeze splits
```

Sau cổng dữ liệu mới triển khai baseline classification và SED.

## Quyết định đã chốt

- Dataset chính: DataSEC + DataSED.
- DataSEC: pretraining/classification/subclass refinement.
- DataSED polyphonic: benchmark SED chính, 21 class.
- DataSED monophonic: benchmark phụ, 22 class.
- Caption phải được sinh từ timeline; không dùng text tự do làm nguồn sự kiện.
- RAG trả lời từ event record và caption đã lưu, kèm recording/time evidence.
- Dự án độc lập với `audio-security-rag`; không import artifact hoặc quyết định ngầm từ dự án cũ.

## Chưa chốt

- Audio encoder baseline và proposed model.
- Thresholding/post-processing strategy.
- Embedding model cho retrieval.
- Database triển khai cuối.
- Cách đánh giá subclass trên continuous audio do DataSED không có subclass ground truth.

## Việc tiếp theo

Xem `docs/PLAN.md`, milestone M0 và M1.

