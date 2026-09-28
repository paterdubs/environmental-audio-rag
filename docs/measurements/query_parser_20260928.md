# Đánh giá parser câu hỏi thành bộ lọc

> Chỉ đo chuyển câu hỏi thành filter; không đọc audio, dev/test annotation hay output SED. Tập `template` là cận trên vì câu hỏi sinh từ mẫu; tập `paraphrase` gồm 40 câu viết tay đã commit trước lần chạy parser đầu tiên.

Model `Qwen3.5-9B`, prompt `query-filter-prompt-v1.1`, greedy temperature 0, seed 20260922; git `38bcf536`, dirty=`false`.

| Tập | n | Parse thành công | Exact toàn filter | P lớp | R lớp | Đúng predicate |
|---|---:|---:|---:|---:|---:|---:|
| paraphrase | 40 | 1.000 (40/40) | 0.925 (37/40) | 0.984 | 1.000 | 1.000 (10) |
| template | 200 | 1.000 (200/200) | 0.855 (171/200) | 1.000 | 1.000 | 0.767 (60) |

## Diễn giải bắt buộc

Exact match yêu cầu đúng toàn bộ filter sau chuẩn hóa; `classes_all` không xét thứ tự, còn vai trò temporal `a`/`b` có xét thứ tự. Lỗi parse được tính là sai, không thay bằng filter gold. Số template không đại diện câu hỏi tự do.
