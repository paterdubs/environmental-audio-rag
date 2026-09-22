# Tests

Ưu tiên test cho ranh giới có thể làm sai kết luận:

- Taxonomy/class order consistency.
- Archive and annotation validation.
- Duplicate groups không xuyên split.
- Onset/offset ↔ frame conversion.
- Window clipping và padding mask.
- Caption không nhắc event ngoài timeline.
- Retrieval hard filters không bị semantic ranker bỏ qua.
- API/inference contract version compatibility.

Không viết test chỉ lặp lại implementation hoặc snapshot số không có ý nghĩa.

