# Đánh giá parser câu hỏi thành bộ lọc

> Chỉ đo chuyển câu hỏi thành filter; không đọc audio, dev/test annotation hay output SED. Tập `template` là cận trên vì câu hỏi sinh từ mẫu; tập `paraphrase` gồm 40 câu viết tay đã commit trước lần chạy parser đầu tiên.

Model `Qwen3.5-9B`, prompt `query-filter-prompt-v1`, greedy temperature 0, seed 20260922; git `3d678979`, dirty=`false`.

| Tập | n | Parse thành công | Exact toàn filter | P lớp | R lớp | Đúng predicate |
|---|---:|---:|---:|---:|---:|---:|
| paraphrase | 40 | 0.975 (39/40) | 0.925 (37/40) | 1.000 | 0.983 | 1.000 (10) |
| template | 200 | 0.990 (198/200) | 0.850 (170/200) | 1.000 | 0.990 | 0.750 (60) |

## Diễn giải bắt buộc

Exact match yêu cầu đúng toàn bộ filter sau chuẩn hóa; `classes_all` không xét thứ tự, còn vai trò temporal `a`/`b` có xét thứ tự. Lỗi parse được tính là sai, không thay bằng filter gold. Số template không đại diện câu hỏi tự do.
