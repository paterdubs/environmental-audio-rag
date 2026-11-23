# Độ trễ demo `lbrv3` (bản ghi TRAIN)

> Sinh bởi `scripts.report_latency`; chỉ upload TRAIN, không chấm metric.

Hệ phục vụ: `ml/runs/sed_served_B0_20261107T175659Z`, thiết bị `cpu`, LBR `ml/runs/sed_lbr_B0v3_20261110T042337Z` điểm `recall_first`.

| Đại lượng | n | Trung vị | p95 | Lớn nhất |
|---|---:|---:|---:|---:|
| Tải lên + phân tích (s) | 10 | 3.89 | 11.96 | 11.96 |
| RTF (thời gian xử lý / độ dài âm thanh) | 10 | 0.072 | 0.294 | 0.294 |
| Truy vấn kết hợp (s) | 5 | 0.221 | 0.302 | 0.302 |

Độ dài âm thanh 3.4 đến 179.6 s.

| Bản ghi | Độ dài (s) | Xử lý (s) | RTF | Bộ nhớ container |
|---|---:|---:|---:|---|
| S-0376 | 3.4 | 0.99 | 0.294 | 1.24GiB / 7.387GiB |
| S-0251 | 16.0 | 1.56 | 0.098 | 1.24GiB / 7.387GiB |
| S-0354 | 25.1 | 2.04 | 0.081 | 1.24GiB / 7.387GiB |
| S-0132 | 34.3 | 2.41 | 0.070 | 1.24GiB / 7.387GiB |
| S-0488 | 49.4 | 3.66 | 0.074 | 1.24GiB / 7.387GiB |
| S-0225 | 67.6 | 4.13 | 0.061 | 1.24GiB / 7.387GiB |
| S-0439 | 87.9 | 6.13 | 0.070 | 1.241GiB / 7.387GiB |
| S-0384 | 108.1 | 10.37 | 0.096 | 1.241GiB / 7.387GiB |
| S-0480 | 123.7 | 7.90 | 0.064 | 1.241GiB / 7.387GiB |
| S-0049 | 144.7 | bỏ qua (đã có) | — | — |
| S-0672 | 179.6 | 11.96 | 0.067 | 1.24GiB / 7.387GiB |
| S-0713 | 818.3 | bỏ qua (đã có) | — | — |
