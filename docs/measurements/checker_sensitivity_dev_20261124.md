# Độ nhạy bộ chấm ảo giác (dev, mô tả đầu–cuối của bốn hệ SED)

> Sinh bởi `scripts.report_checker_sensitivity`; tỷ lệ nhiễu bị bắt (bắt/tổng).

| Nhánh | swap_canonical | swap_synonym | insert_class | insert_oov |
|---|---:|---:|---:|---:|
| unconstrained | 0.998 (464/465) | 1.000 (465/465) | 1.000 (536/536) | 0.623 (334/536) |
| constrained | 1.000 (465/465) | 1.000 (465/465) | 1.000 (536/536) | 0.623 (334/536) |
| template | 1.000 (465/465) | 1.000 (465/465) | 1.000 (536/536) | 0.623 (334/536) |
| constrained_cover | 1.000 (465/465) | 1.000 (465/465) | 1.000 (536/536) | 0.623 (334/536) |
| gộp | 0.999 (1859/1860) | 1.000 (1860/1860) | 1.000 (2144/2144) | 0.623 (1336/2144) |

| Nguồn ngoài taxonomy | Bị bắt |
|---|---:|
| a baby crying | 1.000 (268/268) |
| a door slamming | 1.000 (268/268) |
| a hammer striking | 0.000 (0/268) |
| rain falling | 1.000 (268/268) |
| a crowd cheering | 1.000 (268/268) |
| a cat meowing | 0.985 (264/268) |
| a clock ticking | 0.000 (0/268) |
| a phone vibrating | 0.000 (0/268) |
