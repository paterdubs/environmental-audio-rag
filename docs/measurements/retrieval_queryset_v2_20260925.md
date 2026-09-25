# Query set v2 — nhóm và độ phủ relevance

> Sinh bởi `scripts.build_query_set`. `retrieval_queryset_v2.json` sha256 `e900fec3…`. Câu hỏi chọn theo ground truth **train** (ADR-0027); độ phủ dev/test dưới đây chỉ để báo, không dùng để chọn.

| Nhóm | Số câu |
|---|---:|
| single_class | 21 |
| multi_class | 27 |
| temporal | 30 |
| duration | 22 |

| Split | recording | câu có ≥1 relevant | theo nhóm | trung vị relevant |
|---|---:|---:|---|---:|
| train | 438 | 100/100 | single_class 21, multi_class 27, temporal 30, duration 22 | 15 |
| validation | 137 | 96/100 | single_class 21, multi_class 26, temporal 27, duration 22 | 5 |
| test | 142 | 97/100 | single_class 21, multi_class 26, temporal 28, duration 22 | 5.5 |
