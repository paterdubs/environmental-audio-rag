# Bảng kiểm soát leakage D3/D4

> Sinh tự động bởi `scripts.build_thesis_tables` tại git `0b2069f`.

| Cổng | Chỉ báo | Kết quả | Diễn giải |
|---|---|---:|---|
| D3 | Cặp ứng viên T1/T2/T3 | 24/24/45191 | Audit 3 tầng |
| D3 | Nhóm duplicate | 84 | Nội bộ và xuyên dataset |
| D3 | Nhóm xuyên DataSEC–DataSED | 3 | Đã gom theo leakage group |
| D3 | Clip pretraining bị loại | 11 | Trùng DataSED dev/test |
| D4 | Cổng DataSEC | PASS | 5/5 kiểm tra đạt |
| D4 | Cổng DataSED | PASS | 5/5 kiểm tra đạt |

**Nguồn:** `data/manifests/duplicate_audit.json`; `data/manifests/datasec_leakage_report.json`; `data/manifests/datased_leakage_report.json`; `data/splits/datasec_classification.frozen.json`.
