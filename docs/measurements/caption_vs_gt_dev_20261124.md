# RQ2 ba tầng: mô tả so với dòng thời gian dự đoán và với nhãn gốc (dev, annotated)

> Sinh bởi `scripts.report_caption_vs_gt`; chỉ đọc mô tả dev đã sinh. Ô: trung bình theo bản ghi [CI 95% bootstrap].

## Tỷ lệ ảo giác

| Hệ | Nhánh | n | oracle | e2e so với dự đoán | e2e so với nhãn gốc |
|---|---|---:|---:|---:|---:|
| f2 | template | 134 | 0.000 | 0.000 | 0.011 [0.000, 0.030] |
| f2 | unconstrained | 134 | 0.009 | 0.015 | 0.026 [0.010, 0.047] |
| f2 | constrained | 134 | 0.000 | 0.000 | 0.011 [0.000, 0.030] |
| f2 | constrained_cover | 134 | 0.000 | 0.000 | 0.011 [0.000, 0.030] |
| B0 | template | 134 | — | 0.000 | 0.019 [0.005, 0.039] |
| B0 | unconstrained | 134 | — | 0.012 | 0.034 [0.013, 0.060] |
| B0 | constrained | 134 | — | 0.000 | 0.017 [0.004, 0.038] |
| B0 | constrained_cover | 134 | — | 0.000 | 0.019 [0.005, 0.039] |
| lbrv2 | template | 134 | — | 0.000 | 0.022 [0.006, 0.045] |
| lbrv2 | unconstrained | 134 | — | 0.012 | 0.035 [0.014, 0.058] |
| lbrv2 | constrained | 134 | — | 0.000 | 0.019 [0.004, 0.039] |
| lbrv2 | constrained_cover | 134 | — | 0.000 | 0.022 [0.006, 0.045] |
| lbrv3 | template | 134 | — | 0.000 | 0.178 [0.142, 0.216] |
| lbrv3 | unconstrained | 134 | — | 0.011 | 0.234 [0.192, 0.275] |
| lbrv3 | constrained | 134 | — | 0.000 | 0.192 [0.146, 0.238] |
| lbrv3 | constrained_cover | 134 | — | 0.000 | 0.199 [0.160, 0.241] |

## Tỷ lệ bỏ sót

| Hệ | Nhánh | n | oracle | e2e so với dự đoán | e2e so với nhãn gốc |
|---|---|---:|---:|---:|---:|
| f2 | template | 134 | 0.000 | 0.000 | 0.373 [0.310, 0.432] |
| f2 | unconstrained | 134 | 0.018 | 0.000 | 0.370 [0.306, 0.430] |
| f2 | constrained | 134 | 0.084 | 0.007 | 0.378 [0.316, 0.437] |
| f2 | constrained_cover | 134 | 0.000 | 0.000 | 0.373 [0.310, 0.432] |
| B0 | template | 134 | — | 0.000 | 0.342 [0.283, 0.401] |
| B0 | unconstrained | 134 | — | 0.000 | 0.339 [0.281, 0.399] |
| B0 | constrained | 134 | — | 0.021 | 0.355 [0.295, 0.415] |
| B0 | constrained_cover | 134 | — | 0.000 | 0.342 [0.283, 0.401] |
| lbrv2 | template | 134 | — | 0.000 | 0.415 [0.345, 0.490] |
| lbrv2 | unconstrained | 134 | — | 0.000 | 0.412 [0.340, 0.486] |
| lbrv2 | constrained | 134 | — | 0.007 | 0.419 [0.348, 0.493] |
| lbrv2 | constrained_cover | 134 | — | 0.000 | 0.415 [0.345, 0.490] |
| lbrv3 | template | 134 | — | 0.000 | 0.107 [0.077, 0.140] |
| lbrv3 | unconstrained | 134 | — | 0.031 | 0.105 [0.074, 0.139] |
| lbrv3 | constrained | 134 | — | 0.145 | 0.204 [0.153, 0.253] |
| lbrv3 | constrained_cover | 134 | — | 0.000 | 0.107 [0.077, 0.140] |
