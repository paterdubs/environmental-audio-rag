# RQ3: vì sao bản ghi liên quan lọt khỏi top-10 của hybrid (validation, gold, EN)

> Sinh bởi `scripts.report_rq3_failures` từ danh sách đã lưu.

| Kho | Nhóm | Cặp liên quan | Trúng | SED bỏ sót | Ngoài top-10 hoặc bỏ sót | Trả về không liên quan / tổng trả về |
|---|---|---:|---:|---:|---:|---:|
| f2 | all | 706 | 266 | 346 | 94 | 15 / 281 |
| f2 | duration | 203 | 96 | 81 | 26 | 10 / 106 |
| f2 | multi_class | 112 | 17 | 93 | 2 | 0 / 17 |
| f2 | single_class | 272 | 114 | 98 | 60 | 4 / 118 |
| f2 | temporal | 119 | 39 | 74 | 6 | 1 / 40 |
| B0 | all | 706 | 286 | 300 | 120 | 18 / 304 |
| B0 | duration | 203 | 107 | 63 | 33 | 10 / 117 |
| B0 | multi_class | 112 | 18 | 92 | 2 | 1 / 19 |
| B0 | single_class | 272 | 127 | 68 | 77 | 3 / 130 |
| B0 | temporal | 119 | 34 | 77 | 8 | 4 / 38 |
| lbrv2 | all | 706 | 229 | 417 | 60 | 10 / 239 |
| lbrv2 | duration | 203 | 77 | 114 | 12 | 5 / 82 |
| lbrv2 | multi_class | 112 | 15 | 95 | 2 | 0 / 15 |
| lbrv2 | single_class | 272 | 101 | 131 | 40 | 5 / 106 |
| lbrv2 | temporal | 119 | 36 | 77 | 6 | 0 / 36 |
| lbrv3 | all | 706 | 397 | 108 | 201 | 222 / 619 |
| lbrv3 | duration | 203 | 134 | 16 | 53 | 32 / 166 |
| lbrv3 | multi_class | 112 | 56 | 41 | 15 | 73 / 129 |
| lbrv3 | single_class | 272 | 136 | 9 | 127 | 48 / 184 |
| lbrv3 | temporal | 119 | 71 | 42 | 6 | 69 / 140 |

| Kho | Truy vấn có danh sách hybrid khác khi dùng bộ lọc parser |
|---|---:|
| f2 | 5/96 |
| B0 | 7/96 |
| lbrv2 | 6/96 |
| lbrv3 | 10/96 |
