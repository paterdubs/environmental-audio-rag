# RQ3: vì sao bản ghi liên quan lọt khỏi top-10 của hybrid (test, gold, EN)

> Sinh bởi `scripts.report_rq3_failures` từ danh sách đã lưu.

| Kho | Nhóm | Cặp liên quan | Trúng | SED bỏ sót | Ngoài top-10 hoặc bỏ sót | Trả về không liên quan / tổng trả về |
|---|---|---:|---:|---:|---:|---:|
| f2 | all | 705 | 277 | 350 | 78 | 23 / 300 |
| f2 | duration | 209 | 120 | 66 | 23 | 9 / 129 |
| f2 | multi_class | 119 | 16 | 103 | 0 | 3 / 19 |
| f2 | single_class | 272 | 128 | 89 | 55 | 7 / 135 |
| f2 | temporal | 105 | 13 | 92 | 0 | 4 / 17 |
| B0 | all | 705 | 261 | 349 | 95 | 21 / 282 |
| B0 | duration | 209 | 112 | 74 | 23 | 11 / 123 |
| B0 | multi_class | 119 | 9 | 110 | 0 | 1 / 10 |
| B0 | single_class | 272 | 126 | 74 | 72 | 6 / 132 |
| B0 | temporal | 105 | 14 | 91 | 0 | 3 / 17 |
| lbrv2 | all | 705 | 253 | 381 | 71 | 24 / 277 |
| lbrv2 | duration | 209 | 91 | 101 | 17 | 9 / 100 |
| lbrv2 | multi_class | 119 | 14 | 105 | 0 | 2 / 16 |
| lbrv2 | single_class | 272 | 129 | 89 | 54 | 12 / 141 |
| lbrv2 | temporal | 105 | 19 | 86 | 0 | 1 / 20 |
| lbrv3 | all | 705 | 417 | 127 | 161 | 138 / 555 |
| lbrv3 | duration | 209 | 144 | 18 | 47 | 39 / 183 |
| lbrv3 | multi_class | 119 | 66 | 53 | 0 | 30 / 96 |
| lbrv3 | single_class | 272 | 152 | 6 | 114 | 34 / 186 |
| lbrv3 | temporal | 105 | 55 | 50 | 0 | 35 / 90 |

| Kho | Truy vấn có danh sách hybrid khác khi dùng bộ lọc parser |
|---|---:|
| f2 | 7/97 |
| B0 | 5/97 |
| lbrv2 | 4/97 |
| lbrv3 | 12/97 |
